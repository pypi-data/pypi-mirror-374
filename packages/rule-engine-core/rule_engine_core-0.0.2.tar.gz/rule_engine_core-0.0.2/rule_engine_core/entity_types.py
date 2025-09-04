from enum import Enum
from rule_engine_core.parser import Node
class EntityEnum(Enum):
    RULE = "rule"
    FILTER = "filter"

class EntityNode:
    def __init__(self, node: Node, entity_type: EntityEnum):
        self.entity_type = entity_type
        self.node = node
