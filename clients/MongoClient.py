import pymongo
from bson.objectid import ObjectId
from random import choices
from managers.SheetDataValidationManager import SheetManager
import string
import config


class monclient:
    def __init__(self):
        self.client = pymongo.MongoClient()
        self.vm = SheetManager()
        self.symbols = {
            u'$': '[dol]',
            u'.': '[dot]',
            u'/': '[bl]',
            u'\\': '[nl]'
        }

    def get_client(self):
        return self.client

    def need_serialize(self, s):
        if not type(s) is str:
            return False
        return any(x in s for x, y in self.symbols.items())

    def need_deserialize(self, s):
        if not type(s) is str:
            return False
        return any(y in s for x, y in self.symbols.items())

    def serialize_value(self, s):
        result = s
        for key, value in self.symbols.items():
            result = result.replace(key, value)
        return result

    def deserialize_value(self, s):
        result = s
        for key, value in self.symbols.items():
            result = result.replace(value, key)
        return result

    def preprocess_doc(self, doc):
        return {x: self.serialize_value(y) if self.need_serialize(y) else y for x, y in doc.items()}

    def postprocess_doc(self, doc):
        return {x: self.deserialize_value(y) if self.need_deserialize(y) else y for x, y in doc.items()}

    def encrypt_values(self):
        collections = self.get_db().list_collection_names()
        for collection in collections:
            l = self.find(collection)
            for i in l:
                self.update_one(collection, i, self.preprocess_doc(i))

    def decrypt_values(self):
        collections = self.get_db().list_collection_names()
        for collection in collections:
            l = self.find(collection)
            for i in l:
                self.update_one(collection, i, self.postprocess_doc(i))

    def get_db(self):
        return getattr(self.client, config.db)

    def get_collection(self, collection):
        return getattr(self.get_db(), collection)

    def add(self, collection, doc):
        return self.get_collection(collection).insert_one(doc)

    def remove(self, collection, query):
        return self.get_collection(collection).delete_one(query)

    def update_one(self, collection, query, update):
        return self.get_collection(collection).update_one(query, {"$set": update})

    def update_many(self, collection, query, update):
        return self.get_collection(collection).update_many(query, {"$set": update})

    def delete(self, collection, query):
        return self.get_collection(collection).delete_one(query)

    def find(self, collection, query={}, need_id=False):
        result = self.get_collection(collection).find(query).sort('_id', 1)
        if collection in self.vm.get_list_of_service_name_of_sheet():
            result.sort(self.vm.get_fields(_name=collection)[0]['_name'], 1)
        result = list(result)
        if not need_id:
            for elem in result:
                elem.pop('_id')
        return result

    def get_id(self, collection, query):
        result = list(self.get_collection(collection).find(query))
        ids = []
        for elem in result:
            ids.append(elem['_id'])

    def force_search_by_query(self, collections, query, return_collection=False):
        for collection in collections:
            result = list(self.get_collection(collection).find(query))
            if len(result) == 0:
                continue
            else:
                if return_collection:
                    return [collection, result[0]]
                else:
                    return result[0]

    def force_search_by_id(self, collections, id, return_collection=False):
        for collection in collections:
            result = list(self.get_collection(collection).find({'_id': ObjectId(id)}))
            if len(result) == 0:
                continue
            else:
                if return_collection:
                    return [collection, result[0]]
                else:
                    return result[0]

    def find_by_id(self, collection, id):
        id = ObjectId(id)
        result = self.get_collection(collection).find({'_id': id})[0]
        result.pop('_id')
        return result

    def cache_value(self, value):
        key = ''.join(choices(string.ascii_lowercase+string.digits, k=10))
        self.add('cache', {'key': key, 'value': value})
        return key

    def get_cache(self, **kwargs):
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