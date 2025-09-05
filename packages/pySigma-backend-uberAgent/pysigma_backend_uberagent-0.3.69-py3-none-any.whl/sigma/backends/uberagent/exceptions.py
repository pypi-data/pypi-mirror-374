
class MissingPropertyException(Exception):
    def __init__(self, prop):
        super().__init__("The '{}' property is required!".format(prop))


class MissingFunctionException(Exception):
    def __init__(self, func):
        super().__init__("The '{}' function is not supported in this configuration!".format(func))
