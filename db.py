from tasks.SheetSync import sync
from time import sleep

while True:
    try:
        sync()
    except:
        continue
    sleep(7)
