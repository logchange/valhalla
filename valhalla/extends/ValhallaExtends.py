from typing import List

import requests
from yaml import safe_load

from valhalla.common.logger import info, error
from valhalla.extends.merge_dicts import merge
from valhalla.common.resolver import resolve


def get_from_url(url):
    result = ""
    data = requests.get(resolve(url)).text
    for line in data:
        result += line
    info("Loaded from ULR")
    info("===========================================")
    print(result)
    info("===========================================")
    return result


class ValhallaExtends:

    def __init__(self, extends: List[str]):
        self.extends = extends

    def merge(self, valhalla_yml_dict: dict) -> dict:
        if self.extends is None or len(self.extends) < 1:
            info("There is nothing to extend")
            return valhalla_yml_dict
        elif len(self.extends) == 1:
            info("There is one file to extend")
            extended = get_from_url(self.extends[0])
            extended_dict = safe_load(extended)
            info("yml data as dictionary to extends: " + str(extended_dict))
            info("yml data from valhalla.yml: " + str(valhalla_yml_dict))
            result = merge(extended_dict, valhalla_yml_dict)
            info("final yml data: " + str(result))
            return result
        else:
            error("Currently you can extend only from one url!")
            exit(1)
