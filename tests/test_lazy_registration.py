import unittest

from flask import Flask
from flask_slimrest import SlimRest
from flask_slimrest.decorators import add_endpoint

class LazyTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.api = SlimRest()

        @self.api.add_namespace('/test')
        class TestNamespace:

            @add_endpoint('/hello')
            def hello_endpoint(self):
                return 'Hello world!'

    def test_lazy_unregistered(self):
        with self.app.test_client() as c:
            rv = c.get('/test/hello')
            self.assertEqual(rv.status_code, 404)

    def test_lazy_registered(self):
        self.api.init_app(self.app)
        with self.app.test_client() as c:
            rv = c.get('/test/hello')
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(rv.data, b'Hello world!')