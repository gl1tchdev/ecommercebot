from managers.DbSearchManager import SearchManager

sm = SearchManager()

print(sm.dynamic_search('start/devices'))
print(sm.dynamic_search('start/devices/1'))
print(sm.dynamic_search('start/devices'))

