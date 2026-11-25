"""Versioned evidence records and cross-record release integrity checks."""

from datetime import date
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

type Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
type Term = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]*$")]
type Key = Annotated[str, Field(pattern=r"^[a-z][a-z0-9-]*@[1-9][0-9]*$")]
type Kind = Literal["operational", "fixture"]


class Record(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class Approval(Record):
    """Attestation recorded by the human reviewer in version control."""

    reviewer: Text
    role: Text
    reviewed_on: date
    independent_human: Literal[True]


class CuratedRevision(Record):
    key: Key
    synthetic: bool
    extracted_by: Text
    status: Literal["screening", "pending", "approved"]
    approval: Approval | None

    @model_validator(mode="after")
    def explicit_review(self) -> Self:
        if (self.status == "approved") != (self.approval is not None):
            raise ValueError("approved status requires an explicit approval decision")
        if self.approval and self.approval.reviewer.casefold() == self.extracted_by.casefold():
            raise ValueError("extraction requires an independent reviewer")
        return self


class SourceRevision(CuratedRevision):
    citation: Text
    doi: Annotated[str, Field(pattern=r"^10\.\d{4,9}/\S+$")] | None
    record_url: Annotated[str, Field(pattern=r"^https://\S+$")]
    published_on: date
    design: Text
    access: Literal["full-text", "abstract"]
    checked_on: date
    publication_check: Text
    rights: Text
    appraisal: Text
    next_review: date


class Population(Record):
    population: Term
    experience: Term


class Scope(Population):
    question: Term
    objective: Term
    intervention: Term
    comparator: Term
    outcome: Term
    horizon: Term
    block_context: Term


class Transfer(Population):
    argument: Text


class Support(Record):
    source: Key
    locator: Text
    result: Text
    restriction: Text


class ClaimRevision(CuratedRevision):
    scope: Scope
    assertion: Text
    limitations: Text
    quality: Literal["low", "moderate", "high"]
    assessment: Text
    transfers: tuple[Transfer, ...]
    support: Annotated[tuple[Support, ...], Field(min_length=1)]


class Relation(Record):
    key: Key
    kind: Literal["conflicts-with", "qualifies", "supersedes"]
    subject: Key
    object: Key
    reason: Text


class MethodRevision(CuratedRevision):
    question: Term
    description: Text
    provenance: Text
    tradeoffs: Text
    claims: tuple[Key, ...]


class Question(Record):
    id: Term
    description: Text
    gap: Text


class Withdrawal(Record):
    claim: Key
    withdrawn_on: date
    reason: Text


def unique[T](values: tuple[T, ...], label: str) -> set[T]:
    distinct = set(values)
    if len(distinct) != len(values):
        raise ValueError(f"duplicate {label}")
    return distinct


class CorpusRelease(Record):
    schema_version: Literal[1]
    release_id: Term
    kind: Kind
    assembled_on: date
    approval: Approval | None
    questions: tuple[Question, ...]
    sources: tuple[SourceRevision, ...]
    claims: tuple[ClaimRevision, ...]
    relations: tuple[Relation, ...]
    methods: tuple[MethodRevision, ...]
    withdrawals: tuple[Withdrawal, ...]

    @model_validator(mode="after")
    def validate_manifest(self) -> Self:
        questions = unique(tuple(q.id for q in self.questions), "question")
        records = (*self.sources, *self.claims, *self.methods)
        unique(tuple(r.key for r in (*records, *self.relations)), "revision key")
        if self.kind == "operational" and any(r.synthetic for r in records):
            raise ValueError("synthetic records in operational release")
        if any(r.approval for r in records) and not self.approval:
            raise ValueError("eligible records require a reviewed manifest")
        sources = {s.key: s for s in self.sources}
        claims = {c.key: c for c in self.claims}
        for claim in self.claims:
            if claim.scope.question not in questions:
                raise ValueError("unknown claim question")
            unique(tuple((t.population, t.experience) for t in claim.transfers), "transfer")
            for edge in claim.support:
                if edge.source not in sources:
                    raise ValueError("unknown supporting source revision")
                if claim.approval and not sources[edge.source].approval:
                    raise ValueError("approved claim needs reviewed sources")
        withdrawn = unique(tuple(w.claim for w in self.withdrawals), "withdrawal")
        if withdrawn - claims.keys():
            raise ValueError("withdrawal references unknown claim")
        superseded: set[str] = set()
        for relation in self.relations:
            if relation.subject not in claims or relation.object not in claims:
                raise ValueError("unknown relation endpoint")
            a, b = claims[relation.subject], claims[relation.object]
            if a == b or a.scope.question != b.scope.question:
                raise ValueError("relation must connect distinct claims on the same question")
            if relation.kind == "supersedes":
                a_id, a_rev = a.key.split("@")
                b_id, b_rev = b.key.split("@")
                if a_id != b_id or int(a_rev) <= int(b_rev) or not a.approval:
                    raise ValueError(
                        "supersession requires a later approved revision of this claim"
                    )
                superseded.add(b.key)
        eligible = {c.key for c in self.claims if c.approval} - withdrawn - superseded
        unique(tuple(k.split("@")[0] for k in eligible), "active claim ID")
        for method in self.methods:
            if method.question not in questions or set(method.claims) - claims.keys():
                raise ValueError("unknown method question or claim")
            if method.approval and set(method.claims) - eligible:
                raise ValueError("approved method references ineligible claim")
        return self
