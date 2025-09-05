class Field:
    """
    Represents a field within the uberAgent pipeline.

    Each field is associated with a specific version of uberAgent and has a
    unique name which is used to identify it during rule processing.

    Attributes:
    - version (str): The version of uberAgent associated with this field.
    - name (str): The unique name of the field.

    Methods:
    - __str__(): Returns the name of the field.
    """

    def __init__(self, version: str, name: str):
        """
        Initialize a new Field instance.

        Parameters:
        - version (str): The version of uberAgent associated with this field.
        - name (str): The unique name of the field.
        """
        self.version = version
        self.name = name

    def __str__(self) -> str:
        """
        Return the string representation of the Field object, which is its name.

        Returns:
        - str: The name of the field.
        """
        return self.name
