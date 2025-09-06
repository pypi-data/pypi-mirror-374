import os
import pytest  # type: ignore
from unittest.mock import patch
from pathlib import Path
from pydantic import ValidationError
from openstates.cli.committees import CommitteeDir, PersonMatcher
from openstates.models.committees import (
    Committee,
    Link,
    ScrapeCommittee,
    Membership,
)

JURISDICTION_ID = "ocd-jurisdiction/country:us/state:wa/government"

TEST_DATA_PATH = Path(__file__).parent / "testdata"


def test_validation_chamber():
    ScrapeCommittee(name="Education", chamber="lower")
    ScrapeCommittee(name="Education", chamber="upper")
    ScrapeCommittee(name="Education", chamber="legislature")
    with pytest.raises(ValidationError):
        ScrapeCommittee(name="Education", chamber="joint")


def test_parent_validation_subcommittee():
    # subcommittees can be any string...
    ScrapeCommittee(
        name="Pre-K", chamber="upper", parent="Education", classification="subcommittee"
    )
    # must set parent if subcommittee
    with pytest.raises(ValidationError):
        ScrapeCommittee(name="Pre-K", chamber="upper", classification="subcommittee")
    # must set can't set parent without subcommittees
    with pytest.raises(ValidationError):
        ScrapeCommittee(name="Pre-K", chamber="upper", parent="Education")


@pytest.fixture
def person_matcher():
    pm = PersonMatcher("wa", TEST_DATA_PATH / "no-such-dir")
    pm.add_name("lower", "Jones", "ocd-person/00000000-0000-0000-0000-111111111111")
    pm.add_name("lower", "Nguyen", "ocd-person/00000000-0000-0000-0000-222222222222")
    pm.add_name("lower", "Green", "ocd-person/00000000-0000-0000-0000-333333333333")
    # two Cristobals
    pm.add_name("lower", "Cristobal", "ocd-person/00000000-0000-0000-0000-000888888888")
    pm.add_name("lower", "Cristobal", "ocd-person/00000000-0000-0000-0000-000999999999")
    return pm


def test_person_matcher_match(person_matcher):
    assert (
        person_matcher.match("lower", "Jones")
        == "ocd-person/00000000-0000-0000-0000-111111111111"
    )
    assert (
        person_matcher.match("lower", "Nguyen")
        == "ocd-person/00000000-0000-0000-0000-222222222222"
    )
    # two matches
    assert person_matcher.match("lower", "Cristobal") is None
    # no matches
    assert person_matcher.match("lower", "Gordy") is None


def test_merge_committees_name():
    comdir = CommitteeDir(abbr="wa", directory=TEST_DATA_PATH / "committees")
    id_one = "ocd-organization/00000000-0000-0000-0000-000000000001"
    id_two = "ocd-organization/00000000-0000-0000-0000-000000000002"
    c1 = Committee(
        id=id_one,
        jurisdiction=JURISDICTION_ID,
        chamber="upper",
        name="Education",
        members=[Membership(name="Someone", role="member")],
    )
    c2 = Committee(
        id=id_two,
        jurisdiction=JURISDICTION_ID,
        chamber="upper",
        name="Education & Children",
        members=[Membership(name="Someone", role="member")],
    )
    merged = comdir.merge_committees(c1, c2)
    assert merged.id == c1.id
    assert merged.name == c2.name


def test_merge_committees_invalid():
    comdir = CommitteeDir(abbr="wa", directory=TEST_DATA_PATH / "committees")

    id_one = "ocd-organization/00000000-0000-0000-0000-000000000001"
    id_two = "ocd-organization/00000000-0000-0000-0000-000000000002"
    c1 = Committee(
        id=id_one,
        jurisdiction=JURISDICTION_ID,
        chamber="upper",
        name="Education",
        members=[Membership(name="Someone", role="member")],
    )
    c2 = Committee(
        id=id_two,
        jurisdiction=JURISDICTION_ID,
        chamber="lower",
        name="Education & Children",
        members=[Membership(name="Someone", role="member")],
    )
    with pytest.raises(ValueError):
        comdir.merge_committees(c1, c2)


