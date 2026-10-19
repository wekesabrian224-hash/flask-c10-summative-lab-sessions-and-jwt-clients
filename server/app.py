from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Note


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")
        confirmation = data.get("password_confirmation")

        if not password:
            return {"errors": ["Password is required."]}, 422
        if password != confirmation:
            return {"errors": ["Passwords do not match."]}, 422

        try:
            user = User(username=username)
            user.password = password
            db.session.add(user)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username is already taken."]}, 422

        session["user_id"] = user.id
        return {"id": user.id, "username": user.username}, 201


api.add_resource(Signup, "/signup", endpoint="signup")


if __name__ == "__main__":
    app.run(port=5555, debug=True)