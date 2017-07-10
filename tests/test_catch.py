import json

from flask_slimrest.decorators import add_endpoint, dump, catch
from marshmallow import Schema, fields

from .slimrest_test_case import SlimRestTestCase


class CatchTestCase(SlimRestTestCase):
    def setUp(self):
        super(CatchTestCase, self).setUp()

        @self.api.add_namespace('/test')
        class TestNamespace:
            @add_endpoint('/catch')
            @catch(ValueError, 'Catch test')
            def catch_endpoint(self):
                raise ValueError()


    def test_catch(self):
        with self.app.test_client() as c:
            rv = c.get('/test/catch')
            self.assertEqual(rv.status_code, 500)
            self.assertJSONData(rv, {'message': 'Catch test'})
