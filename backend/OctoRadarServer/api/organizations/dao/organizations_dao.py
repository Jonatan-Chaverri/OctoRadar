from app.db import DatabaseManager

class OrganizationsDao:

    def __init__(self):
        self.db = DatabaseManager()
        self.collection_name = "organizations"

    def find_all(self, query=None):
        result = self.db.find_all(self.collection_name, query)
        for item in result:
            item['_id'] = str(item['_id'])
        return result
