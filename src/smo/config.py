"""Flask app configurations."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Database connection and configuration settings.

    This class holds configuration settings for database connection and Kubernetes configuration.
    It constructs the SQLAlchemy database URI and the path to the Kubernetes configuration file
    using environment variables. Default values are provided if the environment variables are not set.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): The connection URI for the PostgreSQL database constructed
            from environment variables: DB_USER, DB_PASSWORD, DB_HOST, and DB_NAME. Defaults are
            'root', 'password', 'localhost', and 'smo' respectively if variables are not set.
        KARMADA_KUBECONFIG (str): The file path to the Kubernetes configuration, constructed from
            the environment variable KARMADA_KUBECONFIG. Defaults to 'karmada-apiserver.config' if
            the variable is not set.
    """

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:  # noqa: N802
        if "FLASK_SQLALCHEMY_DATABASE_URI" in os.environ:
            return os.environ["FLASK_SQLALCHEMY_DATABASE_URI"]

        return "postgresql://{}:{}@{}:5432/{}".format(
            os.getenv("DB_USER", "root"),
            os.getenv("DB_PASSWORD", "password"),
            os.getenv("DB_HOST", "localhost"),
            os.getenv("DB_NAME", "smo"),
        )

    # Get the kubeconfig or default
    KARMADA_KUBECONFIG = "/home/python/.kube/{}".format(
        os.getenv("KARMADA_KUBECONFIG", "karmada-apiserver.config")
    )


class ProdConfig(Config):
    """Production settings configuration class.

    This class defines the configuration settings for a production environment.
    It sets specific environment variables for Flask applications.

    Usage:
        This class should be used when deploying a Flask application in a production environment to ensure
        that the application runs with the appropriate settings.
    """

    FLASK_ENV = "production"
    DEBUG = False


class DevConfig(Config):
    """Represents the development configuration settings.

    This class inherits from the base `Config` class and overrides specific
    settings that are meant for a development environment.
    """

    FLASK_ENV = "development"
    DEBUG = True


configs = {
    "default": ProdConfig,
    "production": ProdConfig,
    "development": DevConfig,
}
