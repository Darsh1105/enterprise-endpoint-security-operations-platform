from endpoint_operations.endpoint_repository import (
    get_all_devices,
    get_endpoint_by_hostname
)


def load_devices():
    """
    Returns all active devices.
    """

    return get_all_devices()


def search_endpoint(hostname):
    """
    Returns one endpoint.
    """

    return get_endpoint_by_hostname(hostname)