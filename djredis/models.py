import pickle
from functools import partial
from django.db import models

from redish.client import Client
from redish import serialization


# override and divide and balance with settings?
# db = Client(host="localhost", port=6379, db="") # default settings.
db = Client(serializer=serialization.Plain())
db_pickle = Client(serializer=serialization.Pickler())
db_json = Client(serializer=serialization.JSON())

######
#Class-level fields
####################

# INCR

def _get_incr_class(key):
    @classmethod
    def get_incr_value(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        return int(db.api.get(full_key)) if db.api.get(full_key) else 0
    return get_incr_value

def _incr_class(key):
    @classmethod
    def incr_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        return db.api.incr(full_key)
    return incr_class

def _decr_class(key):
    @classmethod
    def decr_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        return db.api.decr(full_key)
    return decr_class

# Plain String

def _get_str_class(key):
    @classmethod
    def get_str_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        if db.api.get(full_key):
            return db[full_key]
        else:
            db[full_key] = ''
            return ''
    return get_str_class

# Object

def _get_object_class(key):
    @classmethod
    def get_object_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        if db.api.get(full_key):
            return db_pickle[full_key]
        else:
            return None
    return get_object_class

def _set_object_class(key):
    @classmethod
    def set_object_class(cls, value):
        full_key = '%s:%s' % (cls.redis_base(), key)
        db_pickle[full_key] = value
    return set_object_class

def _getset_object_class(key):
    @classmethod
    def getset(cls, obj):
        full_key = '%s:%s' % (cls.redis_base(), key)
        return pickle.loads(db.api.getset(full_key, pickle.dumps(obj)))
    return getset

#List
def _get_list_class(key):
    @classmethod
    def get_list(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        return db.List(full_key)
    return get_list

#Dict
def _get_dict_class(key):
    @classmethod
    def get_dict(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        return db.Dict(full_key)
    return get_dict

#Set
def _get_set_class(key):
    @classmethod
    def get_set(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        return db.Set(full_key)
    return get_set

#SortedSet
def _get_zset_class(key):
    @classmethod
    def get_zset(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        return db.SortedSet(full_key)
    return get_zset


######
#Instance-level fields
#######################

#Incr/Decr
def _get_incr(key):
    def get_incr_value(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        return int(db.api.get(full_key)) if db.api.get(full_key) else 0
    return get_incr_value

def _incr(key):
    def incr(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        return db.api.incr(full_key)
    return incr

def _decr(key):
    def decr(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        return db.api.decr(full_key)
    return decr

def _save_incr(key, persist_field):
    def redis_save(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        value = int(db.api.get(full_key)) if db.api.get(full_key) else 0
        setattr(self, persist_field, value)
        self.save()
    return redis_save

#String

def _get_string(key):
    def get(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        if db.api.get(full_key):
            return db[full_key]
        else:
            db[full_key] = ''
            return ''
    return get

def _append_string(key):
    def append(self, value):
        full_key = '%s:%s' % (self.redis_key(), key)
        if not full_key in db:
            db.api.set(full_key, value)
        else:
            db.api.append(full_key, value)
        return db.api.get(full_key)

    return append

def _exists_string(key):
    def exists(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        return db.api.exists(full_key)
    return exists

def _save_string(key, persist_field):
    def redis_save(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        value = db.api.get(full_key) if db.api.get(full_key) else ''
        setattr(self, persist_field, value)
        self.save()
    return redis_save

#Object

def _get_object(key):
    def get(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        if db.api.get(full_key):
            return db_pickle[full_key]
        else:
            return None
    return get

def _set_object(key):
    def set(self, value):
        full_key = '%s:%s' % (self.redis_key(), key)
        db_pickle[full_key] = value
        #return value
    return set

def _getset_object(key):
    def getset(self, obj):
        full_key = '%s:%s' % (self.redis_key(), key)
        return pickle.loads(db.api.getset(full_key, pickle.dumps(obj)))
    return getset

def _save_object(key, persist_field):
    def redis_save(self):
        full_key = '%s:%s' % (self.redis_key(), key)
        value = db.api.get(full_key) if db.api.get(full_key) else ''
        setattr(self, persist_field, value)
        self.save()
    return redis_save


class BaseField(object):

    def __init__(self):
        pass

    def contribute_to_class(self, cls, name):
        self.key = name
        #signals.pre_init.connect(self.instance_pre_init, sender=cls, weak=False)
        setattr(cls, name, self)

    def __delete__(self, obj):
        del(db[self.full_key])


class List(BaseField):

    def __get__(self, obj, objname=None):
        self.full_key = '%s:%s' % (obj.redis_key(), self.key)
        return db.List(self.full_key)

    def __set__(self, obj, value):
        if db.api.exists(self.full_key):
            del(db[self.full_key])
        db.List(self.full_key, value)


class Dict(BaseField):

    def __get__(self, obj, objname=None):
        self.full_key = '%s:%s' % (obj.redis_key(), self.key)
        return db.Dict(self.full_key)

    def __set__(self, obj, value):
        if db.api.exists(self.full_key):
            del(db[self.full_key])
        db.Dict(self.full_key, value)


class Set(BaseField):

    def __get__(self, obj, objname=None):
        self.full_key = '%s:%s' % (obj.redis_key(), self.key)
        return db.Set(self.full_key)

    def __set__(self, obj, value):
        '''value is an iterable'''
        if db.api.exists(self.full_key):
            del(db[self.full_key])
        db.Set(self.full_key, value)

class Zset(BaseField):

    def __get__(self, obj, objname=None):
        full_key = '%s:%s' % (obj.redis_key(), self.key)
        return db.SortedSet(full_key)

    def __set__(self, obj, value):
        '''value is an iterable of key/score tuples'''
        if db.api.exists(self.full_key):
            del(db[self.full_key])
        db.SortedSet(self.full_key, value)


class DredisMixin(object):
    '''Mixin class to go with models.Model

    ex::

        class C(models.Model, DredisMixin):
            ...
            # optionally add your own key
            def redis_key(self):
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

    ####
    #Base mixin methods
    ###################

    def redis_key(self):
        return '%s:%s:%s' % (self._meta.app_label, self._meta.module_name, self.pk)

    def redis_items(self):
        return db.items(pattern='%s*' % self.redis_key())

    def redis_keys(self):
        return db.keys('%s*' % self.redis_key())

    @classmethod
    def redis_base(cls):
        return '%s:%s' % (cls._meta.app_label, cls._meta.module_name)

    ###
    #Add class methods
    ##################

    @classmethod
    def add_incr_to_class(cls, key):
        setattr(cls, key, _get_incr_class(key))
        setattr(cls, '%s_incr' % key, _incr_class(key))
        setattr(cls, '%s_decr' % key, _decr_class(key))

    @classmethod
    def add_string_to_class(cls, key):
        setattr(cls, key, _get_str_class(key))

    @classmethod
    def add_object_to_class(cls, key):
        '''Pickled objects'''
        setattr(cls, key, _get_object_class(key))
        setattr(cls, '%s_set' % key, _set_object_class(key))
        setattr(cls, '%s_getset' % key, _getset_object_class(key))

    @classmethod
    def add_list_to_class(cls, key):
        setattr(cls, key, _get_list_class(key))

    @classmethod
    def add_dict_to_class(cls, key):
        setattr(cls, key, _get_dict_class(key))

    @classmethod
    def add_set_to_class(cls, key):
        setattr(cls, key, _get_set_class(key))

    @classmethod
    def add_zset_to_class(cls, key):
        setattr(cls, key, _get_zset_class(key))


    ######
    #Add instance methods
    #####################

    @classmethod
    def add_incr(cls, key, persist_field=None):
        cls.add_to_class(key, _get_incr(key))
        cls.add_to_class('%s_incr' % key, _incr(key))
        cls.add_to_class('%s_decr' % key, _decr(key))
        if persist_field:
            cls.add_to_class('%s_save' % key, _save_incr(key, persist_field))

    @classmethod
    def add_string(cls, key, persist_field=None):
        cls.add_to_class(key, _get_string(key))
        cls.add_to_class('%s_append' % key, _append_string(key))
        cls.add_to_class('%s_exists' % key, _exists_string(key))
        if persist_field:
            cls.add_to_class('%s_save' % key, _save_string(key, persist_field))

    '''
    @classmethod
    def add_object(cls, key, persist_field=None):
        cls.add_to_class(key, _get_object(key))
        cls.add_to_class('%s_set' % key, _set_object(key))
        cls.add_to_class('%s_getset' % key, _getset_object(key))
        if persist_field:
            cls.add_to_class('%s_save' % key, _save_object(key, persist_field))

    '''
