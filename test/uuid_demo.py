import uuid
import get_uuid

openid = 'odCyJ5lnyp-x_FKd42fdXNtNfGM8'

print(uuid.uuid5(uuid.NAMESPACE_DNS, openid))
print(uuid.uuid5(uuid.NAMESPACE_DNS, openid))

print(get_uuid(openid))