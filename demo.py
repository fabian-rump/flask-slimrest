from math import ceil
from flask import Flask, url_for, request
from flask_slimrest import SlimRest
from flask_slimrest.decorators import add_endpoint, load, dump, catch, paginate
from flask_slimrest.pagination import PaginationResult
from marshmallow import Schema, fields


app = Flask(__name__)
app.debug = True
api = SlimRest(app)


# Auxiliary functions for pagination

def _get_page_link(page_number):
    return url_for(request.url_rule.endpoint, page=page_number, _external=True)


def _pagination_helper(objects, per_page=2):
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


# Define our model and Marshmallow Schema

class Hero:
    def __init__(self, id, hero_name, character_trait):
        self.id = id
        self.hero_name = hero_name
        self.character_trait = character_trait


class HeroSchema(Schema):
    id = fields.Int(dump_only=True)
    hero_name = fields.String(required=True)
    character_trait = fields.String(required=True)


# Very simple in-memory "database"

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


# Define our heroes API

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
