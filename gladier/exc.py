

class GladierException(Exception):
    """Top level Gladier Exception"""
    pass


class AuthException(GladierException):
    """There was a problem with Globus Auth"""
    def __init__(self, message, missing_scopes=tuple()):
        self.missing_scopes = missing_scopes
        super().__init__(message)


class ConfigException(GladierException):
    """Something in Gladier wasn't configured properly"""
    pass


class DevelopmentException(GladierException):
    """A developer messed up."""
    pass


class RegistrationException(ConfigException):
    """Something needs to be registered"""
    def __init__(self, message, items=tuple()):
        self.items = items
        super().__init__(message)


class NoFlowRegistered(RegistrationException):
    pass


class ObsoleteException(RegistrationException):
    """A funcx function or flow has local changes not reflected
    in the currently registered id"""
    pass


class FlowObsolete(ObsoleteException):
    """The local flow definition has changed and needs to be updated"""
    pass


class FunctionObsolete(ObsoleteException):
    """A local funcx function definition has changed and needs to be updated"""
    pass
