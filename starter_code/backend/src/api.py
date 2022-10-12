import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()
\
# ROUTES
@app.route('/',  methods=["GET"])
@app.route('/drinks',  methods=["GET"])
def get_drinks():
    try:
        drinks_set = Drink.query.all()
        drinks=[drink.short() for drink in drinks_set]
        return jsonify({
            'success':True,
            'drinks': drinks
        })
    except Exception as err:
        print(str(err))
        abort(404)

@app.route('/drinks-detail',  methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks_set = Drink.query.all()
        drinks=[drink.long() for drink in drinks_set]
        return jsonify({
            'success': True,
            'drinks': drinks
        }) 
    except Exception as err:
        print(str(err))
        abort(404)    
        
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):

    body = request.get_json()
    #print(body)

    try:
        new_recipe = json.dumps(body['recipe'])
        new_title = body['title']

        new_drink=Drink(title=new_title, recipe=new_recipe)

        new_drink.insert()
        drink = [new_drink.long()]

        return jsonify({
            'success': True,
            'drinks': drink
            })
    except Exception as err:
        print(str(err))
        abort(422)      

@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload,drink_id):

    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)

    body = request.get_json()
    #if 'title' or 'recipe' not in body:
        #abort(404)

    try:
        new_title = body.get('title', None)
        new_recipe = json.dumps(body.get('recipe', None))

        drink.title=new_title
        drink.recipe = new_recipe

        drink.update()  

        return jsonify({
            "success":True,
            "drinks":[drink.long()]
        })    

    except Exception as err:
        print(str(err))
        abort(422)        

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload,drink_id):

    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)

    try:
        drink.delete()
        return jsonify({
            "success":True,
            "delete":drink_id
        }), 200
    except:
        abort(422) 


# Error Handling
@app.errorhandler(404)
def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

@app.errorhandler(422)
def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

@app.errorhandler(400)
def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code 