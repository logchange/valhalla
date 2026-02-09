from typing import List

from valhalla.common.executor import Executor
from valhalla.common.logger import error, info
from valhalla.common.resolver import resolve
from valhalla.version.version_to_release import BASE_PREFIX


def execute(commands: List[str]):
    for command in commands:
        command = resolve(command)
        result = Executor.run(command, check=False)

        if result is None:
            error(f"Unexpected error occurred during executing command: {command}")
            exit(1)

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
