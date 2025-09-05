import json
import re
from typing import ClassVar, Dict, Tuple, Pattern, List, Any, Optional, Union

from sigma.conditions import ConditionItem, ConditionAND, ConditionOR, ConditionNOT, ConditionFieldEqualsValueExpression
from sigma.conversion.base import TextQueryBackend
from sigma.conversion.state import ConversionState
from sigma.rule import SigmaRule, SigmaLevel
from sigma.types import SigmaCompareExpression, SigmaRegularExpressionFlag
from sigma.conversion.deferred import DeferredQueryExpression
from sigma.processing.pipeline import ProcessingPipeline

from sigma.backends.uberagent.exceptions import MissingPropertyException, MissingFunctionException
from sigma.backends.uberagent.rule import Rule
from sigma.pipelines.uberagent.version import UA_VERSION_CURRENT_RELEASE, Version


def get_mitre_annotation_from_tag(tag):
    tag = str(tag).lower()
    if tag.startswith('attack.t'):
        return tag[7:].upper()
    return None


def ua_annotation(version: Version, tags: List[str], author: str) -> Optional[str]:
    mitre_annotation_objects = []
    for tag in tags:
        mitre_annotation = get_mitre_annotation_from_tag(tag)
        if mitre_annotation is not None:
            mitre_annotation_objects.append(mitre_annotation)

    result: dict = {}

    if len(mitre_annotation_objects) > 0:
        result['mitre_attack'] = mitre_annotation_objects

    # New in upcoming version: Author is included in annotations.
    if version.is_version_7_2_or_newer() and author is not None:
        result['author'] = author

    if len(result.keys()) > 0:
        return json.dumps(result)

    return None


def ua_tag(name: str) -> str:
    """Converts the given Sigma rule name to uberagent ESA Tag property."""
    tag = name.lower().replace(" ", "-")
    tag = re.sub(r"-{2,}", "-", tag, count=0, flags=re.IGNORECASE)
    return tag


def ua_risk_score(level: SigmaLevel) -> int:
    """Converts the given Sigma rule level to uberagent ESA RiskScore property."""

    if level is None:
        return 0

    levels = {
        "critical": 100,
        "high": 75,
        "medium": 50,
        "low": 25,
        "informational": 1
    }

    level = str(level).lower()
    return levels[level]


