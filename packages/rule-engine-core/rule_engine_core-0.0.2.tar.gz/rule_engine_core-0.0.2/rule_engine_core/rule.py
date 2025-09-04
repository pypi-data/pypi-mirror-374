"""
This module defines the Rule class, which represents a rule in the rule engine.
Each rule contains a combination of filters or existing rule.
Rules can be made in the following ways:
    -> Rule with filters: A rule can be created with a combination of filters. Filters can be either combined with binary operators or can be used as a single filter optionally with a unary operators.
    -> Rule with filters and existing rules: A rule can be created with a combination of filters and existing rules using binary operators.
    -> Rule with existing rules: A rule can be created with a combination of existing rules using binary operators.
The Rule class has following methods:
    -> validate: validates whether the operands of the rule are valid. The operands of rule being rules and filters. It queries the underlying store to check if filter and rule exist.
    -> evaluate: evaluates the rule against the given data. The evaluation is done by evaluating each operand and combining the results using the operator.
    -> __init__: initializes the Rule object with a string representing the expression string of the rule. The expression string is parsed to create a expression tree. The nodes of the tree are created using the Filter and Rule classes. The tree is then used to evaluate the rule.
"""

from rule_engine_core.metadata_store import MetadataStore
from rule_engine_core.entity_dao import EntityDao
from rule_engine_core.entity_types import EntityEnum, EntityNode
from rule_engine_core.entity_base import EntityBase
from rule_engine_core.parser import Node, OPERATOR_SET
import logging
from rule_engine_core.filter import Filter

_logger = logging.getLogger(__name__)

class Rule(EntityBase):
    def __init__(self, rule_name: str, expression: str, metadata_store: MetadataStore, entity_dao: EntityDao):
        """
        Initializes the Rule object with a string representing the expression string of the rule.
        The expression string is parsed to create a expression tree. The nodes of the tree are created using the Filter and Rule classes. The tree is then used to evaluate the rule.
        """
        super().__init__(expression, EntityEnum.RULE, rule_name)
        self.rule_name = rule_name
        self._metadata_store = metadata_store
        self._entity_dao = entity_dao
    
    def _validate_node(self, node: Node) -> bool:
        # Recursively validates the operands of the rule.
        if node is None:
            return True
        if node.value in OPERATOR_SET:
            return self._validate_node(node.left) and self._validate_node(node.right)

        # debug log if rule is a number or a field in the metadata store or an existing rule/filter in the database
        _logger.debug(f"Node: {node.value} is node a number {self._check_if_node_is_number(node.value)} or a field in the metadata store {self._metadata_store.does_field_exist(node.value)} or an existing filter in the database {self._entity_dao.entity_exists(EntityEnum.FILTER, node.value)} or existing rule in the database {self._entity_dao.entity_exists(EntityEnum.RULE, node.value)}")
        # todo: do we want the rules to have primary operands or just composed of rules and filters ?
        # check if node value is a number or a field in the metadata store or an existing filter in the database
        return self._check_if_node_is_number(node.value) or \
            self._metadata_store.does_field_exist(node.value) or \
            self._entity_dao.entity_exists(EntityEnum.FILTER, node.value) or \
            self._entity_dao.entity_exists(EntityEnum.RULE, node.value)

    def _evaluate_node(self, node: EntityNode, pos_data: dict[str, str|int|float], entity_eval_cache: dict[EntityEnum, dict[str, int|float|bool]], entity_cache: dict[EntityEnum, dict[str, EntityBase]]) -> float|int|bool:
        _logger.info(f"Evaluating rule {self.rule_name} with value {node.node.value} and node type {node.entity_type}")
        # Evaluates the node against the given data. And updates the cache with the result. 
        # check is rule_name is cached in entity_eval_cache
        if self.rule_name in entity_eval_cache[EntityEnum.RULE]:
            return entity_eval_cache[EntityEnum.RULE][self.rule_name]
        if node.entity_type != EntityEnum.RULE or node.node is None:
            raise ValueError(f"Invalid node type: {node.entity_type} or invalide node: {node.node}")
        
        if node.node.value not in OPERATOR_SET:
            raise ValueError(f"Invalid operator: {node.node.value}")
        
        def evaluate_node_or_leaf(node_ident: str) -> float|int|bool:
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
                        if entity_cache[EntityEnum.FILTER].get(node_ident, None) is None and \
                            entity_cache[EntityEnum.RULE].get(node_ident, None) is None:
                            err_msg = f"Filter {node_ident} is not a valid entity for this rule evaluation cycle. FIlter keys {entity_cache[EntityEnum.FILTER].keys()} Rule keys {entity_cache[EntityEnum.RULE].keys()}"
                            _logger.error(err_msg)
                            # propagata the error to the rule evaluation 
                            raise ValueError(err_msg)
                        if (node_ident in entity_cache[EntityEnum.FILTER] and entity_cache[EntityEnum.FILTER].get(node_ident).node_type is not EntityEnum.FILTER) or (node_ident in entity_cache[EntityEnum.RULE] and entity_cache[EntityEnum.RULE].get(node_ident).node_type is not EntityEnum.RULE):
                            err_msg = f"Filter {node_ident}: has bad expression tree"
                            _logger.error(err_msg)
                            # propagata the error to the rule evaluation 
                            raise ValueError(err_msg)
                        _logger.debug(f"Evaluating child node {node_ident} of type {EntityEnum.FILTER.value if node_ident in entity_cache[EntityEnum.FILTER] else EntityEnum.RULE.value}")
                        # import pdb; pdb.set_trace()
                        return entity_cache[EntityEnum.FILTER][node_ident].evaluate(pos_data, entity_eval_cache, entity_cache) if entity_cache[EntityEnum.FILTER][node_ident].node_type == EntityEnum.FILTER else \
                            entity_cache[EntityEnum.RULE][node_ident].evaluate(pos_data, entity_eval_cache, entity_cache)
                    
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
        entity_eval_cache[EntityEnum.RULE][self.rule_name] = result
        return result

