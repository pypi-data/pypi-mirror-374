from typing import List

from sigma.pipelines.uberagent.version import Version


class MalformedRuleException(Exception):
    """
    MalformedRuleException
    Helper class to ignore exceptions.py to malformed rules.
    """
    pass


class Rule:
    """
    Rule
    This class wraps a [Rule] configuration stanza.
    """

    def __init__(self, version: Version):
        self.id = ""
        self.version = version
        self.name = ""
        self.event_type = None
        self.tag = ""
        self.query = ""
        self.risk_score = 0
        self.description = ""
        self.annotation = ""
        self.generic_properties = []
        self.platform = ""
        self.author = ""

    # Query =
    # Available since uberagent 6.0+
    def set_query(self, query: str):
        """Sets the generated query property."""
        self.query = query

    # RuleName =
    # Available since uberagent 6.0+
    def set_name(self, name: str):
        """Sets the RuleName."""
        self.name = name

    # Tag =
    # Available since uberagent 6.0+
    def set_tag(self, tag: str):
        """Sets the Tag property."""
        self.tag = tag

    # EventType =
    # Available since uberagent 6.0+
    def set_event_type(self, event_type: str):
        """Sets the EventType property."""
        self.event_type = event_type

    # RiskScore =
    # Available since uberagent 6.0+
    def set_risk_score(self, risk_score: str):
        """Sets the RiskScore property."""
        self.risk_score = risk_score

    # RuleId =
    # Available since uberagent 7.0+
    def set_id(self, rule_id: str):
        """Sets the RuleId property."""
        self.id = rule_id

    # Annotation =
    # Available since uberagent 7.0+
    def set_annotation(self, annotation: str):
        """Set the Annotation property."""
        self.annotation = annotation

    # GenericProperty1 =
    # ..
    # GenericPropertyN =
    # Available since uberagent 6.1+
    def set_generic_properties(self, fields: List[str]) -> None:
        """
        Set the generic properties.

        This method filters out specific properties that are always included in
        all tagging events to avoid redundancy and sorts the fields by name.

        Parameters:
        - fields (List[str]): List of fields to be considered as generic properties.

        Notes:
        - Properties such as "Process.Path", "Process.CommandLine", and "Process.Name"
          are always included in all tagging events. Thus, they are removed from
          the fields list to avoid redundancy.
        """

        # The following properties are included in all tagging events anyways.
        # There is no need to send them twice to the backend so we are ignoring them here.
        filtered_fields = [prop for prop in fields if prop not in ["Process.Path", "Process.CommandLine", "Process.Name"]]
        self.generic_properties = filtered_fields

    # Not used as configuration setting, but to comment the rule.
    # Available since uberagent 6.0+
    def set_description(self, description: str):
        """Set the Description property."""
        self.description = description

    # Not used as configuration setting, but to comment the rule.
    def set_author(self, author: str):
        """Set the Author property."""
        self.author = author

    # Used to determine the platform where a rule is being evaluated on.
    # Adds the platform = X configuration to a [ActivityMonitoringRule] stanza.
    #
    # Available since uberagent 7.0+
    def set_platform(self, product: str):
        """Set the platform property. """
        self.platform = product

    # Utility to make/modify tag names.
    def _prefixed_tag(self):
        prefixes = {
            "Process.Start": "proc-start"
        }

        if self.event_type not in prefixes:
            return self.tag

        return "{}-{}".format(prefixes[self.event_type], self.tag)
    
    def _stanza_name(self):
        if self.version.is_version_7_2_or_newer():
            return "ThreatDetectionRule"
        return "ActivityMonitoringRule"

    def __str__(self):
        """Builds and returns the [ActivityMonitoringRule] configuration block."""

        # The default is available since uberagent 6.
        result = "[{}]\n".format(self._stanza_name())

        # Starting with uberagent 7.1 and newer we slightly change the configuration stanza.
        # Example. [ActivityMonitoringRule platform=Windows] or [ActivityMonitoringRule platform=MacOS]
        if self.version.is_version_7_1_or_newer():
            result = "[{}".format(self._stanza_name())
            if self.platform in ["windows", "macos"]:
                result += " platform="
                if self.platform == "windows":
                    result += "Windows"
                elif self.platform == "macos":
                    result += "MacOS"
            result += "]\n"

        # The Description is optional.
        if self.description is not None and len(self.description) > 0:
            for description_line in self.description.splitlines():
                result += "# {}\n".format(description_line)

        if self.author is not None and len(self.author) > 0:
            result += "# Author: {}\n".format(self.author)

        # Make sure all required properties have at least a value that is somehow usable.
        if self.event_type is None or len(self.event_type) == 0:
            raise MalformedRuleException()

        if self.tag is None or len(self.tag) == 0:
            raise MalformedRuleException()

        if self.name is None or len(self.name) == 0:
            raise MalformedRuleException()

        if self.query is None or len(self.query) == 0:
            raise MalformedRuleException()

        if self.version.is_version_7_0_or_newer():
            if self.id is None or len(str(self.id)) == 0:
                raise MalformedRuleException()
            result += "RuleId = {}\n".format(self.id)

        result += "RuleName = {}\n".format(self.name)
        result += "EventType = {}\n".format(self.event_type)
        result += "Tag = {}\n".format(self._prefixed_tag())

        # The RiskScore is optional.
        # Set it, if a risk_score value is present.
        if self.risk_score > 0:
            result += "RiskScore = {}\n".format(self.risk_score)

        if self.version.is_version_7_0_or_newer():
            if self.annotation is not None and len(self.annotation) > 0:
                result += "Annotation = {}\n".format(self.annotation)

        result += "Query = {}\n".format(self.query)

        if self.event_type == "Reg.Any":
            result += "Hive = HKLM,HKU\n"

        # uberagent supports generic properties to be added to an activity rule since version 6.1
        if self.version.is_version_6_1_or_newer():
            counter = 1
            for prop in self.generic_properties:
                # Generic properties are limited to 10.
                if counter > 10:
                    break

                result += "GenericProperty{} = {}\n".format(counter, prop)
                counter += 1

        return result
