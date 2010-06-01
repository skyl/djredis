import pickle
from functools import partial
#from django.db import models

from redish.client import Client
from redish import serialization


# override and divide and balance with settings?
# db = Client(host="localhost", port=6379, db="") # default settings.
# should also consider making the db non-global, local to the instance
# and configurable in a more fine-grained way

db = Client(serializer=serialization.Plain())
db_pickle = Client(serializer=serialization.Pickler())
db_json = Client(serializer=serialization.JSON())


######
#Class-level fields
####################

# INCR
def _get_incr_class(cls, key):
    full_key = '%s:%s' % (cls.redis_base(), key)
    return db.Incr(full_key)

def _del_incr_class(key):
    @classmethod
    def del_incr_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        if db.api.exists(full_key):
            del(db[full_key])
    return del_incr_class


# Plain String
def _get_str_class(cls, key):
    full_key = '%s:%s' % (cls.redis_base(), key)
    return db.String(full_key)

def _del_string_class(key):
    @classmethod
    def del_string_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        if db.api.exists(full_key):
            del(db[full_key])
    return del_string_class


# Object
def _get_object_class(cls, key):
    full_key = '%s:%s' % (cls.redis_base(), key)
    return db.Object(full_key)

def _del_object_class(key):
    @classmethod
    def del_object_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        if db.api.exists(full_key):
            del(db[full_key])
    return del_object_class


#List
def _get_list_class(cls, key):
    full_key = '%s:%s' % (cls.redis_base(), key)
    return db.List(full_key)

def _del_list_class(key):
    @classmethod
    def del_list_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        if db.api.exists(full_key):
            del(db[full_key])
    return del_list_class


#Dict
def _get_dict_class(cls, key):
    full_key = '%s:%s' % (cls.redis_base(), key)
    return db.Dict(full_key)

def _del_dict_class(key):
    @classmethod
    def del_dict_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        if db.api.exists(full_key):
            del(db[full_key])
    return del_dict_class


#Set
def _get_set_class(cls, key):
    full_key = '%s:%s' % (cls.redis_base(), key)
    return db.Set(full_key)

def _del_set_class(key):
    @classmethod
    def del_set_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        if db.api.exists(full_key):
            del(db[full_key])
    return del_set_class


#SortedSet
def _get_zset_class(cls, key):
    full_key = '%s:%s' % (cls.redis_base(), key)
    return db.SortedSet(full_key)

def _del_zset_class(key):
    @classmethod
    def del_zset_class(cls):
        full_key = '%s:%s' % (cls.redis_base(), key)
        if db.api.exists(full_key):
            del(db[full_key])
    return del_zset_class



class BaseField(object):

    def __init__(self, persist_field=None):
        self.persist_field = persist_field

    def contribute_to_class(self, cls, name):
        self.key = name
        self.model = cls
        #signals.pre_init.connect(self.instance_pre_init, sender=cls, weak=False)
        setattr(cls, name, self)

    '''
        if self.persist_field:
            setattr(cls, '%s_save' % self.key, self._save)

    # right now, there is no support for persistence, more thought needed.
    # the following would just store the repr() in a TextField say ..
    # adhoc hacking of the save() method/signals is probably going to be
    # the right level of abstraction for now

    def _save(self):
        if hasattr(self, 'obj'):
            setattr(self.obj, self.persist_field, self.__get__(self.obj))
            self.obj.save()

        else:
            raise AttributeError(u"The descriptor has not been prepared")
    '''

    def _prepare_descriptor(self, obj):
        if obj is None:
            raise AttributeError(u"%s must be accessed via instance" % self.key)

        self.obj = obj
        self.full_key = '%s:%s' % (obj.redis_key(), self.key)

    def __get__(self, obj, objname=None):
        self._prepare_descriptor(obj)

    def __set__(self, obj, value):
        self._prepare_descriptor(obj)
        if db.api.exists(self.full_key):
            del(db[self.full_key])

    def __delete__(self, obj):
        self._prepare_descriptor(obj)
        if db.api.exists(self.full_key):
            del(db[self.full_key])


