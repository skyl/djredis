Add redis fields to your django models.

Requirements
============

djredis requires redis-server, redis-py and redish.

http://github.com/antirez/redis

http://github.com/andymccurdy/redis-py

http://github.com/ask/redish

The DredisMixin Class
=====================

Using the DredisMixin is shown below.  Optionally add a method, ``redis_key`` to your modelclass
that returns the unique keyspace for the instance.

::

  from djredis.models import DredisMixin

  class Blog(models.Model, DredisMixin): # inherit from the mixin class
      author = models.ForeignKey('Author')
      title = models.CharField(max_length=200)
      ...

      # optionally add a unique keyspace for the instance - default is shown below
      def redis_key(self):
          return '%s:%s:%s' % (self._meta.app_label, self._meta.module_name, self.pk)

  Blog.add_incr('viewcount') # add the viewcount methods to your instances


The call to ``.add_incr('viewcount')`` gives us 3 methods on our instances,
``viewcount()`` retrieves the viewcount, 
``viewcount_incr()`` adds 1 to the viewcount, 
``viewcount_decr()`` subtracts 1 from the viewcount.

Using your model from the shell, instances should now have these new attrs:

::

    >>> b = Blog.objects.get(..) # get a Blog instance
    >>> b.viewcount()
    0
    >>> b.viewcount_incr()
    1
    >>> b.viewcount_incr()
    2
    >>> b.viewcount()
    2
    >>> b.viewcount_decr()
    1

Note that you should not run your redis methods on unsaved model instances.
The pk is used in building the redis key.  So, running the
methods on unsaved instances will save the data in redis under say,
``content:blog:None`` instead of say ``content:blog:53``::

    >>> b = Blog()
    >>> b.mylist().append('bar')
    >>> b.redis_keys()
    ['content:blog:None:mylist']

This behavior serves no apparent purpose and will probably be changed.

You may create a field in your model to persist the data in your rdbms.
Pass the name of this field as a string to ``.add_incr`` and you get another method, ``_save()``.
Checkout out the same example modified to use this functionality::

  from djredis.models import DredisMixin

  class Blog(models.Model, DredisMixin): # inherit from the mixin class
      ...
      views = models.PositiveIntegerField(blank=True, null=True)
      ...

  Blog.add_incr('viewcount', 'views') # add the viewcount methods to your instances

Now you can save the number to the rdbms when you want::

    >>> b=Blog.objects.all()[0] # get an object that is already in the db
    >>> b.viewcount()
    0
    >>> b.viewcount_incr()
    1
    >>> b.viewcount_incr()
    2
    >>> b.views # still none until we save
    >>> b.viewcount_save()
    >>> b.views # now that we have saved, we get the number back
    2
    >>> Blog.objects.all().order_by('views') # and we can use the ORM on this field


Other types of fields
~~~~~~~~~~~~~~~~~~~~~

``MyModel.add_string('fieldname', persist_field=None)`` corresponds to string values
that are not serialized with pickle::

    inst.fieldname() # returns value
    inst.fieldname_append('mystr') # appends 'mystr' to the string at fieldname
    inst.fieldname_exists() # True/False
    # if you supply a persist_field on your model, you can write with:
    inst.fieldname_save()
    # more to come

``MyModel.add_object('fieldname')``.  Redis can actually store any picklable python objects::

    inst.fieldname() # returns the object at the key.
    inst.fieldname_set({'foo': barobject}) # puts the dict in the db, objs and all
    inst.fieldname_getset({}) # sets the field to the python object, returning the current
    # more to come

``MyModel.add_list('fieldname')``.  Adds a redish list at fieldname::

    inst.fieldname() # returns the redish list
    # this object can be interacted with directly:
    inst.fieldname().append('some string')
    inst.fieldname().appendleft('baz')
    # see http://github.com/ask/redish

``MyModel.add_dict('fieldname')``.  Adds a callable at `fieldname`
returning a redish.types.Dict::

    inst.fieldname() # returns the redish dict
    inst.fieldname().update({'foo':'bar'})
    # work with this object directly:
    inst.fieldname().pop(dict_key) # removes the k/v at dict_key and returns the value

``MyModel.add_set('fieldname')``.  Adds a callable at `fieldname`
returning a redish.types.Set::

    inst.fieldname() # returns the redish set
    # work with this object directly
    inst.fieldname().add('somestring')
    inst.fieldname().intersection(other_set) # returns a new set

``MyModel.add_zset('fieldname')``.  Adds a callable at `fieldname`
returning a redish.types.SortedSet::

    inst.fieldname() # returns the set
    # work with this object
    inst.fieldname().add('some string') # returns True if added else False


Table-level fields
~~~~~~~~~~~~~~~~~~

Redis methods can also be added as classmethods.
The same api is evolving for this.  The persist_field option does not exist
for these calls.  To add classmethods to your class, the following methods are currently
available.

``add_incr_to_class``.  After MyModel inherits from the mixin::

    MyModel.add_incr_to_class('countername')
    MyModel.countername() # returns the number, (0 if no key in db)
    MyModel.countername_incr() # adds 1
    MyModel.countername_decr() # subtracts 1
    

``add_string_to_class``.  This is for adding an unpickled string field to your ModelClass::

    MyModel.add_string_to_class('foostring')
    MyModel.foostring() # returns the string
    # more to come

``add_object_to_class``.  For adding a pickled object to you ModelClass::

    MyModel.add_object_to_class('myobject')
    MyModel.myobject() # returns the stored object, None if the key has not been set.
    MyModel.myobject_set(obj) # stores obj
    MyModel.myobject_getset(obj) # returns the stored object and sets the value to obj

The following methods create callables that return redish objects.
See the redish docs for more on how to interact with them.

``add_list_to_class``.  Creates a callable on the class that returns a
redish.types.List::

    MyModel.add_list_to_class('mylist')
    MyModel.mylist() # returns List object
    MyModel.mylist().appendleft('foo') #appends the string to the head of the list
    MyModel.mylist().popleft() # returns 'foo' and removes it from the db

``add_dict_to_class``.  Creates a callable on the class that returns a
redish.types.Dict::

    MyModel.add_dict_to_class('mydict')
    MyModel.mydict() # returns the Dict object

``add_set_to_class``.  Creates a callable on the class that returns a
redish.types.Set::

    MyModel.add_set_to_class('myset')
    MyModel.myset() # returns the Set object

``add_zset_to_class``.  Creates a callable on the class that returns a
redish.types.SortedSet::

    MyModels.add_zset_to_class('myzset')
    MyModel.myzset() # returns the SortedSet object


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

