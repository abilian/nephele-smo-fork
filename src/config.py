"""Flask app configurations."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Database connection credentials."""
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:5432/{}'.format(
        os.getenv('DB_USER', 'root'),
        os.getenv('DB_PASSWORD', 'password'),
        os.getenv('DB_HOST', 'localhost'),
        os.getenv('DB_NAME', 'smo')
    )
    KARMADA_KUBECONFIG = '/kube/{}'.format(
        os.getenv('KARMADA_KUBECONFIG', 'karmada-apiserver.config')
    )


class ProdConfig(Config):
    """Production settings."""
    FLASK_ENV = 'production'
    DEBUG = False


class DevConfig(Config):
    """Development settings."""
    FLASK_ENV = 'development'
    DEBUG = True


configs = {
    'default': ProdConfig,
    'production': ProdConfig,
    'development': DevConfig,
}
