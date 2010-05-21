from functools import partial
from django.db import models

'''
class RedisFunction(models.Model):

    transaction=models.CharField(max_length='100', choices=transaction_choices)
'''

from redish.client import Client
from redish import serialization

#override and divide and balance with settings?
#db = Client(host="localhost", port=6379, db="") # default settings.
db = Client()
db_pickle = Client(serializer=serialization.Pickler())
db_json = Client(serializer=serialization.JSON())


def _make_get_value(key):
    def foo(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        return int(db.api.get(full_key)) if db.api.get(full_key) else None
    return foo

def _make_incr(key):
    def foo(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        return db.api.incr(full_key)
    return foo

def _make_decr(key):
    def foo(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        return db.api.decr(full_key)
    return foo

class DredisMixin(object):
    @classmethod
    def add_incr(cls, key):
        cls.add_to_class(key, _make_get_value(key))
        cls.add_to_class(key+'_incr', _make_incr(key))
        cls.add_to_class(key+'_decr', _make_decr(key))


