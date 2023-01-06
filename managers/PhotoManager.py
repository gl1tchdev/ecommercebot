from urllib.request import urlopen
from urllib.error import HTTPError
from classes.Singleton import Singleton
from validators import url
from clients.MongoClient import monclient
import os
import httplib2

class PhotoManager(Singleton):

    def __init__(self):
        temp = os.path.dirname(__file__).replace('managers', '')
        self.picpath = os.path.join(temp, 'photos')
        self.cachepath = os.path.join(self.picpath, '.cache')
        self.mc = monclient()

    def delete_photo(self, url):
        query = ['photos', {'url': url}]
        file = self.mc.find(*query)[0]['filename']
        self.mc.delete(*query)
        try:
            os.remove(file)
        except:
            pass

    def is_img_valid(self, urls):
        if not url(urls):
            return False
        image_formats = ("image/png", "image/jpeg")
        try:
            site = urlopen(urls)
        except HTTPError:
            return False
        meta = site.info()  # get header of the http request
        if meta["content-type"] in image_formats:  # check if the content-type is a image
            return True
        return False

    def download(self, url):
        filename = os.path.join(self.picpath, url.rsplit('/', 1)[-1])
        h = httplib2.Http(self.cachepath)
        response, content = '', ''
        try:
            response, content = h.request(url)
        except TimeoutError:
            return
        out = open(filename, 'wb')
        out.write(content)
        out.close()
        return filename

