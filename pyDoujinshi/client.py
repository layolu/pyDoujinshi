from collections import OrderedDict
import math
from requests import Session
import xmltodict


class QueryError(Exception):
    pass

class UnknownError(Exception):
    pass

class Client:
    ENDPOINT_BASE = 'https://www.doujinshi.org/api/{}/'
    IMAGE_BASE = 'https://img.doujinshi.org/{}/{}/{}.jpg'
    BOOK_BASE = 'https://www.doujinshi.org/book/{}/'
    ITEM_BASE = 'https://www.doujinshi.org/browse/{}/{}/'

    def __init__(self, key):
        self.endpoint = self.ENDPOINT_BASE.format(key)
        self._session = Session()
        self.auth()

    def _parse_res(self, res):
        data = xmltodict.parse(res.text)['LIST']
        if 'ERROR' in data:
            raise QueryError('ERROR code {CODE}: {EXACT}'.format(**data['ERROR']))
        else:
            self.user = data['USER']
            ret = []
            books = data.get('BOOK')
            if books:
                if type(books) is not list:
                    books = [books]
                for book in books:
                    book['@TYPE'] = 'BOOK'
                    num_id = int(book['@ID'][1:])
                    image_dir = math.floor(num_id/2000)
                    book['url'] = self.BOOK_BASE.format(num_id)
                    book['image_big'] = self.IMAGE_BASE.format('big',image_dir,num_id)
                    book['image_tn'] = self.IMAGE_BASE.format('tn',image_dir,num_id)
                ret.extend(books)
            items = data.get('ITEM')
            if items:
                if type(items) is not list:
                    items = [items]
                for item in items:
                    num_id = int(item['@ID'][1:])
                    item['url'] = self.ITEM_BASE.format(item['@TYPE'], num_id)
                ret.extend(items)
            return ret


    def get_query(self, **kwargs):
        res = self._session.get(self.endpoint, params=kwargs)
        return self._parse_res(res)

        
    def post_query(self, files={}, **kwargs):
        res = self._session.post(self.endpoint, params=kwargs, files=files)
        return self._parse_res(res)

    def auth(self): 
        self.get_query() 
    
    def get_id(self, id_): 
        return self.get_query(S='getID', ID=id_)
    
    def item_search(self, type_, keyword='', order='title', flow='ASC', date='', cont=''):
        return self.get_query(S='itemSearch', T=type_, sn=keyword, order=order, flow=flow, date=date, cont=cont)
    
    def object_search(self, keyword='', order='title', flow='ASC', date='', date2='', cont='', 
                      age='Y', anth='Y', bcopy='Y', slist=''):
        return self.get_query(S='objectSearch', sn=keyword, order=order, flow=flow, date=date, cont=cont, 
                              age=age, anth=anth, bcopy=bcopy, slist=slist)
    
    def image_search(self, image_file, **kwargs):
        return self.post_query(S='imageSearch', files={'img': image_file}, **kwargs)
