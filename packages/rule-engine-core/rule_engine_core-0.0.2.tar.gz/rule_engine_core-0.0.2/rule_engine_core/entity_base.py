"""
This is the base class for filter and rule entities.
"""

from abc import ABC, abstractmethod
from rule_engine_core.parser import Node, Parser

from rule_engine_core.entity_types import EntityEnum, EntityNode

class EntityBase(ABC):
    """
    Base class for entities like Filter and Rule.
    Provides a common implementation for evaluate and enforces validate implementation.
    """

    def __init__(self, expression: str, node_type: EntityEnum, name: str):
        """
        Initializes the entity with an expression string and parses it into an expression tree.
        """
        self.expression = expression
        self.expression_tree: Node = self._parse_expression(expression)
        self.node_type = node_type
        self.name = name

    def validate(self) -> bool:
        """
        Validates whether the operands of the entity are valid.
        _validate_node must be implemented by subclasses
        """
        return self._validate_node(self.expression_tree)

    @abstractmethod
    def _validate_node(self, node: Node) -> bool:
        """
        Validates the operands of the entity.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _evaluate_node(self, node: Node, data: dict, entity_cache: dict, entity_eval_cache) -> float|int|bool:
        """
        Evaluates a single node of the expression tree.
        Must be implemented by subclasses.
        """
        pass
    """
    During eval, entity_cache should not be modified, if any lock is to be acquired, it should be acquired
    before evaluation. Similarly, entity_eval_cache should not be modified during eval.
    """
    def evaluate(self, pos_data: dict, entity_eval_cache: dict, entity_cache: dict[EntityEnum, dict[str, Node]]) -> float|int|bool:
        """
        Evaluates the entity against the given data.
        The evaluation is done by traversing the expression tree and evaluating each node.
        Arguments:
            pos_data: Dictionary of data where keys are position id and the value is a dictionary of fields and their resepective values for the position.
            entity_eval_cache: Dictionary of cached evaluation results for entities. We do a dfs sort of thing and keep on populating the cache with the results.
            entity_cache: Dictionary of cached entities. This is used to get entity object by entity id.
        """
        return self._evaluate_node(EntityNode(self.expression_tree, self.node_type), pos_data, entity_eval_cache, entity_cache)

    def _parse_expression(self, expression: str) -> Node:
        """
        Parses the expression string into an expression tree.
        """
        return Parser.parse(expression)
    
    def _check_if_node_is_number(self, node_ident: str) -> bool:
        """
        Check if the node is a number (int/float)
        """
        try:
            int(node_ident)
            return True
        except ValueError:
            try:
                float(node_ident)
                return True
            except ValueError:
                return False

    def __getstate__(self):
        """Control what gets pickled, excluding connection objects and other unpicklable items"""
        # only copy expression tree, expression, name and node_type
        # rest everything is not needed
        state = {
            'expression': self.expression,
            'node_type': self.node_type,
            'name': self.name,
            'expression_tree': self.expression_tree,
        }
        
        
        return state