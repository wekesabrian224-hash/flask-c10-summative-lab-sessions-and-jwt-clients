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


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        user = User.query.filter_by(username=data.get("username")).first()

        if user and user.authenticate(data.get("password") or ""):
            session["user_id"] = user.id
            return {"id": user.id, "username": user.username}, 200

        return {"errors": ["Invalid username or password."]}, 401


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None

        if user:
            return {"id": user.id, "username": user.username}, 200

        return {}, 200


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 200


class Notes(Resource):
    def get(self):
        """Return the logged-in user's notes, one page at a time."""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)

        # keep values sensible so nobody can request page 0 or 1,000,000 notes
        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)

        pagination = (
            Note.query.filter_by(user_id=session["user_id"])
            .order_by(Note.created_at.desc(), Note.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )

        return {
            "notes": [n.to_dict() for n in pagination.items],
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    def post(self):
        """Create a note owned by the logged-in user."""
        data = request.get_json() or {}
        title = data.get("title")
        content = data.get("content")

        if not title or not content:
            return {"errors": ["Title and content are required."]}, 422

        note = Note(title=title, content=content, user_id=session["user_id"])
        db.session.add(note)
        db.session.commit()
        return note.to_dict(), 201


class NoteById(Resource):
    def patch(self, id):
        """Update a note. Returns 404 if it doesn't exist or isn't yours."""
        note = Note.query.filter_by(id=id, user_id=session["user_id"]).first()
        if not note:
            return {"errors": ["Note not found."]}, 404

        data = request.get_json() or {}
        for field in ("title", "content"):
            if field in data:
                if not data[field]:
                    return {"errors": [f"{field} cannot be empty."]}, 422
                setattr(note, field, data[field])

        db.session.commit()
        return note.to_dict(), 200

    def delete(self, id):
        """Delete a note. Returns 404 if it doesn't exist or isn't yours."""
        note = Note.query.filter_by(id=id, user_id=session["user_id"]).first()
        if not note:
            return {"errors": ["Note not found."]}, 404

        db.session.delete(note)
        db.session.commit()
        return {}, 204


api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(Notes, "/notes", endpoint="notes")
api.add_resource(NoteById, "/notes/<int:id>", endpoint="note_by_id")


OPEN_ENDPOINTS = {"signup", "login", "check_session", "logout"}

@app.before_request
def require_login():
    """Block every route except the open ones when nobody is logged in."""
    # Let CORS preflight requests, unknown URLs (404s) and static files through
    if request.method == "OPTIONS" or request.endpoint is None or request.endpoint == "static":
        return None

    if request.endpoint not in OPEN_ENDPOINTS and not session.get("user_id"):
        return {"errors": ["Unauthorized"]}, 401


if __name__ == "__main__":
    app.run(port=5555, debug=True)