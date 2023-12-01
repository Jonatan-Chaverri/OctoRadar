from .mongo_client import MongoDBClient


class OrganizationsDao(MongoDBClient):

    def __init__(self, host, port, database):
        super().__init__(host=host, port=port, database=database)
        self.collection = 'organizations'

    def insert_one(self, organization_name, description):
        """
        Inserts a new organization into the database.
        """
        document = {
            'name': organization_name,
            'description': description
        }
        return super().insert_one(self.collection, document)

    def find_all(self, organization_names=None):
        """
        Finds all organizations in the database or filter by
        organization_names.
        """
        query = {}
        if organization_names:
            query = {'name': {'$in': organization_names}}
        result = super().find_all(self.collection, query)
        if result:
            return list(result)
        return result

    def find_organizations_not_in_list(self, organization_names):
        """
        Finds organizations that are in the database but not in the
        organization_names list.

        :param list[str] organization_names: A list of organization names.
        """
        query = {
            'name': {'$nin': organization_names},
        }
        result = super().find_all(self.collection, query)
        if result:
            return list(result)
        return result

    def delete_organizations(self, organization_names):
        """
        Deletes organizations that are no longer active.
        """
        query = {'name': {'$in': organization_names}}
        return super().delete_many(self.collection, query)
