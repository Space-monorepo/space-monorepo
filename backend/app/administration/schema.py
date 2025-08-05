from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.communities.schema import CommunityMemberRoleEnum

class ImportMembers(BaseModel):
    emails: list[EmailStr] = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'emails': ['user1@example.com', 'user2@example.com']
            }
        }
    )

class MemberRoleUpdate(BaseModel):
    new_role: CommunityMemberRoleEnum = Field(..., description='The new role for the member')

    model_config = ConfigDict(
        use_enum_values=True,
        json_schema_extra={
            'example': {
                'new_role': 'moderator'
            }
        }
    )
        

    