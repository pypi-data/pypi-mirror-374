__all__ = [
    "GremlinMissingLabelException",
    "LKMultipleException",
    "GremlinMissingSessionException",
]


class BaseGremlinException(Exception):
    """
    Base exception for all Gremlin-related errors.
    """


class GremlinMissingLabelException(BaseGremlinException):
    """
    Exception raised when a Gremlin model is missing a label.
    """

    def __init__(self, model_name: str):
        super().__init__(f"Model {model_name} is missing a label.")
        self.model_name = model_name

    def __repr__(self):
        return f"Gremlin model '{self.model_name}' must have a label defined."


class LKMultipleException(BaseGremlinException):
    """
    Exception raised when a Gremlin model has multiple label keys defined.
    """

    def __init__(self, model_name: str, message: str):
        super().__init__(f"{model_name}: {message}")
        self.model_name = model_name
        self.message = message

    def __repr__(self):
        return f"Gremlin model '{self.model_name}' has multiple label keys defined: {self.message}"


class GremlinMissingSessionException(BaseGremlinException):
    """
    Exception raised when a Gremlin model operation is attempted without an active session.
    """

    def __init__(self, model_name: str, message: str):
        super().__init__(f"{model_name}: {message}")
        self.model_name = model_name
        self.message = message

    def __repr__(self):
        return f"Gremlin model '{self.model_name}' operation failed due to missing session: {self.message}"
