import os

from valhalla.common.logger import info, error


def get_valhalla_token() -> str:
    token = os.getenv('VALHALLA_TOKEN')

    if token:
        info(f'Variable VALHALLA_TOKEN is set to: {"*" * len(token)}')

        return token
    else:
        error('VALHALLA_TOKEN environment variable is not set! \n' +
              'This tool cannot be used if there is no token! \n' +
              'Please generate token (f.e. Personal Access Token) \n' +
              'and add it as environment variable with name VALHALLA_TOKEN')
        exit(-1)
