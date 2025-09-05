from typing import Dict, List

from sigma.pipelines.common import logsource_windows_process_creation, logsource_windows_image_load, \
    logsource_windows_dns_query, logsource_windows_network_connection, logsource_windows_create_remote_thread, \
    logsource_windows_registry_add, logsource_windows_registry_set, \
    logsource_windows_registry_delete, logsource_windows_registry_event, logsource_windows_driver_load, \
    logsource_windows_file_rename, logsource_windows_file_delete, logsource_windows_file_change, \
    logsource_windows_file_event, logsource_windows_file_access
from sigma.processing.conditions import LogsourceCondition, RuleProcessingItemAppliedCondition, RuleContainsDetectionItemCondition
from sigma.processing.pipeline import ProcessingPipeline, ProcessingItem
from sigma.processing.transformations import RuleFailureTransformation, SetStateTransformation

from sigma.pipelines.uberagent.condition import ExcludeFieldConditionLowercase, IncludeFieldConditionLowercase
from sigma.pipelines.uberagent.field import Field
from sigma.pipelines.uberagent.logsource import Logsource
from sigma.pipelines.uberagent.transformation import ChangeLogsourceCategoryTransformation, FieldMappingTransformationLowercase, \
    FieldDetectionItemFailureTransformation, ReferencedFieldTransformation
from sigma.pipelines.uberagent.version import UA_VERSION_6_0, UA_VERSION_6_1, UA_VERSION_6_2, UA_VERSION_7_0, \
    UA_VERSION_7_1, UA_VERSION_7_2, UA_VERSION_7_3, UA_VERSION_7_4, UA_VERSION_7_5, UA_VERSION_DEVELOP, UA_VERSION_CURRENT_RELEASE, Version

# Maps all known Sigma fields to uberAgent Process Event Properties
# Note: The process properties are re-usable for all event types as all events are linked to a process.
#
# Documentation:
# https://uberagent.com/docs/uberagent/latest/esa-features-configuration/threat-detection-engine/event-properties/common-event-properties/
ua_process_creation_mapping: Dict[str, Field] = {

    # Common fields.
    # The fields here are usable in all other event types if supported by Sigma.
    "image"                 : Field(UA_VERSION_6_0, "Process.Path"),
    "childimage"            : Field(UA_VERSION_6_0, "Process.Path"),
    "originalfilename"      : Field(UA_VERSION_6_0, "Process.Name"),
    "commandline"           : Field(UA_VERSION_6_0, "Process.CommandLine"),
    "parentimage"           : Field(UA_VERSION_6_0, "Parent.Path"),
    "parentcommandline"     : Field(UA_VERSION_6_0, "Parent.CommandLine"),
    "company"               : Field(UA_VERSION_6_0, "Process.Company"),
    "user"                  : Field(UA_VERSION_6_0, "Process.User"),
    "username"              : Field(UA_VERSION_6_0, "Process.User"),
    "md5"                   : Field(UA_VERSION_6_1, "Process.Hash.MD5"),
    "sha1"                  : Field(UA_VERSION_6_1, "Process.Hash.SHA1"),
    "sha256"                : Field(UA_VERSION_6_1, "Process.Hash.SHA256"),
    "imphash"               : Field(UA_VERSION_6_1, "Process.Hash.IMP"),
    "signed"                : Field(UA_VERSION_6_1, "Process.IsSigned"),
    "signature"             : Field(UA_VERSION_6_1, "Process.Signature"),
    "signaturestatus"       : Field(UA_VERSION_6_1, "Process.SignatureStatus"),
    # ""                    : Field(UA_VERSION_6_1, "Parent.Hash.MD5")
    # ""                    : Field(UA_VERSION_6_1, "Parent.Hash.SHA1")
    # ""                    : Field(UA_VERSION_6_1, "Parent.Hash.SHA256")
    # ""                    : Field(UA_VERSION_6_1, "Parent.Hash.IMP")
    # ""                    : Field(UA_VERSION_6_1, "Parent.IsSigned")
    # ""                    : Field(UA_VERSION_6_1, "Parent.Signature")
    # ""                    : Field(UA_VERSION_6_1, "Parent.SignatureStatus")
    # ""                    : Field(UA_VERSION_6_2, "Parent.Hashes")
    "hashes"                : Field(UA_VERSION_6_2, "Process.Hashes")
}

