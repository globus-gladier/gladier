

class GladierException(Exception):
    """Top level Gladier Exception"""
    pass


class AuthException(GladierException):
    """There was a problem with Globus Auth"""
    pass


class ConfigException(GladierException):
    """Something in Gladier wasn't configured properly"""
    pass