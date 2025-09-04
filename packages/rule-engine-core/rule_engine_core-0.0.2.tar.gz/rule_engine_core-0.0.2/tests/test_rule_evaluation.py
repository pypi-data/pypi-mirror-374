# Tests the rule evaluation
# These are integration tests which first create the rule and then evaluate it.
from rule_engine_core.rule import Rule
from rule_engine_core.entity_dao import EntityDao
from rule_engine_core.entity_types import EntityEnum, EntityNode
from rule_engine_core.filter import Filter
from rule_engine_core.parser import Node
from rule_engine_core.metadata_store import MetadataStore
import uuid
import logging
import random, string

_logger = logging.getLogger(__name__)

def generate_random_alphanumeric(length=8):
    """
    Generate a random alphanumeric string of specified length
    where the first character is always a letter.
    
    Args:
        length (int): The length of the string to generate (default: 8)
        
    Returns:
        str: A random alphanumeric string starting with a letter
    """
    if length < 1:
        raise ValueError("Length must be at least 1")
    
    # Generate a random letter for the first character
    first_char = random.choice(string.ascii_letters)
    
    # Generate random alphanumeric characters for the rest of the string
    if length > 1:
        rest_chars = ''.join(random.choices(
            string.ascii_letters + string.digits, 
            k=length-1
        ))
        return first_char + rest_chars
    else:
        return first_char

def test_rule_evaluation(entity_dao: EntityDao):
    metadata_store = MetadataStore("tests/test_metadatastore.json")
    # Create a filter with a filter name which is just alpha numeric and no dash
    
    filter_name = generate_random_alphanumeric()
    _logger.debug('filter1_name: %s', filter_name)
    expression = "col2 > 10"
    filter_obj = Filter(filter_name, expression, metadata_store, entity_dao)
    # Validate the filter
    assert filter_obj.validate() == True
    # Store the filter
    entity_dao.store_entity(EntityEnum.FILTER, filter_obj)
    # create another filter
    filter_name2 = generate_random_alphanumeric()
    _logger.debug('filter2_name: %s', filter_name2)
    expression2 = "col3 < 20"
    filter_obj2 = Filter(filter_name2, expression2, metadata_store, entity_dao)
    # Validate the filter
    assert filter_obj2.validate() == True
    # Store the filter
    entity_dao.store_entity(EntityEnum.FILTER, filter_obj2)
    # Create a rule
    rule_name = generate_random_alphanumeric()
    expression = f"{filter_name} AND {filter_name2}"
    rule_obj = Rule(rule_name, expression, metadata_store, entity_dao)
    # Validate the rule
    assert rule_obj.validate() == True
    # Store the rule
    entity_dao.store_entity(EntityEnum.RULE, rule_obj)
    # import pdb; pdb.set_trace()
    # populate the entity_cache for evaluation
    entity_cache = {}
    rule_entities = entity_dao.get_all_entities(EntityEnum.RULE)
    entity_cache[EntityEnum.RULE] = {}
    for rule_name, rule_obj in rule_entities.items():
        entity_cache[EntityEnum.RULE][rule_name] = Rule(rule_name, rule_obj.expression, metadata_store, entity_dao)
    filter_entities = entity_dao.get_all_entities(EntityEnum.FILTER)
    entity_cache[EntityEnum.FILTER] = {}
    for filter_name, filter_obj in filter_entities.items():
        entity_cache[EntityEnum.FILTER][filter_name] = Filter(filter_name, filter_obj.expression, metadata_store, entity_dao)
    for key in entity_cache.keys():
        _logger.info(f"entity_cache: {key.value}: {entity_cache[key].keys()}")
    # initialise the entity_eval_cache for evaluation
    # populate the pos_data for evaluation. pos_data is a list of all positions, each position
    # containing the data for the columns. where columns are the fields in the metadata store
    pos_data = [
        {
            "col1": "abc",
            "col2": 15,
            "col3": 25
        },
        {
            "col1": "def",
            "col2": 5,
            "col3": 10
        },
        {
            "col1": "ghi",
            "col2": 12,
            "col3": 19
        }
    ]
    expectations = [False, False, True]
    for rule_name, rule_obj in entity_cache[EntityEnum.RULE].items():
        for pos, exp in zip(pos_data, expectations):
            entity_eval_cache = {EntityEnum.RULE: {}, EntityEnum.FILTER: {}}
            _logger.info(f"evaluating rule {rule_name} for pos {pos}")
            # evaluate the rule
            result = rule_obj.evaluate(pos, entity_eval_cache, entity_cache)
            _logger.debug(f"state of entity_eval_cache: {entity_eval_cache}")
            _logger.debug(f"expectation: {exp}")
            _logger.info(f"result: {result}")
            assert result == exp
    