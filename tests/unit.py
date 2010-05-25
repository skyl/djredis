import unittest
#from django.conf import settings
#settings.configure()

from djredis.models import DredisMixin, db, db_pickle

class FakeMeta(object):
    app_label = 'fakemeta'
    module_name = 'myobject'

class FakeModel(object):
    _meta = FakeMeta()

class MyObj(FakeModel, DredisMixin):
    pk = 1

class TestRedis(unittest.TestCase):

    def setUp(self):
        self.obj = MyObj()
        self.cls = MyObj
        self.db = db

    def test_incr_class(self):
        key = 'classincr'
        self.cls.add_incr_to_class(key)
        self.assertEqual(self.cls.classincr(), 0)
        self.cls.classincr_incr()
        self.assertEqual(self.cls.classincr(), 1)
        self.cls.classincr_decr()
        self.assertEqual(self.cls.classincr(), 0)
        self.cls.classincr_delete()
        self.assertEqual(db.api.exists('%s:%s' % (self.cls.redis_base(), key)), False)

    def test_str_class(self):
        key = 'mystring'
        self.cls.add_string_to_class('mystring')
        self.assertEqual(self.cls.mystring(), '')
        self.assertEqual(db.api.exists('%s:%s' % (self.cls.redis_base(), key)), True)
        #what else are we going to do with strings?
        self.cls.mystring_delete()
        self.assertEqual(db.api.exists('%s:%s' % (self.cls.redis_base(), key)), False)

if __name__ == '__main__':
    unittest.main()

