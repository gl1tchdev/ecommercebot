import pymongo
from bson.objectid import ObjectId
from random import choices
from managers.SheetDataValidationManager import SheetManager
import string


class monclient:
    def __init__(self):
        self.client = pymongo.MongoClient()
        self.vm = SheetManager()

    def get_сlient(self):
        return self.client

    def add(self, collection, doc):
        return getattr(self.client.vapeshop, collection).insert_one(doc)

    def remove(self, collection, query):
        return getattr(self.client.vapeshop, collection).delete_one(query)

    def update_one(self, collection, query, update):
        return getattr(self.client.vapeshop, collection).update_one(query, {"$set": update})

    def update_many(self, collection, query, update):
        return getattr(self.client.vapeshop, collection).update_many(query, {"$set" :update})

    def delete(self, collection, query):
        return getattr(self.client.vapeshop, collection).delete_one(query)

    def find(self, collection, query={}, need_id=False):
        result = getattr(self.client.vapeshop, collection).find(query).sort('_id', 1)
        if collection in self.vm.get_list_of_service_name_of_sheet():
            result.sort(self.vm.get_fields(_name=collection)[0]['_name'], 1)
        result = list(result)
        if not need_id:
            for elem in result:
                elem.pop('_id')
        return result

    def get_id(self, collection, query):
        result = list(getattr(self.client.vapeshop, collection).find(query))
        ids = []
        for elem in result:
            ids.append(elem['_id'])

    def force_search_by_query(self, collections, query, return_collection=False):
        for collection in collections:
            result = list(getattr(self.client.vapeshop, collection).find(query))
            if len(result) == 0:
                continue
            else:
                if return_collection:
                    return [collection, result[0]]
                else:
                    return result[0]

    def force_search_by_id(self, collections, id, return_collection=False):
        for collection in collections:
            result = list(getattr(self.client.vapeshop, collection).find({'_id': ObjectId(id)}))
            if len(result) == 0:
                continue
            else:
                if return_collection:
                    return [collection, result[0]]
                else:
                    return result[0]

    def find_by_id(self, collection, id):
        id = ObjectId(id)
        result = getattr(self.client.vapeshop, collection).find({'_id': id})[0]
        result.pop('_id')
        return result

    def cache_value(self, value):
        key = ''.join(choices(string.ascii_lowercase+string.digits, k=10))
        self.add('cache', {'key': key, 'value': value})
        return key

    def get_cache(self, **kwargs):
        result = 0
        if not kwargs.get('key') is None:
            search_key = kwargs['key']
            result = list(getattr(self.client.vapeshop, 'cache').find({'key': search_key}))
            return result[0]['value'] if len(result) > 0 else None
        if not kwargs.get('value') is None:
            search_value = kwargs['value']
            result = list(getattr(self.client.vapeshop, 'cache').find({'value': search_value}))
            return result[0]['key'] if len(result) > 0 else None

    def is_cached(self, value):
        result = list(getattr(self.client.vapeshop, 'cache').find({'value': value}))
        return True if len(result) > 0 else False