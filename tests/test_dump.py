import json
from math import ceil

from flask import request, url_for
from flask_slimrest.decorators import add_endpoint, dump, paginate
from flask_slimrest.exceptions import NoMatchingSchemaError
from flask_slimrest.pagination import PaginationResult
from marshmallow import Schema, fields

from .slimrest_test_case import SlimRestTestCase


def _get_page_link(page_number):
    return url_for(request.url_rule.endpoint, page=page_number, _external=True)


def _pagination_helper(objects, per_page=2):
    if 'page' in request.args:
        page = int(request.args['page'])
    else:
        page = 1

    page_count = ceil(len(objects)/per_page)
    paginated_objects = objects[(page-1)*per_page:per_page]

    return PaginationResult(
        paginated_objects,
        page,
        page_count,
        _get_page_link(page+1) if page < page_count else None,
        _get_page_link(page-1) if page > 1 else None
    )


class DumpTestCase(SlimRestTestCase):
    def setUp(self):
        super(DumpTestCase, self).setUp()

        class TestA:
            def __init__(self, hello):
                self.hello = hello

        class TestB:
            def __init__(self, foo):
                self.foo = foo

        class TestSchemaA(Schema):
            hello = fields.String(required=True)

        class TestSchemaB(Schema):
            foo = fields.String(required=True)


        @self.api.add_namespace('/test')
        class TestNamespace:

            @add_endpoint('/valid_a')
            @dump(TestSchemaA())
            def valid_endpoint(self):
                return TestA('Hello world!')

            @add_endpoint('/invalid_a')
            @dump(TestSchemaA())
            def invalid_endpoint(self):
                return TestB('I am not TestA')

            @add_endpoint('/valid_mapping')
            @dump({'TestA': TestSchemaA()})
            def valid_mapping_endpoint(self):
                return TestA('Hello world!')

            @add_endpoint('/invalid_mapping')
            @dump({'TestA': TestSchemaA()})
            def invalid_mapping_endpoint(self):
                return TestB('I am not TestA')

            @add_endpoint('/incorrect_type')
            @dump('This is not the right type')
            def incorrect_type_endpoint(self):
                return None

            @add_endpoint('/valid_paginated')
            @dump(TestSchemaA(), paginated=True)
            @paginate(_pagination_helper)
            def valid_paginated_endpoint(self):
                return [TestA('1'), TestA('2'), TestA('3'), TestA('4')]

            @add_endpoint('/invalid_paginated')
            @dump(TestSchemaA(), paginated=True)
            def invalid_paginated_endpoint(self):
                return 'This is not a PaginationResult object'

    def test_valid_a(self):
        with self.app.test_client() as c:
            rv = c.get('/test/valid_a')
            self.assertEqual(rv.status_code, 200)
            self.assertJSONData(rv, {'hello': 'Hello world!'})

    def test_invalid_a(self):
        with self.app.test_client() as c:
            rv = c.get('/test/invalid_a')
            self.assertEqual(rv.status_code, 200)
            self.assertJSONData(rv, {})

    def test_valid_mapping(self):
        with self.app.test_client() as c:
            rv = c.get('/test/valid_mapping')
            self.assertEqual(rv.status_code, 200)
            self.assertJSONData(rv, {'hello': 'Hello world!'})

    def test_invalid_mapping(self):
        with self.assertRaises(NoMatchingSchemaError):
            with self.app.test_client() as c:
                rv = c.get('/test/invalid_mapping')

    def test_incorrect_type(self):
        with self.assertRaises(TypeError):
            with self.app.test_client() as c:
                rv = c.get('/test/incorrect_type')

    def test_valid_paginated(self):
        with self.app.test_client() as c:
            rv = c.get('/test/valid_paginated')
            self.assertEqual(rv.status_code, 200)
            result = json.loads(rv.data.decode())
            self.assertEqual(result['page'], 1)
            self.assertEqual(result['page_count'], 2)
            self.assertEqual(result['next'], url_for('test_namespace_valid_paginated_endpoint', page=2, _external=True))

    def test_invalid_paginated(self):
        with self.assertRaises(TypeError):
            with self.app.test_client() as c:
                rv = c.get('/test/invalid_paginated')
