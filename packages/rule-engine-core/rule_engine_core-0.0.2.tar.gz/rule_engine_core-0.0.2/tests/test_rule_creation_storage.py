# Tests the rule creation and storage functionality
# These are integration tests that check if the rule engine can create and store rules correctly.
from rule_engine_core.rule import Rule
from rule_engine_core.entity_dao import EntityDao
from rule_engine_core.entity_types import EntityEnum, EntityNode
from rule_engine_core.filter import Filter
from rule_engine_core.parser import Node
from rule_engine_core.metadata_store import MetadataStore
import uuid

def test_filter_creation_validation_storage_retrieval():
    metadata_store = MetadataStore("tests/test_metadatastore.json")
    entity_dao = EntityDao()
    # Create a filter
    filter_name = str(uuid.uuid4())
    expression = "col2 > 10"
    filter_obj = Filter(filter_name, expression, metadata_store, entity_dao)
    # Validate the filter
    assert filter_obj.validate() == True
    # Store the filter
    entity_dao.store_entity(EntityEnum.FILTER, filter_obj)
    # Retrieve the filter
    does_filter_exist = entity_dao.entity_exists(EntityEnum.FILTER, filter_name)
    assert does_filter_exist is True
    # Validate the retrieved filter
    all_filters = entity_dao.get_all_entities(EntityEnum.FILTER)
    is_filter_present = any(
        filter_obj.name == filter_name and filter_obj.expression == expression
        for filter_obj in all_filters.values()
    )
    assert is_filter_present is True
    # Clean up
    assert entity_dao.delete_entity(EntityEnum.FILTER, filter_name)

