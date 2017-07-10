Quickstart and Tutorial
=======================

If you have completed the `Installation` of Flask-SlimREST, it is time to code your first API.
To explain the basic features of Flask-SlimREST, we will look at a simple example application.
The full source code of this application is available in the file ``demo.py`` in the Flask-SlimREST
repository on Github.

First things first: Define a model
----------------------------------

If you already have a working Flask application, you most likely already have some model classes.
Maybe you are even using some sort of object-relational mapper (e.g. SQLAlchemy). This is totally
fine. Since Flask-SlimREST is designed to work independently of the underlying data source, you
may keep your models.

For this tutorial we want to start from scratch. To keep things simple, we won't be using a fancy
ORM, but rather just a plain, simple Python class:

.. code-block:: python

    class Hero:
        def __init__(self, id, hero_name, character_trait):
            self.id = id
            self.hero_name = hero_name
            self.character_trait = character_trait

Create a Marshmallow schema
---------------------------

Since the serialization and deserialization of Flask-SlimREST uses Marshmallow, we need to create
a Marshmallow schema for our model. Please note that there are some great packages to simplify the
creation of schemas and the integration with your ORM, e.g.:

* for SQLAlchemy: `<https://pypi.python.org/pypi/marshmallow-sqlalchemy>`_
* for Mongoengine: `<https://pypi.python.org/pypi/marshmallow-mongoengine/>`_

Again, to keep things simple we just use a plain Marshmallow schema in our example:

.. code-block:: python

    class HeroSchema(Schema):
        id = fields.Int(dump_only=True)
        hero_name = fields.String(required=True)
        character_trait = fields.String(required=True)

A "database" for our example application
----------------------------------------

Finally we define a simple data structure to manage our model objects. Obviously this is only for testing
purposes and will keep all objects in memory, so when you restart the application all added objects are lost.

.. code-block:: python

    class HeroDatabase:
        def _next_hero_id(self):
            self._id_counter += 1
            return self._id_counter

        def __init__(self):
            self._id_counter = 0
            self._heroes = [
                Hero(self._next_hero_id(), 'Star-Lord', 'Always wears his Walkman'),
                Hero(self._next_hero_id(), 'Gamora', 'Has green skin'),
                Hero(self._next_hero_id(), 'Drax', 'Does not understand metaphors'),
                Hero(self._next_hero_id(), 'Rocket', 'Loves big guns'),
                Hero(self._next_hero_id(), 'Groot', 'I am Groot!')
            ]

        def get_heroes(self):
            return self._heroes

        def get_hero(self, id):
            for hero in self._heroes:
                if hero.id == id:
                    return hero
            raise ValueError('No hero with this ID found.')

        def add_hero(self, hero):
            hero.id = self._next_hero_id()
            self._heroes.append(hero)
            return hero


    db = HeroDatabase()

Time for our first REST API!
----------------------------

Now we have everything in place which is needed to create our REST API. As you will see, the API code itself is
very lean thanks to the decorators of Flask-SlimREST. Before we get into the details, here is the complete code
for our Heroes API:

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


    def main():
        app.run()

    if __name__ == '__main__':
        main()

Initialize the API
~~~~~~~~~~~~~~~~~~~~

Everthing starts with defining an instance of :class:`flask_slimrest.SlimRest`. This object is used to properly
register all namespaces and endpoints. It needs access to the Flask application and may be defined like this:

.. code-block:: python

    app = Flask(__name__)
    api = SlimRest(app)

However, the SlimRest object also supports *lazy initilization*:

.. code-block:: python

    api = SlimRest()
    # do some other stuff ...
    api.init_app(app)

If you are using blueprints, Flask-SlimREST works just fine:

.. code-block:: python

    api_blueprint = Blueprint('api', __name__)
    api = SlimRest(api_blueprint)

Add a namespace
~~~~~~~~~~~~~~~

In Flask-SlimREST your API endpoints are organized in namespaces. Theoretically you could create just a single
namespace and add all your endpoints to that namespace. However, to keep your code clean and organized, we strongly
suggest to use a suitable separation of namespaces. However, in our small example, we have only one namespace:

.. code-block:: python

    @api.add_namespace('/heroes')
    class HeroNamespace:
        # Define namespace endpoints...

As you can see, the namespace is registered with our API using the :func:`flask_slimrest.SlimRest.add_namespace` decorator.
With the first argument of this decorator we can specifiy the URL prefix to be used for all endpoints in this namespace.
Please notet that this URL prefix should *always start with a slash*.

Add the first endpoint
~~~~~~~~~~~~~~~~~~~~~~

Now we can start to add endpoints to our namespace. Here is the complete code for our first endpoint:

