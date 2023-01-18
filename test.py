from clients.MongoClient import monclient

mc = monclient()


collections = mc.get_db().list_collection_names()
for collection in collections:
    l = mc.find(collection)
    for i in l:
        mc.update_one(collection, i, mc.postprocess_doc(i))