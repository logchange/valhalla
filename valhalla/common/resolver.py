from valhalla.common.logger import info, error

VERSION = "not_set"
VALHALLA_TOKEN = "not_set"
CUSTOM_VARIABLES_DICT = dict()


def init_str_resolver(version: str, token: str):
    global VERSION
    global VALHALLA_TOKEN
    VERSION = version
    VALHALLA_TOKEN = token


def init_str_resolver_custom_variables(variables: dict):
    global CUSTOM_VARIABLES_DICT
    CUSTOM_VARIABLES_DICT.update(variables)

    for key, value in CUSTOM_VARIABLES_DICT.items():
        info(f"Custom variable: {key} set to: {value}")


def resolve(string: str):
    global VERSION
    global VALHALLA_TOKEN
    global CUSTOM_VARIABLES_DICT

    if VERSION == "not_set":
        error("There was no init_str_resolver(...) call in the code, so resolving strings does not work!")
        error("There is bug in valhalla! Please report it here: https://github.com/logchange/valhalla/issues")
        exit(1)

    string = string.replace("{VERSION}", VERSION)
    string = string.replace("{VALHALLA_TOKEN}", VALHALLA_TOKEN)

    for key, value in CUSTOM_VARIABLES_DICT.items():
        string = string.replace("{" + key + "}", value)

    info("String resolving output: " + string)
    return string
