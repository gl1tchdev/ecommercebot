from classes.Singleton import Singleton

class HTMLManager(Singleton):

    def bold(self, str):
        return '<b>%s</b>' % str

    def underline(self, str):
        return '<u>%s</u>' % str

    def italic(self, str):
        return '<em>%s</em>' % str

    def spoiler(self, str):
        return '||str||'
