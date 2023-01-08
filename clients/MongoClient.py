from pymongo import MongoClient
from bson.objectid import ObjectId


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

    def find(self, collection, query={}, need_id=False):
        result = list(getattr(self.client.vapeshop, collection).find(query))
        if not need_id:
            for elem in result:
                elem.pop('_id')
        return result

    def get_id(self, collection, query):
        result = list(getattr(self.client.vapeshop, collection).find(query))
        ids = []
        for elem in result:
            ids.append(elem['_id'])

    def find_by_id(self, collection, id):
        id = ObjectId(id)
        result = getattr(self.client.vapeshop, collection).find({'_id': id})[0]
        result.pop('_id')
        return result