# Maps all known Sigma fields to uberAgent Image Load (or Driver) Event Properties
#
# Documentation:
# https://uberagent.com/docs/uberagent/latest/esa-features-configuration/threat-detection-engine/event-properties/image-load-event-properties/
ua_image_load_mapping: Dict[str, Field] = {

    # Common
    "image"                 : Field(UA_VERSION_6_0, "Process.Path"),
    "childimage"            : Field(UA_VERSION_6_0, "Image.Path"),
    "imageloaded"           : Field(UA_VERSION_6_0, "Image.Path"),
    "originalfilename"      : Field(UA_VERSION_6_0, "Process.Name"),
    "commandline"           : Field(UA_VERSION_6_0, "Process.CommandLine"),

    # Image/Driver Load Event
    "md5"                   : Field(UA_VERSION_6_1, "Image.Hash.MD5"),
    "sha1"                  : Field(UA_VERSION_6_1, "Image.Hash.SHA1"),
    "sha256"                : Field(UA_VERSION_6_1, "Image.Hash.SHA256"),
    "imphash"               : Field(UA_VERSION_6_1, "Image.Hash.IMP"),
    "signed"                : Field(UA_VERSION_6_1, "Image.IsSigned"),
    "signature"             : Field(UA_VERSION_6_1, "Image.Signature"),
    "signaturestatus"       : Field(UA_VERSION_6_1, "Image.SignatureStatus"),
    "hashes"                : Field(UA_VERSION_6_2, "Image.Hashes")
}

# Maps all known Sigma fields to uberAgent DNS Query Event Properties
#
# Documentation:
# https://uberagent.com/docs/uberagent/latest/esa-features-configuration/threat-detection-engine/event-properties/dns-query-event-properties/
ua_dns_query_mapping: Dict[str, Field] = {

    # Common
    "image"                 : Field(UA_VERSION_6_0, "Process.Path"),
    "originalfilename"      : Field(UA_VERSION_6_0, "Process.Name"),
    "commandline"           : Field(UA_VERSION_6_0, "Process.CommandLine"),

    # DNS Query Event
    "query"                 : Field(UA_VERSION_6_1, "Dns.QueryRequest"),
    "queryname"             : Field(UA_VERSION_6_1, "Dns.QueryRequest"),
    "answer"                : Field(UA_VERSION_6_1, "Dns.QueryResponse")
}

# Maps all known Sigma fields to uberAgent Network Event Properties
#
# Documentation:
# https://uberagent.com/docs/uberagent/latest/esa-features-configuration/threat-detection-engine/event-properties/network-event-properties/
ua_network_connection_mapping: Dict[str, Field] = {

    # Common
    "image"                 : Field(UA_VERSION_6_0, "Process.Path"),
    "originalfilename"      : Field(UA_VERSION_6_0, "Process.Name"),
    "commandline"           : Field(UA_VERSION_6_0, "Process.CommandLine"),

    # Network Event
    "dst_ip"                : Field(UA_VERSION_6_0, "Net.Target.Ip"),
    "destinationip"         : Field(UA_VERSION_6_0, "Net.Target.Ip"),
    "destinationhostname"   : Field(UA_VERSION_6_0, "Net.Target.Name"),
    "destinationport"       : Field(UA_VERSION_6_0, "Net.Target.Port"),
    # ""                    : Field(UA_VERSION_6_2, "Net.Target.PortName")
    # ""                    : Field(UA_VERSION_6_0, "Net.Target.Protocol")
    "destinationisipv6"     : Field(UA_VERSION_6_2, "Net.Target.IpIsV6"),
    "src_ip"                : Field(UA_VERSION_6_2, "Net.Source.Ip"),
    # ""                    : Field(UA_VERSION_6_2, "Net.Source.Name")
    "sourceport"            : Field(UA_VERSION_6_2, "Net.Source.Port")
    # ""                    : Field(UA_VERSION_6_2, "Net.Source.PortName")
    # ""                    : Field(UA_VERSION_6_2, "Net.Source.IpIsV6")
}

