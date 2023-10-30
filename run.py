import config
from flask_app import app, views

app.app.register_blueprint(views.endpoints)

if __name__ == "__main__":
    app.app.run(host=config.HOST, port=config.PORT)
