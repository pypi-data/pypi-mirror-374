import fastapi_babel

from ..utils import T, lazy

__all__ = ["lazy_text", "translate", "_"]

logger = None


class lazy_text(lazy[T]):
    """
    Lazily translates a message using FastAPI Babel.
    """

    def __init__(self, message: T, *args, **kwargs):
        """
        Initializes a lazy_text instance that lazily translates the given message.

        Args:
            message (T): the message to be translated.
            *args: positional arguments to format the message.
            **kwargs: keyword arguments to format the message.
        """
        super().__init__(
            lambda: translate(message).format(*args, **kwargs),
            cache=False,
            only_instance=True,
        )

    @classmethod
    def _(cls, message: str, *args, **kwargs):
        """
        Class method to create a lazy_text instance that can be automatically found by `pybabel extract`.

        Args:
            message (str): the message to be translated.
            *args: positional arguments to format the message.
            **kwargs: keyword arguments to format the message.

        Returns:
            lazy_text: an instance of lazy_text that will lazily translate the message.
        """
        return cls(message, *args, **kwargs)

    def __repr__(self):
        """
        When reading it as a string, it should return the formatted message.

        Returns:
            str: the formatted message.
        """
        return self.__call__()


def translate(message: str, *args, ensure_context=False, **kwargs):
    """
    Translates a message using FastAPI Babel.

    Args:
        message (str): the message to be translated.
        *args: positional arguments to format the message.
        ensure_context (bool): Whether to ensure the context is already set to know which language to use. If false, it will return the message as is if the translation is not found. Defaults to False.
        **kwargs: keyword arguments to format the message.

    Returns:
        str: the translated message.
    """
    try:
        return fastapi_babel._(message).format(*args, **kwargs)
    except LookupError as e:
        if not ensure_context:
            global logger
            if not logger:
                from ..const import logger as base_logger

                logger = base_logger.getChild("lang")

            logger.warning(
                f"Translation not found for '{message}'. Returning the original message."
            )
            return message.format(*args, **kwargs)
        raise e


_ = translate  # Alias for convenience
