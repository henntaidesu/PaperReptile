import uuid


def UUID():
    uuid_obj = uuid.uuid4()
    uuid_str = str(uuid_obj)
    return uuid_str
