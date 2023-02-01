from classes.Singleton import Singleton
from managers.SheetDataValidationManager import SheetManager
from clients.MongoClient import monclient
from decorators.DbSearch import fullpath
from managers.HTMLManager import HTMLManager
from data.Tree import Tree
from copy import deepcopy

class SearchManager(Singleton):
    vm = SheetManager()
    mc = monclient()
    hm = HTMLManager()
    TREE = Tree()

    def __init__(self):
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
            'ask_question': self.ask_question,
            'model_card': self.model_card,
            'cartridge_card': self.cartridge_card,
            'evaporator_card': self.evaporator_card,
            'liquid_card': self.liquid_card,
            'other_card': self.other_card,
            'tank_card': self.tank_card
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
            'global_search': 'Поиск 🔎',
            'ask_question': 'Задать вопрос❔',
            'liquids': self.vm.get_sheet_name_by_service_name('liquids'),
            'liquids_brands': self.vm.get_sheet_name_by_service_name('liquids_brands'),
            'cartridges': self.vm.get_sheet_name_by_service_name('cartridges'),
            'evaporators': self.vm.get_sheet_name_by_service_name('evaporators'),
            'tanks': self.vm.get_sheet_name_by_service_name('tanks'),
            'other': self.vm.get_sheet_name_by_service_name('other'),
            'manufacturers': self.vm.get_sheet_name_by_service_name('manufacturers')
        }

        self.search_list = {
            'manufacturers': ['start/devices/{0}', 'ID_manufacturer'],
            'liquids_brands': ['start/liquids/{0}', 'ID_brand'],
            'cartridges': ['start/devices/{0}/cartridges/{1}', 'ID_manufacturer', 'ID_cartridge'],
            'liquids': ['start/liquids/{0}/{1}/{2}', 'ID_brand', 'strength', 'ID_liquid'],
            'models': ['start/devices/{0}/models/{1}', 'ID_manufacturer', 'ID_model'],
            'evaporators': ['start/devices/{0}/evaporators/{1}', 'ID_manufacturer', 'ID_evaporator'],
            'tanks': ['start/devices/{0}/tanks/{1}', 'ID_manufacturer', 'ID_tank'],
            'other': ['start/devices/{0}/other/{1}', 'ID_manufacturer', 'ID_element']
        }

    @fullpath
    def dynamic_search(self, path):
        keyload = ''
        temp = ''
        if path.endswith('/'):
            path = path[:-1]
        mpath = path.split('/')
        for elem in mpath:
            if not temp:
                temp = self.TREE.TREE
            for key in temp:
                if type(key) is str:
                    if key[0] == '$' and key[1:] in self.load.keys():
                        keyload = key
            if keyload:
                a = temp.pop(keyload)
                try:
                    temp.update(dict.fromkeys(self.load[keyload[1:]](self.get_query(mpath)).keys(), a))
                except AttributeError:
                    return None
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

    def get_search_list(self):
        return list(self.search_list.keys())

    def filter_categories(self, prev_last, last, l, d = False):
        c = self.get_search_field(prev_last)
        if prev_last == 'devices':
            a = filter(lambda value: not self.empty(self.get_search_word(value), {c[1]: int(last)}), l)
        else:
            if prev_last == 'liquids':
                a = filter(lambda value: not self.empty(self.get_search_word(value), {c[1]: int(last), 'strength': value}), l)
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

    def check(self, s):
        return s if s else 'empty'

    def get_devices(self, query):
        search = self.mc.find('models', query)
        if len(search) == 0:
            return 'empty'
        else:
            return search[0]['name']

    def get_query(self, mpath):
        result = {}
        for i in range(len(mpath)):
            if mpath[i].isdigit() and i != 0:
                word = mpath[i-1]
                info = self.get_search_field(word)
                result.update({info[1]: int(mpath[i])})
        return result if len(result) > 0 else None

    def get_path_by_query(self, collection, query):
        searchlist = deepcopy(self.search_list)
        mquery = searchlist[collection]
        path = mquery.pop(0)
        res = []
        for elem in mquery:
            for key in query:
                if elem == key:
                    res.append(query[elem])
        return path.format(*res)


    def to_dict(self, l, fields):
        to_d = {}
        for elem in l:
            to_d.update({elem[fields[1]]: str(elem[fields[0]])})
        return to_d


    def list_comments(self, query):
        out = '\n'
        id = str(self.mc.force_search_by_query(self.vm.get_list_of_service_name_of_sheet(), query)['_id'])
        comments = self.mc.find('comments', {'doc_id': id})
        if len(comments) == 0:
            return None
        for comment in comments:
            out += '[%s] (%s): %s\n' % (comment['time'], comment['nickname'], comment['text'])
        return out


    def force_search(self, query):
        c = self.vm.get_list_of_service_name_of_sheet()
        result = self.mc.force_search_by_query(c, query)
        return result


    def search_by_text(self, text):
        result = []
        search_fields = {}
        sheet_list = self.search_list.keys()
        for sheet in sheet_list:
            fields = self.vm.get_fields(sheet_name=sheet)
            for field in fields:
                if 'name' in field['_name']:
                    search_fields.update({self.vm.get_service_name_by_sheet_name(sheet): field['_name']})
        for key in search_fields:
            items = self.mc.find(key, {search_fields[key]: text})
            if len(items) > 0:
                for item in items:
                    result.append([key, item])
        buttons = {}
        for item in result:
            fieldname = ''
            for key in item[1]:
                if 'name' in key:
                    fieldname = item[1][key]
            path = self.get_path_by_query(item[0], item[1])
            buttons.update({path: ('%i. [%s] ' % (result.index(item)+1, self.translate(item[0])))+fieldname})
        return buttons

    def global_search(self, query):
        pass

    def ask_question(self, query):
        pass

    def liquids_manufacturer(self, query):
        liquids = self.mc.find('liquids_brands')
        return self.to_dict(liquids, ['brand_name', 'ID_brand']) if len(liquids) > 0 else None

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
        query.update({'strength': 'hard'})
        l_hard = self.mc.find('liquids', query)
        return self.to_dict(l_hard, ['name', 'ID_liquid']) if len(l_hard) > 0 else None

    def liquids_medium(self, query):
        query.update({'strength': 'medium'})
        l_medium = self.mc.find('liquids', query)
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
            result.append('model')
            result.append({self.hm.bold('Название'): model['name']})
            result.append({self.hm.italic('Описание'): self.check(model['description'])})
            comments = self.list_comments(query)
            if not comments is None:
                result.append({self.hm.underline('Комментарии'): comments})
            result.append(self.check(model['url']))
            return result
        else:
            return None

    def cartridge_card(self, query):
        result = []
        cartridge = self.mc.find('cartridges', query)
        if len(list(cartridge)) > 0:
            cartridge = list(cartridge)[0]
            result.append('cartridge')
            result.append({self.hm.bold('Название'): cartridge['name']})
            result.append({self.hm.underline('Подходит на устройства'): self.get_devices({'ID_model': int(cartridge['ID_model'])})})
            comments = self.list_comments(query)
            if not comments is None:
                result.append({self.hm.underline('Комментарии'): comments})
            result.append(self.check(cartridge['url']))
            return result
        else:
            return None

    def evaporator_card(self, query):
        result = []
        item = self.mc.find('evaporators', query)
        if len(list(item)) > 0:
            item = list(item)[0]
            result.append('evaporator')
            result.append({self.hm.bold('Название'): item['name']})
            result.append({self.hm.underline('Подходит на устройства'): self.get_devices({'ID_model': int(item['ID_model'])})})
            comments = self.list_comments(query)
            if not comments is None:
                result.append({self.hm.underline('Комментарии'): comments})
            result.append(self.check(item['url']))
            return result
        else:
            return None

    def liquid_card(self, query):
        result = []
        item = self.mc.find('liquids', query)
        if len(list(item)) > 0:
            item = list(item)[0]
            result.append('liquid')
            result.append({self.hm.bold('Название'): item['name']})
            result.append({self.hm.italic('Крепость'): item['strength']})
            comments = self.list_comments(query)
            if not comments is None:
                result.append({self.hm.underline('Комментарии'): comments})
            result.append(self.check(item['url']))
            return result
        else:
            return None

    def tank_card(self, query):
        result = []
        item = self.mc.find('tanks', query)
        if len(list(item)) > 0:
            item = list(item)[0]
            result.append('tank')
            result.append({self.hm.bold('Название'): item['name']})
            result.append({self.hm.underline('Подходит на устройства'): self.get_devices({'ID_model': int(item['ID_model'])})})
            comments = self.list_comments(query)
            if not comments is None:
                result.append({self.hm.underline('Комментарии'): comments})
            result.append(self.check(item['url']))
            return result
        else:
            return None

    def other_card(self, query):
        result = []
        item = self.mc.find('other', query)
        if len(list(item)) > 0:
            item = list(item)[0]
            result.append('other')
            result.append({self.hm.bold('Название'): item['name']})
            comments = self.list_comments(query)
            if not comments is None:
                result.append({self.hm.underline('Комментарии'): comments})
            result.append(self.check(item['url']))
            return result
        else:
            return None