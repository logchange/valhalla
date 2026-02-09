from valhalla.common.executor import Executor
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
        from_command = resolve(self.__from_command)
        result = Executor.run(from_command)

        if result:
            return result.stdout

        return "error, check valhalla release logs"
