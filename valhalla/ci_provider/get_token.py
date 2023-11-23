import os

from valhalla.common.logger import info, error


def get_token() -> str:
    token = os.environ.get('VALHALLA_TOKEN')

    if token:
        info(f'Variable VALHALLA_TOKEN is set to: {"*" * len(token)}')

        return token
    else:
        error('VALHALLA_TOKEN environment variable is not set!')
        exit(-1)
