Add redis fields to your django models.


The DredisMixin
===============

Using the DredisMixin is shown below.  Add a method, ``redis_key`` to your modelclass
that returns the unique keyspace for the instance.

::


  from djredish.models import DredisMixin

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

Other types of fields
~~~~~~~~~~~~~~~~~~~~~


``MyModel.add_string('fieldname')`` supplies::

    inst.fieldname() # returns value
    inst.fieldname_append('mystr') # appends 'mystr' to the string at fieldname
    inst.fieldname_exists() # True/False
    # more to come

``MyModel.add_object('fieldname')``.  Redis can actually store any picklable python objects::

    inst.fieldname() # returns the object at the key.
    inst.fieldname_set({'foo': barobject}) # puts the dict in the db, objs and all
    # more to come

``MyModel.add_list('fieldname')``.  Adds a redis list at fieldname::

    inst.fieldname() # returns the list stored at fieldname
    inst.fieldname_lpush('somestring') # I think it's just strings right now
    inst.fieldname_rpush('somestring')
    # more to come

