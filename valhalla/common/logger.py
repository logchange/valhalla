def info(msg):
    msg = str(msg)
    lines = msg.split('\n')
    for line in lines:
        print(f"[INFO] {line}")


def error(msg):
    msg = str(msg)
    lines = msg.split('\n')
    for line in lines:
        print(f"[ERROR] {line}")
