from .mongo_client import MongoDBClient


class RepositoryDao(MongoDBClient):

    def __init__(self, host, port, database):
        super().__init__(host=host, port=port, database=database)
        self.collection = 'repositories'

    def insert_one(self, repository_document):
        """
        Inserts a new repository into the database.
        """
        return super().insert_one(self.collection, repository_document)

    def find_all(self, repository_name=None, organization_name=None):
        """
        Finds all repositories in the database or filter by repository_name
        and organization_name.
        """
        query = {}
        if repository_name:
            query['name'] = repository_name

        if organization_name:
            query['organization'] = organization_name

        result = super().find_all(self.collection, query)
        if result:
            return list(result)
        return result

    def update_one(self, repository_name, organization_name, document):
        """
        Updates a repository in the database.
        """
        query = {
            'name': repository_name,
            'organization': organization_name
        }
        return super().update_one(self.collection, query, document)
