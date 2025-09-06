from typing import TypedDict, Callable, Coroutine
from graphql_generate.support import GqlContext, GqlWebSocketContext, GqlSubscriptionData, GqlSubscriptionErrors, tracer

from queries_lib.schema import String, Int, Float, Boolean, ID, BigInt, BigFloat, Cursor, Datetime, JwtToken, Base64EncodedBinary, JSON, LdataNodeType, LdataNodeAccessLevel, LdataNodesOrderBy, PermLevel, LdataDataCreator, TeamRole, PodBackupStatus, TaskStatus, ExecutionStatus, ExecutionNodeStatus, DatasetDownloadStatus, LdataEventType, LdataWfExStatus, DatasetMetadataType, LdataTagType, LdataTreeEdgesOrderBy, LdataObjectMetasOrderBy, AccountInfosOrderBy, DatasetDownloadInfosOrderBy, DatasetPurchasesOrderBy, DatasetInfoTagsOrderBy, CurationInferenceModel, CurationInferenceEventsOrderBy, LdataNodeEventsOrderBy, WorkflowGraphNodeType, GpuType, WorkflowGraphNodesOrderBy, WorkflowGraphBranchType, WorkflowGraphBranchesOrderBy, TaskExecutionStatus, ContainerInfosOrderBy, TaskExecutionInfosOrderBy, ExecutionGraphNodesOrderBy, WorkflowGraphEdgesOrderBy, WorkflowSubscriptionsOrderBy, ExecutionInfosOrderBy, LpInfosOrderBy, WorkflowTagsOrderBy, AutomationVersionsOrderBy, AutomationRunLdataEventsOrderBy, AutomationTriggerLdataEventsOrderBy, AutomationRunIntervalEventsOrderBy, AutomationTriggerIntervalEventsOrderBy, WorkflowInfosOrderBy, WorkflowFamilySubscriptionsOrderBy, OrgInfosOrderBy, AccountCreditLimitVerifiedEmailsOrderBy, TeamInvitesOrderBy, TeamMembersOrderBy, PackageRedemptionLdataNodeMappingsOrderBy, PackageRedemptionsOrderBy, LatchDevelopStagingImagesOrderBy, TeamInfosOrderBy, VerifiedEmailsOrderBy, WorkspaceSubscriptionInfosOrderBy, OrgMembersOrderBy, OrgInvitesOrderBy, PackageInfosOrderBy, OrgSupportWindowsOrderBy, OrgSubscriptionsOrderBy, PackageVersionInfosOrderBy, PackageCodesOrderBy, PackageLdataNodesOrderBy, PackageWorkflowFamiliesOrderBy, PodStatus, InstanceSize, PodInfosOrderBy, PodTemplateVersionsOrderBy, PodTemplateSubscriptionsOrderBy, LdataPodTemplateSettingsOrderBy, PackagePodTemplatesOrderBy, PodBackupsOrderBy, PlotNotebookTemplateVersionsOrderBy, PodBackupRequestsOrderBy, PodDeploymentInfoTaskDataOrderBy, PodSessionEventsOrderBy, PodSessionsOrderBy, EbsSessionsOrderBy, TaskEventsOrderBy, TaskStorageDevicesOrderBy, TaskDataOrderBy, TaskLoadBalancersOrderBy, TaskIpsOrderBy, NfsSharesOrderBy, TaskNodeMountsOrderBy, NfProcessEdgesOrderBy, NfTaskInfosOrderBy, NfTaskExecutionInfosOrderBy, NfForchTaskExecutionInfosOrderBy, NfForchRuntimesOrderBy, LatchDevelopSessionInfosOrderBy, PodTasksOrderBy, CatalogEventType, CatalogEventsOrderBy, CatalogSampleColumnDataOrderBy, CatalogExperimentsOrderBy, BenchlingImportsOrderBy, CatalogExperimentColumnDefinitionsOrderBy, CatalogSamplesOrderBy, CatalogExperimentViewsOrderBy, PlotInfosOrderBy, PlotDataSourceInfosOrderBy, PackageCatalogExperimentSnapshotsOrderBy, PlotCellValueViewersOrderBy, PlotTransformInfosOrderBy, PlotTransformSourceCodesOrderBy, PlotTransformExecutionsOrderBy, PlotNotebookCheckpointInfosOrderBy, PlotNotebookCrdtUpdatesOrderBy, PlotNotebookRestoreEventsOrderBy, PlotNotebookTemplateFamilyVersionAssociationsOrderBy, PlotNotebookTemplateSubscriptionsOrderBy, PackagePlotTemplateFamiliesOrderBy, PackageInstallationsOrderBy, TaskExecutionMessagesOrderBy, SnakemakeExecutionInfosOrderBy, NfProcessNodesOrderBy, SmJobExecutionInfosOrderBy, SmJobEdgesOrderBy, SmJobInfosOrderBy, NotificationStatus, ExecutionBatchMembersOrderBy, NotificationType, ExecutionNotificationInfosOrderBy, IgvGenomesOrderBy, LdataWfExesOrderBy, LdataLinkDataOrderBy, LdataShareInvitesOrderBy, LdataSharePermissionsOrderBy, LdataNodeTagsOrderBy, IgvTracksOrderBy, PlotNotebookInfosOrderBy, TaskInfosOrderBy, ExecutionCreatorsOrderBy, LdataS3MountAccessProvensOrderBy, LdataS3MountConfiguratorRolesOrderBy, CreditsOrderBy, WorkflowFamilyInfosOrderBy, LdataShareLinkNodesOrderBy, PublicKeyInfosOrderBy, BasespaceApiTokensOrderBy, WorkflowPinsOrderBy, AccountAccessPoliciesOrderBy, CatalogProjectsOrderBy, AccountSecretsOrderBy, PodTemplatesOrderBy, ExecutionBatchInfosOrderBy, PodGroupInfosOrderBy, AutomationInfosOrderBy, PlotLayoutInfosOrderBy, BenchlingImportRunsOrderBy, NextflowTaskType, NextflowNodeInfosOrderBy, LdataGoogleVerifiedBucketsOrderBy, LdataGoogleVerifiedProjectsOrderBy, PlotNotebookTemplateFamiliesOrderBy, WorkflowPersonalizationsOrderBy, AccountCreditLimitsOrderBy, BenchlingApiTokensOrderBy, CatalogExperimentPermissionOverridesOrderBy, DatasetAgreementsOrderBy, DatasetInfosOrderBy, ExecutionRefLpInfosOrderBy, GithubPersonalAccessTokensOrderBy, IncidentInfosOrderBy, IntegrationsGoogleAuthsOrderBy, LdataNodeEventChildRemovesOrderBy, LdataNodeEventIngressesOrderBy, LdataNodeEventMovesOrderBy, LdataNodeEventRemovesOrderBy, LdataS3MountRolesOrderBy, NfExecutionInfosOrderBy, NfForchWorkflowInfosOrderBy, NfLustreInfosOrderBy, OrgInfoPublicDataTypesOrderBy, OrgOwnedWorkspaceSecurityOverridesOrderBy, OrgSecurityOverridesOrderBy, OrgWorkspacesSecurityPoliciesOrderBy, PackageRedemptionSharedAnalyticsTypesOrderBy, PlotTransformTemplateInfosOrderBy, PlotWhitelistsOrderBy, PodDeploymentInfosOrderBy, PvcExecutionUsagesOrderBy, PvcInfosOrderBy, SharingReceiverSharedDataTypesOrderBy, StripeSubscriptionInfosOrderBy, TaskExecutionRuntimeInfosOrderBy, UserInfosOrderBy, UserInfoSharedDataTypesOrderBy, WhitelistForchesOrderBy, WorkflowFamilyInfoOldsOrderBy, WorkflowGraphSubWfsOrderBy, WorkflowPreviewsOrderBy, WorkspaceInviteLinksOrderBy, WorkspaceRoleSettingsOrderBy, WorkspaceSecurityOverridesOrderBy, BillingGroupsOrderBy, IpEventAttachedDataOrderBy, IpEventsOrderBy, IpsOrderBy, LoadBalancerEventsOrderBy, NodeEventProvisionResultDataOrderBy, NodeEventProvisionWriteAheadDataOrderBy, NodeEventsOrderBy, ForchNodesOrderBy, ResourceGroupsOrderBy, SecretsOrderBy, StorageDeviceEventAttachedDataOrderBy, StorageDeviceEventResizeRequestedDataOrderBy, StorageDeviceEventsOrderBy, StorageDevicesOrderBy, TaskDatumSpecsOrderBy, TaskEventContainerCreatedDataOrderBy, TaskEventContainerExitedDataOrderBy, TaskEventNodeAssignedDataOrderBy, TaskFirewallEntriesOrderBy, TasksOrderBy, AutomationTriggerType

