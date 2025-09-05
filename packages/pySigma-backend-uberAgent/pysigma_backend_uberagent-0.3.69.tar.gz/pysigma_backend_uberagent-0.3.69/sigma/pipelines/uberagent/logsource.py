from typing import List, Dict

from sigma.processing.conditions import LogsourceCondition
from sigma.pipelines.uberagent.field import Field


class Logsource:
    """
    Represents a specific category within the uberAgent pipeline.

    Each category is associated with a specific version of uberAgent and contains
    a set of conditions and field mappings that dictate how logs of that category
    should be processed.

    Attributes:
    - version (str): The version of uberAgent associated with this category.
    - name (str): The name of the category.
    - conditions (List[LogsourceCondition]): A list of conditions associated with the category.
    - fields (Dict[str, Field]): A mapping of field names to their respective Field objects.

    Methods:
    - __str__(): Returns the name of the category.
    """

    def __init__(self, version: str, name: str, conditions: List[LogsourceCondition] = [], fields: Dict[str, Field] = {}):
        """
        Initialize a new Category instance.

        Parameters:
        - version (str): The version of uberAgent associated with this category.
        - name (str): The name of the category.
        - conditions (List[LogsourceCondition], optional): A list of conditions associated with the category.
                                                           Defaults to an empty list.
        - fields (Dict[str, Field], optional): A mapping of field names to their respective Field objects.
                                               Defaults to an empty dictionary.
        """
        self.version = version
        self.name = name
        self.conditions = conditions
        self.fields = fields

    def __str__(self) -> str:
        """
        Return the string representation of the Category object, which is its name.

        Returns:
        - str: The name of the category.
        """
        return self.name
