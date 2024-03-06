"""Flask error classes."""

import subprocess

import yaml


class SubprocessError(subprocess.CalledProcessError):
    code = 500
    description = 'Subprocess error'


class YamlReadError(yaml.YAMLError):
    code = 500
    description = 'Yaml read error'