# Maps all known Sigma fields to uberAgent Remote Thread Event Properties
#
# Documentation:
# https://uberagent.com/docs/uberagent/latest/esa-features-configuration/threat-detection-engine/event-properties/remote-thread-event-properties/
ua_create_remote_thread_mapping: Dict[str, Field] = {

    # Common
    "targetimage"           : Field(UA_VERSION_6_0, "Process.Path"),

    # Thread Event
    "startmodule"           : Field(UA_VERSION_6_2, "Thread.StartModule"),
    "startfunction"         : Field(UA_VERSION_6_2, "Thread.StartFunctionName"),
    # ""                    : Field(UA_VERSION_6_2, "Thread.Process.Id")
    # ""                    : Field(UA_VERSION_6_2, "Thread.Parent.Id")
    # ""                    : Field(UA_VERSION_6_2, "Thread.StartAddress")
    # ""                    : Field(UA_VERSION_6_2, "Thread.Timestamp")
}

# Maps all known Sigma fields to uberAgent Registry Event Properties
#
# Documentation:
# https://uberagent.com/docs/uberagent/latest/esa-features-configuration/threat-detection-engine/event-properties/registry-event-properties/
ua_registry_event_mapping: Dict[str, Field] = {

    # Common
    "image"                 : Field(UA_VERSION_6_0, "Process.Path"),
    "originalfilename"      : Field(UA_VERSION_6_0, "Process.Name"),
    "commandline"           : Field(UA_VERSION_6_0, "Process.CommandLine"),

    # Registry Event
    # ""                    : Field(UA_VERSION_6_0, "Reg.Key.Path")
    # ""                    : Field(UA_VERSION_6_0, "Reg.Key.Name")
    # ""                    : Field(UA_VERSION_6_0, "Reg.Parent.Key.Path")
    # ""                    : Field(UA_VERSION_6_0, "Reg.Parent.Key.Path")
    "newname"               : Field(UA_VERSION_6_0, "Reg.Key.Path.New"),
    # ""                    : Field(UA_VERSION_6_0, "Reg.Key.Path.Old"),
    # ""                    : Field(UA_VERSION_6_0, "Reg.Value.Name"),
    # ""                    : Field(UA_VERSION_6_0, "Reg.File.Name"),
    # ""                    : Field(UA_VERSION_6_0, "Reg.Key.Sddl"),
    # ""                    : Field(UA_VERSION_6_0, "Reg.Key.Hive"),
    "targetobject"          : Field(UA_VERSION_7_2, "Reg.TargetObject"),
    "details"               : Field(UA_VERSION_7_2, "Reg.Value.Data"),
    # ""                    : Field(UA_VERSION_7_2, "Reg.Value.Data.Number")
    # ""                    : Field(UA_VERSION_7_2, "Reg.Value.Data.String")
    "eventtype"             : Field(UA_VERSION_7_2, "Reg.EventType")
    # ""                    : Field(UA_VERSION_7_1, "Reg.Value.Type")
}

# Maps all known Sigma fields to uberAgent File System Event Properties
#
# Documentation:
# https://uberagent.com/docs/uberagent/latest/esa-features-configuration/threat-detection-engine/event-properties/file-system-activity-event-properties/
ua_file_event_mapping: Dict[str, Field] = {

    # Common
    "image"                 : Field(UA_VERSION_6_0, "Process.Path"),
    "originalfilename"      : Field(UA_VERSION_6_0, "Process.Name"),
    "commandline"           : Field(UA_VERSION_6_0, "Process.CommandLine"),
    "parentimage"           : Field(UA_VERSION_6_0, "Parent.Path"),
    "parentcommandline"     : Field(UA_VERSION_6_0, "Parent.CommandLine"),
    "user"                  : Field(UA_VERSION_6_0, "Process.User"),

    # File System Event
    # TODO: <creationutctime> Requires UTC String formatting from uberAgent
    # ""                    : Field(UA_VERSION_7_1, "File.CreationDate"),
    # TODO: This field is only available on macOS
    # ""                    : Field(UA_VERSION_7_1, "File.HasExecPermissions"),
    # ""                    : Field(UA_VERSION_7_1, "File.IsExecutable"),
    # ""                    : Field(UA_VERSION_7_1, "File.Name"),
    # TODO: <previouscreationutctime> Requires UTC String formatting from uberAgent
    # TODO: This field is only available on Windows
    # ""                    : Field(UA_VERSION_7_1, "File.PreviousCreationDate"),
    # ""                    : Field(UA_VERSION_7_1, "File.PreviousName"),
    # ""                    : Field(UA_VERSION_7_1, "File.PreviousPath"),
    "targetfilename"        : Field(UA_VERSION_7_1, "File.Path"),
    "filename"              : Field(UA_VERSION_7_1, "File.Path"),
    "sourcefilename"        : Field(UA_VERSION_7_1, "File.PreviousPath")
}


