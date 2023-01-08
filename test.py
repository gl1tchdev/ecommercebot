from tasks.SheetSync import sync
from time import sleep
from managers.FunctionsManager import FunctionsManager
from managers.DbSearchManager import SearchManager

while True:
    sync()
    sleep(10)
