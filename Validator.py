from classes.Singleton import Singleton

class Validator(Singleton):
    body = []
    message = ''
    result = False


    def getResult(self):
        return self.result

    def setBody(self, array):
        self.body = array

    def isRowFull(self, sheet, data):
        return len(data) == len(self.rules[sheet])

    def process(self, sheet, data):
        pass