# No built-in function available. Used a custom condition.
# Only one rule was applicable at the time of creation.
def logsource_windows_process_tampering():
    return LogsourceCondition(category="process_tampering", product="windows")


def logsource_macos_process_creation() -> LogsourceCondition:
    return LogsourceCondition(
        category="process_creation",
        product="macos",
    )


def logsource_macos_file_event():
    return LogsourceCondition(
        category="file_event",
        product="macos",
    )


def logsource_macos_file_delete():
    return LogsourceCondition(
        category="file_delete",
        product="macos",
    )


def logsource_macos_file_rename():
    return LogsourceCondition(
        category="file_rename",
        product="macos",
    )


def logsource_macos_file_change() -> LogsourceCondition:
    return LogsourceCondition(
        category="file_change",
        product="macos",
    )


def logsource_macos_dns_query() -> LogsourceCondition:
    return LogsourceCondition(
        category="dns_query",
        product="macos",
    )

def logsource_common_firewall() -> LogsourceCondition:
    return LogsourceCondition(
        category="firewall"
    )


#
# Lists all Threat Detection Engine event types of uberAgent and maps them to Sigma log sources.
# Some event types of uberAgent are not used in Sigma but if so, uncomment the matching event types and
# add particular log sources.
#
# A full list of available event types is documented here:
# https://uberagent.com/docs/uberagent/latest/esa-features-configuration/threat-detection-engine/event-types/
#
ua_categories: List[Logsource] = [
    #
    # Process & Image Events
    #
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Process.Stop") // Windows,
    # Not yet used/mappable: Logsource(UA_VERSION_7_1, "Process.Stop") // macOS,

    Logsource(UA_VERSION_6_0, "Process.Start",
              conditions=[logsource_windows_process_creation()],
              fields=ua_process_creation_mapping),

    Logsource(UA_VERSION_7_1, "Process.Start",
              conditions=[logsource_macos_process_creation()],
              fields=ua_process_creation_mapping),

    Logsource(UA_VERSION_6_2, "Process.CreateRemoteThread",
              conditions=[logsource_windows_create_remote_thread()],
              fields=ua_create_remote_thread_mapping),

    Logsource(UA_VERSION_6_2, "Process.TamperingEvent",
              conditions=[logsource_windows_process_tampering()],
              fields=ua_process_creation_mapping),

    Logsource(UA_VERSION_6_0, "Image.Load",
              conditions=[logsource_windows_image_load()],
              fields=ua_image_load_mapping),

    Logsource(UA_VERSION_7_1, "Driver.Load",
              conditions=[logsource_windows_driver_load()],
              fields=ua_image_load_mapping),

    #
    # Network Events
    #
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Net.Send"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Net.Receive"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Net.Connect"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Net.Reconnect"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Net.Retransmit"),

    # TODO: Update this missing event type in vlDocs
    Logsource(UA_VERSION_6_2, "Net.Any",
              conditions=[
                  logsource_windows_network_connection(),
                  logsource_common_firewall()
              ],
              fields=ua_network_connection_mapping),

    #
    # Registry Events
    #
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.Create"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Value.Write"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Delete"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.Delete"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Value.Delete"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.SecurityChange"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.Rename"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.SetInformation"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.Load"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.Unload"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.Save"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.Restore"),
    # Not yet used/mappable: Logsource(UA_VERSION_6_0, "Reg.Key.Replace"),

    Logsource(UA_VERSION_6_0, "Reg.Any",
              conditions=[
                 logsource_windows_registry_event(),
                 logsource_windows_registry_add(),
                 logsource_windows_registry_delete(),
                 logsource_windows_registry_set()
             ],
              fields=ua_registry_event_mapping),

    #
    # DNS Query Events
    #
    Logsource(UA_VERSION_6_1, "Dns.Query",
              conditions=[logsource_windows_dns_query()],
              fields=ua_dns_query_mapping),

    Logsource(UA_VERSION_7_1, "Dns.Query",
              conditions=[logsource_macos_dns_query()],
              fields=ua_dns_query_mapping),

    #
    # File System Events
    #
    # Not yet used/mappable: Logsource(UA_VERSION_7_1, "File.ChangeCreationTime"),
    # Not yet used/mappable: Logsource(UA_VERSION_7_1, "File.CreateStream"),
    # Not yet used/mappable: Logsource(UA_VERSION_7_1, "File.PipeCreate"),
    # Not yet used/mappable: Logsource(UA_VERSION_7_1, "File.PipeConnected"),
    # Not yet used/mappable: Logsource(UA_VERSION_7_1, "File.RawAccessRead"),

    Logsource(UA_VERSION_7_1, "File.Create",
              conditions=[logsource_windows_file_event(), logsource_macos_file_event()],
              fields=ua_file_event_mapping),

    Logsource(UA_VERSION_7_1, "File.Delete",
              conditions=[logsource_windows_file_delete(), logsource_macos_file_delete()],
              fields=ua_file_event_mapping),

    Logsource(UA_VERSION_7_1, "File.Rename",
              conditions=[logsource_windows_file_rename(), logsource_macos_file_rename()],
              fields=ua_file_event_mapping),

    Logsource(UA_VERSION_7_1, "File.Write",
              conditions=[logsource_windows_file_change(), logsource_macos_file_change()],
              fields=ua_file_event_mapping),

    Logsource(UA_VERSION_7_1, "File.Read",
              conditions=[logsource_windows_file_access()],
              fields=ua_file_event_mapping)
]


