from classes.Singleton import Singleton
from clients.MongoClient import monclient


class UploadManager(Singleton):
    mc = monclient()

    def get_client(self):
        return self.mc

    def split_data(self, keys, array):
        result = {}
        for i in range(len(keys)):
            result.update({keys[i]: array[i]})
        return result

    def upload(self, collection, elem):
        return self.mc.add(collection, elem)

    def delete(self, collection, elem):
        return self.mc.delete(collection, elem)

    def is_in_db(self, collection, elem):
        key = next(iter(elem))
        search = {key: elem[key]}
        result = self.mc.find(collection, search)
        if len(result) == 0:
            return False
        else:
            return True

    def has_copies_in_db(self, collection, elem):
        key = next(iter(elem))
        search = {key: elem[key]}
        result = self.mc.find(collection, search)
        if len(result) > 0:
            return False
        else:
            return True

    def full_check(self, collection, search):
        return True if len(self.mc.find(collection, search)) == 0 else False

    def get_difference_to_deploy(self, collection, batch):
        collection_data = self.mc.find(collection)
        return [x for x in batch if x not in collection_data]

    def get_difference_to_delete(self, collection, batch):
        collection_data = self.mc.find(collection)
        return [x for x in collection_data if x not in batch]