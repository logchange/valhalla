from valhalla.ci_provider.merge_request_hook import MergeRequestHook

TOKEN: str = "not_set"
MR_HOOK: MergeRequestHook | None = None
MR_HOOK_COMMENTS_COUNT: int = 0
PENDING_MR_COMMENTS: list = []


# Allows to hide sensitive data
def init_logger(token: str):
    global TOKEN
    TOKEN = token


def init_logger_mr_hook(mr_hook: MergeRequestHook):
    global MR_HOOK, MR_HOOK_COMMENTS_COUNT, PENDING_MR_COMMENTS
    MR_HOOK = mr_hook

    if MR_HOOK is None or not PENDING_MR_COMMENTS:
        PENDING_MR_COMMENTS = []
        return

    pending = PENDING_MR_COMMENTS
    PENDING_MR_COMMENTS = []
    for comment in pending:
        if MR_HOOK_COMMENTS_COUNT >= 50:
            break
        MR_HOOK.add_comment(comment)
        MR_HOOK_COMMENTS_COUNT += 1


def log_message(level, msg):
    from valhalla.common import resolver
    import sys
    global TOKEN, MR_HOOK, MR_HOOK_COMMENTS_COUNT, PENDING_MR_COMMENTS
    msg = str(msg)
    msg = resolver.resolve(msg, suppress_log=True)
    msg = msg.replace(TOKEN, "*" * len(TOKEN))
    lines = msg.split('\n')

    formatted_msg = ""
    for line in lines:
        line_to_print = f"[{level}] {line}"
        print(line_to_print)
        if formatted_msg == "":
            formatted_msg = line_to_print
        else:
            formatted_msg += "  \n" + line_to_print

    if level != "WARN" and level != "ERROR":
        return

    if MR_HOOK is None:
        PENDING_MR_COMMENTS.append(formatted_msg)
        return

    if MR_HOOK_COMMENTS_COUNT >= 50:
        error_msg = f"[ERROR] Too many comments added to Merge Request (limit: 50). Please fix previous warnings."
        MR_HOOK.add_comment(error_msg)
        print(error_msg)
        sys.exit(1)
    MR_HOOK.add_comment(formatted_msg)
    MR_HOOK_COMMENTS_COUNT += 1


def info(msg):
    log_message("INFO", msg)


def warn(msg):
    log_message("WARN", msg)


def error(msg):
    log_message("ERROR", msg)
