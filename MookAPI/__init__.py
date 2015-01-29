from flask import Flask
from flask.ext.mongoengine import MongoEngine


### CREATE FLASK APP
app = Flask(__name__)
app.config["SECRET_KEY"] = "cj3ff02m617k3WxO703dYke088HcU94R"


### SETUP DATABASE
app.config["MONGODB_SETTINGS"] = {'DB': "mookbsf"}
db = MongoEngine(app)


### LOAD APP-LEVEL MODULES
## Views: define HTTP endpoints
import views
