from dataclasses import dataclass, field
from typing import Optional, Union, List

from sigma.exceptions import SigmaTransformationError
from sigma.processing.transformations import FieldMappingTransformation, DetectionItemTransformation, Transformation
from sigma.rule import SigmaDetectionItem, SigmaRule, SigmaLogSource


@dataclass
class FieldMappingTransformationLowercase(FieldMappingTransformation):
    """
    Represents a transformation that maps fields using case-insensitive comparison.

    This class extends the basic `FieldMappingTransformation` by allowing field mapping
    to be performed in a case-insensitive manner.

    Methods:
    - get_mapping(field): Fetches the mapped value(s) for a given field considering lowercase
                          comparison of field names.
    """

    def get_mapping(self, field: str) -> Union[None, str, List[str]]:
        """
        Retrieve the mapping for the provided field using case-insensitive comparison.

        The field name is transformed to lowercase before attempting to fetch its mapping.
        This ensures that the field mapping is case-insensitive.

        Parameters:
        - field (str): The field name for which the mapping should be fetched.

        Returns:
        - Union[None, str, List[str]]: Returns the mapped value(s) for the field. It could be None
                                       (if no mapping exists), a string (single mapping), or a list
                                       of strings (multiple mappings).
        """
        return super().get_mapping(field.lower())


@dataclass
class FieldDetectionItemFailureTransformation(DetectionItemTransformation):
    """
    A transformation that raises an error for a specific Sigma detection item.

    When the transformation is applied, it raises a `SigmaTransformationError` with
    a specified error message. This class is intended for situations where a detection
    item is known to be unsupported or problematic and needs to be flagged during
    processing.

    Attributes:
    - message (str): The error message template that will be formatted with the
                     detection item's field and raised as a `SigmaTransformationError`.

    Methods:
    - apply_detection_item: Applies the transformation to a given Sigma detection item.
    """
    message: str

    def apply_detection_item(self, detection_item: SigmaDetectionItem) -> None:
        """
        Applies the transformation to the provided detection item.

        This method raises a `SigmaTransformationError` using the `message` attribute
        formatted with the detection item's field.

        Parameters:
        - detection_item (SigmaDetectionItem): The Sigma detection item to be transformed.

        Raises:
        - SigmaTransformationError: Raised with the formatted message.
        """
        raise SigmaTransformationError(self.message.format(detection_item.field))


class ReferencedFieldTransformation(Transformation):
    """
    This class extends the `Transformation` class and overrides the `apply` method to transform
    the `field_mappings` of a given `pipeline` and store the transformed fields in the pipeline's state.
    """
    def apply(self, pipeline: "sigma.processing.pipeline.Process", rule: SigmaRule) -> None:
        """
        Applies the transformation on the `field_mappings` of the given `pipeline`.

        The method performs the following transformations:
        - Checks if each value in `field_mappings` is of type set. Raises a `TypeError` otherwise.
        - Checks if each set contains exactly one element. Raises a `ValueError` otherwise.
        - Converts the single element in the set to a string and appends it to a list.
        - Stores the list of transformed fields in the `state` of the `pipeline` under the key "Fields".

        Parameters:
        - pipeline (sigma.processing.pipeline.Process): The pipeline on which the transformation is to be applied.
        - rule (SigmaRule): The Sigma rule that is being processed (not used in this transformation).

        Raises:
        - TypeError: If a value in `field_mappings` is not of type set.
        - ValueError: If a set in `field_mappings` does not contain exactly one element.

        Returns:
        - None
        """
        super().apply(pipeline, rule)
        fields: List[str] = []
        for key in pipeline.field_mappings.keys():
            value = pipeline.field_mappings[key]

            # Check if value is of type set
            if not isinstance(value, set):
                raise TypeError(f"Expected a set for key '{key}', but got {type(value).__name__} instead.")

            # Check if set contains exactly one element
            if len(value) != 1:
                raise ValueError(
                    f"Expected a set with exactly one element for key '{key}', but got {len(value)} elements instead.")

            value_str = str(list(value)[0])  # Convert set to list and get the first element
            fields.append(value_str)
        pipeline.state["Fields"] = fields

@dataclass
class ChangeLogsourceCategoryTransformation(Transformation):
    """
    A class used to replace the log source category in a Sigma rule.

    This class extends the `Transformation` class and overrides the `apply` method
    to replace the `logsource` category of a given `SigmaRule` with a new category
    defined in the transformation parameters.

    Attributes:
    - category (Optional[str]): The new log source category to be set. Default is None.
    """
    category: Optional[str] = field(default=None)


    """
    Applies the transformation on the `logsource` of the given `rule`.

    The method performs the following transformations:
    - Replaces the `logsource` category of the `rule` with the `category` specified
        in the transformation parameters, while keeping the `product` and `service`
        unchanged.

    Parameters:
    - pipeline (sigma.processing.pipeline.ProcessingPipeline): The pipeline on which the
        transformation is to be applied.
    - rule (SigmaRule): The Sigma rule whose `logsource` category is to be replaced.

    Returns:
    - None
    """
    def apply(
        self, pipeline: "sigma.processing.pipeline.ProcessingPipeline", rule: SigmaRule
    ) -> None:
        super().apply(pipeline, rule)
        logsource = SigmaLogSource(self.category, rule.logsource.product, rule.logsource.service)
        rule.logsource = logsource


# Convenience to explicitly force Windows logsource product.
@dataclass
class ChangeLogsourceCategoryTransformationWindows(Transformation):
    """
    A class used to explicitly set the log source product to 'windows' in a Sigma rule.

    This class extends the `Transformation` class and overrides the `apply` method
    to replace the `logsource` product of a given `SigmaRule` with 'windows', while
    keeping the `category` and `service` unchanged.

    Usage:
    Convenience to explicitly force the log source product to 'windows'.
    """
    def apply(
        self, pipeline: "sigma.processing.pipeline.ProcessingPipeline", rule: SigmaRule
    ) -> None:
        """
        Applies the transformation on the `logsource` of the given `rule`.

        The method performs the following transformation:
        - Replaces the `logsource` product of the `rule` with 'windows', while keeping
          the `category` and `service` unchanged.

        Parameters:
        - pipeline (sigma.processing.pipeline.ProcessingPipeline): The pipeline on which the
          transformation is to be applied.
        - rule (SigmaRule): The Sigma rule whose `logsource` product is to be replaced with 'windows'.

        Returns:
        - None
        """
        super().apply(pipeline, rule)
        logsource = SigmaLogSource(rule.logsource.category, "windows", rule.logsource.service)
        rule.logsource = logsource
