from flask import Flask

def create_app():
    app = Flask(__name__,static_folder='static')
    app.secret_key = "TEST"
    # Initialize Flask extensions here

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
