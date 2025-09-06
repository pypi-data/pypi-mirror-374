__all__ = [
    "OdeProposalPopulationSample",
    "OdeProposalPopulationSampleMethod",
    "TruncatedSSE",
]

from dataclasses import dataclass

from serialite import abstract_serializable, serializable

from .ode_optimization_configuration import OdeOptimizationConfiguration
from .scenario import Scenario


@abstract_serializable
class OdeProposalPopulationSampleMethod:
    pass


@serializable
@dataclass(frozen=True)
class TruncatedSSE(OdeProposalPopulationSampleMethod):
    sample_n: int = 1000
    optimization_configuration: OdeOptimizationConfiguration = OdeOptimizationConfiguration(min_objective=0.0)


@serializable
@dataclass(frozen=True)
class OdeProposalPopulationSample:
    seed: int
    method: OdeProposalPopulationSampleMethod
    scenario: Scenario
    active_parameters: set[str] | None = None
