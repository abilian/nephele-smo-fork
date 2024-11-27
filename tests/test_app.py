from __future__ import annotations

from smo.flask.app import create_app


class TestConfig:
    """Database connection credentials."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # SQLALCHEMY_DATABASE_URI = "postgresql://localhost/smo_test"
    # KARMADA_KUBECONFIG = '/home/python/.kube/{}'.format(
    #     os.getenv('KARMADA_KUBECONFIG', 'karmada-apiserver.config')
    # )

    # FLASK_ENV = 'development'
    # DEBUG = True


def test_app():
    create_app(config=TestConfig)
