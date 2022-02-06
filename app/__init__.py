from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

fapp = Flask(__name__)
fapp.config.from_object(Config)
db = SQLAlchemy(fapp)
migrate = Migrate(fapp, db)


from app import view