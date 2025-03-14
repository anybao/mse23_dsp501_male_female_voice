from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # Register routes (if in separate files)
    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)

    return app