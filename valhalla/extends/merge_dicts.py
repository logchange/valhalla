import copy


def merge(parent: dict, child: dict):
    parent_copy = copy.deepcopy(parent)
    child_copy = copy.deepcopy(child)

    return __merge(parent_copy, child_copy)


def __merge(parent_org: dict, child_org: dict):
    parent_copy = copy.deepcopy(parent_org)
    child_copy = copy.deepcopy(child_org)

    if isinstance(child_copy, dict):
        for k, v in child_copy.items():
            if k in parent_copy:
                parent_copy[k] = __merge(parent_copy.get(k), v)
            else:
                parent_copy[k] = v
        return parent_copy
    else:
        return child_copy
