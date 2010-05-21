Add redis fields to your django models.


The DredisMixin
===============

Using the DredisMixin is shown below.  Add a method, ``redis_key`` to your modelclass
that returns the unique keyspace for the instance.

.. code-block:: python


  from djredish.models import DredisMixin

  class Blog(models.Model, DredisMixin): # inherit from the mixin class
      author = models.ForeignKey('Author')
      title = models.CharField(max_length=200)
      ...

      # add this method so that each instance gets a unique keyspace
      def redis_key(self):
          return '%s:%s:%s' % (self._meta.app_label, self._meta.module_name, self.id)


  Blog.add_incr('viewcount') # add the viewcount methods to your instances


The call to ``.add_incr('viewcount')`` gives us 3 methods on our instances,
``viewcount()`` retrieves the viewcount, 
``viewcount_incr()`` adds 1 to the viewcount, 
``viewcount_decr()`` subtracts 1 from the viewcount.

Using you model from the shell, instances should now have these new attrs:

.. code-block:: pycon

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

