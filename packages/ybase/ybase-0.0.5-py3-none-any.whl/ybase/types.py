from abc import ABC, abstractmethod


class RequiresAsyncInit(ABC):
    """
    Abstract base class for objects that must be initialized asynchronously.
    This is used to ensure that the object can be initialized with an async method.
    """

    @abstractmethod
    async def init(self, _constructor_token) -> bool:
        """
        Initialize the object asynchronously.
        Returns:
            bool: True if initialization was successful, False otherwise.
        """
        pass

    @classmethod
    @abstractmethod
    async def create(cls, *args, **kwargs):
        """
        Factory method to create an instance of the class.
        This method should be implemented by subclasses to return an instance of the class.
        """
        pass


class RequiresAsyncAsTree(ABC):
    """
    Abstract base class for objects that must be converted to a tree structure asynchronously.
    This is used to ensure that the object can be converted to a tree structure with an async method.
    """

    @abstractmethod
    async def as_tree(self) -> dict:
        """
        Convert the object to a tree structure asynchronously.
        Returns:
            dict: The tree representation of the object.
        """
        pass
