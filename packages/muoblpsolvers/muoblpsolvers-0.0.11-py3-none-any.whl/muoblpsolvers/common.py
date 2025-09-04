from collections import defaultdict

from muoblp.model.multi_objective_lp import MultiObjectiveLpProblem
from pulp import LpConstraintLE, LpConstraint

from muoblpsolvers.types import (
    CandidateId,
    Cost,
    TotalBudget,
    Utility,
    VoterId,
)


def get_total_budget_constraint(lp: MultiObjectiveLpProblem) -> LpConstraint:
    all_candidates: set[CandidateId] = set(
        [
            variable.name
            for variable in lp.variables()
            if variable.name != "__dummy"
        ]
    )

    pb_constraints = []
    for constraint in lp.constraints.values():
        candidates = set([variable.name for variable, _ in constraint.items()])
        if candidates == all_candidates and constraint.sense == LpConstraintLE:
            pb_constraints.append(constraint)

    if len(pb_constraints) == 0:
        raise Exception("Problem does not have PB constraint")
    if len(pb_constraints) > 1:
        pass  # TODO - fix duplicated constraints for single district and city wide
        # raise Exception("Problem has too many PB constraint")
    return pb_constraints[0]


def prepare_mes_parameters(
    lp: MultiObjectiveLpProblem,
) -> tuple[
    list[CandidateId],
    dict[CandidateId, Cost],
    list[VoterId],
    dict[CandidateId, list[tuple[VoterId, Utility]]],
    dict[CandidateId, Utility],
    TotalBudget,
]:
    projects: list[CandidateId] = [
        candidate.name
        for candidate in lp.variables()
        if candidate.name != "__dummy"
    ]

    costs: dict[CandidateId, Cost] = {
        candidate.name: cost
        # TODO: some constraints have repeated variables, but we just override them with the same value
        for constraint in lp.constraints.values()
        # [C_ub_Bieńczyce: 25000 V_BO.D16.10_24 + 40500 V_BO.D16.11_24 <= 100000, ...]
        for candidate, cost in constraint.items()
    }

    voters: list[VoterId] = [voter.name for voter in lp.objectives]

    approvals_utilities: dict[CandidateId, list[tuple[VoterId, Utility]]] = (
        defaultdict(list)
    )
    for voter in (
        lp.objectives
    ):  # [T_6080: 80550 V_BO.D10.14_24 + 340000 V_BO.D10.1_24, ....]
        for candidate, utility in voter.items():
            approvals_utilities[candidate.name] += [(voter.name, utility)]

    total_utilities: dict[CandidateId, Utility] = {
        candidate: sum([u for v, u in voters_utilities])
        for candidate, voters_utilities in approvals_utilities.items()
    }

    no_vote_projects = []
    for project in projects:
        if project not in approvals_utilities:
            no_vote_projects.append(project)

    for project in no_vote_projects:
        print(f"Removing project with zero votes {project}")
        projects.remove(project)
        del costs[project]

    total_budget = abs(get_total_budget_constraint(lp).constant)
    return (
        projects,
        costs,
        voters,
        approvals_utilities,
        total_utilities,
        total_budget,
    )


def set_selected_candidates(
    problem: MultiObjectiveLpProblem, selected: list[str]
) -> None:
    for variable in problem.variables():
        variable.setInitialValue(1 if variable.name in selected else 0)
