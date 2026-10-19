# Notes API

A secure Flask REST API where users keep private notes. It uses session-based
authentication, so each user can only view and change their own notes.

## Description

- Session authentication with signed cookies
- Passwords hashed with Flask-Bcrypt
- Full CRUD for notes, owned by the logged-in user
- Paginated notes index
- Built to work with the `client-with-sessions` React client

## Installation

```bash
cd server
pipenv install
pipenv shell
export FLASK_APP=app.py
flask db upgrade
python seed.py
```

`flask db upgrade` builds the database from the migrations, and `python seed.py`
adds sample data. Seeded users: `lucky`, `sam`, `amina` (password `password123`).

## Running

```bash
python app.py
```

The server runs on http://localhost:5555, the port the client's proxy expects.

## Endpoints

### Authentication

| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/signup` | No | Create a user and log in. Body: `username`, `password`, `password_confirmation`. Returns 201. |
| POST | `/login` | No | Log in. Body: `username`, `password`. Returns 200, or 401 if invalid. |
| GET | `/check_session` | No | Returns the logged-in user, or `{}` if nobody is logged in. |
| DELETE | `/logout` | Yes | Ends the session. |

### Notes

All notes routes require login and only touch the current user's notes.

| Method | Route | Description |
|---|---|---|
| GET | `/notes?page=1&per_page=5` | Paginated list. Returns `notes`, `page`, `per_page`, `total`, `pages`. |
| POST | `/notes` | Create a note. Body: `title`, `content`. Returns 201. |
| PATCH | `/notes/<id>` | Update `title` and/or `content`. Returns 404 if the note isn't yours. |
| DELETE | `/notes/<id>` | Delete a note. Returns 204, or 404 if it isn't yours. |

### Status codes

| Code | Meaning |
|---|---|
| 401 | Not logged in, or wrong credentials |
| 404 | Note not found, or not owned by you |
| 422 | Invalid or missing data |