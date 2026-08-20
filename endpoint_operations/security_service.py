from endpoint_operations.security_repository import get_security_status


def load_security_status(device_id):

    return get_security_status(device_id)