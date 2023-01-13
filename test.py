from tasks.SheetSync import sync
from time import sleep
from managers.UserDataManager import UserDataManager

'''
udm = UserDataManager()
print(udm.get_last_message('ImBadTempered'))

'''
while True:
    sync()
    sleep(10)
