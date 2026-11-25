import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from fitness_intelligence.evidence import Scope, load_release
from fitness_intelligence.evidence.retrieval import Catalog, verify_release

FIXTURE = Path(__file__).parent / "fixtures/evidence/c2.json"
PIN = "d3af4f778f2012d282d9a3b3e135d92de55d22e367cf9a6ec9a79cd0e3b52a1a"


def fixture() -> Catalog:
    return verify_release(FIXTURE.read_bytes(), "fixture-c2", PIN, kind="fixture")


def load_modified(data: dict[str, Any]) -> Catalog:
    content = json.dumps(data).encode()
    return verify_release(
        content, data["release_id"], sha256(content).hexdigest(), kind=data["kind"]
    )


def test_bundle_contains_only_screening_material() -> None:
    catalog = load_release("j1-screening-1")
    assert sum(s.status == "screening" for s in catalog.release.sources) == 1
    assert sum(s.status == "pending" for s in catalog.release.sources) == 5
    assert len(catalog.release.claims) == 5
    for claim in catalog.release.claims:
        result = catalog.retrieve(claim.scope)
        assert claim.status == "pending"
        assert result.gaps and not result.matches
        assert catalog.ineligibility(claim.key) == "pending"
        assert not catalog.methods(claim.scope.question)
    with pytest.raises(ValueError, match="unknown release"):
        load_release("fixture-c2")


def test_pinned_release_and_results_are_immutable() -> None:
    data = FIXTURE.read_bytes()
    with pytest.raises(ValueError, match="digest"):
        verify_release(data + b" ", "fixture-c2", PIN, kind="fixture")
    for release_id, kind in [("other", "fixture"), ("fixture-c2", "operational")]:
        with pytest.raises(ValueError, match="identity or kind"):
            verify_release(data, release_id, PIN, kind=kind)
    with pytest.raises(ValidationError, match="frozen"):
        fixture().release.claims[0].support[0].locator = "different"


@pytest.mark.parametrize(
    ("path", "value", "error"),
    [
        (("claims", 1, "key"), "effect-a@1", "duplicate revision key"),
        (("claims", 1, "key"), "effect-a@2", "unknown relation endpoint"),
        (("claims", 0, "support"), [], "at least 1"),
        (("claims", 0, "support", 0, "result"), " ", "at least 1"),
        (("claims", 0, "support", 0, "locator"), "", "at least 1"),
        (("claims", 0, "support", 0, "source"), "paper-b@2", "unknown supporting source"),
        (("claims", 0, "approval"), None, "explicit approval"),
        (("claims", 0, "approval", "independent_human"), False, "True"),
        (("claims", 0, "approval", "reviewer"), "Fixture author", "independent reviewer"),
        (("claims", 0, "scope", "question"), "absent", "unknown claim question"),
        (("relations", 0, "object"), "absent@1", "unknown relation endpoint"),
        (("methods", 0, "claims"), ["paper-a@1"], "unknown method"),
        (("approval",), None, "reviewed manifest"),
        (("kind",), "operational", "synthetic records"),
    ],
)
def test_invalid_manifest(path: tuple[str | int, ...], value: Any, error: str) -> None:
    data = json.loads(FIXTURE.read_bytes())
    record = data
    for part in path[:-1]:
        record = record[part]
    record[path[-1]] = value
    with pytest.raises(ValidationError, match=error):
        load_modified(data)


def test_synthetic_source_alone_blocks_operational_release() -> None:
    data = json.loads(FIXTURE.read_bytes())
    data["kind"] = "operational"
    for r in data["sources"] + data["methods"] + data["claims"]:
        r["synthetic"] = False
    data["sources"][1]["synthetic"] = True
    with pytest.raises(ValidationError, match="synthetic records"):
        load_modified(data)


def test_unreviewed_source_cannot_support_approved_claim() -> None:
    data = json.loads(FIXTURE.read_bytes())
    data["sources"][0].update(status="pending", approval=None)
    with pytest.raises(ValidationError, match="reviewed sources"):
        load_modified(data)


def test_c2_competing_results_and_separate_method_preference() -> None:
    catalog = fixture()
    query = catalog.release.claims[0].scope
    result = catalog.retrieve(query)
    assert result == fixture().retrieve(query)
    assert (result.release_id, result.digest, result.algorithm) == (
        "fixture-c2",
        PIN,
        "structured-v1",
    )
    assert result.query == query and not result.gaps
    # Golden expectations were specified for each invented paper, independently of retrieval.
    expected = [
        ("effect-a@1", "paper-a@1", "Table A, change score", "A favors the increase."),
        ("effect-b@1", "paper-b@1", "Figure B, fixed-dose contrast", "B favors the fixed dose."),
    ]
    observed = []
    for match, other in zip(result.matches, reversed(expected), strict=True):
        evidence = match.evidence
        (citation,) = evidence.citations
        observed.append(
            (
                evidence.claim.key,
                citation.support.source,
                citation.support.locator,
                citation.support.result,
            )
        )
        assert citation.record_url.endswith(citation.support.source.split("@")[0])
        assert evidence.applicability == "direct" and evidence.claim.limitations
        (related,) = match.related
        assert related.evidence.claim.key == other[0]
        assert related.evidence.citations[0].support.locator == other[2]
        assert related.relation.kind == "conflicts-with" and related.relation.reason
    assert observed == expected
    (method,) = catalog.methods(query.question)
    assert method.key == "preferred-increase@1" and method.claims == ()


