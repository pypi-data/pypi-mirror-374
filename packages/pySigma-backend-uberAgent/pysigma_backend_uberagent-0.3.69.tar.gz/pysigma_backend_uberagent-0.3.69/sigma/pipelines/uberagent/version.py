from typing import Dict, List

from sigma.pipelines.uberagent.logsource import Logsource
from sigma.pipelines.uberagent.field import Field

# Constants representing various versions of uberAgent
UA_VERSION_6_0 = "6.0.0"
UA_VERSION_6_1 = "6.1.0"
UA_VERSION_6_2 = "6.2.0"
UA_VERSION_7_0 = "7.0.0"
UA_VERSION_7_1 = "7.1.0"
UA_VERSION_7_2 = "7.2.0"
UA_VERSION_7_3 = "7.3.0"
UA_VERSION_7_4 = "7.4.0"
UA_VERSION_7_5 = "7.5.0"

# Represents the next upcoming version
UA_VERSION_DEVELOP = "develop"
UA_VERSION_CURRENT_RELEASE = UA_VERSION_7_4


class Version:
    """
    Represents a version of uberAgent.

    This class facilitates the comparison of uberAgent versions and checking
    compatibility/support for various platforms, logsources, and fields.

    Attributes:
    - _outputVersion (str): Internal representation of the uberAgent version.

    Methods:
    - Various utility methods to check if the current version is greater than
      or equal to specific versions.
    - Methods to check if a platform, field, or logsource is supported by
      the current version.
    """
    def __init__(self, version: str):
        """
        Initialize a Version instance based on a provided version string.

        Parameters:
        - version (str): The version of uberAgent to be represented.
        """
        if version.count('.') == 1:
            version += ".0"
        elif version == "main":
            version = UA_VERSION_CURRENT_RELEASE
        elif version == "develop":
            version = UA_VERSION_DEVELOP

        self._outputVersion = version

    # Various methods to check version compatibility
    def is_version_6_1_or_newer(self) -> bool:
        return self.is_version_develop() or self._version() >= self._version_tuple(UA_VERSION_6_1)

    def is_version_6_2_or_newer(self) -> bool:
        return self.is_version_develop() or self._version() >= self._version_tuple(UA_VERSION_6_2)

    def is_version_7_0_or_newer(self) -> bool:
        return self.is_version_develop() or self._version() >= self._version_tuple(UA_VERSION_7_0)

    def is_version_7_1_or_newer(self) -> bool:
        return self.is_version_develop() or self._version() >= self._version_tuple(UA_VERSION_7_1)

    def is_version_7_2_or_newer(self) -> bool:
        return self.is_version_develop() or self._version() >= self._version_tuple(UA_VERSION_7_2)

    def is_version_7_3_or_newer(self) -> bool:
        return self.is_version_develop() or self._version() >= self._version_tuple(UA_VERSION_7_3)

    def is_version_7_4_or_newer(self) -> bool:
        return self.is_version_develop() or self._version() >= self._version_tuple(UA_VERSION_7_4)
    
    def is_version_7_5_or_newer(self) -> bool:
        return self.is_version_develop() or self._version() >= self._version_tuple(UA_VERSION_7_5)

    def is_version_develop(self) -> bool:
        return self._outputVersion == UA_VERSION_DEVELOP

    def is_platform_supported(self, platform) -> bool:
        """
        Check if a given platform is supported by the current uberAgent version.

        Parameters:
        - platform (str): The platform to check support for.

        Returns:
        - bool: True if supported, False otherwise.
        """
        platform_per_version = {
            UA_VERSION_6_0: ["common", "windows"],
            UA_VERSION_7_1: ["common", "windows", "macos"]
        }

        if platform in platform_per_version[UA_VERSION_6_0]:
            return True

        if self.is_version_7_1_or_newer() and platform in platform_per_version[UA_VERSION_7_1]:
            return True

        return False

    def reduce_mapping(self, mapping: Dict[str, Field]):
        """
        Reduces a mapping to only include fields supported by the current version.

        Parameters:
        - mapping (Dict[str, Field]): Mapping of fields.

        Returns:
        - List[str]: List of field keys supported by the current version.
        """
        result: List[str] = []
        for k in mapping.keys():
            v: Field = mapping[k]
            if self.is_field_supported(v):
                result.append(k)
        return result

    def is_field_supported(self, field: Field) -> bool:
        """
        Determines if the given field is supported by the current version of uberAgent.

        This method checks if the field's version is compatible with the current uberAgent version.

        Parameters:
        - field (Field): The field object whose compatibility needs to be checked.

        Returns:
        - bool: True if the field is supported by the current version, False otherwise.
        """
        if field.version == UA_VERSION_6_0:
            return True

        if self.is_version_6_1_or_newer() and field.version == UA_VERSION_6_1:
            return True

        if self.is_version_6_2_or_newer() and field.version == UA_VERSION_6_2:
            return True

        if self.is_version_7_0_or_newer() and field.version == UA_VERSION_7_0:
            return True

        if self.is_version_7_1_or_newer() and field.version == UA_VERSION_7_1:
            return True

        if self.is_version_7_2_or_newer() and field.version == UA_VERSION_7_2:
            return True

        if self.is_version_7_3_or_newer() and field.version == UA_VERSION_7_3:
            return True

        if self.is_version_7_4_or_newer() and field.version == UA_VERSION_7_4:
            return True

        if self.is_version_develop() and field.version == UA_VERSION_DEVELOP:
            return True

        return False

    def is_logsource_supported(self, logsource: Logsource) -> bool:
        """
        Determines if the given logsource is known and supported by the current version of uberAgent ESA.

        This method checks if the logsource's version is compatible with the current uberAgent version.

        Parameters:
        - logsource (Logsource): The logsource object whose compatibility needs to be checked.

        Returns:
        - bool: True if the logsource is supported by the current version, False otherwise.
        """
        if logsource.version == UA_VERSION_6_0:
            return True

        if self.is_version_6_1_or_newer() and logsource.version == UA_VERSION_6_1:
            return True

        if self.is_version_6_2_or_newer() and logsource.version == UA_VERSION_6_2:
            return True

        if self.is_version_7_0_or_newer() and logsource.version == UA_VERSION_7_0:
            return True

        if self.is_version_7_1_or_newer() and logsource.version == UA_VERSION_7_1:
            return True

        if self.is_version_7_2_or_newer() and logsource.version == UA_VERSION_7_2:
            return True

        if self.is_version_7_3_or_newer() and logsource.version == UA_VERSION_7_3:
            return True

        if self.is_version_7_4_or_newer() and logsource.version == UA_VERSION_7_4:
            return True

        if self.is_version_develop() and logsource.version == UA_VERSION_DEVELOP:
            return True

        return False

    def _version(self):
        """
        Convert the version string into a tuple of integers for easier comparison.

        Returns:
        - tuple: The version as a tuple of integers.
        """
        return self._version_tuple(self._outputVersion)

    @staticmethod
    def _version_tuple(v):
        """
        Convert a version string into a tuple of integers.

        Parameters:
        - v (str): Version string to be converted.

        Returns:
        - tuple: The version as a tuple of integers.
        """
        return tuple(map(int, (v.split("."))))

    def __str__(self):
        """
        Return the string representation of the Version object, which is its version string.

        Returns:
        - str: The version string.
        """
        return self._outputVersion
