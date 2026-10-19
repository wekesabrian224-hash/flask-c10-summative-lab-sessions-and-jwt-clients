from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_restful import Api
from flask_cors import CORS

  # creating the app
app = Flask(__name__)
  #configuration
app.secret_key="change_this_to_a_long_random_string"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

#database
db = SQLAlchemy(app)

#migrations
migrate = Migrate(app, db)


#password hashing
bcrypt = Bcrypt(app)
api = Api(app)
CORS(app, supports_credentials=True)


