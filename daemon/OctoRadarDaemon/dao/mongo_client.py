from pymongo import MongoClient


class MongoDBClient:
    """
    MongoDBClient is a class that provides a simple interface to interact with
    a MongoDB database.

    :param str host: The host of the MongoDB database.
    :param int port: The port of the MongoDB database.
    :param str database: The name of the database to use.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Implemented using the Singleton pattern.
        """
        if not cls._instance:
            cls._instance = super(MongoDBClient, cls).__new__(cls)
        return cls._instance

    def __init__(self, host='localhost', port=27017, database='my_database'):
        if not hasattr(self, 'client'):
            self.client = MongoClient(host, port)
            self.db = self.client[database]

    def insert_one(self, collection, document):
        return self.db[collection].insert_one(document).inserted_id

    def find_one(self, collection, query):
        return self.db[collection].find_one(query)

    def find_all(self, collection, query):
        return self.db[collection].find(query)

    def update_one(self, collection, query, new_values):
        return self.db[collection].update_one(
            query, {'$set': new_values}
        ).modified_count

    def delete_one(self, collection, query):
        return self.db[collection].delete_one(query)

    def delete_many(self, collection, query):
        """
        Deletes all documents in a collection that match the query.
        """
        return self.db[collection].delete_many(query).deleted_count
