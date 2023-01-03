from managers.DbSearchManager import SearchManager

sm = SearchManager()
a = sm.dynamic_search('start/devices/1/other/1')
print(a)