from functools import partial
from django.db import models


from redish.client import Client
from redish import serialization

# override and divide and balance with settings?
# db = Client(host="localhost", port=6379, db="") # default settings.
db = Client()
db_pickle = Client(serializer=serialization.Pickler())
db_json = Client(serializer=serialization.JSON())



#####
Incr/Decr
###########
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

#####
String
#############

def _make_get(key):
    def foo(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        return db.api.get(full_key)
    return foo

def _make_append(key):
    def foo(self, value):
        full_key = '%s:%s' % (self.redis_key(), key)
        return db.api.append(full_key, value)
    return foo

def _make_exists(key):
    def foo(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        return db.api.exists(full_key)
    return foo



class DredisMixin(object):
    '''Mixin class to go with models.Model

    ex::

        class C(models.Model, DredisMixin):
            ...

            def red_key(self):
                return 'unique_space:%s' % (self.id)

        C.add_incr(C, 'timesfavorited')

        >>> c = C()
        >>> c.timesfavorited_incr()
        1
        >>> c.timesfavorited()
        1
        >>> c.timesfavorited_decr()
        0
    '''

    @classmethod
    def add_incr(cls, key):
        cls.add_to_class(key, _make_get_value(key))
        cls.add_to_class('%s_incr' % key, _make_incr(key))
        cls.add_to_class('%s_decr' % key, _make_decr(key))

    @classmethod
    def add_string(cls, key):
        cls.add_to_class(key, _make_get_value(key))
        cls.add_to_class('%s_append' % key, _make_append(key))
        cls.add_to_class('%s_exists' % key, _make_exists(key))

