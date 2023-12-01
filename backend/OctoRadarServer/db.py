import pymongo

import logging


class DatabaseManager:
    """
    A database manager class for handling connections to a MongoDB database.

    This class provides a convenient interface for establishing and managing
    connections to a MongoDB database. It encapsulates common database
    operations and connection handling, making it easier to work with MongoDB
    in your application.
    """
    _instance = None

    def __new__(cls, host="", port=27017, db_name=""):
        """
        Returns an instance of the class. Uses a singleton design pattern to
        ensure that all application uses just one connection to the database
        and not create multiple.

        :param str host: host url where the database is.
        :param int port: the port number to use to connect to the db.
        :param db_name: the name of the database to use.

        :return: an instance of the DatabaseManager class.
        :rtype: DatabaseManager
        """
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.client = pymongo.MongoClient(host, port)
            cls._instance.db = cls._instance.client[db_name]
        return cls._instance

    def insert_one(self, collection_name, document):
        """
        Insert one document in a specific collection.

        :param str collection_name: the name of the collection where to insert
         the document.
        :param dict document: the document to insert.

        :return: the inserted object id
        :rtype: ObjectId
        """
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            logging.error(f"Error inserting document: {e}")
            return None

    def insert_many(self, collection_name, documents):
        """
        Insert a list of documents in a specific collection.

        :param str collection_name: the name of the collection where to insert
         the documents.
        :param list documents: the list of documents to insert.

        :return: the inserted object ids
        :rtype: list<ObjectId>
        """
        try:
            collection = self.db[collection_name]
            result = collection.insert_many(documents)
            return result.inserted_ids
        except Exception as e:
            logging.error(f"Error inserting documents: {e}")
            return None

    def find_all(self, collection_name, query=None):
        """
        Retrieves all documents in a specific collection that matches a query
        filter (optional).

        :param str collection_name: the name of the collection where to search
         the documents.
        :param dict query: the filter query dict.

        :return: the list of documents found.
        :rtype: list<dict>
        """
        try:
            collection = self.db[collection_name]
            cursor = collection.find(query)
            return list(cursor)
        except Exception as e:
            logging.error(f"Error finding documents: {e}")
            return []

    def find_one(self, collection_name, query=None):
        """
        Retrieves a document in a specific collection that matches a query
        filter (optional).

        :param str collection_name: the name of the collection where to search
         the document.
        :param dict query: the filter query dict.

        :return: the document found.
        :rtype: dict
        """
        try:
            collection = self.db[collection_name]
            cursor = collection.find_one(query)
            return cursor
        except Exception as e:
            logging.error(f"Error finding document: {e}")
            return None

    def update_one(self, collection_name, filter_query, update_query):
        """
        Update one document in a specific collection that matches a query
        filter (optional).

        :param str collection_name: the name of the collection where to search
         the document.
        :param dict filter_query: the filter query dict.
        :param dict update_query: the update query that indicates what needs to
         be updated.

        :return: 1 if document was modified, 0 if no documents were found
        :rtype: integer
        """
        try:
            collection = self.db[collection_name]
            result = collection.update_one(filter_query, update_query)
            return result.modified_count
        except Exception as e:
            logging.error(f"Error updating document: {e}")
            return 0

    def delete_one(self, collection_name, filter_query):
        """
        Delete one document in a specific collection that matches a query
        filter (optional).

        :param str collection_name: the name of the collection where to search
         the document.
        :param dict filter_query: the filter query dict.

        :return: 1 if document was deleted, 0 if no documents were found
        :rtype: integer
        """
        try:
            collection = self.db[collection_name]
            result = collection.delete_one(filter_query)
            return result.deleted_count
        except Exception as e:
            logging.error(f"Error deleting document: {e}")
            return 0

    def close(self):
        """
        Closes the connection to the database.
        """
        self.client.close()
