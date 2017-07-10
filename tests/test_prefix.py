import json
from flask import url_for
from flask_slimrest.decorators import add_endpoint

from .slimrest_test_case import SlimRestTestCase


class PrefixTestCase(SlimRestTestCase):
    def setUp(self):
        super(PrefixTestCase, self).setUp()
        self.app.config['SERVER_NAME'] = 'localhost'

        @self.api.add_namespace('/test', namespace_endpoint_prefix='testprefix')
        class TestNamespace:
            @add_endpoint('/hello')
            def hello_endpoint(self):
                return 'Hello world!'


    def test_prefix(self):
        with self.app.app_context():
            self.assertEqual(url_for('testprefix_hello_endpoint'), 'http://localhost/test/hello')
