"""Main Flask app entrypoint."""

from __future__ import annotations

import os
import subprocess

import yaml
from flasgger import Swagger
from flask import Flask

from smo.config import configs
from smo.extensions import db

from . import error_handlers
from .routes.graph import graph

env = os.environ.get("FLASK_ENV", "development")


def create_app(app_name="smo", *, config=None) -> Flask:
    """Create and configure a Flask application.

    This function initializes a Flask application with specified configurations
    and error handlers, sets up Swagger for API documentation, and prepares the
    database.

    Input:
    - app_name: The name of the Flask application (default: "smo").
    - config: An optional configuration object. If not provided, a default
      configuration based on the environment will be used.

    Returns:
    - A configured Flask application instance.
    """

    # Get the directory where this files resides
    ROOT_PATH = os.path.dirname(__file__)
    # Initialize the Flask app with root path
    app = Flask(app_name, root_path=ROOT_PATH)
    # Configure Swagger for API documentation
    app.config["SWAGGER"] = {
        "title": "SMO-API",
        "uiversion": 3,
    }
    Swagger(app)

    if config:
        # Load configuration from the provided object,
        # useful for tests
        app.config.from_object(config)
    else:
        # Load configuration from default environment settings,
        # useful for production or development
        app.config.from_object(configs[env]())

    app.register_blueprint(graph)

    # Register error handlers for specific exceptions
    app.register_error_handler(
        subprocess.CalledProcessError, error_handlers.handle_subprocess_error
    )
    app.register_error_handler(yaml.YAMLError, error_handlers.handle_yaml_read_error)

    db.init_app(app)
    with app.app_context():
        # Create all database tables
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()
