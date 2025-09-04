"""
Copyright (C) 2022-2024 Stella Technologies (UK) Limited.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, RootModel

from stellanow_api_internals.core.helpers import StellaDateFormatter
from stellanow_api_internals.datatypes.core import (
    StellaBaseIdName,
    StellaBaseName,
    StellaExcludeNone,
    StellaFormattedDateTime,
)


class StellaBaseFieldType(BaseModel):
    value: str


class StellaPropagatedFrom(StellaBaseIdName):
    eventName: str


class StellaPropagatedFromList(RootModel):
    root: List[StellaPropagatedFrom]


class StellaPropagatedFromCreate(BaseModel):
    id: str


class StellaPropagatedFromCreateList(RootModel):
    root: List[StellaPropagatedFromCreate]


class StellaRouting(BaseModel):
    entity: bool
    workflow: bool
    dataLake: bool
    default: bool


class StellaProject(StellaBaseIdName, StellaFormattedDateTime):
    organizationId: str
    archived: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.archived:
            self.archived = self.format_date(self.archived)


class StellaProjectDetailed(StellaProject):
    description: Optional[str] = None


class StellaProjectCreate(StellaBaseName):
    description: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class StellaModelFieldType(StellaBaseFieldType):
    modelRef: Optional[str] = None


class StellaModelField(BaseModel):
    id: str
    name: str
    fieldType: StellaModelFieldType


class StellaModelFieldList(RootModel):
    root: List[StellaModelField]


class StellaModelCreate(StellaBaseName):
    description: Optional[str] = None
    fields: StellaModelFieldList

    model_config = ConfigDict(extra="ignore")


class StellaEntityId(BaseModel):
    id: str


class StellaEntityIdList(RootModel):
    root: List[StellaEntityId]


class StellaShortEntity(BaseModel):
    id: str
    name: str


class StellaShortEntityList(RootModel):
    root: List[StellaShortEntity]


class StellaShortEvent(BaseModel):
    id: str
    name: str


class StellaShortEventList(RootModel):
    root: List[StellaShortEvent]


class StellaBaseEntity(StellaShortEntity, StellaFormattedDateTime):
    projectId: str
    isActive: bool


class StellaEntity(StellaBaseEntity):
    eventsCount: int


class StellaEntityField(StellaBaseIdName):
    fieldType: StellaBaseFieldType
    propagatedFrom: Optional[List[StellaPropagatedFrom]] = None


class StellaEntityFieldList(RootModel):
    root: List[StellaEntityField]


class StellaEntityFieldCreate(StellaBaseIdName):
    fieldType: StellaBaseFieldType


class StellaEntityFieldCreateList(RootModel):
    root: List[StellaEntityFieldCreate]


class StellaEntityFieldUpdate(BaseModel):
    name: Optional[str] = None
    fieldType: Optional[StellaBaseFieldType] = None
    propagatedFrom: Optional[List[str]] = None
    action: str = "update"
    id: Optional[str] = None


class StellaEntityFieldUpdateList(RootModel):
    root: List[StellaEntityFieldUpdate]


class StellaEntityDetailed(StellaBaseEntity):
    description: Optional[str] = None
    fields: Optional[List[StellaEntityField]] = None
    events: Optional[List[StellaShortEvent]] = None


class StellaEntityDetailedList(RootModel):
    root: List[StellaEntityDetailed]


class StellaEntityCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[StellaEntityFieldCreateList] = None

    model_config = ConfigDict(extra="ignore")


class StellaEntityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[StellaEntityFieldUpdateList] = None

    model_config = ConfigDict(extra="ignore")


class StellaFieldType(StellaBaseFieldType):
    modelRef: Optional[str] = None


class StellaSubField(BaseModel):
    id: str
    name: str
    fieldType: StellaFieldType
    required: bool
    path: List[str]
    modelFieldId: Optional[str] = None


class StellaSubFieldCreate(BaseModel):
    modelFieldId: str
    required: bool


class StellaSubFieldList(RootModel):
    root: List[StellaSubField]


class StellaField(BaseModel):
    id: str
    name: str
    fieldType: StellaFieldType
    required: bool
    subfields: Optional[List[StellaSubField]] = None


class StellaFieldCreate(BaseModel):
    name: str
    fieldType: StellaFieldType
    required: bool
    subfields: Optional[List[StellaSubFieldCreate]] = None


class StellaFieldList(RootModel):
    root: List[StellaField]


class StellaEvent(StellaShortEvent, StellaFormattedDateTime):
    projectId: str
    isActive: bool
    routing: StellaRouting


class StellaEventDetailed(StellaEvent):
    description: Optional[str] = None
    fields: List[StellaField]
    entities: List[StellaShortEntity]


class StellaEventDetailedList(RootModel):
    root: List[StellaEventDetailed]


class StellaEventCreate(StellaShortEvent):
    description: Optional[str] = None
    routing: StellaRouting
    fields: List[StellaFieldCreate]
    entities: List[StellaShortEntity]


class StellaModel(StellaFormattedDateTime):
    id: str
    name: str


class StellaModelDetailed(StellaModel):
    description: Optional[str] = None
    fields: StellaModelFieldList


class StellaModelDetailedList(RootModel):
    root: List[StellaModelDetailed]


class StellaWorkflow(StellaBaseIdName, StellaFormattedDateTime):
    projectId: str
    tags: Optional[List[str]] = None
    publishedVersion: Optional[int] = None
    isActive: bool


class StellaWorkflowDetailed(StellaWorkflow):
    description: Optional[str] = None
    events: List[StellaShortEvent]
    entities: List[StellaShortEntity]
    activatedAt: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.activatedAt:
            self.activatedAt = self.format_date(self.activatedAt)


class StellaWorkflowDetailedList(RootModel):
    root: List[StellaWorkflowDetailed]


class StellaWorkflowCreate(StellaBaseName):
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    entities: StellaEntityIdList


class StellaWorkflowDAGPosition(BaseModel):
    x: int
    y: int


class StellaWorkflowDAGDisplayInfo(BaseModel):
    title: str
    description: Optional[str] = None


class DAGNodeEventTypeFieldDefinition(BaseModel):
    type: Optional[str] = None
    id: str
    fieldId: str
    multiValue: bool
    eventName: str
    fieldName: str


class DAGNodeEntityTypeFieldDefinition(BaseModel):
    type: str
    id: str
    fieldId: str
    multiValue: bool
    entityName: str
    fieldName: str


class DAGNodeExplicitTypeFieldDefinition(BaseModel):
    id: str
    type: str
    value: str
    multiValue: bool


class DAGNodeWorkflowVariableDefinition(BaseModel):
    id: str
    type: str
    variableName: str
    multiValue: bool


class DAGLimitedAggregationIntervalType(BaseModel):
    interval: str
    intervalStart: datetime
    intervalLength: int


class DAGNodeEventMetadataDefinition(BaseModel):
    id: str
    fieldName: str


class Condition(StellaExcludeNone):
    id: str
    fieldType: StellaBaseFieldType
    value: Optional[Union[bool, str, int, float, datetime, None]] = None
    left: Union[
        DAGNodeEventMetadataDefinition,
        DAGNodeEventTypeFieldDefinition,
        DAGNodeEntityTypeFieldDefinition,
        DAGNodeWorkflowVariableDefinition,
    ]
    right: Union[
        DAGNodeEventTypeFieldDefinition,
        DAGNodeEntityTypeFieldDefinition,
        DAGNodeExplicitTypeFieldDefinition,
        DAGNodeWorkflowVariableDefinition,
    ]
    condition: str
    negate: bool


class ConditionList(RootModel):
    root: List[Condition]


class DAGNodeWithCondition(StellaExcludeNone):
    id: str
    operator: str
    conditions: ConditionList


class DAGNodeEmpty(StellaExcludeNone):
    id: str


class DAGConditionNodeData(DAGNodeWithCondition):
    pass


class DAGFilterNodeData(DAGNodeWithCondition):
    pass


class DAGNotificationField(BaseModel):
    targetFieldName: str
    source: Union[
        DAGNodeEventTypeFieldDefinition,
        DAGNodeEntityTypeFieldDefinition,
        DAGNodeExplicitTypeFieldDefinition,
        DAGNodeWorkflowVariableDefinition,
    ]


class DAGNotificationFieldList(RootModel):
    root: List[DAGNotificationField]


class DAGNotificationNodeData(StellaExcludeNone):
    id: str
    channel: str
    fields: DAGNotificationFieldList


class DAGPropagateToField(StellaExcludeNone):
    id: Optional[str] = None
    source: Optional[
        Union[
            DAGNodeEventTypeFieldDefinition,
            DAGNodeEntityTypeFieldDefinition,
            DAGNodeExplicitTypeFieldDefinition,
            DAGNodeWorkflowVariableDefinition,
        ]
    ] = None
    targetFieldId: Optional[str] = None
    targetFieldName: Optional[str] = None


class DAGPropagateToFieldList(RootModel):
    root: List[DAGPropagateToField]


class DAGPropagateToEntityNodeData(StellaExcludeNone):
    id: str
    entityName: str
    fields: DAGPropagateToFieldList


class DAGClearEntityNodeData(DAGNodeEmpty):
    pass


class DAGPropagateToSourceNodeData(DAGNodeEmpty):
    pass


class DAGPropagateToFaasNodeData(StellaExcludeNone):
    id: str
    faasFunctionName: str


class DAGTerminationNodeData(DAGNodeEmpty):
    pass


class DAGTransformationFiled(StellaExcludeNone):
    function: str
    id: Optional[str] = None
    parameterName: Optional[str] = None
    functionParameters: Optional[List[str]] = None
    script: Optional[str] = None
    source: Optional[
        Union[
            DAGNodeEventTypeFieldDefinition,
            DAGNodeEntityTypeFieldDefinition,
            DAGNodeExplicitTypeFieldDefinition,
            DAGNodeWorkflowVariableDefinition,
        ]
    ] = None
    targetFieldId: Optional[str] = None
    targetFieldName: Optional[str] = None


class DAGTransformationFiledList(RootModel):
    root: List[DAGTransformationFiled]


class DAGTransformationNodeData(StellaExcludeNone):
    id: str
    eventName: Optional[str] = None
    fields: DAGTransformationFiledList


class DAGVariableOperationsFiled(BaseModel):
    id: Optional[str] = None
    function: str
    functionParameters: Optional[List[str]] = None
    parameterName: Optional[str] = None
    script: Optional[str] = None
    source: Optional[
        Union[
            DAGNodeEventTypeFieldDefinition,
            DAGNodeEntityTypeFieldDefinition,
            DAGNodeExplicitTypeFieldDefinition,
            DAGNodeWorkflowVariableDefinition,
        ]
    ] = None
    targetVariableId: Optional[str] = None
    targetVariableName: Optional[str] = None


class DAGVariableOperationsList(RootModel):
    root: Optional[List[DAGVariableOperationsFiled]] = []


class DAGAwaitNodeData(StellaExcludeNone):
    id: str
    eventName: str
    waitTime: int


class DAGAggregationNodeData(StellaExcludeNone):
    id: str
    aggregated: DAGNodeEventTypeFieldDefinition
    source: Union[DAGNodeEventTypeFieldDefinition, DAGNodeEntityTypeFieldDefinition, DAGNodeWorkflowVariableDefinition]
    interval: Optional[str] = None
    intervalStart: Optional[str] = None
    intervalLength: Optional[int] = None


class StellaWorkflowDAGEntityFieldDefinition(BaseModel):
    id: str
    fieldId: str
    multiValue: bool
    entityName: str
    fieldName: str


class StellaWorkflowDAGSource(BaseModel):
    EntityFieldDefinition: StellaWorkflowDAGEntityFieldDefinition


class DAGNodeConfig(StellaExcludeNone):
    id: str
    aggregationData: Optional[dict] = None
    clearEntityData: Optional[dict] = None
    conditionData: Optional[dict] = None
    filterData: Optional[dict] = None
    notificationData: Optional[dict] = None
    propagateToEntityData: Optional[dict] = None
    propagateToSourceData: Optional[dict] = None
    propagateToFaasData: Optional[dict] = None
    terminationData: Optional[dict] = None
    transformationData: Optional[dict] = None
    awaitData: Optional[dict] = None

    def to_dict(self):
        """Flatten the config and remove None values."""
        result = {"id": str(self.id)}
        for key, value in self.dict().items():
            if value is not None and key != "id":
                result.update(value)
        return result


class StellaWorkflowDAGData(StellaExcludeNone):
    displayInfo: StellaWorkflowDAGDisplayInfo
    config: Union[
        DAGAggregationNodeData,
        DAGClearEntityNodeData,
        DAGConditionNodeData,
        DAGFilterNodeData,
        DAGNotificationNodeData,
        DAGPropagateToEntityNodeData,
        DAGPropagateToSourceNodeData,
        DAGPropagateToFaasNodeData,
        DAGTerminationNodeData,
        DAGTransformationNodeData,
        DAGAwaitNodeData,
    ]
    isStateful: bool
    variableOperations: DAGVariableOperationsList


class StellaWorkflowDAGNodes(StellaExcludeNone):
    id: str
    type: str
    position: StellaWorkflowDAGPosition
    data: StellaWorkflowDAGData


class StellaWorkflowDAGNodesList(RootModel):
    root: List[StellaWorkflowDAGNodes]


class StellaWorkflowDAGEdge(BaseModel):
    id: str
    source: str
    target: str


class StellaWorkflowDAGEdgeList(RootModel):
    root: List[StellaWorkflowDAGEdge]


class StellaWorkflowDAGVariable(BaseModel):
    id: str
    variableName: str
    variableType: StellaBaseFieldType
    multiValue: bool = False


class StellaWorkflowDAGVariableList(RootModel):
    root: List[StellaWorkflowDAGVariable]


class StellaInterval(BaseModel):
    intervalType: str
    start: str
    length: float


class StellaWorkflowDAGWindow(BaseModel):
    interval: StellaInterval


class StellaWorkflowDAGStructure(StellaExcludeNone):
    nodes: StellaWorkflowDAGNodesList
    edges: StellaWorkflowDAGEdgeList
    variables: StellaWorkflowDAGVariableList
    # window: StellaWorkflowDAGWindow


class StellaWorkflowDAG(BaseModel, StellaDateFormatter):
    id: str
    workflowId: str
    commitMessage: Optional[str] = None
    versionNumber: int
    isLatest: bool
    isPublished: bool
    createdAt: str
    structure: StellaWorkflowDAGStructure

    def __init__(self, **data):
        super().__init__(**data)
        self.createdAt = self.format_date(self.createdAt)


class StellaWorkflowDAGList(RootModel):
    root: List[StellaWorkflowDAG]


class StellaWorkflowDagCreate(BaseModel):
    commitMessage: Optional[str] = None
    structure: StellaWorkflowDAGStructure
