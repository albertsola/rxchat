from typing import List

from pydantic import BaseModel

class ChatChannel(BaseModel):
    id: str
    users_count: int

def get_channel_ids() -> List[str]:
    return ["Welcome", "Jokes", "Tech"]