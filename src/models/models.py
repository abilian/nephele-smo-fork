"""
DB models declaration.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.graph import Graph
from models.service import Service
