import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"*": {"origins": "*"}})

# db_drop_and_create_all()

# ROUTES


@app.route("/drinks")
def get_drinks():
        try:
                drinks = [drink.short() for drink in Drink.query.all()]
                return jsonify({
                        "success": True,
                        "drinks": drinks
                })
        except:
            abort(500)


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_detail():
        try:
                drinks = [drink.long() for drink in Drink.query.all()]
                return jsonify({
                        "success": True,
                        "drinks": drinks
                })
        except:
                abort(500)


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink():
        try:
                id = request.json.get("id")
                title = request.json.get("title")
                recipe = json.dumps(request.json.get("recipe"))
        except:
                abort(400)

        try:
                newDrink = Drink(title=title, recipe=recipe)
                db.session.add(newDrink)
                db.session.commit()
        except:
                abort(500)

        return jsonify({
                "success": True,
                "drinks": newDrink.long()
        })


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def patch_drink(id):
        try:
                id = request.json.get("id")
                title = request.json.get("title")
                recipe = json.dumps(request.json.get("recipe"))
        except:
                abort(400)

        drink = Drink.query.get(id)
        if drink in None:
                abort(404)

        try:
                drink.title = title
                drink.recipe = recipe
                db.session.commit()
        except:
                db.session.rollback()
                abort(500)

        return jsonify({
                "success": True,
                "drinks": drink.long()
        })


@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(id):
        drink = Drink.query.get(id)

        if drink is None:
                abort(404)

        try:
                db.session.delete(drink)
                db.session.commit()
        except:
                db.session.rollback()
                abort(500)

        return jsonify({
                "success": True,
                "drinks": drink.long()
        })


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
        return jsonify({
                "success": False,
                "error": 422,
                "message": "unprocessable"
        }), 422


@app.errorhandler(404)
def not_found(error):
        return jsonify({
                "success": False,
                "error": 404,
                "message": "not found"
        }), 404


@app.errorhandler(500)
def internal_server_error(error):
        return jsonify({
                "success": False,
                "error": 500,
                "message": "internal server error"
        }), 500


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
                "success": False,
                "error": error.error["code"],
                "message": error.error["description"]
        }), error.status_code
