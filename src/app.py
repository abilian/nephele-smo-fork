"""
Main Flask app entrypoint.
"""

import os

from flask import Flask

from config import configs
from errors import errors, error_handlers
from models.models import db
from routes.graph import graph

env = os.environ.get('FLASK_ENV', 'development')


def create_app(app_name='smo'):
    """
    Function that returns a configured Flask app.
    """

    app = Flask(app_name)
    app.config.from_object(configs[env])

    app.register_blueprint(graph)

    app.register_error_handler(
        errors.SubprocessError,
        error_handlers.handle_subprocess_error
    )

    db.init_app(app)
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
