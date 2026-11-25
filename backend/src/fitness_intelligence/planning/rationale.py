"""Sealed evidence selection for the synthetic press block. Release policy is deployment-owned."""

from typing import Literal

from fitness_intelligence.evidence import Scope, load_release
from fitness_intelligence.evidence.catalog import MethodRevision
from fitness_intelligence.evidence.retrieval import Catalog, Result

from .outcomes import Frozen, WeeklyOutcomes

CURRENT_RELEASE = "j1-screening-1"
DOSE_QUERY = Scope(
    question="strength-dose",
    objective="strength-development",
    population="unknown",
    experience="unknown",
    intervention="one-additional-press-set",
    comparator="unchanged-weekly-dose",
    outcome="press-strength",
    horizon="eight-weeks",
    block_context="concurrent-training",
)


def current_catalog() -> Catalog:
    return load_release(CURRENT_RELEASE)


class Rationale(Frozen):
    version: Literal["e3.press.v1"] = "e3.press.v1"
    outcomes: WeeklyOutcomes | None
    selection: Result
    eligible_claim_count: int
    programming_options: tuple[MethodRevision, ...]

    @classmethod
    def retrieve(cls, outcomes: WeeklyOutcomes | None, catalog: Catalog) -> "Rationale":
        return cls(
            outcomes=outcomes,
            eligible_claim_count=sum(
                catalog.ineligibility(c.key) is None for c in catalog.release.claims
            ),
            selection=catalog.retrieve(DOSE_QUERY),
            programming_options=catalog.methods(DOSE_QUERY.question),
        )

    @property
    def claim_keys(self) -> tuple[str, ...]:
        """Primary and related empirical revisions in the pinned retrieval result."""
        keys = set()
        for match in self.selection.matches:
            keys.add(match.evidence.claim.key)
            keys.update(r.evidence.claim.key for r in match.related)
        return tuple(sorted(keys))

    def cites_claim(self, key: str) -> bool:
        return key in self.claim_keys or any(key in m.claims for m in self.programming_options)

    def eligibility(self) -> tuple[str, ...]:
        current = current_catalog()
        alerts = [
            f"{key} {reason}" for key in self.claim_keys if (reason := current.ineligibility(key))
        ]
        eligible_methods = current.methods(self.selection.query.question)
        for method in self.programming_options:
            if method not in eligible_methods:
                alerts.append(f"Programming method {method.key} is no longer eligible.")
            for key in method.claims:
                if reason := current.ineligibility(key):
                    alerts.append(
                        f"Programming method {method.key} supporting claim {key} {reason}"
                    )
        return tuple(alerts)

    def verify_selection(self) -> bool:
        return self.retrieve(self.outcomes, load_release(self.selection.release_id)) == self
