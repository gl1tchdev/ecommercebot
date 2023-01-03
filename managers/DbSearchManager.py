from classes.Singleton import Singleton
from managers.SheetDataValidationManager import SheetManager
from clients.MongoClient import monclient

class SearchManager(Singleton):
    vm = SheetManager()
    mc = monclient()

    def __init__(self):
        self.TREE = {
            'start': {
                'global_search': '$search',
                'devices':
                    {
                        '$device_manufacturer':
                            {
                                'models':
                                    {
                                        '$model': '$model_card'
                                    },
                                'cartridges':
                                    {
                                        '$cartridge': '$cartridge_card'
                                    },
                                'evaporators':
                                    {
                                        '$evaporator': '$evaporator_card'
                                    },
                                'tanks':
                                    {
                                        '$tank': '$tank_card'
                                    },
                                'other':
                                    {
                                        '$other': '$other_card'
                                    }
                            }
                    },
                'liquids':
                    {
                        '$liquids_manufacturer':
                            {
                                'hard':
                                    {
                                        '$liquids_hard': '$liquid_card'
                                    },
                                'medium':
                                    {
                                        '$liquids_medium': '$liquid_card'
                                    }
                            }
                    }
            }
        }
        self.load = {
            'device_manufacturer': self.device_manufacturer,
            'model': self.model,
            'cartridge': self.cartridge,
            'evaporator': self.evaporator,
            'tank': self.tank,
            'other': self.other,
            'liquids_manufacturer': self.liquids_manufacturer,
            'liquids_hard': self.liquids_hard,
            'liquids_medium': self.liquids_medium,
        }
        self.endpoints = {
            'search': self.global_search,
            'model_card': self.model_card,
            'cartridge_card': self.cartridge_card,
            'evaporator_card': self.evaporator_card,
            'liquid_card': self.liquid_card,
            'other_card': self.other_card
        }
        self.collections = {
            'devices': ['manufacturers', 'ID_manufacturer'],
            'liquids': ['liquids', 'ID_brand'],
            'model': ['models', 'ID_model'],
            'cartridge': ['cartridges', 'ID_cartridge'],
            'evaporator': ['evaporators', 'ID_evaporator'],
            'tanks': ['tanks', 'ID_tank'],
            'other': ['other', 'ID_element'],
            'liquids_hard': ['liquids', 'ID_liquid'],
            'liquids_medium': ['liquids', 'ID_liquid'],
            'medium': ['liquids', 'ID_liquid'],
            'hard': ['liquids', 'ID_liquid'],
        }
        self.translations = {
            'models': self.vm.get_sheet_name_by_service_name('models'),
            'devices': 'Устройства',
            'global_search': 'Поиск',
            'liquids': 'Жидкости',
            'cartridges': self.vm.get_sheet_name_by_service_name('cartridges'),
            'evaporators': self.vm.get_sheet_name_by_service_name('evaporators'),
            'tanks': self.vm.get_sheet_name_by_service_name('tanks'),
            'other': self.vm.get_sheet_name_by_service_name('other')
        }

    def dynamic_search(self, path):
        keyload = ''
        temp = ''
        if path.endswith('/'):
            path = path[:-1]
        mpath = path.split('/')
        for elem in mpath:
            if not temp:
                temp = self.TREE
            for key in temp:
                if type(key) is str:
                    if key[0] == '$' and key[1:] in self.load.keys():
                        keyload = key
            if keyload:
                a = temp.pop(keyload)
                temp.update(dict.fromkeys(self.load[keyload[1:]](self.get_query(mpath)).keys(), a))
                keyload = ''
            if elem.isdigit():
                elem = int(elem)
            if not elem in temp.keys():
                return None
            else:
                temp = temp[elem]
        if type(temp) is str:
            if temp[0] == '$' and temp[1:] in self.endpoints.keys():
                return self.endpoints[temp[1:]](self.get_query(mpath))
        else:
            for key in temp:
                if type(key) is str:
                    if key[0] == '$' and key[1:] in self.load.keys():
                        return self.load[key[1:]](self.get_query(mpath))
        if len(temp.keys()) > 0:
            l = list(temp.keys())
            prev_last = mpath[len(mpath) - 2]
            last = mpath[len(mpath) - 1]
            if last.isdigit():
                return self.filter_categories(prev_last, last, l)
            else:
                return {value: self.translate(value) for value in l}
        else:
            return None

    def get_search_word(self, word):
        csearch = None
        if not word in self.vm.get_dict_of_sheet_names().keys():
            if word in self.collections.keys():
                csearch = self.collections[word][0]
            elif word[:-1] in self.collections.keys():
                csearch = self.collections[word[:-1]][0]
        else:
            csearch = word
        return csearch

    def filter_categories(self, prev_last, last, l, d = False):
        c = self.get_search_field(prev_last)
        if prev_last == 'devices':
            a = filter(lambda value: not self.empty(self.get_search_word(value), {c[1]: int(last)}), l)
        else:
            if prev_last == 'liquids':
                a = filter(lambda value: not self.empty(self.get_search_word(value), {c[1]: int(last),'strength': value}), l)
            else:
                a = filter(lambda value: not self.empty(self.get_search_word(value), {c[1]: value}), l)
        if not d:
            result = {value: self.translate(value) for value in a}
        else:
            result = list(a)
        return result if len(result) > 0 else None

    def get_search_field(self, word):
        csearch = None
        if word in self.collections.keys():
            csearch = self.collections[word]
        elif word[:-1] in self.collections.keys():
            csearch = self.collections[word[:-1]]
        return csearch

    def translate(self, word):
        if word in self.translations.keys():
            return self.translations[word]
        else:
            return word

    def empty(self, collection, search):
        result = self.mc.find(collection, search)
        return True if len(result) == 0 else False

    def get_query(self, mpath):
        result = {}
        for i in range(len(mpath)):
            if mpath[i].isdigit() and i != 0:
                word = mpath[i-1]
                info = self.get_search_field(word)
                result.update({info[1]: int(mpath[i])})
        return result if len(result) > 0 else None

    def to_dict(self, l, fields):
        to_d = {}
        for elem in l:
            to_d.update({elem[fields[1]]: str(elem[fields[0]])})
        return to_d

    def global_search(self, query):
        return [1, 2, 3, 4]

    def liquids_manufacturer(self, query):
        liquids = self.mc.find('liquids_brands')
        return self.to_dict(liquids, ['name', 'ID_brand']) if len(liquids) > 0 else None

    def device_manufacturer(self, query):
        manufacturers = self.mc.find('manufacturers')
        return self.to_dict(manufacturers, ['manufacturer_name', 'ID_manufacturer']) if len(manufacturers) > 0 else None

    def model(self, query):
        models = self.mc.find('models', query)
        return self.to_dict(models, ['name', 'ID_model']) if len(models) > 0 else None

    def cartridge(self, query):
        cartridges = self.mc.find('cartridges', query)
        return self.to_dict(cartridges, ['name', 'ID_cartridge']) if len(cartridges) > 0 else None

    def liquids_hard(self, query):
        l_hard = self.mc.find('liquids', {'strength': 'hard'})
        return self.to_dict(l_hard, ['name', 'ID_liquid']) if len(l_hard) > 0 else None

    def liquids_medium(self, query):
        l_medium = self.mc.find('liquids', {'strength': 'medium'})
        return self.to_dict(l_medium, ['name', 'ID_liquid']) if len(l_medium) > 0 else None

    def evaporator(self, query):
        evaporators = self.mc.find('evaporators', query)
        return self.to_dict(evaporators, ['name', 'ID_evaporator']) if len(evaporators) > 0 else None

    def tank(self, query):
        tanks = self.mc.find('tanks', query)
        return self.to_dict(tanks, ['name', 'ID_tank']) if len(tanks) > 0 else None

    def other(self, query):
        other = self.mc.find('other', query)
        return self.to_dict(other, ['name', 'ID_element']) if len(other) > 0 else None

    def model_card(self, query):
        result = []
        model = self.mc.find('models', query)
        if len(list(model)) > 0:
            model = list(model)[0]
            result.append(model['name'])
            result.append(model['description'])
            photo_url = model['url']
            if len(photo_url) > 0:
                photo_obj = self.mc.find('photos', {'url': model['url']})
                if len(photo_obj) > 0:
                    result.append(photo_obj[0]['filename'])
            return result
        else:
            return None

    def cartridge_card(self, query):
        result = []
        cartridge = self.mc.find('cartridges', query)
        if len(list(cartridge)) > 0:
            cartridge = list(cartridge)[0]
            result.append(cartridge['name'])
            devices = self.mc.find('models', {'ID_model': int(cartridge['ID_model'])})
            end = ''
            if len(devices) > 1:
                for device in devices:
                    end += device['name'] + ';'
            else:
                end = devices[0]['name']
            result.append(end)
            photo_url = cartridge['url']
            if len(photo_url) > 0:
                photo_obj = self.mc.find('photos', {'url': cartridge['url']})
                if len(photo_obj) > 0:
                    result.append(photo_obj[0]['filename'])
            return result
        else:
            return None

    def evaporator_card(self, query):
        result = []
        item = self.mc.find('evaporators', query)
        if len(list(item)) > 0:
            item = list(item)[0]
            result.append(item['name'])
            devices = self.mc.find('models', {'ID_model': int(item['ID_model'])})
            end = ''
            if len(devices) > 1:
                for device in devices:
                    end += device['name'] + ';'
            else:
                end = devices[0]['name']
            result.append(end)
            photo_url = item['url']
            if len(photo_url) > 0:
                photo_obj = self.mc.find('photos', {'url': item['url']})
                if len(photo_obj) > 0:
                    result.append(photo_obj[0]['filename'])
            return result
        else:
            return None

    def liquid_card(self, query):
        result = []
        item = self.mc.find('liquids', query)
        if len(list(item)) > 0:
            item = list(item)[0]
            result.append(item['name'])
            result.append(item['strength'])
            photo_url = item['url']
            if len(photo_url) > 0:
                photo_obj = self.mc.find('photos', {'url': item['url']})
                if len(photo_obj) > 0:
                    result.append(photo_obj[0]['filename'])
            return result
        else:
            return None

    def other_card(self, query):
        result = []
        item = self.mc.find('other', query)
        if len(list(item)) > 0:
            item = list(item)[0]
            result.append(item['name'])
            photo_url = item['url']
            if len(photo_url) > 0:
                photo_obj = self.mc.find('photos', {'url': item['url']})
                if len(photo_obj) > 0:
                    result.append(photo_obj[0]['filename'])
            return result
        else:
            return None