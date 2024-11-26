"""Flask error handlers."""

from __future__ import annotations


def handle_subprocess_error(e):
    """Handle subprocess errors by creating a structured response.

    Input:
    e: Exception object that must have an 'output' attribute containing error details.

    Returns:
    tuple: A dictionary with error details and an HTTP status code 500.

    Raises:
    AttributeError: If the exception object does not have an 'output' attribute.
    """
    response = {"error": "Subprocess error", "message": e.output}

    return response, 500


def handle_yaml_read_error(e):
    """Handle errors that occur during YAML file reading.

    Input:
    - e: Exception object that was raised during the YAML reading process.

    Returns:
    - response: A dictionary containing the error type and message.
    - 500: HTTP status code indicating an internal server error.

    Raises:
    - This function does not raise exceptions itself, but handles exceptions passed to it.
    """
    response = {"error": "Yaml read error", "message": str(e)}

    return response, 500
