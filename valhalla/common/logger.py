from valhalla.ci_provider.merge_request_hook import MergeRequestHook

TOKEN: str = "not_set"
MR_HOOK: MergeRequestHook | None = None


# Allows to hide sensitive data
def init_logger(token: str):
    global TOKEN
    TOKEN = token


def init_logger_mr_hook(mr_hook: MergeRequestHook):
    global MR_HOOK
    MR_HOOK = mr_hook


def log_message(level, msg):
    global TOKEN, MR_HOOK
    msg = str(msg)
    msg = msg.replace(TOKEN, "*" * len(TOKEN))
    lines = msg.split('\n')

    formatted_msg = ""
    for line in lines:
        line_to_print = f"[{level}] {line}"
        print(line_to_print)
        if formatted_msg == "":
            formatted_msg = line_to_print
        else:
            formatted_msg += "\n" + line_to_print

    if MR_HOOK is not None and (level == "WARN" or level == "ERROR"):
        MR_HOOK.add_comment(formatted_msg)


def info(msg):
    log_message("INFO", msg)


def warn(msg):
    log_message("WARN", msg)


def error(msg):
    log_message("ERROR", msg)
