"""DB models declaration."""

from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.graph import Graph
from models.service import Service
