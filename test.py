import pymongo

from tasks.SheetSync import sync
from time import sleep
from managers.UserDataManager import UserDataManager
from managers.DbSearchManager import SearchManager
from managers.SheetDataValidationManager import SheetManager
from clients.MongoClient import monclient

'''
udm = UserDataManager()
print(udm.get_last_message('ImBadTempered'))

sm = SearchManager()
print(sm.dynamic_search('start/devices/1/evaporators'))

mc = monclient()
print(list(mc.get_сlient().vapeshop.evaporators.find().sort('_id', pymongo.ASCENDING)))
'''
while True:
    sync()
    sleep(10)
