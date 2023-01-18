from tasks.SheetSync import sync
from time import sleep

while True:
    sync()
    sleep(10)
