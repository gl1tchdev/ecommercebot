from clients.MongoClient import monclient
from managers.UserDataManager import UserDataManager

mc = monclient()
udm = UserDataManager()

udm.set_card_id('ImBadTempered', 0)

'''
collections = mc.get_db().list_collection_names()
for collection in collections:
    l = mc.find(collection)
    for i in l:
        mc.update_one(collection, i, mc.postprocess_doc(i))
'''