from opentelemetry.trace import Span
from latch_o11y.o11y import trace_function_with_span, dict_to_attrs

# >>> NodeInfo
class NodeInfoFragment_LdataObjectMeta(TypedDict):
    """
    Part of NodeInfoFragment_LdataObjectMeta
    """
    contentSize: str | None
    modifyTime: str | None
    accessTime: str | None
    birthTime: str | None

class NodeInfoFragment(TypedDict):
    """
    Part of NodeInfoFragment
    """
    id: str
    name: str
    type: LdataNodeType
    removed: bool | None
    pending: bool | None
    ldataObjectMeta: NodeInfoFragment_LdataObjectMeta | None
    """
    Reads a single `LdataObjectMeta` that is related to this `LdataNode`.
    """

query_str_node_info_fragment = "fragment NodeInfo on LdataNode{id name type removed pending ldataObjectMeta{contentSize modifyTime accessTime birthTime}}"

# >>> LDataSubtreeByPath
class LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges_Nodes_Child_FinalLinkTarget(NodeInfoFragment, TypedDict):
    """
    Part of LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges_Nodes_Child_FinalLinkTarget
    """
    ...

class LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges_Nodes_Child(NodeInfoFragment, TypedDict):
    """
    Part of LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges_Nodes_Child
    """
    finalLinkTarget: LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges_Nodes_Child_FinalLinkTarget | None

class LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges_Nodes(TypedDict):
    """
    Part of LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges_Nodes
    """
    child: LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges_Nodes_Child
    """
    Reads a single `LdataNode` that is related to this `LdataTreeEdge`.
    """

class LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges(TypedDict):
    """
    Part of LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges
    """
    nodes: list[LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges_Nodes]
    """
    A list of `LdataTreeEdge` objects.
    """

class LDataSubtreeByPathQueryResult_LdataResolvePathData(TypedDict):
    """
    Part of LDataSubtreeByPathQueryResult_LdataResolvePathData
    """
    id: str
    path: str | None
    removed: bool | None
    childLdataTreeEdges: LDataSubtreeByPathQueryResult_LdataResolvePathData_ChildLdataTreeEdges
    """
    Reads and enables pagination through a set of `LdataTreeEdge`.
    """

class LDataSubtreeByPathQueryResult(TypedDict):
    """
    Part of LDataSubtreeByPathQueryResult
    """
    ldataResolvePathData: LDataSubtreeByPathQueryResult_LdataResolvePathData | None

class LDataSubtreeByPathQueryVariables(TypedDict):
    path: str

query_str_l_data_subtree_by_path_query = query_str_node_info_fragment + "query LDataSubtreeByPath($path:String!){ldataResolvePathData(argPath:$path){id path removed childLdataTreeEdges{nodes{child{...NodeInfo finalLinkTarget{...NodeInfo}}}}}}"

@trace_function_with_span(tracer)
async def query_l_data_subtree_by_path_query(span: Span, ctx: GqlContext, variables: LDataSubtreeByPathQueryVariables):
    span.set_attributes({**dict_to_attrs(variables, "variables")})
    return await ctx.query(query_str=query_str_l_data_subtree_by_path_query, variables=variables, result_type=LDataSubtreeByPathQueryResult)

# >>> Unlink
class UnlinkMutationResult_LdataUnlink(TypedDict):
    """
    Part of UnlinkMutationResult_LdataUnlink
    """
    clientMutationId: str | None
    """
    The exact same `clientMutationId` that was provided in the mutation input,
    unchanged and unused. May be used by a client to track mutations.
    """

class UnlinkMutationResult(TypedDict):
    """
    Part of UnlinkMutationResult
    """
    ldataUnlink: UnlinkMutationResult_LdataUnlink | None

class UnlinkMutationVariables(TypedDict):
    path: str

query_str_unlink_mutation = "mutation Unlink($path:String!){ldataUnlink(input:{argPath: $path}){clientMutationId}}"

@trace_function_with_span(tracer)
async def query_unlink_mutation(span: Span, ctx: GqlContext, variables: UnlinkMutationVariables):
    span.set_attributes({**dict_to_attrs(variables, "variables")})
    return await ctx.query(query_str=query_str_unlink_mutation, variables=variables, result_type=UnlinkMutationResult)

# >>> Mkdir
class MkdirMutationResult_LdataMkdirNoParents(TypedDict):
    """
    Part of MkdirMutationResult_LdataMkdirNoParents
    """
    clientMutationId: str | None
    """
    The exact same `clientMutationId` that was provided in the mutation input,
    unchanged and unused. May be used by a client to track mutations.
    """

class MkdirMutationResult(TypedDict):
    """
    Part of MkdirMutationResult
    """
    ldataMkdirNoParents: MkdirMutationResult_LdataMkdirNoParents | None

class MkdirMutationVariables(TypedDict):
    path: str

query_str_mkdir_mutation = "mutation Mkdir($path:String!){ldataMkdirNoParents(input:{argPath: $path}){clientMutationId}}"