def test_input_order_does_not_rank_claims() -> None:
    data = json.loads(FIXTURE.read_bytes())
    for group in ("claims", "sources"):
        data[group].reverse()
    query = fixture().release.claims[0].scope
    assert load_modified(data).retrieve(query).matches == fixture().retrieve(query).matches


def test_c2_transfer_requires_reviewed_argument() -> None:
    catalog = fixture()
    query = catalog.release.claims[0].scope.model_copy(update={"experience": "recreational"})
    matches = catalog.retrieve(query).matches
    assert len(matches) == 2
    assert all(m.evidence.applicability == "indirect" for m in matches)
    assert all(
        m.evidence.reasons == ("Shared task, less practice. Direction may differ.",)
        for m in matches
    )


@pytest.mark.parametrize("dimension", tuple(Scope.model_fields))
@pytest.mark.parametrize("term", ["unknown", "unmatched"])
def test_mismatches_return_gap_without_fallback(dimension: str, term: str) -> None:
    catalog = fixture()
    query = catalog.release.claims[0].scope.model_copy(update={dimension: term})
    result = catalog.retrieve(query)
    assert result.gaps and not result.matches
    if dimension != "question":
        assert len(result.exclusions) == 2
        assert catalog.methods(query.question)  # available preference cannot fill this gap


def test_material_counterevidence_outside_population_is_context_only() -> None:
    data = json.loads(FIXTURE.read_bytes())
    data["claims"][1]["scope"]["population"] = "other"
    catalog = load_modified(data)
    (match,) = catalog.retrieve(catalog.release.claims[0].scope).matches
    (related,) = match.related
    assert related.evidence.claim.key == "effect-b@1"
    assert related.evidence.applicability == "context-only"
    assert related.evidence.reasons == ("population or experience",)


def test_pending_counterclaim_is_a_gap_without_its_assertion() -> None:
    data = json.loads(FIXTURE.read_bytes())
    data["claims"][1].update(status="pending", approval=None)
    catalog = load_modified(data)
    result = catalog.retrieve(catalog.release.claims[0].scope)
    (match,) = result.matches
    assert not match.related
    assert result.gaps == ("Related claim effect-b@1 is unavailable: pending",)


def test_c3_historical_selection_and_current_withdrawal() -> None:
    old = fixture()
    query = old.release.claims[0].scope
    historical = old.retrieve(query)
    data = json.loads(FIXTURE.read_bytes())
    data.update(
        release_id="fixture-c3",
        withdrawals=[
            {"claim": "effect-a@1", "reason": "Fixture correction", "withdrawn_on": "2000-01-11"}
        ],
    )
    current = load_modified(data)
    cited = historical.matches[0].evidence.claim.key
    assert old.ineligibility(cited) is None
    assert current.ineligibility(cited) == "withdrawn: Fixture correction"
    assert current.ineligibility("absent@1") == "absent from release"
    (remaining,) = current.retrieve(query).matches
    assert remaining.evidence.claim.key == "effect-b@1" and not remaining.related
    assert fixture().retrieve(query) == historical


def test_replacement_requires_forward_revision_and_prevents_two_active_ids() -> None:
    data = json.loads(FIXTURE.read_bytes())
    replacement = deepcopy(data["claims"][0])
    replacement.update(key="effect-a@2", assertion="Revised fixture assertion.")
    data["claims"].append(replacement)
    with pytest.raises(ValidationError, match="duplicate active claim ID"):
        load_modified(data)
    data["relations"].append(
        dict(
            key="revision@1",
            kind="supersedes",
            subject="effect-a@2",
            object="effect-a@1",
            reason="Updated fixture review.",
        )
    )
    catalog = load_modified(data)
    assert catalog.ineligibility("effect-a@1") == "superseded by effect-a@2"
    result = catalog.retrieve(catalog.release.claims[0].scope)
    assert [m.evidence.claim.key for m in result.matches] == ["effect-a@2", "effect-b@1"]
    data["relations"].append(
        dict(
            key="cycle@1",
            kind="supersedes",
            subject="effect-a@1",
            object="effect-a@2",
            reason="Invalid cycle.",
        )
    )
    with pytest.raises(ValidationError, match="later approved revision"):
        load_modified(data)


def test_published_releases_preserve_revision_identity_and_withdrawals() -> None:
    """Run over all shipped snapshots on every catalog change, in registry order."""
    from fitness_intelligence.evidence.retrieval import _PINS

    seen = {}
    withdrawn = {}
    retired = set()
    for release_id in _PINS:
        catalog = load_release(release_id)
        release = catalog.release
        for record in (*release.sources, *release.claims, *release.relations, *release.methods):
            assert seen.setdefault(record.key, record) == record
        current_withdrawals = {w.claim: w for w in release.withdrawals}
        assert withdrawn.items() <= current_withdrawals.items()
        withdrawn = current_withdrawals
        assert all(catalog.ineligibility(key) is not None for key in retired)
        retired.update(r.object for r in release.relations if r.kind == "supersedes")


def test_citation_matches_the_particular_assertion_and_bibliography() -> None:
    catalog = fixture()
    result = catalog.retrieve(catalog.release.claims[0].scope)
    assert [
        (m.evidence.claim.assertion, c.citation, c.support.locator)
        for m in result.matches
        for c in m.evidence.citations
    ] == [
        (
            "The comparison favors increased intensity in A.",
            "Invented paper A, fixture proceedings (2000).",
            "Table A, change score",
        ),
        (
            "The comparison favors fixed intensity in B.",
            "Invented paper B, fixture proceedings (2000).",
            "Figure B, fixed-dose contrast",
        ),
    ]
