Add redis fields to your django models.

Requirements
============

djredis requires redis-server, redis-py and redish.

http://github.com/antirez/redis

http://github.com/andymccurdy/redis-py

I've added a couple of types to the main redish, hopefully we can get these
put into:
http://github.com/ask/redish

For right now, we have to run djredish with my fork:
http://github.com/skyl/redish.git


The DredisMixin Class
=====================

Using the DredisMixin is shown below.  Optionally add a method, ``redis_key`` to your modelclass
that returns the unique keyspace for the instance.

::

    from djredis.models import DredisMixin
    import djredis.models

    class Blog(models.Model, DredisMixin): # inherit from the mixin class
        # use django's normal models stuff
        author = models.ForeignKey('Author')
        title = models.CharField(max_length=200)
        
        # add some redis fields to the model instances declaratively:
        mycounter = djredis.models.Incr()
        mystring = djredis.models.String()
        myobject = djredis.models.Object()
        mydict = djredis.models.Dict()
        mylist = djredis.models.List()
        myset = djredis.models.Set()
        myzset = djredis.models.Zset()
     
      # optionally add a unique keyspace for the instance - default is shown below
      def redis_key(self):
          return '%s:%s:%s' % (self._meta.app_label, self._meta.module_name, self.pk)

    # add table-level redis fields to the class
    Blog.add_incr_to_class('classincr')
    Blog.add_string_to_class('classstring')
    Blog.add_object_to_class('classobject')
    Blog.add_dict_to_class('classdict')
    Blog.add_list_to_class('classlist')
    Blog.add_set_to_class('classset')
    Blog.add_zset_to_class('classzset')

``djredis.models.X()`` is a data descriptor instance that has `__get__`, `__set__` and
`__delete__` defined.  So, we can now grab a Blog instance and get and set the
attributes that we created in our model definition.

``djredis.models.Incr()``, a descriptor for redish.types.Incr::

    >>> b = Blog.objects.get(...) # get a blog instance
    >>> b.mycounter
    0
    >>> type(b.mycounter)
    <class 'redish.types.Incr'>
    >>> b.mycounter.incr(5)
    5
    >>> b.mycounter.decr(1)
    4
    >>> del(b.mycounter)
    >>> b.mycounter
    0
    >>> b.mycounter = 10
    >>> type(b.mycounter)
    <class 'redish.types.Incr'>
    
``djredis.models.String()``, a descriptor for redish.types.String::

    >>> b.mystring
    ''
    >>> type(b.mystring)
    <class 'redish.types.String'>
    >>> b.mystring = 'foobar'
    >>> b.mystring.getset('bar')
    'foobar'
    >>> b.mystring
    'bar'
    >>> del(b.mystring)
    >>> type(b.mystring)
    <class 'redish.types.String'>

``djredis.models.Object()``, a descriptor for redish.types.Object, able to
store any picklable python objects::

    >>> b.myobject
    None
    >>> type(b.myobject)
    <class 'redish.types.Object'>
    >>> b.myobject = int
    >>> b.myobject
    <type 'int'>
    >>> b.myobject.getset({})
    <type 'int'>
    >>> b.myobject
    {}
    >>> type(b.myobject)
    <class 'redish.types.Object'>
    >>> del(b.myobject)
    >>> b.myobject
    None

``Dict``, ``List``, ``Set`` and ``Zset`` work similarly.  They are also data
descriptors that allow
access to their respective ``redish.types`` and should be documented as the 
underlying apis stabilize.

Note that you should not use the descriptors on unsaved model instances.
The pk is used in building the redis key.  So, setting and accessing
the attributes on an unsaved model instance will save the data in redis under say,
``content:blog:None:mylist`` instead of say ``content:blog:53:mylist``::

    >>> b = Blog()
    >>> b.mylist.append('bar')
    >>> b.redis_keys()
    ['content:blog:None:mylist']
    >>> b.mylist.name
    'content:blog:None:mylist'

This behavior serves no apparent purpose and will probably be changed.



Table-level fields
~~~~~~~~~~~~~~~~~~

Redis types can also be added as attributes of the class using classmethods.
The attributes on the class that are created by the calls to the class methods
are not descriptors however.  Therefore, one must be careful not to try to
use set or delete these attributes.  Setting these attributes directly is not
supported.  One may clear the value in redis by calling ``MyModel.myname_delete()``.

``add_incr_to_class``.  After MyModel inherits from the mixin::

    MyModel.add_incr_to_class('classincr')
    MyModel.classincr # the redish.types.Incr object
    MyModel.classincr.incr() # adds 1
    MyModel.classincr.decr() # subtracts 1
    # delete the value in the db
    MyModel.classincr_delete()
    
``add_string_to_class``.  This is for adding an unpickled string field to your ModelClass::

    MyModel.add_string_to_class('foostring')
    MyModel.foostring # the redish.types.String object
    MyModel.foostring_delete()
    # more to come

``add_object_to_class``.  For adding a pickled object to you ModelClass::

    MyModel.add_object_to_class('classobject')
    MyModel.classobject # the redish.types.Object object
    MyModel.classobject_set(obj) # stores obj
    MyModel.classobject_getset(obj) # returns the stored object and sets the value to obj
    MyModel.classobject_delete() # remove the k/v from the db

The following methods create callables that return redish objects.
See the redish docs for more on how to interact with them.

``add_list_to_class``.  Creates a callable on the class that returns a
redish.types.List::

    MyModel.add_list_to_class('classlist')
    MyModel.classlist # the redish.types.List object
    MyModel.classlist.appendleft('foo') #appends the string to the head of the list
    MyModel.classlist.popleft() # returns 'foo' and removes it from the db
    MyModel.classlist_delete() # remove the k/v from redis

``add_dict_to_class``.  Creates a callable on the class that returns a
redish.types.Dict::

    MyModel.add_dict_to_class('classdict')
    MyModel.classdict() # the redish.types.Dict object
    MyModel.classdict_delete()

``add_set_to_class``.  Creates a callable on the class that returns a
redish.types.Set::

    MyModel.add_set_to_class('classset')
    MyModel.classset # the redish.types.Set object
    MyModel.classset_delete()

``add_zset_to_class``.  Creates a callable on the class that returns a
redish.types.SortedSet::

    MyModels.add_zset_to_class('classzset')
    MyModel.classzset() # the redish.types.SortedSet object


Base methods
~~~~~~~~~~~~

Some methods are added to your class and instances by using the mixin.
These methods are added without further action.

Instance methods
----------------

``redis_key``.  Returns the unique key for the instance.

``redis_keys``.  Returns the existing keys in the db for the instance.

``redis_items``.  Returns the items (list of (k,v) pairs

Class methods
-------------

``redis_base``.  Returns the unique key for the modelclass.