def test_merge_committees_links():
    comdir = CommitteeDir(abbr="wa", directory=TEST_DATA_PATH / "committees")
    id_one = "ocd-organization/00000000-0000-0000-0000-000000000001"
    id_two = "ocd-organization/00000000-0000-0000-0000-000000000002"
    c1 = Committee(
        id=id_one,
        jurisdiction=JURISDICTION_ID,
        chamber="upper",
        name="Education",
        links=[
            Link(url="https://example.com/1"),
            Link(url="https://example.com/2"),
        ],
        members=[Membership(name="Someone", role="member")],
    )
    c2 = Committee(
        id=id_two,
        jurisdiction=JURISDICTION_ID,
        chamber="upper",
        name="Education & Children",
        links=[
            Link(url="https://example.com/1", note="first"),
            Link(url="https://example.com/3"),
        ],
        members=[Membership(name="Someone", role="member")],
    )
    merged = comdir.merge_committees(c1, c2)
    assert merged.links == [
        Link(url="https://example.com/1", note="first"),
        Link(url="https://example.com/2"),
        Link(url="https://example.com/3"),
    ]


def test_merge_committees_members():
    comdir = CommitteeDir(abbr="wa", directory=TEST_DATA_PATH / "committees")
    id_one = "ocd-organization/00000000-0000-0000-0000-000000000001"
    id_two = "ocd-organization/00000000-0000-0000-0000-000000000002"
    person_id = "ocd-person/00000000-0000-0000-0000-000000000002"
    c1 = Committee(
        id=id_one,
        jurisdiction=JURISDICTION_ID,
        chamber="upper",
        name="Education",
        members=[
            Membership(name="Amy", role="chair"),
            Membership(name="Bo", role="chair"),
        ],
    )
    c2 = Committee(
        id=id_two,
        jurisdiction=JURISDICTION_ID,
        chamber="upper",
        name="Education & Children",
        members=[
            Membership(name="Amy", role="chair", person_id=person_id),
            Membership(name="Charlize", role="member"),
        ],
    )
    merged = comdir.merge_committees(c1, c2)
    assert merged.members == [
        Membership(name="Amy", role="chair", person_id=person_id),
        Membership(name="Bo", role="chair"),
        Membership(name="Charlize", role="member"),
    ]


def test_load_data():
    comdir = CommitteeDir(abbr="wa", directory=TEST_DATA_PATH / "committees")

    assert len(comdir.coms_by_parent_and_name["lower"]) == 3
    assert len(comdir.coms_by_parent_and_name["upper"]) == 1
    assert comdir.errors == []


def test_load_data_with_errors():
    comdir = CommitteeDir(
        abbr="wa",
        directory=TEST_DATA_PATH / "broken-committees",
        raise_errors=False,
    )

    assert len(comdir.coms_by_parent_and_name["lower"]) == 0
    assert len(comdir.coms_by_parent_and_name["upper"]) == 0
    assert len(comdir.errors) == 2
    # error order isn't deterministic
    path0, msg0 = comdir.errors[0]
    path1, msg1 = comdir.errors[1]
    if "lower" in str(path0):
        msg0, msg1 = msg1, msg0
    assert "9 validation errors" in str(msg0)
    assert "members -> 3 -> who" in str(msg0)
    assert "members -> 3 -> name" in str(msg0)
    assert "2 validation errors" in str(msg1)
    assert "not a valid enumeration member" in str(msg1)
    assert "extra fields not permitted" in str(msg1)


def test_load_data_with_errors_raised():
    # default is to raise error right away, test_load_data_with_errors catches errors for linter
    with pytest.raises(ValidationError):
        CommitteeDir(
            abbr="wa",
            directory=TEST_DATA_PATH / "broken-committees",
        )


def test_get_new_filename():
    comdir = CommitteeDir(
        abbr="wa",
        directory=TEST_DATA_PATH / "committees",
    )
    simple = Committee(
        id="ocd-organization/00001111-2222-3333-4444-555566667777",
        jurisdiction=JURISDICTION_ID,
        name="Simple",
        chamber="lower",
        members=[Membership(name="Someone", role="member")],
    )
    longer = Committee(
        id="ocd-organization/00001111-2222-3333-4444-999999999999",
        jurisdiction=JURISDICTION_ID,
        name="Ways, Means & Taxes",
        chamber="upper",
        members=[Membership(name="Someone", role="member")],
    )
    assert (
        comdir.get_new_filename(simple)
        == "lower-Simple-00001111-2222-3333-4444-555566667777.yml"
    )
    assert (
        comdir.get_new_filename(longer)
        == "upper-Ways-Means--Taxes-00001111-2222-3333-4444-999999999999.yml"
    )


