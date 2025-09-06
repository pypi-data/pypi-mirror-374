from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from uuid import UUID

from serialite import AbstractSerializableMixin, abstract_serializable, field, serializable

from .ode_model import OdeModel


#######################################################
# Dosing
#######################################################
@abstract_serializable
@dataclass(frozen=True, kw_only=True)
class DosingScheduleState:
    dose_amount: str
    dose_duration: str | None
    is_rate: bool


@serializable
@dataclass(frozen=True, kw_only=True)
class SingleDoseScheduleState(DosingScheduleState):
    start_time: str


@serializable
@dataclass(frozen=True, kw_only=True)
class RegularDosesScheduleState(DosingScheduleState):
    start_time: str
    number_doses: str
    interval: str


@serializable
@dataclass(frozen=True, kw_only=True)
class CustomDoseScheduleState(DosingScheduleState):
    dose_times: str


@abstract_serializable
@dataclass(frozen=True, kw_only=True)
class DoseStateBase:
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class BolusDoseState(DoseStateBase):
    amount: str
    unit: str | None


@serializable
@dataclass(frozen=True, kw_only=True)
class GeneralBolusDoseState(DoseStateBase):
    amount: str


@serializable
@dataclass(frozen=True, kw_only=True)
class GeneralInfusionState(DoseStateBase):
    infusion_rate: str
    duration: str


#######################################################
# Units
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class BaseUnitState:
    symbol: str


@serializable
@dataclass(frozen=True, kw_only=True)
class PrefixState:
    symbol: str
    definition: float


@serializable
@dataclass(frozen=True, kw_only=True)
class NamedDerivedUnitState:
    symbol: str
    definition: str


@serializable
@dataclass(frozen=True, kw_only=True)
class SimulationBaseUnitsState:
    base_unit_id: UUID
    simulation_base_unit: str


#######################################################
# Indices
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class IndexIndexValuePairState:
    index_id: UUID
    index_value: int


@serializable
@dataclass(frozen=True, kw_only=True)
class IndexRelativeValueState:
    id: UUID
    offset: int | None = None
    offset_wraps: bool | None = None
    index_value: str | None = None
    index_value_variable: str | None = None


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyState:
    pairs: list[IndexIndexValuePairState]
    runtime_pairs: list[IndexRelativeValueState]


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyValuePairStateFloat:
    key_state: MultipleIndicesKeyState
    value: float


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyValueCollectionStateFloat:
    index_ids: list[UUID]
    pairs: list[MultipleIndicesKeyValuePairStateFloat]


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyValuePairStateUuid:
    key_state: MultipleIndicesKeyState
    value: UUID


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyValueCollectionStateUuid:
    index_ids: list[UUID]
    pairs: list[MultipleIndicesKeyValuePairStateUuid]


@serializable
@dataclass(frozen=True, kw_only=True)
class IndexCreatorIndexValuePairState:
    index_creator_id: UUID
    index_value: int


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyIndexCreatorsState:
    pairs: list[IndexCreatorIndexValuePairState]
    runtime_pairs: list[IndexRelativeValueState]


#######################################################
# Assess metadata
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class AlternativeInputUnitMetadataState:
    # c.f. UnitOption
    unit: str | None
    transform: str
    default_lower_limit: float | None
    default_upper_limit: float | None


@serializable
@dataclass(frozen=True, kw_only=True)
class DiscreteValueMetadataState:
    # c.f. DropDown
    label: str
    value: int | float


@serializable
@dataclass(frozen=True, kw_only=True)
class QuantityInputMetadataState:
    name: str
    description: str
    symbol: str
    default_value: int | float
    is_global: bool
    default_unit: str | None
    alternative_units: list[AlternativeInputUnitMetadataState]
    discrete_values: list[DiscreteValueMetadataState]


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyValuePairStateOfQuantityInputMetadataState:
    key_state: MultipleIndicesKeyState
    value: QuantityInputMetadataState


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyValueCollectionStateOfQuantityInputMetadataState:
    index_ids: list[UUID]
    pairs: list[MultipleIndicesKeyValuePairStateOfQuantityInputMetadataState]


