"""
This module defines the EntityDao class.
This is responsible for storing and managing filter and rule entities.
We will store these in a postgres database.
"""
import json
from psycopg2.extensions import connection as PgConnection
import psycopg2
from rule_engine_core.parser import Node
import os, logging
from typing import Optional
import pickle
import sys
from rule_engine_core.entity_types import EntityEnum, EntityNode

# Add an alias for backwards compatibility with pickled data
# This allows pickle to find the module at the old path
sys.modules['entity_types'] = sys.modules['rule_engine_core.entity_types']
sys.modules['parser'] = sys.modules['rule_engine_core.parser']

from rule_engine_core.entity_base import EntityBase

_logger = logging.getLogger(__name__)

def create_connection(config: Optional[dict] = None) -> PgConnection:
    if config is None:
        # Load the config from the environment variables
        # and assume db is on the same host as the application
        # using the default port: 5432
        config = {
            "database": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            # "port": os.getenv("POSTGRES_PORT", 5432),
        }
    connection = psycopg2.connect(
        dbname=config["database"],
        user=config["user"],
        password=config["password"],
        host=config["host"],
    )
    # check and log if the connection is successful
    if connection.closed == 0:
        _logger.info("Connection to the database was successful")
        return connection
    else:
        _logger.error("Connection to the database failed")
        return None

class EntityDao:
    """
    This class is a dao for the postgres database which stores the filters and rules.
    """    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        Initializes the MetadataStore object with an empty dictionary to store metadata.
        """
        if config_file_path is not None:
            with open(config_file_path, 'r') as f:
                config = json.load(f)
        self._connection = create_connection(config if config_file_path is not None else None)
        if self._connection is None:
            raise RuntimeError("Failed to create a connection to the database")
    
    def get_all_entities(self, entity_type: EntityEnum) -> dict[str, EntityBase]:
        """
        Retrieves all entities of the specified type from the store.
        """
        # if entity_type is filter, read from the filter table
        # if entity_type is rule, read from the rule table
        # and then return the result as a dictionary. Where the key maps to rule_name/filter_name and the value maps to rule_data/filter_data
        if entity_type == EntityEnum.FILTER:
            query = "SELECT * FROM filters"
        elif entity_type == EntityEnum.RULE:
            query = "SELECT * FROM rules"
        else:
            raise ValueError(f"Invalid entity type: {entity_type}")
        with self._connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            entities = {}
            for row in rows:
                entity_id = row[0]
                entity_data = row[1]
                try:
                    # convert the entity data to a Node object
                    node = pickle.loads(entity_data)
                    entities[entity_id] = node
                except Exception as e:
                    _logger.error(f"Failed to unpickle entity {entity_id}: {e}")
                    # Skip this entity and continue
                    continue
            return entities
        

    def store_entity(self, entity_enum: EntityEnum, entity: EntityBase) -> bool:
        """
        Stores the entity and the expression in the store.
        """
        print(f"Storing entity: {entity.name} of type: {entity_enum}")
        # if entity_enum is filter, store in the filter table
        # if entity_enum is rule, store in the rule table
        # and then return True if the operation was successful, False otherwise
        
        # Compare by value instead of direct equality
        if entity_enum.value == EntityEnum.FILTER.value:
            query = "INSERT INTO filters (filter_name, filter_data) VALUES (%s, %s)"
        elif entity_enum.value == EntityEnum.RULE.value:
            query = "INSERT INTO rules (rule_name, rule_data) VALUES (%s, %s)"
        else:
            raise ValueError(f"Invalid entity type: {entity_enum}")
        
        with self._connection.cursor() as cursor:
            try:
                # there shouldnt be a need to store the expression tree in the database
                # todo: change it later
                cursor.execute(query, (entity.name, pickle.dumps(entity)))
                self._connection.commit()
                return True
            except Exception as e:
                _logger.error(f"Failed to store entity: {e}")
                self._connection.rollback()
                return False
        
    
    def entity_exists(self, entity_enum: EntityEnum, entity_id: str) -> bool:
        """
        Checks if the entity exists in the store.
        """
        # if entity_enum is filter, check in the filter table
        # if entity_enum is rule, check in the rule table
        # and then return True if the entity exists, False otherwise
        if entity_enum.value == EntityEnum.FILTER.value:
            query = "SELECT * FROM filters WHERE filter_name = %s"
        elif entity_enum.value == EntityEnum.RULE.value:
            query = "SELECT * FROM rules WHERE rule_name = %s"
        else:
            raise ValueError(f"Invalid entity type: {entity_enum}")
        with self._connection.cursor() as cursor:
            cursor.execute(query, (entity_id,))
            rows = cursor.fetchall()
            if len(rows) > 0:
                return True
            else:
                return False
        # close the connection
    
    def delete_entity(self, entity_enum: EntityEnum, entity_id: str) -> bool:
        """
        Deletes the entity from the store.
        """
        # if entity_enum is filter, delete from the filter table
        # if entity_enum is rule, delete from the rule table
        # and then return True if the operation was successful, False otherwise
        if entity_enum == EntityEnum.FILTER:
            query = "DELETE FROM filters WHERE filter_name = %s"
        elif entity_enum == EntityEnum.RULE:
            query = "DELETE FROM rules WHERE rule_name = %s"
        else:
            raise ValueError(f"Invalid entity type: {entity_enum}")
        
        with self._connection.cursor() as cursor:
            try:
                cursor.execute(query, (entity_id,))
                self._connection.commit()
                return True
            except Exception as e:
                _logger.error(f"Failed to delete entity: {e}")
                self._connection.rollback()
                return False

    # create destructor for EntityDao class to close the connection
    def __del__(self):
        if self._connection is not None:
            self._connection.close()
            _logger.info("Connection to the database closed")
        else:  
            _logger.error("Connection to the database was not established")
