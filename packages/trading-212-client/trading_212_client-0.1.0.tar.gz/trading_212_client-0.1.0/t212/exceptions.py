def not_implemented_client_field(*args):
    def wrapper(*args, **kwargs):
        raise NotImplementedError("This client has not yet implemented this api")

    return wrapper


def not_implemented_api_field(*args):
    def wrapper(*args, **kwargs):
        raise NotImplementedError("Trading212 has not yet implemented this api")

    return wrapper
