TOKEN = "not_set"


# Allows to hide sensitive data
def init_logger(token: str):
    global TOKEN
    TOKEN = token


def log_message(level, msg):
    global TOKEN
    msg = str(msg)
    msg = msg.replace(TOKEN, "*" * len(TOKEN))
    lines = msg.split('\n')
    for line in lines:
        print(f"[{level}] {line}")


def info(msg):
    log_message("INFO", msg)


def warn(msg):
    log_message("WARN", msg)


def error(msg):
    log_message("ERROR", msg)
