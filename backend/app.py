from flask import Flask, has_request_context, request
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "privateKey"
    CORS(app, resources={r"/*": {"origins": "*"}})

    from views.routes import api

    app.register_blueprint(api)

    from models.models import db

    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db.sqlite" 
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8080)