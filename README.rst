Add redis fields to your django models.


The DredisMixin
===============

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
          return '%s:%s:%s' % (self._meta.app_label, self._meta.module_name, self.id)


  Blog.add_incr('viewcount') # add the viewcount methods to your instances


The call to ``.add_incr('viewcount')`` gives us 3 methods on our instances,
``viewcount()`` retrieves the viewcount, 
``viewcount_incr()`` adds 1 to the viewcount, 
``viewcount_decr()`` subtracts 1 from the viewcount.

Using you model from the shell, instances should now have these new attrs:

::

    >>> b = Blog()
    >>> b.viewcount()
    >>> b.viewcount_incr()
    1
    >>> b.viewcount_incr()
    2
    >>> b.viewcount()
    2
    >>> b.viewcount_decr()
    1

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
of the redish.types.Dict type::

    inst.fieldname() # returns the redish dict
    # work with this object directly:
    inst.fieldname().pop(dict_key) # removes the k/v at dict_key and returns the value

``MyModel.add_set('fieldname')``.  Adds a callable at `fieldname`
of the redish.types.Set type::

    inst.fieldname() # returns the redish set
    # work with this object directly
    inst.fieldname().add('somestring')
    inst.fieldname().intersection(other_set) # returns a new set