def ua_create_mapping(uaVersion: Version, category: Logsource) -> List[ProcessingItem]:
    """
    Generate a list of processing items based on supported sigma keys for a given uberAgent version and category.

    This function produces a series of processing items that map sigma fields to their
    respective transformations based on the capabilities of the specified uberAgent version.
    It first establishes a mapping for unsupported fields, then generates individual
    transformations for each supported field, and finally applies a log source transformation.

    Parameters:
    - uaVersion (Version): The version of uberAgent for which the mapping is being created.
    - category (Category): The category of events for which the mapping is created.

    Returns:
    - List[ProcessingItem]: A list of processing items tailored to the given uberAgent version and category.
    """

    # Retrieve a list of sigma fields supported by the given version.
    keys: List[str] = uaVersion.reduce_mapping(category.fields)

    # Initialize the list of processing items.
    items: List[ProcessingItem] = [
        ProcessingItem(
            identifier=f"ua_{category.name}_unsupported",
            transformation=FieldDetectionItemFailureTransformation("Cannot transform field <{0}>."),
            rule_conditions=category.conditions,
            rule_condition_linking=any,
            field_name_conditions=[ExcludeFieldConditionLowercase(fields=keys)]
        )
    ]

    # All the event types here are supported.
    # Any other event type raises an error.
    items.append(
        ProcessingItem(
            identifier=f"ua_registry_unsupported",
            transformation=FieldDetectionItemFailureTransformation("Cannot transform registry field <{0}>."),
            rule_conditions=[
                RuleContainsDetectionItemCondition(field="EventType", value="CreateKey"),
                RuleContainsDetectionItemCondition(field="EventType", value="DeleteKey"),
                RuleContainsDetectionItemCondition(field="EventType", value="RenameKey"),
                RuleContainsDetectionItemCondition(field="EventType", value="DeleteValue"),
                RuleContainsDetectionItemCondition(field="EventType", value="SetValue")
            ],
            rule_condition_linking=any,
            rule_condition_negation=True,
            field_name_conditions=[IncludeFieldConditionLowercase(fields=["eventtype"])]
        )
    )

    # Create individual field transformations for each supported field.
    # Each field is handled separately to facilitate individual state transformations.
    for field in keys:
        transformed_field = str(category.fields[field])
        fm: Dict[str] = {field: transformed_field}

        # Field Transformation: Convert the sigma rule field to its corresponding TDE field name.
        items.append(
            ProcessingItem(
                identifier=f"ua_{category.name}_field_{field}",
                transformation=FieldMappingTransformationLowercase(fm),
                rule_conditions=category.conditions,
                rule_condition_linking=any,
                field_name_conditions=[
                    IncludeFieldConditionLowercase(fields=[field])
                ]
            )
        )

    # State Transformation: Mark the transformed fields in the pipeline state. This enables
    #                       the backend to retrieve the actual used fields and populate generic
    #                       properties at runtime.
    items.append(
        ProcessingItem(
            identifier=f"ls_fields_{category.name}_state",
            transformation=ReferencedFieldTransformation(),
            rule_conditions=category.conditions,
            rule_condition_linking=any
        )
    )

    # Log Source Transformation: Specify the log source category and platform.
    items.append(
        ProcessingItem(
            identifier=f"ls_{category.name}",
            transformation=ChangeLogsourceCategoryTransformation(category.name),
            rule_conditions=category.conditions,
            rule_condition_linking=any
        )
    )

    return items


