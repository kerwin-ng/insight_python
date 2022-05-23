import uuid


def get_uuid(openid):
    openid_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, openid)
    return openid_uuid
