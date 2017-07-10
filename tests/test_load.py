import json
from flask_slimrest.decorators import add_endpoint, dump, load, load_json
from marshmallow import Schema, fields

from .slimrest_test_case import SlimRestTestCase

class LoadTestCase(SlimRestTestCase):
    def setUp(self):
        super(LoadTestCase, self).setUp()

        class TestA:
            def __init__(self, hello):
                self.hello = hello

        class TestSchemaA(Schema):
            hello = fields.String(required=True)

        @self.api.add_namespace('/test')
        class TestNamespace:

            @add_endpoint('/post', methods=['POST'])
            @dump(TestSchemaA())
            @load(TestSchemaA())
            def post_endpoint(self, data):
                return data.data

            @add_endpoint('/post_json', methods=['POST'])
            @load_json
            def post_json_endpoint(self, data):
                return json.dumps(data)

    def test_post_correct(self):
        with self.app.test_client() as c:
            data = {
                'hello': 'World'
            }
            rv = c.post('/test/post', data=json.dumps(data), content_type='application/json')
            self.assertEqual(rv.status_code, 200)
            self.assertJSONData(rv, data)

    def test_post_no_data(self):
        with self.app.test_client() as c:
            rv = c.post('/test/post')
            self.assertEqual(rv.status_code, 400)

    def test_post_incorrect_data(self):
        with self.app.test_client() as c:
            rv = c.post('/test/post', data='Some random stuff', content_type='application/json')
            self.assertEqual(rv.status_code, 400)

    def test_post_wrong_content_type(self):
        with self.app.test_client() as c:
            data = {
                'hello': 'World'
            }
            rv = c.post('/test/post', data=json.dumps(data))
            self.assertEqual(rv.status_code, 400)

    def test_post_validation_fails(self):
        with self.app.test_client() as c:
            data = {
                'nohello': 'present'
            }
            rv = c.post('/test/post', data=json.dumps(data), content_type='application/json')
            self.assertEqual(rv.status_code, 400)

    def test_post_json_correct(self):
        with self.app.test_client() as c:
            data = {
                'hello': 'World'
            }
            rv = c.post('/test/post_json', data=json.dumps(data), content_type='application/json')
            self.assertEqual(rv.status_code, 200)
            self.assertJSONData(rv, data)

    def test_post_json_incorrect_data(self):
        with self.app.test_client() as c:
            rv = c.post('/test/post_json', data='Some random stuff', content_type='application/json')
            self.assertEqual(rv.status_code, 400)

    def test_post_json_wrong_content_type(self):
        with self.app.test_client() as c:
            data = {
                'hello': 'World'
            }
            rv = c.post('/test/post_json', data=json.dumps(data))
            self.assertEqual(rv.status_code, 400)