class uberagent(TextQueryBackend):
    """uAQL backend."""
    # TODO: change the token definitions according to the syntax. Delete these not supported by your backend.
    # See the pySigma documentation for further information:
    # https://sigmahq-pysigma.readthedocs.io/en/latest/Backends.html

    # Operator precedence: tuple of Condition{AND,OR,NOT} in order of precedence.
    # The backend generates grouping if required
    name: ClassVar[str] = "uAQL backend"
    formats: Dict[str, str] = {
        "default": "Plain uAQL queries",
        "conf": "Configuration"
    }

    config: Dict[str, Any] = {
        "version": "str"
    }

    requires_pipeline: bool = True
    precedence: ClassVar[Tuple[ConditionItem, ConditionItem, ConditionItem]] = (ConditionNOT, ConditionAND, ConditionOR)

    # Expression for precedence override grouping as format string with {expr} placeholder
    group_expression: ClassVar[str] = "({expr})"

    # Generated query tokens
    token_separator: str = " "  # separator inserted between all boolean operators
    or_token: ClassVar[str] = "or"
    and_token: ClassVar[str] = "and"
    not_token: ClassVar[str] = "not"

    # Token inserted between field and value (without separator)
    eq_token: ClassVar[str] = " == "

    # String output Fields Quoting Character used to quote field characters if field_quote_pattern matches (or not,
    # depending on field_quote_pattern_negation). No field name quoting is done if not set.
    field_quote: ClassVar[str] = None

    # Quote field names if this pattern (doesn't) matches, depending on field_quote_pattern_negation. Field name is
    # always quoted if pattern is not set.
    field_quote_pattern: ClassVar[Pattern] = re.compile("^\\w+$")

    # Negate field_quote_pattern result. Field name is quoted if pattern doesn't matches if set to True (default).
    field_quote_pattern_negation: ClassVar[bool] = True

    # Escaping
    # Character to escape particular parts defined in field_escape_pattern.
    field_escape: ClassVar[str] = "\\"
    # Escape quote string defined in field_quote
    field_escape_quote: ClassVar[bool] = False
    # All matches of this pattern are prepended with the string contained in field_escape.
    field_escape_pattern: ClassVar[Pattern] = re.compile("\\s")

    # Values
    str_quote: ClassVar[str] = '"'  # string quoting character (added as escaping character)
    escape_char: ClassVar[str] = "\\"  # Escaping character for special characters inside string
    wildcard_multi: ClassVar[str] = "%"  # Character used as multi-character wildcard
    wildcard_single: ClassVar[str] = "_"  # Character used as single-character wildcard
    add_escaped: ClassVar[str] = "\\"  # Characters quoted in addition to wildcards and string quote
    filter_chars: ClassVar[str] = ""  # Characters filtered
    bool_values: ClassVar[Dict[bool, str]] = {  # Values to which boolean values are mapped.
        True: "true",
        False: "false",
    }

    # String matching operators. if none is appropriate eq_token is used.
    #
    # 2023-11-16: Disabled because of performance regression vs 'like'.
    #             The 'like' operator is much faster and less resource-hungry than using the functions.
    #             Should be enabled again in a future version; after polishing the mentioned functions.
    #
    # startswith_expression: ClassVar[str] = "istartswith({field}, {value})"
    # endswith_expression: ClassVar[str] = "iendswith({field}, {value})"
    # contains_expression: ClassVar[str] = "icontains({field}, {value})"

    startswith_expression: ClassVar[str] = None
    endswith_expression: ClassVar[str] = None
    contains_expression: ClassVar[str] = None

    # Special expression if wildcards can't be matched with the eq_token operator
    wildcard_match_expression: ClassVar[str] = '{field} like r{value}'

    # Regular expressions
    # Regular expression query as format string with placeholders {field}, {regex}, {flag_x} where x
    # is one of the flags shortcuts supported by Sigma (currently i, m and s) and refers to the
    # token stored in the class variable re_flags.
    re_expression: ClassVar[str] = 'regex_match({field}, "{regex}")'

    # Character used for escaping in regular expressions
    re_escape_char: ClassVar[str] = "\\"

    # List of strings that are escaped
    re_escape: ClassVar[Tuple[str]] = ('"')

    # If True, the escape character is also escaped
    re_escape_escape_char: bool = True

    # If True, the flags are prepended as (?x) group at the beginning of the regular expression, e.g. (?i).
    # If this is not supported by the target, it should be set to False.
    re_flag_prefix: bool = False

    # Mapping from SigmaRegularExpressionFlag values to static string templates that are used in
    # flag_x placeholders in re_expression template.
    # By default, i, m and s are defined. If a flag is not supported by the target query language,
    # remove it from re_flags or don't define it to ensure proper error handling in case of appearance.
    re_flags: Dict[SigmaRegularExpressionFlag, str] = {
        # SigmaRegularExpressionFlag.IGNORECASE: "i",
        # SigmaRegularExpressionFlag.MULTILINE: "m",
        # SigmaRegularExpressionFlag.DOTALL: "s",
    }

    # Case-sensitive string matching expression. String is quoted/escaped like a normal string.
    # Placeholders {field} and {value} are replaced with field name and quoted/escaped string.
    case_sensitive_match_expression: ClassVar[str] = "{field} === {value}"

    # Case-sensitive string matching operators similar to standard string matching. If not provided,
    # case_sensitive_match_expression is used.
    case_sensitive_startswith_expression: ClassVar[str] = "startswith({field}, {value})"
    case_sensitive_endswith_expression: ClassVar[str] = "endswith({field}, {value})"
    case_sensitive_contains_expression: ClassVar[str] = "contains({field}, {value})"

    # CIDR expressions: define CIDR matching if backend has native support. Else pySigma expands
    # CIDR values into string wildcard matches.
    # CIDR expression query as format string with placeholders {field}, {value} (the whole CIDR value), {network}
    # (network part only), {prefixlen} (length of network mask prefix) and {netmask} (CIDR network mask only).
    cidr_expression: ClassVar[Optional[str]] = None

    # Numeric comparison operators
    # Compare operation query as format string with placeholders {field}, {operator} and {value}
    compare_op_expression: ClassVar[str] = "{field} {operator} {value}"

    # Mapping between CompareOperators elements and strings used as replacement for {operator} in compare_op_expression
    compare_operators: ClassVar[Dict[SigmaCompareExpression.CompareOperators, str]] = {
        SigmaCompareExpression.CompareOperators.LT: "<",
        SigmaCompareExpression.CompareOperators.LTE: "<=",
        SigmaCompareExpression.CompareOperators.GT: ">",
        SigmaCompareExpression.CompareOperators.GTE: ">=",
    }

    # Expression for comparing two event fields
    # Field comparison expression with the placeholders {field1} and {field2} corresponding to left field and right
    # value side of Sigma detection item
    field_equals_field_expression: ClassVar[Optional[str]] = None

    # If regular field-escaping/quoting is applied to field1 and field2.
    # A custom escaping/quoting can be implemented in the convert_condition_field_eq_field_escape_and_quote method.
    field_equals_field_escaping_quoting: Tuple[bool, bool] = (True, True)

    # Null/None expressions
    # Expression for field has null value as format string with {field} placeholder for field name
    field_null_expression: ClassVar[str] = "isnull({field})"

    # Field existence condition expressions.
    # Expression for field existence as format string with {field} placeholder for field name
    # TODO: "exists({field})"
    field_exists_expression: ClassVar[str] = None

    # Expression for field non-existence as format string with {field} placeholder for field name. If not set,
    # field_exists_expression is negated with boolean NOT.
    # TODO: "notexists({field})"
    field_not_exists_expression: ClassVar[str] = None

    # Field value in list, e.g. "field in (value list)" or "field containsall (value list)"
    convert_or_as_in: ClassVar[bool] = True  # Convert OR as in-expression
    convert_and_as_in: ClassVar[bool] = True  # Convert AND as in-expression

    # Values in list can contain wildcards. If set to False (default) only plain values are converted into
    # in-expressions.
    in_expressions_allow_wildcards: ClassVar[bool] = False

    # Expression for field in list of values as format string with placeholders {field}, {op} and {list}
    field_in_list_expression: ClassVar[str] = "{field} {op} [{list}]"

    # Operator used to convert OR into in-expressions. Must be set if convert_or_as_in is set
    or_in_operator: ClassVar[str] = "in"

    # Operator used to convert AND into in-expressions. Must be set if convert_and_as_in is set
    # TODO: "contains-all"
    and_in_operator: ClassVar[str] = None

    # List element separator
    list_separator: ClassVar[str] = ", "

    # Value not bound to a field
    # Expression for string value not bound to a field as format string with placeholder {value}
    unbound_value_str_expression: ClassVar[str] = '"{value}"'

    # Expression for number value not bound to a field as format string with placeholder {value}
    unbound_value_num_expression: ClassVar[str] = '{value}'

    # Expression for regular expression not bound to a field as format string with placeholder {value} and {flag_x}
    # as described for re_expression
    unbound_value_re_expression: ClassVar[str] = '_=~{value}'

    # Query finalization: appending and concatenating deferred query part
    deferred_start: ClassVar[str] = "\n| "  # String used as separator between main query and deferred parts
    deferred_separator: ClassVar[str] = "\n| "  # String used to join multiple deferred query parts
    deferred_only_query: ClassVar[str] = "*"  # String used as query if final query only contains deferred expression

    def __init__(self,
                 processing_pipeline: Optional[ProcessingPipeline] = None,
                 collect_errors: bool = False,
                 backend_version: Optional[str] = None,
                 **kwargs):

        ua_backend_version: Version = Version(UA_VERSION_CURRENT_RELEASE)
        if backend_version is not None:
            ua_backend_version = Version(backend_version)

        # The default behavior is to utilize the version provided by the specified pipeline.
        # However, in certain situations, it is crucial to employ the version that is accessible
        # as a backend configuration option.
        #
        # This allows for adjustments to the syntax-specific aspects of rule generation.

        # Regular expressions are handled differntly in current development version.
        if ua_backend_version.is_version_7_2_or_newer():
            self.re_expression = '{field} regex "{regex}"'

        super().__init__(processing_pipeline, collect_errors)

    def get_version_from_state(self, state: ConversionState) -> Version:
        version = Version("develop")
        if "uaVersion" in state.processing_state:
            version = Version(state.processing_state["uaVersion"])
        return version


    # Make sure that the function 'isnull' is only used for uberAgent 7.0+ versions.
    # Previous versions do not support that expression.
    def convert_condition_field_eq_val_null(
        self, cond: ConditionFieldEqualsValueExpression, state: ConversionState
    ) -> Union[str, DeferredQueryExpression]:
        version = self.get_version_from_state(state)
        if version.is_version_7_0_or_newer():
            return super().convert_condition_field_eq_val_null(cond, state)
        raise MissingFunctionException("isnull")


    def finalize_query_conf(self, rule: SigmaRule, query: str, index: int, state: ConversionState) -> str:

        if rule.id is None or len(str(rule.id)) == 0:
            raise MissingPropertyException("id")

        if rule.title is None or len(rule.title) == 0:
            raise MissingPropertyException("title")

        version = self.get_version_from_state(state)

        ua_rule: Rule = Rule(version)
        ua_rule.set_query(self.finalize_query_default(rule, query, index, state))
        ua_rule.set_id(rule.id)
        ua_rule.set_name(rule.title)
        ua_rule.set_tag(ua_tag(rule.title))
        ua_rule.set_event_type(rule.logsource.category)
        ua_rule.set_risk_score(ua_risk_score(rule.level))
        ua_rule.set_description(rule.description)
        ua_rule.set_author(rule.author)
        ua_rule.set_annotation(ua_annotation(version, rule.tags, rule.author))
        ua_rule.set_generic_properties(state.processing_state["Fields"])
        ua_rule.set_platform(rule.logsource.product)

        return str(ua_rule)

    def finalize_output_conf(self, queries: List[Any]) -> Any:
        return self.finalize_output_default(queries)
