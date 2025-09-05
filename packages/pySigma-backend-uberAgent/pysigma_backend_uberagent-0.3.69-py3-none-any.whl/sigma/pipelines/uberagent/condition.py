from dataclasses import dataclass
from typing import Optional

from sigma.processing.conditions import IncludeFieldCondition


@dataclass
class IncludeFieldConditionLowercase(IncludeFieldCondition):
    """
    Condition class to match on a field name, considering case-insensitive comparison.

    This class extends the basic `IncludeFieldCondition` by adding support for case-insensitive
    field name matching.

    Methods:
    - match_field_name(pipeline, field): Check if the given field name (case-insensitive) exists
                                         in the defined fields list.
    """

    def match_field_name(
            self,
            pipeline: "sigma.processing.pipeline.ProcessingPipeline",
            field: Optional[str],
    ) -> bool:
        """
        Match the field name against the list of fields in a case-insensitive manner.

        Parameters:
        - pipeline (ProcessingPipeline): The processing pipeline under consideration.
        - field (Optional[str]): The field name to be matched.

        Returns:
        - bool: True if the field name exists (case-insensitively) in the fields list, otherwise False.
        """
        if field is None:
            return False
        return field.lower() in [f.lower() for f in self.fields]


@dataclass
class ExcludeFieldConditionLowercase(IncludeFieldConditionLowercase):
    """
    Condition class to ensure a field name does not match, considering case-insensitive comparison.

    This class extends the `IncludeFieldConditionLowercase` class and reverses its logic to ensure
    that a field name (case-insensitive) does not exist in the defined fields list.

    Methods:
    - match_field_name(pipeline, field): Check if the given field name (case-insensitive) does not
                                         exist in the defined fields list.
    """

    def match_field_name(
            self,
            pipeline: "sigma.processing.pipeline.ProcessingPipeline",
            field: Optional[str],
    ) -> bool:
        """
        Ensure the field name does not exist in the list of fields in a case-insensitive manner.

        Parameters:
        - pipeline (ProcessingPipeline): The processing pipeline under consideration.
        - field (Optional[str]): The field name to be checked.

        Returns:
        - bool: True if the field name does not exist (case-insensitively) in the fields list, otherwise False.
        """
        return not super().match_field_name(pipeline, field)
