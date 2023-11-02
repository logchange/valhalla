def log_message(level, msg):
    msg = str(msg)
    lines = msg.split('\n')
    for line in lines:
        print(f"[{level}] {line}")


def info(msg):
    log_message("INFO", msg)


def warn(msg):
    log_message("WARN", msg)


def error(msg):
    log_message("ERROR", msg)
