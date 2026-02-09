import pytest
import tempfile
from pathlib import Path

from epstein_enhanced.core.linkedin_parser import LinkedInParser, LinkedInContact


@pytest.fixture
def sample_csv():
    csv_content = """First Name,Last Name,Email Address,Company,Position,Connected On
John,Doe,john@example.com,Acme Inc,CEO,01 Jan 2020
Jane,Smith,jane@example.com,Tech Corp,CTO,15 Mar 2021
Bob,Johnson,,Startup LLC,Founder,"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(csv_content)
        temp_path = f.name
    
    yield temp_path
    
    Path(temp_path).unlink()


def test_parse_csv_basic(sample_csv):
    contacts = LinkedInParser.parse_csv(sample_csv)
    
    assert len(contacts) == 3
    assert contacts[0].first_name == "John"
    assert contacts[0].last_name == "Doe"
    assert contacts[0].full_name == "John Doe"
    assert contacts[0].company == "Acme Inc"
    assert contacts[0].position == "CEO"


def test_parse_csv_missing_data(sample_csv):
    contacts = LinkedInParser.parse_csv(sample_csv)
    
    bob = [c for c in contacts if c.first_name == "Bob"][0]
    assert bob.email is None or bob.email == ""
    assert bob.company == "Startup LLC"


def test_contact_search_variations():
    contact = LinkedInContact(
        first_name="John Michael",
        last_name="Doe",
        email="john@example.com",
        company="Acme",
        position="CEO",
        connected_on="2020"
    )
    
    variations = contact.search_variations
    
    assert "John Michael Doe" in variations
    assert "Doe John Michael" in variations or "John Doe" in variations


def test_filter_common_names():
    contacts = [
        LinkedInContact("John", "Smith", "john@example.com", "Acme", "CEO", "2020"),
        LinkedInContact("Alice", "Johnson", "alice@example.com", "Tech", "CTO", "2021"),
        LinkedInContact("Bob", "Williams", "bob@example.com", "Corp", "CFO", "2022"),
    ]
    
    filtered = LinkedInParser.filter_common_names(contacts)
    
    names = [c.full_name for c in filtered]
    assert "John Smith" not in names
    assert "Alice Johnson" in names


def test_filter_short_names():
    contacts = [
        LinkedInContact("A", "B", "ab@example.com", "Acme", "CEO", "2020"),
        LinkedInContact("John", "Doe", "john@example.com", "Tech", "CTO", "2021"),
    ]
    
    filtered = LinkedInParser.filter_common_names(contacts, min_name_length=4)
    
    assert len(filtered) == 1
    assert filtered[0].full_name == "John Doe"


def test_invalid_csv():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("Invalid,CSV,Content\n1,2,3")
        temp_path = f.name
    
    try:
        with pytest.raises(ValueError):
            LinkedInParser.parse_csv(temp_path)
    finally:
        Path(temp_path).unlink()


def test_csv_with_utf8_bom(sample_csv):
    with open(sample_csv, 'rb') as f:
        content = f.read()
    
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
        f.write(b'\xef\xbb\xbf')
        f.write(content)
        temp_path = f.name
    
    try:
        contacts = LinkedInParser.parse_csv(temp_path)
        assert len(contacts) > 0
    finally:
        Path(temp_path).unlink()