# Plot metadata


@serializable
@dataclass(frozen=True, kw_only=True)
class AlternativePlotUnitMetadataState:
    # c.f. OutputPlotUnit
    unit: str  # Not on OutputPlotUnit, probably because units on OutputPlotOption is a dict
    transform: str


@serializable
@dataclass(frozen=True, kw_only=True)
class QuantityPlotMetadataState:
    title: str
    unit: str
    description: str | None = None
    alternative_units: list[AlternativePlotUnitMetadataState]
    plotted_by_default: bool
    log_scale: bool


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyValuePairStateOfQuantityPlotMetadataState:
    key_state: MultipleIndicesKeyState
    value: QuantityPlotMetadataState


@serializable
@dataclass(frozen=True, kw_only=True)
class MultipleIndicesKeyValueCollectionStateOfQuantityPlotMetadataState:
    index_ids: list[UUID]
    pairs: list[MultipleIndicesKeyValuePairStateOfQuantityPlotMetadataState]


@serializable
@dataclass(frozen=True, kw_only=True)
class ModifierOption:
    name: str
    value: str


@serializable
@dataclass(frozen=True, kw_only=True)
class Modifier:
    id: str
    name: str
    options: list[ModifierOption]
    description: str | None = None


@serializable
@dataclass(frozen=True, kw_only=True)
class Reducer:
    id: str
    name: str
    expression_template: str
    description: str | None = None


@serializable
@dataclass(frozen=True, kw_only=True)
class Criterion:
    id: str
    time_value_template: str  # JavaScript template literal that, upon substitution is an Expression
    modifiers: list[Modifier]
    reducers: list[Reducer]
    name: str
    default_threshold: float
    value_unit: str
    value_min: float
    value_max: float
    value_scale: str
    description: str


@serializable
@dataclass(frozen=True, kw_only=True)
class AssessOutputTime:
    name: str
    expression: str


@serializable
@dataclass(frozen=True, kw_only=True)
class QspDesignerModelMetadata:
    # TODO: Consider removing most of these defaults
    id: str = "TODO"
    pack: str = ""
    name: str = ""
    headline: str = ""
    description: str = ""
    thumbnail: str = ""
    diagram: str = ""
    pharmacology_diagram: str | None = None
    documentation: str = ""
    criteria: list[Criterion] = field(default_factory=list)
    default_criterion: str = "TODO"
    default_scan_parameter_1: str = "TODO"
    default_scan_parameter_2: str = "TODO"
    default_n_1: int = 51
    default_n_2: int = 51
    default_scale_1: Literal["linear", "log"] = "log"
    default_scale_2: Literal["linear", "log"] = "log"
    default_route: str = "TODO"
    default_linear_solver: Literal["KLU", "SPGMR"] = "KLU"
    default_optima_method: Literal["brentq", "cubic_spline"] = "brentq"
    default_abstol: float = 1e-11  # These are the QSP Designer defaults
    default_reltol: float = 1e-8
    default_maxord: Literal[1, 2, 3, 4, 5] = 5
    output_interval: str = "1"
    output_starts: dict[str, AssessOutputTime] = field(default_factory=dict)
    output_stops: dict[str, AssessOutputTime] = field(default_factory=dict)
    output_n: int = 101  # This n is the number of timepoints in the replicated LinspaceTimes
    default_output_start: str = "TODO"
    default_output_stop: str = "TODO"
    plot_time_unit: str = "d"
    plot_time_transform: float = 86400.0
    tags: list[str] = field(default_factory=list)


#######################################################
# Edge end types
#######################################################
@abstract_serializable
@dataclass(frozen=True, kw_only=True)
class EdgeEndState:
    node_id: UUID


@serializable
@dataclass(frozen=True, kw_only=True)
class NonSpecificEdgeEndState(EdgeEndState):
    each_updated_by_all: bool  # TODO: what does this mean?


