# Copyright (c) 2024, Abilian SAS

"""
Ref/tuto:

- https://github.com/jwbargsten/pytest-archon
- https://xebia.com/blog/how-to-tame-your-python-codebase/
"""
from __future__ import annotations

import pytest
from pytest_archon import archrule


@pytest.mark.skip(reason="Needs to be fixed")
def test_layers_bad() -> None:
    (
        archrule("Services should not import flask")
        .match("smo.services.*")
        .should_not_import("flask")
        .check("smo")
    )


def test_layers() -> None:
    (
        archrule("Models should not import flask")
        .match("smo.models.*")
        .should_not_import("flask")
        .check("smo")
    )

    (
        archrule("Utils should not import flask")
        .match("smo.utils.*")
        .should_not_import("flask")
        .check("smo")
    )

    (
        archrule("CLI should not import flask")
        .match("smo.cli.*")
        .should_not_import("flask")
        .check("smo")
    )
