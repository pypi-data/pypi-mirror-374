import os
import subprocess
from typing import Dict


class BashCmd:
    """Represents a command to be run in the shell."""

    def __init__(self, cmd: str, env: Dict[str, str] = None):
        self.cmd = cmd
        self.env = env

    def run(self) -> str:
        env = None
        if self.env:
            env = os.environ.copy()
            env.update(self.env)
        print(f"> {self.cmd}")
        try:
            result = subprocess.check_output(
                self.cmd, shell=True, text=True, env=env, stderr=subprocess.STDOUT
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code {e.returncode}: {e.output}")
            exit(1)
        
class EmptyCmd(BashCmd):
    """Represents an empty command that does nothing."""

    def __init__(self):
        super().__init__("true")

    def run(self) -> str:
        print("No operation performed.")
        return "No operation performed."        
