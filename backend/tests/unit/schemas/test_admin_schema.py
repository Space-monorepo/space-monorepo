import pytest
from pydantic import ValidationError

from app.api.administration.schema import ImportMembers

@pytest.mark.unit
def test_import_members_schema():
    import_members = ImportMembers(emails=['user1@example.com', 'user2@example.com'])
    assert import_members.emails == ['user1@example.com', 'user2@example.com']


@pytest.mark.unit
def test_import_members_schema_invalid():
    with pytest.raises(ValidationError):
        ImportMembers(emails=['example.com', 'invalid-email'])