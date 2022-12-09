from classes.Singleton import Singleton
from clients.MongoClient import monclient


class UploadManager(Singleton):
    body = {}
    collection = ''
    mc = monclient()

    def set_body(self, keys, array):
        result = {}
        for i in range(len(keys)):
            result.update({keys[i]: array[i]})
        self.body = result

    def set_collection(self, collection):
        self.collection = collection

    def upload(self):
        return self.mc.add(self.collection, self.body)

    def is_unique(self):
        search = {}
        for key in self.body:
            if key[0:2] == 'ID':
                search = {key: self.body[key]}
        result = len(list(self.mc.find(self.collection, search)))
        if result == 0:
            return True
        else:
            return False

    def wipe(self):
        self.body = []
        self.collection = ''