def test_get_filename_by_id():
    comdir = CommitteeDir(
        abbr="wa",
        directory=TEST_DATA_PATH / "committees",
    )
    assert comdir.get_filename_by_id(
        "ocd-organization/11111111-2222-3333-4444-111111111111"
    ) == (
        TEST_DATA_PATH
        / "committees/lower-Agriculture-11111111-2222-3333-4444-111111111111.yml"
    )

    with pytest.raises(FileNotFoundError):
        comdir.get_filename_by_id(
            "ocd-organization/99999999-9999-9999-9999-999999999999"
        )


def test_get_filename_by_name():
    comdir = CommitteeDir(
        abbr="wa",
        directory=TEST_DATA_PATH / "committees",
    )
    assert comdir.get_filename_by_name("lower", "Agriculture") == (
        TEST_DATA_PATH
        / "committees/lower-Agriculture-11111111-2222-3333-4444-111111111111.yml"
    )

    with pytest.raises(FileNotFoundError):
        comdir.get_filename_by_name("lower", "Weird")


# TODO: test_save_committee, test_add_committee


def test_add_committee():
    comdir = CommitteeDir(
        abbr="wa",
        directory=TEST_DATA_PATH / "committees",
    )
    with patch.object(comdir, "save_committee") as patch_obj:
        sc = ScrapeCommittee(
            chamber="lower",
            name="New Business",
            members=[Membership(name="Someone", role="member")],
        )
        comdir.add_committee(sc)
        full_com = comdir.coms_by_parent_and_name[sc.chamber][sc.name]
        assert full_com.name == sc.name
        assert full_com.id.startswith("ocd-organization")
        assert full_com.jurisdiction == JURISDICTION_ID
        assert patch_obj.called_once_with(full_com)


def test_ingest_scraped_json():
    comdir = CommitteeDir(
        abbr="wa",
        directory=TEST_DATA_PATH / "committees",
    )
    os.environ["OS_PEOPLE_DIRECTORY"] = str(TEST_DATA_PATH)
    committees = comdir.ingest_scraped_json(TEST_DATA_PATH / "scraped-committees")
    assert len(committees) == 2
    assert {"Judiciary 2", "Judiciary 4"} == {c.name for c in committees}


def test_ingest_scraped_json_names_resolved():
    comdir = CommitteeDir(
        abbr="wa",
        directory=TEST_DATA_PATH / "committees",
    )
    richardson_id = "ocd-person/11111111-0000-0000-0000-555555555555"
    comdir.person_matcher = PersonMatcher("wa", TEST_DATA_PATH / "no-such-dir")
    comdir.person_matcher.add_name("lower", "Richardson", richardson_id)
    committees = comdir.ingest_scraped_json(TEST_DATA_PATH / "scraped-committees")
    assert len(committees) == 2
    committees = sorted(committees, key=lambda c: c.name)
    assert committees[0].name == "Judiciary 2"
    # ensure that names are matched
    assert committees[0].members[0].name == "Richardson"
    assert committees[0].members[0].role == "chair"
    assert committees[0].members[0].person_id == richardson_id
    assert committees[1].name == "Judiciary 4"


def test_get_merge_plan_by_parent(person_matcher):
    comdir = CommitteeDir(
        abbr="wa",
        directory=TEST_DATA_PATH / "committees",
    )
    comdir.person_matcher = person_matcher

    newdata = [
        # identical
        ScrapeCommittee(
            name="Education",
            chamber="lower",
            sources=[Link(url="https://example.com/committee")],
            members=[
                Membership(name="Jones", role="chair"),
                Membership(name="Nguyen", role="co-chair"),
                Membership(name="Green", role="member"),
                Membership(name="Cristobal", role="member"),
            ],
        ),
        # new
        ScrapeCommittee(
            name="Science",
            chamber="lower",
            sources=[Link(url="https://example.com/committee")],
            members=[
                Membership(name="Jones", role="chair"),
                Membership(name="Nguyen", role="co-chair"),
            ],
        ),
        # changed
        ScrapeCommittee(
            name="Rules",
            chamber="lower",
            sources=[Link(url="https://example.com/committee")],
            members=[
                Membership(name="Fox", role="chair"),
                Membership(name="Fawkes", role="co-chair"),
                Membership(name="Faux", role="member"),
            ],
        ),
    ]

    plan = comdir.get_merge_plan_by_parent("lower", newdata)
    assert plan.names_to_add == {"Science"}
    assert plan.names_to_remove == {"Agriculture"}
    assert plan.same == 1  # Edcuation
    assert len(plan.to_merge) == 1
    old, new = plan.to_merge[0]
    assert old.name == new.name == "Rules"
    assert len(old.members) < len(new.members)
