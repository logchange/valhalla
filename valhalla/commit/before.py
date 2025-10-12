import subprocess
from typing import List

from valhalla.common.logger import error, info
from valhalla.common.resolver import resolve
from version.version_to_release import BASE_PREFIX


def execute(commands: List[str]):
    try:
        for command in commands:
            command = resolve(command)
            result = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
            stdout = result.stdout
            stderr = result.stderr
            if stdout:
                info(f"Output for command '{command}':\n{stdout}")
            if stderr:
                error(f"Error output for command '{command}':\n{stderr}")

            if result.returncode != 0:
                error(f"\n\n\n-----------------------------------------------------------\n"
                      f"Executing command {command} finished with code: {result.returncode} , valhalla cannot \n" +
                      f"continue releasing process! Fix it and retry!\n" +
                      f"Delete this branch (and tag if created), fix your main branch \n"
                      f"and create {BASE_PREFIX}* branch again, this simplifies fixes and reduce mistakes \n"
                      f"-----------------------------------------------------------\n\n")
                exit(result.returncode)
            else:
                info(f"Successfully executed command: '{command}'")
    except subprocess.CalledProcessError as e:  # run is called with check=False, so it should not be called
        error(f"Error executing command '{e.cmd}': {e.stderr}")
        for line in e.output.splitlines():
            error("------" + line)
        exit(1)
    except Exception as e:
        error(f"Exception occurred: {str(e)} during executing command")
        exit(1)
