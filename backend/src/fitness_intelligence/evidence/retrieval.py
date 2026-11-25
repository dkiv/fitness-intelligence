"""Local retrieval from an explicitly pinned release. No athlete state or planner dependency."""

from dataclasses import dataclass
from hashlib import sha256
from importlib.resources import files
from typing import Literal

from .catalog import ClaimRevision, CorpusRelease, Kind, MethodRevision, Relation, Scope, Support

ALGORITHM = "structured-v1"

# Published pins are append-only. Resolve IDs through this table, never as caller-supplied paths.
_PINS = {"j1-screening-1": "ae9a27a9a257f7b48375ad1892206c5f10d07a6e0625ee717974fe9d73b3cf64"}


@dataclass(frozen=True)
class Citation:
    support: Support
    citation: str
    doi: str | None
    record_url: str


@dataclass(frozen=True)
class Evidence:
    claim: ClaimRevision
    citations: tuple[Citation, ...]
    applicability: Literal["direct", "indirect", "context-only"]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class Related:
    relation: Relation
    evidence: Evidence


@dataclass(frozen=True)
class Match:
    evidence: Evidence
    related: tuple[Related, ...]


@dataclass(frozen=True)
class Exclusion:
    claim: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class Result:
    release_id: str
    digest: str
    query: Scope
    matches: tuple[Match, ...]
    exclusions: tuple[Exclusion, ...]
    gaps: tuple[str, ...]
    algorithm: str = ALGORITHM


@dataclass(frozen=True)
class Catalog:
    release: CorpusRelease
    digest: str

    def ineligibility(self, key: str) -> str | None:
        """Check a previously cited revision against this (e.g. current) manifest."""
        for entry in self.release.withdrawals:
            if entry.claim == key:
                return f"withdrawn: {entry.reason}"
        for relation in self.release.relations:
            if relation.kind == "supersedes" and relation.object == key:
                return f"superseded by {relation.subject}"
        for claim in self.release.claims:
            if claim.key == key:
                return None if claim.approval else claim.status
        return "absent from release"

    def methods(self, question: str) -> tuple[MethodRevision, ...]:
        return tuple(
            sorted(
                (m for m in self.release.methods if m.question == question and m.approval),
                key=lambda m: m.key,
            )
        )

    def retrieve(self, query: Scope) -> Result:
        candidates = sorted(
            (c for c in self.release.claims if c.scope.question == query.question),
            key=lambda c: c.key,
        )
        evidence = {}
        exclusions = []
        for claim in candidates:
            if reason := self.ineligibility(claim.key):
                exclusions.append(Exclusion(claim.key, (reason,)))
                continue
            item = self._evidence(claim, query)
            evidence[claim.key] = item
            if item.applicability == "context-only":
                exclusions.append(Exclusion(claim.key, item.reasons))

        matches = []
        gaps = set()
        for item in evidence.values():
            if item.applicability == "context-only":
                continue
            related = []
            for relation in self.release.relations:
                if relation.kind == "supersedes":
                    continue
                if item.claim.key == relation.subject:
                    other = relation.object
                elif item.claim.key == relation.object:
                    other = relation.subject
                else:
                    continue
                if other in evidence:
                    related.append(Related(relation, evidence[other]))
                else:
                    gaps.add(f"Related claim {other} is unavailable: {self.ineligibility(other)}")
            matches.append(Match(item, tuple(sorted(related, key=lambda r: r.relation.key))))
        if not matches:
            question = next((q for q in self.release.questions if q.id == query.question), None)
            gaps.add("No eligible claim matches the requested scope.")
            gaps.add(question.gap if question else "Question outside the release vocabulary.")
        quality_order = {"high": 0, "moderate": 1, "low": 2}
        matches.sort(
            key=lambda m: (
                m.evidence.applicability != "direct",
                quality_order[m.evidence.claim.quality],
                m.evidence.claim.key,
            )
        )
        return Result(
            self.release.release_id,
            self.digest,
            query,
            tuple(matches),
            tuple(exclusions),
            tuple(sorted(gaps)),
        )

    def _evidence(self, claim: ClaimRevision, query: Scope) -> Evidence:
        scope = claim.scope
        mismatch = [
            field
            for field in (
                "objective",
                "intervention",
                "comparator",
                "outcome",
                "horizon",
                "block_context",
            )
            if getattr(query, field) == "unknown" or getattr(query, field) != getattr(scope, field)
        ]
        target = (query.population, query.experience)
        transfer = None
        if "unknown" in target:
            mismatch.append("unknown population or experience")
        elif target != (scope.population, scope.experience):
            transfer = next(
                (t for t in claim.transfers if (t.population, t.experience) == target), None
            )
            if transfer is None:
                mismatch.append("population or experience")
        sources = {s.key: s for s in self.release.sources}
        citations = tuple(
            Citation(
                edge,
                sources[edge.source].citation,
                sources[edge.source].doi,
                sources[edge.source].record_url,
            )
            for edge in sorted(claim.support, key=lambda e: (e.source, e.locator))
        )
        if mismatch:
            return Evidence(claim, citations, "context-only", tuple(mismatch))
        if transfer:
            return Evidence(claim, citations, "indirect", (transfer.argument,))
        return Evidence(claim, citations, "direct", ())


def verify_release(data: bytes, release_id: str, digest: str, *, kind: Kind) -> Catalog:
    """Verify exact file bytes against a trusted external pin, then validate the entire graph."""
    if sha256(data).hexdigest() != digest:
        raise ValueError("release digest mismatch")
    release = CorpusRelease.model_validate_json(data)
    if release.release_id != release_id or release.kind != kind:
        raise ValueError("release identity or kind mismatch")
    return Catalog(release, digest)


def load_release(release_id: str) -> Catalog:
    """Production entry point. Unknown or invalid releases fail closed."""
    if release_id not in _PINS:
        raise ValueError("unknown release ID")
    data = files(__package__).joinpath("releases", f"{release_id}.json").read_bytes()
    return verify_release(data, release_id, _PINS[release_id], kind="operational")
