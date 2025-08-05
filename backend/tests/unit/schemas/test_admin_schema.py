from app.administration.schema import ImportMembers

def test_import_members_schema():
    import_members = ImportMembers(emails=['user1@example.com', 'user2@example.com'])
    assert import_members.emails == ['user1@example.com', 'user2@example.com']
    