import json


def compare_(obj1, obj2):
    if type(obj1) != type(obj2):
        return False
    if isinstance(obj1, list):
        if len(obj2) != len(obj1):
            return False
        for i in range(len(obj1)):
            if not compare_(obj1[i], obj2[i]):
                return False
    if isinstance(obj1, dict):
        if len(obj1) != len(obj2):
            return False
        for key, value in obj1.items():
            if key not in obj2:
                return False
            if not compare_(value, obj2[key]):
                return False
    return obj1 == obj2


def compare_jsons(fp1, fp2):
    with open(fp1) as f1:
        o1 = json.load(f1)
    with open(fp2) as f2:
        o2 = json.load(f2)
    return compare_(o1, o2)
