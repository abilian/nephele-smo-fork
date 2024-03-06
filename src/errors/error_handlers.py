"""Flask error handlers."""

from flask import jsonify


def handle_subprocess_error(e):
    response = {
        'error': e.description,
        'message': e.message
    }

    return jsonify(response), e.code


def handle_yaml_read_error(e):
    response = {
        'error': e.description,
        'message': e.message
    }

    return jsonify(response), e.code
