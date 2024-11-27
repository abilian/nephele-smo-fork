from __future__ import annotations

from pathlib import Path

import yaml


def register_commands(subparsers):
    add_command(subparsers, DeployCommand())
    add_command(subparsers, GetCommand())
    add_command(subparsers, ListCommand())
    add_command(subparsers, PlacementCommand())
    add_command(subparsers, RemoveCommand())
    add_command(subparsers, StartCommand())
    add_command(subparsers, StopCommand())


def add_command(subparsers, command):
    class_name = command.__class__.__name__
    name = getattr(command, "name", None)
    if not name:
        name = class_name.replace("Command", "").lower()
    swagger_name = getattr(command, "swagger_name", name)
    swagger_file = (
        Path(__file__).parent.parent / "routes" / "swagger" / f"{swagger_name}.yaml"
    )
    swagger_data = yaml.safe_load(swagger_file.read_text())
    description = swagger_data["description"]
    parser = subparsers.add_parser(name, help=description)
    parser.set_defaults(func=command.run)


class StartCommand:
    def run(self, args):
        print("Starting the application")


class StopCommand:
    def run(self, args):
        print("Stopping the application")


class DeployCommand:
    def run(self, args):
        print("Deploying the application")


class ListCommand:
    name = "list-graphs"
    swagger_name = "get_all_graphs"

    def run(self, args):
        print("Getting all graphs")


class GetCommand:
    name = "get-graph"
    swagger_name = "get_graph"

    def run(self, args):
        print("Getting a graph")


class PlacementCommand:
    def run(self, args):
        print("Running the placement algorithm")


class RemoveCommand:
    def run(self, args):
        print("Removing the graph")