class Incr(BaseField):

    def __get__(self, obj, objname=None):
        super(Incr, self).__get__(obj, objname)
        return db.Incr(self.full_key)

    def __set__(self, obj, value):
        super(Incr, self).__set__(obj, value)
        db.Incr(self.full_key).set(value)


class String(BaseField):

    def __get__(self, obj, objname=None):
        super(String, self).__get__(obj, objname)
        return db.String(self.full_key)

    def __set__(self, obj, value):
        super(String, self).__set__(obj, value)
        db.api.set(self.full_key, value)


class Object(BaseField):

    def __get__(self, obj, objname=None):
        super(Object, self).__get__(obj, objname)
        return db.Object(self.full_key)

    def __set__(self, obj, value):
        super(Object, self).__set__(obj, value)
        db.Object(self.full_key).set(value)


class List(BaseField):

    def __get__(self, obj, objname=None):
        super(List, self).__get__(obj, objname)
        return db.List(self.full_key)

    def __set__(self, obj, value):
        super(List, self).__set__(obj, value)
        db.List(self.full_key, value)


class Dict(BaseField):

    def __get__(self, obj, objname=None):
        super(Dict, self).__get__(obj, objname)
        return db.Dict(self.full_key)

    def __set__(self, obj, value):
        super(Dict, self).__set__(obj, value)
        db.Dict(self.full_key, value)


class Set(BaseField):

    def __get__(self, obj, objname=None):
        super(Set, self).__get__(obj, objname)
        return db.Set(self.full_key)

    def __set__(self, obj, value):
        '''value is an iterable'''
        super(Set, self).__set__(obj, value)
        db.Set(self.full_key, value)


class Zset(BaseField):

    def __get__(self, obj, objname=None):
        super(Zset, self).__get__(obj, objname)
        return db.SortedSet(self.full_key)

    def __set__(self, obj, value):
        '''value is an iterable of key/score tuples'''
        super(Zset, self).__set__(obj, value)
        db.SortedSet(self.full_key, value)


class DredisMixin(object):
    '''Mixin class to go with models.Model

    ex::

        import djredis.models

        class C(models.Model, DredisMixin):
            ...

            # add you instance descriptors declaratively
            counter = djredis.models.Incr()
            myzset = djredis.models.Zset()

            # optionally add your own key
            def redis_key(self):
                return 'unique_space:%s' % (self.id)


        >>> c = C.objects.get(...) # get an object that has been saved
        >>> c.counter
        0
        >>> c.counter.incr()
        1
        >>> c.counter.decr()
        0
        >>> c.myzset
        <SortedSet: []>
        >>> c.myzset.add('foo', 10)
        True
        >>> c.myzset
        <SortedSet: ['foo']>

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
        setattr(cls, key, _get_incr_class(cls, key))
        setattr(cls, '%s_delete' % key, _del_incr_class(key))

    @classmethod
    def add_string_to_class(cls, key):
        setattr(cls, key, _get_str_class(cls, key))
        setattr(cls, '%s_delete' % key, _del_string_class(key))

    @classmethod
    def add_object_to_class(cls, key):
        setattr(cls, key, _get_object_class(cls, key))
        setattr(cls, '%s_delete' % key, _del_object_class(key))

    @classmethod
    def add_list_to_class(cls, key):
        setattr(cls, key, _get_list_class(cls, key))
        setattr(cls, '%s_delete' % key, _del_list_class(key))

    @classmethod
    def add_dict_to_class(cls, key):
        setattr(cls, key, _get_dict_class(cls, key))
        setattr(cls, '%s_delete' % key, _del_dict_class(key))

    @classmethod
    def add_set_to_class(cls, key):
        setattr(cls, key, _get_set_class(cls, key))
        setattr(cls, '%s_delete' % key, _del_set_class(key))

    @classmethod
    def add_zset_to_class(cls, key):
        setattr(cls, key, _get_zset_class(cls, key))
        setattr(cls, '%s_delete' % key, _del_zset_class(key))

