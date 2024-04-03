import os
import re

from valhalla.common.logger import info, error

VERSION = "not_set"
VERSION_SLUG = "not_set"
VALHALLA_TOKEN = "not_set"
CUSTOM_VARIABLES_DICT = dict()


def init_str_resolver(version: str, token: str):
    global VERSION
    global VERSION_SLUG
    global VALHALLA_TOKEN
    VERSION = version
    VERSION_SLUG = __get_slug(version)
    VALHALLA_TOKEN = token


def init_str_resolver_custom_variables(variables: dict):
    global CUSTOM_VARIABLES_DICT
    CUSTOM_VARIABLES_DICT.update(variables)

    for key, value in CUSTOM_VARIABLES_DICT.items():
        info(f"Custom variable: {key} set to: {value}")


def resolve(string: str):
    if VERSION == "not_set":
        error("There was no init_str_resolver(...) call in the code, so resolving strings does not work!")
        error("There is bug in valhalla! Please report it here: https://github.com/logchange/valhalla/issues")
        exit(1)

    string = __resolve_predefined(string)
    string = __resolve_custom_variables(string)
    string = __resolve_from_env(string)

    info("String resolving output: " + string)
    return string


def __resolve_predefined(string: str):
    global VERSION
    global VERSION_SLUG
    global VALHALLA_TOKEN

    string = string.replace("{VERSION}", VERSION)
    string = string.replace("{VERSION_SLUG}", VERSION_SLUG)
    string = string.replace("{VALHALLA_TOKEN}", VALHALLA_TOKEN)

    return string


def __resolve_custom_variables(string: str):
    global CUSTOM_VARIABLES_DICT

    for key, value in CUSTOM_VARIABLES_DICT.items():
        string = string.replace("{" + key + "}", value)

    return string


def __resolve_from_env(string: str):
    # Iterating over each environment variable
    for env_var in os.environ:
        string = string.replace('{' + env_var + '}', os.environ.get(env_var, ''))
    return string


def __get_slug(version):
    slug = re.sub(r'[^0-9a-zA-Z]+', '-', version).lower()
    slug = slug.strip('-')
    return slug