@serializable
@dataclass(frozen=True, kw_only=True)
class LegacySpecificEdgeEndState(EdgeEndState):
    key: MultipleIndicesKeyIndexCreatorsState


@serializable
@dataclass(frozen=True, kw_only=True)
class SpecificEdgeEndState(EdgeEndState):
    component: str  # Currently assumed to be an expanded quantity name


#######################################################
# Node traits
#######################################################
@dataclass(frozen=True, kw_only=True)
class Deactivatable:
    is_deactivated: bool


@dataclass(frozen=True, kw_only=True)
class Exposable:
    is_exposed: bool


@dataclass(frozen=True, kw_only=True)
class Subgraphable:
    subgraph_definition_id: UUID


#######################################################
# Abstract graph entity type
#######################################################
@dataclass(frozen=True, kw_only=True)
class GraphEntityState(AbstractSerializableMixin):
    id: UUID


#######################################################
# Abstract node types
#######################################################
@dataclass(frozen=True, kw_only=True)
class LocalNodeState(GraphEntityState):
    name: str


@dataclass(frozen=True, kw_only=True)
class LocalQuantityState(LocalNodeState, Subgraphable, Exposable):
    values: MultipleIndicesKeyValueCollectionStateFloat
    unit: str | None
    attached_index_node_ids: list[UUID]
    is_output: bool
    # TODO: None defaults here a temporary fix until the C# adds these fields (or just doesn't deserialize it)
    input_metadata: MultipleIndicesKeyValueCollectionStateOfQuantityInputMetadataState | None = None
    plot_metadata: MultipleIndicesKeyValueCollectionStateOfQuantityPlotMetadataState | None = None


#######################################################
# Node types
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class LocalAssignmentState(LocalNodeState, Subgraphable, Deactivatable):
    is_initial_only: bool
    expression: str | None  # Can be None if is_deactivated is True
    condition: str | None = None
    alternative_expression: str | None = None


@serializable
@dataclass(frozen=True, kw_only=True)
class DosingEffectState:
    type: Literal["Dose", "Jump"]
    target: str
    expression: str


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalDosingPlanState(LocalNodeState, Subgraphable, Exposable, Deactivatable):
    dosing_schedule_state: DosingScheduleState
    effects: list[DosingEffectState]


@serializable
@dataclass(frozen=True, kw_only=True)
class EventEffectState:
    target: str | None
    expression: str


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalEventState(LocalNodeState, Subgraphable, Exposable, Deactivatable):
    condition: str
    effects: list[EventEffectState]


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalIndexNodeState(LocalNodeState, Subgraphable):
    index_values: list[str]
    index_id: UUID
    priority: int


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalRuntimeIndexNodeState(LocalNodeState, Subgraphable):
    range_expression: str
    index_id: UUID
    priority: int


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalReactionState(LocalNodeState, Subgraphable, Exposable, Deactivatable):
    rate: str | None  # Can be None if is_deactivated is True
    reverse_rate: str | None
    index_mapping: str | None


#######################################################
# Quantity node types
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class LocalCompartmentState(LocalQuantityState):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalParameterState(LocalQuantityState):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalSpeciesState(LocalQuantityState):
    owner_id: UUID
    is_concentration: bool = False


#######################################################
# Abstract edge types
#######################################################
@dataclass(frozen=True, kw_only=True)
class EdgeState(GraphEntityState):
    pass


#######################################################
# Edge types
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class LocalAssignmentEdgeState(EdgeState):
    direction: Literal["FromAssignment", "ToAssignment", "ToAssignmentInhibitor"]
    quantity_end: EdgeEndState
    assignment_end: EdgeEndState


@serializable
@dataclass(frozen=True, kw_only=True)
class DosingPlanEdgeState(EdgeState):
    quantity_end: EdgeEndState
    dosing_plan_end: EdgeEndState


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalEventEdgeState(EdgeState):
    edge_type: Literal["Growth", "Product", "Modifier", "Inhibitor"]
    quantity_end: EdgeEndState
    event_end: EdgeEndState


