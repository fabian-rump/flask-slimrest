Flask-SlimREST
================

Flask + marshmallow + Flask-SlimREST = ♥ RESTful APIs ♥
---------------------------------------------------------

In today's world, providing a RESTful interface is often the primary requirement for a backend application server.
Flask has proved to be a very flexible and powerful framework which enables developers to produce great results in a
short time. But while Flask provides great functionality for generating HTML-based content out of the box, this is not
the case for RESTful APIs.

Flask-SlimREST tries to fill this gap by providing some convenience functionality for implementing RESTful applications
with Flask and marshmallow.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   
   tutorial
   decorators

A first look ...
----------------

.. code-block:: python

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

... but what about MethodViews or Flask-RESTful?
------------------------------------------------

When I started to develop RESTful APIs with Flask, a lot of tutorials pointed out that
`Flask's MethodViews <http://flask.pocoo.org/docs/0.12/views/#method-views-for-apis>`_ were the ideal way to do this.
While this is certainly not the worst way, it is most likely not the best either. You have to do a lot of things "by hand",
which means that without some trickery you would certainly violate the
`DRY principle <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_.

`Flask-RESTful <https://flask-restful.readthedocs.io/>`_ tries to solve this problem by providing some abstraction for routing,
argument parsing and data formatting. It is a great extension for those people who want to get results very quickly and don't
think too much about how to organize their code. If you are using Flask-RESTful and are happy with it, keep using it! It is
certainly a great and mature extension!

For my own projects, I quickly felt a bit contrained by the way that Flask-RESTful wanted to handle things. At about the same
time I discovered the awesome `marshmallow <http://marshmallow.readthedocs.io/en/latest/>`_, which is an "ORM/ODM/framework-agnostic
library for converting complex datatypes, such as objects, to and from native Python datatypes".

Leaving all the heavy weightlifting for object serialization and deserialization to marshmallow (and some Flask and ORM-specific addons)
I quickly coded my own API abstraction which I happily used for some time. However, with more and more special cases, things started to
get worse again, so I finally decided to do it clean and from scratch. The result of this is Flask-SlimREST!
   

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
