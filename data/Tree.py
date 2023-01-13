from classes.Singleton import Singleton
import copy

class Tree(Singleton):
    def __init__(self):
        self._TEMP = {
            'start': {
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
                    },
                'global_search': '$search'
            }
        }
    def _get(self):
        return copy.deepcopy(self._TEMP)

    def _set(self, value):
        pass

    def _del(self):
        del self._TEMP

    TREE = property(fget=_get, fset=_set, fdel=_del, doc='property')