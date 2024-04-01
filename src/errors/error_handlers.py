"""Flask error handlers."""


def handle_subprocess_error(e):
    response = {
        'error': 'Subprocess error',
        'message': e.output
    }

    return response, 500


def handle_yaml_read_error(e):
    response = {
        'error': 'Yaml read error',
        'message': str(e)
    }

    return response, 500
