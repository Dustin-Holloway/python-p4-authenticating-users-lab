#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b"Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Login(Resource):
    @app.route("/login", methods=["POST"])
    def post():
        user = User.query.filter(
            User.username == request.get_json()["username"]
        ).first()

        session["user_id"] = user.id

        user_dict = user.to_dict()

        response = make_response(jsonify(user_dict), 200)
        response.headers["Content-type"] = "application/json"

        return response


class CheckSession(Resource):
    @app.route("/check_session", methods=["GET"])
    def get():
        if session["user_id"]:
            user_id = User.query.filter(User.id == session["user_id"]).first()

            user_dict = user_id.to_dict()
            response = make_response(jsonify(user_dict), 200)
            return response
        else:
            response = make_response({}, 401)
            return response


class Logout(Resource):
    @app.route("/logout", methods=["DELETE"])
    def delete():
        session["user_id"] = None
        return {"message": "204: No Content"}, 204


class ClearSession(Resource):
    def delete(self):
        session["page_views"] = None
        session["user_id"] = None

        return {}, 204


class IndexArticle(Resource):
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200


class ShowArticle(Resource):
    def get(self, id):
        session["page_views"] = (
            0 if not session.get("page_views") else session.get("page_views")
        )
        session["page_views"] += 1

        if session["page_views"] <= 3:
            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {"message": "Maximum pageview limit reached"}, 401


# app.add_resource(Login, "/login")

api.add_resource(ClearSession, "/clear")
api.add_resource(IndexArticle, "/articles")
api.add_resource(ShowArticle, "/articles/<int:id>")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
