# See LICENSE.md file in project root directory

def getValueByKey(fields:'list[dict]', key:str) -> (str):
    for f in fields:
        if "key" in f and "value" in f and f["key"] == key:
            return f["value"].replace("\u00a0", "")
    return ""


def getFieldByKey(fields:'list[dict]', key:str):
    for f in fields:
        if "key" not in f or "value" not in f:
            continue
        if f["key"] == key:
            return f
    return None


def getFieldsByKey(fields:'list[dict]', key:str):
    ret = []
    for f in fields:
        if "key" not in f or "value" not in f:
            continue
        if f["key"] == key:
            ret.append(f)
    return ret


def getFieldIndex(fields:'list[dict]', key:str, value:str):
    for i,f in enumerate(fields):
        if "key" not in f or "value" not in f:
            continue
        if f["key"] == key and f["value"] == value:
            return i
    return None