def make_pipeline(uaVersion: Version):
    """
    Create a processing pipeline for a given uberAgent version.

    This function assembles a pipeline of processing items based on the
    supported event types for the given version of uberAgent. It also
    adds a final transformation to filter out unsupported log sources.

    Parameters:
    - uaVersion (Version): The version of uberAgent to build the pipeline for.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline.
    """

    # A list to store converted log sources that have been processed.
    converted_conditions: List[RuleProcessingItemAppliedCondition] = []

    # A list to hold all processing items for the version-specific pipeline.
    items: List[ProcessingItem] = []

    # Iterate over the defined categories for uberAgent.
    for category in ua_categories:

        # If the current version of uberAgent doesn't support the event type,
        # skip the rest of the loop.
        if not uaVersion.is_logsource_supported(category):
            continue

        # Generate and store mappings for each log source and its corresponding fields.
        for item in ua_create_mapping(uaVersion, category):
            items.append(item)

        # Add the name of the converted log source to the list of processed conditions.
        converted_conditions.append(RuleProcessingItemAppliedCondition(f"ls_{category.name}"))

    # Add transformation to have the version used available in backend.
    items.append(
        ProcessingItem(
            identifier=f"ua_version_state",
            transformation=SetStateTransformation("uaVersion", uaVersion._outputVersion),
            rule_conditions=[],
            rule_condition_linking=any
        )
    )

    # Add a transformation item to filter out any unsupported log sources.
    items.append(ProcessingItem(
        identifier="ua_log_source_not_supported",
        rule_condition_linking=any,
        transformation=RuleFailureTransformation("Rule type not yet supported."),
        rule_condition_negation=True,
        rule_conditions=converted_conditions
    ))

    # Return the assembled pipeline with its configured attributes.
    return ProcessingPipeline(
        name=f"uberAgent {uaVersion}",
        allowed_backends={"uberagent"},
        priority=20,
        items=items
    )


def uberagent() -> ProcessingPipeline:
    """
    Create a processing pipeline for the current release version of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for the current release version.
    """
    return make_pipeline(Version(UA_VERSION_CURRENT_RELEASE))


def uberagent600() -> ProcessingPipeline:
    """
    Create a processing pipeline for version 6.0 of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for version 6.0.
    """
    return make_pipeline(Version(UA_VERSION_6_0))


def uberagent610() -> ProcessingPipeline:
    """
    Create a processing pipeline for version 6.1 of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for version 6.1.
    """
    return make_pipeline(Version(UA_VERSION_6_1))


def uberagent620() -> ProcessingPipeline:
    """
    Create a processing pipeline for version 6.2 of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for version 6.2.
    """
    return make_pipeline(Version(UA_VERSION_6_2))


def uberagent700() -> ProcessingPipeline:
    """
    Create a processing pipeline for version 7.0 of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for version 7.0.
    """
    return make_pipeline(Version(UA_VERSION_7_0))


def uberagent710() -> ProcessingPipeline:
    """
    Create a processing pipeline for version 7.1 of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for version 7.1.
    """
    return make_pipeline(Version(UA_VERSION_7_1))


def uberagent720() -> ProcessingPipeline:
    """
    Create a processing pipeline for version 7.2 of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for version 7.2.
    """
    return make_pipeline(Version(UA_VERSION_7_2))


def uberagent730() -> ProcessingPipeline:
    """
    Create a processing pipeline for version 7.3 of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for version 7.3.
    """
    return make_pipeline(Version(UA_VERSION_7_3))


def uberagent740() -> ProcessingPipeline:
    """
    Create a processing pipeline for version 7.4 of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for version 7.4.
    """
    return make_pipeline(Version(UA_VERSION_7_4))


def uberagent750() -> ProcessingPipeline:
    """
    Create a processing pipeline for version 7.5 of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for version 7.5.
    """
    return make_pipeline(Version(UA_VERSION_7_5))


def uberagent_develop() -> ProcessingPipeline:
    """
    Create a processing pipeline for the development version of uberAgent.

    Returns:
    - ProcessingPipeline: The assembled processing pipeline for the development version.
    """
    return make_pipeline(Version(UA_VERSION_DEVELOP))