@serializable
@dataclass(frozen=True, kw_only=True)
class ReactionParameterEdgeState(EdgeState):
    reaction_end: EdgeEndState
    parameter_end: EdgeEndState


@serializable
@dataclass(frozen=True, kw_only=True)
class ReactionSpeciesEdgeState(EdgeState):
    stoichiometry: str
    edge_type: Literal["Substrate", "Product", "Modifier", "Growth", "Inhibitor"]
    reaction_end: EdgeEndState
    species_end: EdgeEndState


#######################################################
# Meta edge types
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class MetaEdgeState(GraphEntityState):
    from_id: UUID
    to_id: UUID


@serializable
@dataclass(frozen=True, kw_only=True)
class WeakCloningMetaEdgeState(MetaEdgeState):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalNonEventBasedAssignerState(LocalNodeState):
    is_initial_only: bool


@serializable
@dataclass(frozen=True, kw_only=True)
class MultiDimensionalConstraintState(LocalNonEventBasedAssignerState, Deactivatable, Exposable, Subgraphable):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalConstraintEdgeState(EdgeState):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalNodeSubgraphProxyState(LocalNodeState, Subgraphable):
    subgraph_instance_id: UUID
    referenced_node_name: str | None


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalReactionSubgraphProxyState(LocalNodeSubgraphProxyState, Exposable, Deactivatable):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalStaticIndexNodeSubgraphProxyState(LocalNodeSubgraphProxyState):
    pass


#######################################################
# Inline functions
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class LocalInlineFunctionState(LocalNodeState, Subgraphable):
    name: str
    arguments: list[str]
    expression: str


#######################################################
# Subgraphs
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class LocalSubgraphDefinitionState(GraphEntityState, Exposable):
    name: str


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalSubgraphInstanceState(GraphEntityState, Subgraphable):  # Technically Subgraphable, but not supported here
    name: str
    definition_node_name: str
    categories_are_prefixed: bool


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalQuantitySubgraphProxyState(LocalNodeSubgraphProxyState):  # Technically Subgraphable, but not supported here
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalCompartmentSubgraphProxyState(LocalQuantitySubgraphProxyState):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalParameterSubgraphProxyState(LocalQuantitySubgraphProxyState):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalSpeciesSubgraphProxyState(LocalQuantitySubgraphProxyState):
    pass


#######################################################
# Imports
#######################################################
@serializable
@dataclass(frozen=True, kw_only=True)
class WorkspaceImportState(GraphEntityState):
    name: str
    job_id: str
    import_type: Literal["Private", "Global"]


@dataclass(frozen=True, kw_only=True)
class LocalQuantityImportState(LocalNodeState):
    workspace_import_name: str
    imported_node_name: str


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalCompartmentImportState(LocalQuantityImportState):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalParameterImportState(LocalQuantityImportState):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class LocalSpeciesImportState(LocalQuantityImportState):
    pass


@serializable
@dataclass(frozen=True, kw_only=True)
class QspDesignerModel(OdeModel):
    base_unit_states: list[BaseUnitState]
    prefix_states: list[PrefixState]
    named_derived_unit_states: list[NamedDerivedUnitState]
    simulation_base_units: list[SimulationBaseUnitsState]
    graph_entity_states: list[GraphEntityState]
    time_unit: str | None
    metadata: QspDesignerModelMetadata = field(default_factory=QspDesignerModelMetadata)
    ignore_units: bool = False
    is_legacy: bool = False


@serializable
@dataclass(frozen=True, kw_only=True)
class QspDesignerModelFromBytes:
    base64_content: str
    imports: dict[Path, str] = field(default_factory=dict)


# abstract_serializable only works on direct subclasses
# Recurse over subclasses to find them all
def get_all_subclasses(cls: type) -> dict[str, type]:
    subclasses = {}
    for subclass in cls.__subclasses__():
        if hasattr(subclass, "__fields_serializer__"):
            subclasses[subclass.__name__] = subclass
        subclasses.update(get_all_subclasses(subclass))
    return subclasses


GraphEntityState.__subclass_serializers__ = get_all_subclasses(GraphEntityState)
