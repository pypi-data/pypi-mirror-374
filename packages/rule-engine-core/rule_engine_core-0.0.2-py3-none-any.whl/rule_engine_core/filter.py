"""
This module defines the Filter class, which represents a filter in the rule engine.
Each filter is a single condition that can be evaluated against a given data.
Filters can be combined with binary operators to create complex rules.
Example of unary filter: !x: which means !(bool(x))
Example of binary filter: x > 5 and y < 10: which means (x > 5) and (y < 10)
The filter operands are a set of variables from financial metadata, which are used to evaluate the filter. The various operands from the metadata are used to define various aspects of a financial transaction.
The Filter class has following methods:
    -> validate: validates whether the operands of the filter are valid. The operands of filter should be either present in our finance metadata or filters database if the filer is composed of more leaf level filters . It queries the underlying store to check if filter operands exist either in the financial metadata or the filters database.
    -> evaluate: evaluates the filter against the given data. The evaluation is done by evaluating each operand and combining the results using the operator.
    -> __init__: initializes the Filter object with a string representing the expression string of the filter. The expression string is parsed to create a expression tree. The nodes of the tree are created using the Filter class. The tree is then used to evaluate the filter.
"""

from rule_engine_core.parser import Node, OPERATOR_SET
from rule_engine_core.metadata_store import MetadataStore
from rule_engine_core.entity_dao import EntityDao
from rule_engine_core.entity_types import EntityEnum, EntityNode
from rule_engine_core.entity_base import EntityBase
import logging

_logger = logging.getLogger(__name__)

class Filter(EntityBase):
    """
    This class represents a filter in the rule engine.
    Each filter is a single condition that can be evaluated against a given data.
    Filters can be combined with binary operators to create complex rules.
    """

    def __init__(self, filter_name: str, expression: str, metadata_store: MetadataStore, entity_dao: EntityDao):
        """
        Initializes the Filter object with a string representing the expression string of the filter.
        The expression string is parsed to create a expression tree. The nodes of the tree are created using the Filter class. The tree is then used to evaluate the filter.
        """
        super().__init__(expression, EntityEnum.FILTER, filter_name)
        self.filter_name = filter_name
        self._metadata_store = metadata_store
        self._entity_dao = entity_dao

        
    def _validate_node(self, node: Node) -> bool:
        """
        Recursively validates the operands of the filter.
        """
        if node is None:
            return True

        if node.value in OPERATOR_SET:
            return self._validate_node(node.left) and self._validate_node(node.right)

        # make a debug log to check if the node is a number or a field in the metadata store or an existing filter in the database
        _logger.debug(f"Node: {node.value} is node a number {self._check_if_node_is_number(node.value)} or a field in the metadata store {self._metadata_store.does_field_exist(node.value)} or an existing filter in the database {self._entity_dao.entity_exists(EntityEnum.FILTER, node.value)}")
        # check if node value is a number or a field in the metadata store or an existing filter in the database
        return self._check_if_node_is_number(node.value) or \
            self._metadata_store.does_field_exist(node.value) or \
            self._entity_dao.entity_exists(EntityEnum.FILTER, node.value)
    
    def _evaluate_node(self, node: EntityNode, pos_data: dict[str, str|int|float], entity_eval_cache: dict[EntityEnum, dict[str, int|float|bool]], entity_cache: dict[EntityEnum, dict[str, EntityBase]]) -> float|int|bool:
        """
        Evaluates the node against the given data. And updates the cache with the result. 
        """
        _logger.info(f"Evaluating filter {self.filter_name} with value {node.node.value} and node type {node.entity_type}")
        # check is filter_name is cached in entity_eval_cache
        if self.filter_name in entity_eval_cache[EntityEnum.FILTER]:
            return entity_eval_cache[EntityEnum.FILTER][self.filter_name]
        if node.entity_type != EntityEnum.FILTER or node.node is None:
            raise ValueError(f"Invalid node type: {node.entity_type} or invalide node: {node.node}")
        
        if node.node.value not in OPERATOR_SET:
            raise ValueError(f"Invalid operator: {node.node.value}")
        
        def evaluate_node_or_leaf(node_ident: str) -> float|int|bool:
            # First check if the node_ident is a number (int/float)
            # then check is it is a metadata field and evaluate the value
            # from pos_data
            # then finally check if it is a filter in the database
            try:
                return int(node_ident)
            except ValueError:
                try:
                    return float(node_ident)
                except ValueError:
                    if self._metadata_store.does_field_exist(node_ident):
                        return pos_data[node_ident]
                    else:
                        # if not found in metadata store, evaluate the filter from struct
                        # since the filter has not been evaluated yet
                        if entity_cache[EntityEnum.FILTER].get(node_ident) is None:
                            err_msg = f"Filter {node_ident} is not a valid entity for this rule evaluation cycle"
                            _logger.error(err_msg)
                            # propagata the error to the rule evaluation 
                            raise ValueError(err_msg)
                        if entity_cache[EntityEnum.FILTER].get(node_ident).node_type is not EntityEnum.FILTER:
                            err_msg = f"Filter {node_ident}: has bad expression tree"
                            _logger.error(err_msg)
                            # propagata the error to the rule evaluation 
                            raise ValueError(err_msg)
                        return entity_cache[EntityEnum.FILTER][node_ident].evaluate(pos_data, entity_eval_cache, entity_cache)
        
        match node.node.value:
            case "!":
                # Unary not operator
                result = not evaluate_node_or_leaf(node.node.left.value)
            case "&":
                # Binary and operator
                result = evaluate_node_or_leaf(node.node.left.value) and \
                    evaluate_node_or_leaf(node.node.right.value)
            case "|":
                # Binary or operator
                result = evaluate_node_or_leaf(node.node.left.value) or \
                    evaluate_node_or_leaf(node.node.right.value)
            case ">":
                # bonary greater than operator
                result = evaluate_node_or_leaf(node.node.left.value) > \
                    evaluate_node_or_leaf(node.node.right.value)
            case "<":
                # Binary less than operator
                result = evaluate_node_or_leaf(node.node.left.value) < \
                    evaluate_node_or_leaf(node.node.right.value)
            case ">=":
                # Binary greater than or equal to operator
                result = evaluate_node_or_leaf(node.node.left.value) >= \
                    evaluate_node_or_leaf(node.node.right.value)
            case "<=":
                # Binary less than or equal to operator
                result = evaluate_node_or_leaf(node.node.left.value) <= \
                    evaluate_node_or_leaf(node.node.right.value)
            case "+":
                # Binary addition operator
                result = evaluate_node_or_leaf(node.node.left.value) + \
                    evaluate_node_or_leaf(node.node.right.value)
            case "-":
                # Binary subtraction operator
                result = evaluate_node_or_leaf(node.node.left.value) - \
                    evaluate_node_or_leaf(node.node.right.value)
            case "*":
                # Binary multiplication operator
                result = evaluate_node_or_leaf(node.node.left.value) * \
                    evaluate_node_or_leaf(node.node.right.value)
            case "/":
                # Binary division operator
                result = evaluate_node_or_leaf(node.node.left.value) / \
                    evaluate_node_or_leaf(node.node.right.value)
        entity_eval_cache[EntityEnum.FILTER][self.filter_name] = result
        return result