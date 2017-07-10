import unittest
import json
from flask import Flask
from flask_slimrest import SlimRest


class SlimRestTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.api = SlimRest(self.app)

    def assertJSONData(self, response, result):
        self.assertEqual(json.loads(response.data.decode()), result)