.. code-block:: python

    @add_endpoint('/<id>')
    @catch(ValueError, 'No hero with this ID found.', 404)
    @dump(HeroSchema())
    def hero_details(self, id):
        return db.get_hero(int(id))

First of all, we will add the :func:`flask_slimrest.decorators.add_endpoint` decorator. This decorator makes sure that
our endpoint is properly registered in our namespace. It is quite similar to the :func:`flask.Flask.route` decorator.
You can specify the URL (relative to the namespace URL prefix), which may contain parameters if required. Additionally, 
we can specify the allowed HTTP methods (see below). By default, each endpoint only accepts ``GET`` requests.

As you can see in the code above, our "database" implementation throws a ``ValueError`` exception if we request an object
with a non-existent ID value. If this happens, we want to return an error message to the user. To do so, we make use of the
:func:`flask_slimrest.decorators.catch` decorator. We specify the exception type, the error message and the HTTP status
code. We can use this decorator multiple times on each endpoint to return different error messages for different exception
types.

The serialization process of the returned object is handled by the :func:`flask_slimrest.decorators.dump` decorator. We
only need to provide an instance of the intended Marshmallow schema.

Using these decorators, all what is left for us to do is to get the appropriate object from our database and return it.

Handling multiple objects, Pagination
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ok, so now we can retrieve a single object. But what about a collection of objects? Of course this is possible. But collections
of objects can get very huge. Hence it is a common practice to use pagination for all collection endpoints to keep the size of
the response within a reasonable boundary. Luckily, Flask-SlimREST is already prepared for paginated collections. However,
since it is designed to work independently of the underlying data source, it does not know *how to actually do* pagination.

If you use some sort of ORM, it most likely already provides some method to do this. For example, Flask-SQLAlchemy provides
the :func:`flask_sqlalchemy.BaseQuery.paginate` function. Flask-MongoEngine has a similar feature with the function
:func:`flask_mongoengine.BaseQuerySet.paginate_field`.

To make Flask-SlimREST and all of our favorite ORMs work together, we have to define a pagination helper function. It is
responsible for invoking the specific pagination methods and returning the paginated results in a consistent way.

Specifically, our pagination helper must return the paginated objects wrapped in an instance of class
:class:`flask_slimrest.pagination.PaginationResult`. This way it is ensured that the rest of Flask-SlimREST knows how
to treat the pagination result. Please note that usually this pagination helper can be written in a generic way, so you
only need to do this once. For our example, we implement the following generic pagination helper function for paginating
Python list structures:

.. code-block:: python

    def _get_page_link(page_number):
        return url_for(request.url_rule.endpoint, page=page_number, _external=True)


    def _pagination_helper(objects, per_page=100):
        if 'page' in request.args:
            page = int(request.args['page'])
        else:
            page = 1

        page_count = ceil(len(objects)/per_page)
        paginated_objects = objects[(page-1)*per_page:page*per_page]

        return PaginationResult(
            paginated_objects,
            page,
            page_count,
            _get_page_link(page+1) if page < page_count else None,
            _get_page_link(page-1) if page > 1 else None
        )

After that we can start right away with defining our collection endpoints:

.. code-block:: python

    @add_endpoint('/')
    @dump(HeroSchema(), paginated=True)
    @paginate(_pagination_helper)
    def hero_collection(self):
        return db.get_heroes()

There are only two differences compared to the first endpoint: First, we make sure that our pagination helper is invoked
by adding the :func:`flask_slimrest.decorators.pagination` decorator. Then, we add ``paginated=True`` to the dump decorator
to express our intention of dumping a paginated set of objects.

Receiving data from the user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Most REST APIs not only provide endpoints to access the available data, but also enable the user to create new objects or
modify existing ones. This is where the :func:`flask_slimrest.decorators.load` decorator comes into play. It can be added
to an API endpoint to deserialize the JSON payload data contained in a request. We can use it like this:

.. code-block:: python

    @add_endpoint('/', methods=['POST'])
    @dump(HeroSchema(), return_code=201)
    @load(HeroSchema())
    def hero_post(self, data):
        return db.add_hero(Hero(None, data.data['hero_name'], data.data['character_trait']))

The load decorator uses the provided Marshmallow schema instance to deserialize and validate the JSON payload. It responds with
and error message if no JSON data is provided or if the provided data is malformed (this can be configured, see the documentation
of :func:`flask_slimrest.decorators.load` for details).

The obtained :class:`marshmallow.UnmarshalResult` object is passed to the decorated endpoint function as the ``data`` kwarg.
In the endpoint function, you can implement the appropriate behaviour to process and store the provided data.

It is a typical convention for REST APIs to return the created object. This can again be achieved by the dump decorator. In this
case we also set the *HTTP 201 Created* status code to inform the user that the operation was successful.