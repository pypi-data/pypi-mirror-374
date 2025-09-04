"""
This module defines the MetadataStore class, which is responsible for retrieval of financial metadata.
The MetadataStore class provides methods for retrieval of metadata.
There should be no writes to this and this is expected to be a read-only store.
The MetadataStore class has the following methods:
    -> get_attributes: Get the list of attributes available for the metadata.
    -> get_all_metadata: retrieves all metadata from the store. The metadata is a list of dictionaries each defining a key value pair.
    -> attribute_exist_for_field: checks if field exists in the store and if the attribute exists for the field.
"""

import json

class MetadataStore:
    def __init__(self, metadata_file_path: str):
        """
        Initializes the MetadataStore object with an empty dictionary to store metadata.
        """
        with open(metadata_file_path, 'r') as f:
            self._metadata_store: dict[str, dict[str, str|int|float]] = json.load(f)
        self._attributes = self._populate_attributes()

    def _populate_attributes(self):
        """
        Populates the attributes from the metadata store.
        """
        attributes_set = set()
        for _, entity_data in self._metadata_store.items():
            for field in entity_data:
                if field not in attributes_set:
                    attributes_set.add(field)
        return attributes_set
    
    def get_all_metadata(self) -> dict[str, dict[str, str|int|float]]:
        """
        Retrieves all metadata from the store. The metadata is a list of dictionaries each defining a key value pair.
        """
        return self._metadata_store

    def does_field_exist(self, field: str) -> bool:
        """
        Checks if field exists in the store.
        """
        return field in self._metadata_store

    def attribute_exist_for_field(self, field: str, attribute: str) -> bool:
        """
        Checks if field exists in the store and if the attribute exists for the field.
        """
        return field in self._metadata_store and attribute in self._metadata_store[field] and self._metadata_store[field][attribute] is not None