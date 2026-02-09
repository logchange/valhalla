import os
import re

VERSION = "not_set"
VERSION_MAJOR = "not_set"
VERSION_MINOR = "not_set"
VERSION_PATCH = "not_set"
VERSION_SLUG = "not_set"
VALHALLA_TOKEN = "not_set"
AUTHOR = "not_set"
CUSTOM_VARIABLES_DICT = dict()


def init_str_resolver(token: str, author: str):
    global VALHALLA_TOKEN
    global AUTHOR

    VALHALLA_TOKEN = token
    AUTHOR = author


def init_str_resolver_set_version(version: str):
    global VERSION
    global VERSION_MAJOR
    global VERSION_MINOR
    global VERSION_PATCH
    global VERSION_SLUG

    VERSION = version
    VERSION_MAJOR = __get_major(version)
    VERSION_MINOR = __get_minor(version)
    VERSION_PATCH = __get_patch(version)
    VERSION_SLUG = __get_slug(version)


def init_str_resolver_custom_variables(variables: dict):
    from valhalla.common.logger import info
    global CUSTOM_VARIABLES_DICT

    CUSTOM_VARIABLES_DICT.update({} if variables is None else variables)

    for key, value in CUSTOM_VARIABLES_DICT.items():
        info(f"Custom variable: {key} set to: {value}")


def resolve(string: str, suppress_log: bool = False):
    if VALHALLA_TOKEN == "not_set":
        return string

    # hierarchy
    string = __resolve_predefined(string)
    string = __resolve_custom_variables(string)
    string = __resolve_from_env(string)

    if not suppress_log:
        from valhalla.common.logger import info
        info("String resolving output: " + string)
    return string


def __resolve_predefined(string: str):
    global VERSION
    global VERSION_MAJOR
    global VERSION_MINOR
    global VERSION_PATCH
    global VERSION_SLUG
    global VALHALLA_TOKEN
    global AUTHOR

    string = string.replace("{VERSION}", VERSION)
    string = string.replace("{VERSION_MAJOR}", VERSION_MAJOR)
    string = string.replace("{VERSION_MINOR}", VERSION_MINOR)
    string = string.replace("{VERSION_PATCH}", VERSION_PATCH)
    string = string.replace("{VERSION_SLUG}", VERSION_SLUG)
    string = string.replace("{VALHALLA_TOKEN}", VALHALLA_TOKEN)
    string = string.replace("{AUTHOR}", AUTHOR)

    return string


def __resolve_custom_variables(string: str):
    global CUSTOM_VARIABLES_DICT

    for key, value in CUSTOM_VARIABLES_DICT.items():
        string = string.replace("{" + key + "}", value)

    return string


def __resolve_from_env(string: str):
    # Iterating over each environment variable
    for env_var in os.environ:
        if os.environ.get(env_var, '') is not None:
            string = string.replace('{' + env_var + '}', os.environ.get(env_var, ''))
    return string


def __get_slug(version):
    slug = re.sub(r'[^0-9a-zA-Z]+', '-', version).lower()
    slug = slug.strip('-')
    return slug


def __get_major(version):
    match = re.match(r'^(\d+)', version)
    if match:
        return match.group(1)
    from valhalla.common.logger import warn
    warn(f"Could not get VERSION_MINOR variable value from version: {version}")
    return ""


def __get_minor(version):
    match = re.match(r'^\d+\.(\d+)', version)
    if match:
        return match.group(1)
    from valhalla.common.logger import warn
    warn(f"Could not get VERSION_MINOR variable value from version: {version}")
    return ""


def __get_patch(version):
    match = re.match(r'^\d+\.\d+\.(\d+)', version)
    if match:
        return match.group(1)
    from valhalla.common.logger import warn
    warn(f"Could not get VERSION_PATCH variable value from version: {version}")
    return ""
