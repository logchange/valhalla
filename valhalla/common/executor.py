import subprocess
from dataclasses import dataclass
from typing import Optional

from valhalla.common.logger import info, error


@dataclass
class ExecutionResult:
    returncode: int
    stdout: str
    stderr: str


class Executor:
    @staticmethod
    def run(command: str, check: bool = True) -> Optional[ExecutionResult]:
        try:
            result = subprocess.run(command, shell=True, executable='/bin/bash', check=check, capture_output=True,
                                    text=True)
            stdout = result.stdout
            stderr = result.stderr

            if stdout:
                info(f"Output for command '{command}':\n{stdout}")
            if stderr:
                error(f"Error output for command '{command}':\n{stderr}")

            return ExecutionResult(result.returncode, stdout, stderr)
        except subprocess.CalledProcessError as e:
            error(f"Error executing command '{e.cmd}': {e.stderr}")
            return ExecutionResult(e.returncode, e.stdout, e.stderr)
        except Exception as e:
            error(f"Error occurred: {str(e)}")
            return None
