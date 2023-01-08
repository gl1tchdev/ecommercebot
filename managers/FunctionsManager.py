from classes.Singleton import Singleton
import importlib
import os

class FunctionsManager(Singleton):
    def __init__(self):
        foldername = 'functions'
        temp = os.path.dirname(__file__).replace('managers', '') + '/' + foldername
        self.modules = []
        dirty_folder = os.listdir(temp)
        clean_folder = filter(lambda value: value != '__pycache__', dirty_folder)
        clean_folder = [elem[:-3] for elem in clean_folder]
        for item in clean_folder:
            self.modules.append(importlib.import_module('%s.%s' % (foldername, item)))

    def any_need_run(self, path):
        for module in self.modules:
            if module.need(path):
                return True
        return False

    def get_func(self, path):
        for module in self.modules:
            if module.need(path):
                return module.run
        return None