from valhalla.common.logger import info, error

VERSION = "not_set"


def init_str_resolver(version: str):
    global VERSION
    VERSION = version


def resolve(string: str):
    global VERSION

    if VERSION == "not_set":
        error("There was no init_str_resolver(...) call in the code, so resolving strings does not work!")
        error("There is bug in valhalla! Please report it here: https://github.com/logchange/valhalla/issues")
        exit(1)

    string = string.replace("{VERSION}", VERSION)

    info("String resolving output: " + string)
    return string
