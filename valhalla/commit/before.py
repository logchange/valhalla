import subprocess
from typing import List

from valhalla.common.logger import error, info
from valhalla.common.resolver import resolve


def execute(commands: List[str]):
    try:
        for command in commands:
            command = resolve(command)
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            stdout = result.stdout
            stderr = result.stderr
            if stdout:
                info(f"Output for command '{command}':\n{stdout}")
            if stderr:
                error(f"Error output for command '{command}':\n{stderr}")
    except subprocess.CalledProcessError as e:
        error(f"Error executing command '{e.cmd}': {e.stderr}")
    except Exception as e:
        error(f"Error occurred: {str(e)}")
