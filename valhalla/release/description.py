import subprocess

from valhalla.common.get_config import ReleaseDescriptionConfig
from valhalla.common.logger import error, info
from valhalla.common.resolver import resolve


class Description:

    def __init__(self, config: ReleaseDescriptionConfig):
        self.__from_command = config.from_command

    def get(self):
        if self.__from_command:
            info("Getting release description from command")
            return self.__get_from_command()

        error("Currently release description can be from command! Fix your valhalla.yml!")
        exit(1)

    def __get_from_command(self):
        try:
            from_command = resolve(self.__from_command)
            result = subprocess.run(from_command, shell=True, check=True, capture_output=True, text=True)
            stdout = result.stdout
            stderr = result.stderr
            if stdout:
                info(f"Output for command '{from_command}':\n{stdout}")
            if stderr:
                error(f"Error output for command '{from_command}':\n{stderr}")

            return stdout
        except subprocess.CalledProcessError as e:
            error(f"Error executing command '{e.cmd}': {e.stderr}")
        except Exception as e:
            error(f"Error occurred: {str(e)}")
