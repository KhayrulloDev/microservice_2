from pydantic import BaseModel
from uuid import UUID

class ChannelSchema(BaseModel):
    user_id: int
    channel_id: str


class ChannelResponse(BaseModel):
    id: UUID
    channel_name: str
    channel_id: str