"""
Flask error classes.
"""

import subprocess


class SubprocessError(subprocess.CalledProcessError):
    code = 500
    description = 'Subprocess Error'