@trace_function_with_span(tracer)
async def query_mkdir_mutation(span: Span, ctx: GqlContext, variables: MkdirMutationVariables):
    span.set_attributes({**dict_to_attrs(variables, "variables")})
    return await ctx.query(query_str=query_str_mkdir_mutation, variables=variables, result_type=MkdirMutationResult)

# >>> Rmdir
class RmdirMutationResult_LdataRmdir(TypedDict):
    """
    Part of RmdirMutationResult_LdataRmdir
    """
    clientMutationId: str | None
    """
    The exact same `clientMutationId` that was provided in the mutation input,
    unchanged and unused. May be used by a client to track mutations.
    """

class RmdirMutationResult(TypedDict):
    """
    Part of RmdirMutationResult
    """
    ldataRmdir: RmdirMutationResult_LdataRmdir | None

class RmdirMutationVariables(TypedDict):
    path: str

query_str_rmdir_mutation = "mutation Rmdir($path:String!){ldataRmdir(input:{argPath: $path}){clientMutationId}}"

@trace_function_with_span(tracer)
async def query_rmdir_mutation(span: Span, ctx: GqlContext, variables: RmdirMutationVariables):
    span.set_attributes({**dict_to_attrs(variables, "variables")})
    return await ctx.query(query_str=query_str_rmdir_mutation, variables=variables, result_type=RmdirMutationResult)

# >>> LDataRenameFuse
class LDataRenameFuseMutationResult_LdataRenameFuse(TypedDict):
    """
    Part of LDataRenameFuseMutationResult_LdataRenameFuse
    """
    clientMutationId: str | None
    """
    The exact same `clientMutationId` that was provided in the mutation input,
    unchanged and unused. May be used by a client to track mutations.
    """

class LDataRenameFuseMutationResult(TypedDict):
    """
    Part of LDataRenameFuseMutationResult
    """
    ldataRenameFuse: LDataRenameFuseMutationResult_LdataRenameFuse | None

class LDataRenameFuseMutationVariables(TypedDict):
    srcPath: str
    destPath: str

query_str_l_data_rename_fuse_mutation = "mutation LDataRenameFuse($srcPath:String!,$destPath:String!){ldataRenameFuse(input:{argSrcPath: $srcPath,argDestPath: $destPath}){clientMutationId}}"

@trace_function_with_span(tracer)
async def query_l_data_rename_fuse_mutation(span: Span, ctx: GqlContext, variables: LDataRenameFuseMutationVariables):
    span.set_attributes({**dict_to_attrs(variables, "variables")})
    return await ctx.query(query_str=query_str_l_data_rename_fuse_mutation, variables=variables, result_type=LDataRenameFuseMutationResult)

# >>> BasicInfo
class BasicInfoQueryResult_AccountInfoCurrent(TypedDict):
    """
    Part of BasicInfoQueryResult_AccountInfoCurrent
    """
    id: str

class BasicInfoQueryResult(TypedDict):
    """
    Part of BasicInfoQueryResult
    """
    accountInfoCurrent: BasicInfoQueryResult_AccountInfoCurrent | None

query_str_basic_info_query = "query BasicInfo{accountInfoCurrent{id}}"

@trace_function_with_span(tracer)
async def query_basic_info_query(span: Span, ctx: GqlContext):
    return await ctx.query(query_str=query_str_basic_info_query, result_type=BasicInfoQueryResult)

# >>> LatchData
class LatchDataSubscriptionResult_ConsoleLdataNode(TypedDict):
    """
    Part of LatchDataSubscriptionResult_ConsoleLdataNode
    """
    table: str
    rowIds: list[str] | None

class LatchDataSubscriptionResult(TypedDict):
    """
    Part of LatchDataSubscriptionResult
    """
    consoleLdataNode: LatchDataSubscriptionResult_ConsoleLdataNode | None

class LatchDataSubscriptionVariables(TypedDict):
    workspaceId: str

query_str_latch_data_subscription = "subscription LatchData($workspaceId:String!){consoleLdataNode(workspaceId:$workspaceId){table rowIds}}"

@trace_function_with_span(tracer)
async def subscribe_latch_data_subscription(span: Span, ctx: GqlWebSocketContext, *, callback: Callable[[GqlSubscriptionData[LatchDataSubscriptionResult] | GqlSubscriptionErrors], Coroutine[object, object, object]], operation_id: str, variables: LatchDataSubscriptionVariables):
    span.set_attributes({"operation_id": operation_id, "callback": callback.__name__, **dict_to_attrs(variables, "variables")})
    return await ctx.subscribe(query_str=query_str_latch_data_subscription, operation_id=operation_id, callback=callback, variables=variables, result_type=LatchDataSubscriptionResult)

