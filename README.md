Flask-SlimREST
==============

[![Build Status](https://travis-ci.org/fabian-marquardt/flask-slimrest.svg?branch=master)](https://travis-ci.org/fabian-marquardt/flask-slimrest)
[![codecov](https://codecov.io/gh/fabian-marquardt/flask-slimrest/branch/master/graph/badge.svg)](https://codecov.io/gh/fabian-marquardt/flask-slimrest)
[![Requirements Status](https://requires.io/github/fabian-marquardt/flask-slimrest/requirements.svg?branch=master)](https://requires.io/github/fabian-marquardt/flask-slimrest/requirements/?branch=master)


Flask + marshmallow + Flask-SlimREST = ♥ RESTful APIs ♥
---------------------------------------------------------

In today’s world, providing a RESTful interface is often the primary requirement for a backend application server. Flask has proved to be a very flexible and powerful framework which enables developers to produce great results in a short time. But while Flask provides great functionality for generating HTML-based content out of the box, this is not the case for RESTful APIs.

Flask-SlimREST tries to fill this gap by providing some convenience functionality for implementing RESTful applications with Flask and marshmallow.

A first look ...
----------------

```python
app = Flask(__name__)
api = SlimRest(app)

@api.add_namespace('/heroes')
class HeroNamespace:
    @add_endpoint('/')
    @dump(HeroSchema(), paginated=True)
    @paginate(_pagination_helper)
    def hero_collection(self):
        return db.get_heroes()

    @add_endpoint('/<id>')
    @catch(ValueError, 'No hero with this ID found.', 404)
    @dump(HeroSchema())
    def hero_details(self, id):
        return db.get_hero(int(id))

    @add_endpoint('/', methods=['POST'])
    @dump(HeroSchema(), return_code=201)
    @load(HeroSchema())
    def hero_post(self, data):
        return db.add_hero(Hero(None, data.data['hero_name'], data.data['character_trait']))
```

Installation
------------

Using pip:

    pip install flask-slimrest

Documentation
-------------

[Documentation](http://flask-slimrest.readthedocs.io/en/latest/)
