"""DB models declaration."""

from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from smo.models.graph import Graph as Graph
from smo.models.service import Service as Service
