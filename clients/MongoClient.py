from pymongo import MongoClient


class monclient:
    def __init__(self):
        self.client = MongoClient()

    def get_сlient(self):
        return self.client

    def add(self, collection, doc):
        return getattr(self.client.vapeshop, collection).insert_one(doc)

    def remove(self, collection, query):
        return getattr(self.client.vapeshop, collection).delete_one(query)

    def update_one(self, collection, query, update):
        return getattr(self.client.vapeshop, collection).update_one(query, update)

    def update_many(self, collection, query, update):
        return getattr(self.client.vapeshop, collection).update_many(query, update)

    def delete(self, collection, query):
        return getattr(self.client.vapeshop, collection).delete_one(query)

    def find(self, collection, query={}):
        result = list(getattr(self.client.vapeshop, collection).find(query))
        for elem in result:
            elem.pop('_id')
        return result