from enum import Enum
from typing import Dict, List
from pydantic import BaseModel, field_validator, model_validator

from agency_swarm import Agent
from ExampleAgency.agency import agency

# Create dynamic RecipientAgent enum
agent_names = {agent.name: agent.name for agent in agency.agents}
RecipientAgent = Enum('RecipientAgent', agent_names)

# Store agent instances for easy lookup
AGENT_INSTANCES: Dict[str, 'Agent'] = {agent.name: agent for agent in agency.agents}

class AttachmentTool(BaseModel):
    type: str


class Attachment(BaseModel):
    file_id: str
    tools: List[AttachmentTool]


class AgencyRequest(BaseModel):
    message: str
    message_files: List[str] = None
    yield_messages: bool = False
    recipient_agent: str = None # Will be automatically converted to the Agent instance
    additional_instructions: str = None
    attachments: List[Attachment] = []
    tool_choice: dict = None
    verbose: bool = False
    response_format: dict = None

    @field_validator('recipient_agent')
    def validate_recipient_agent(cls, v):
        if v is not None:
            if v not in AGENT_INSTANCES:
                raise ValueError(f"Invalid agent name. Available agents: {list(AGENT_INSTANCES.keys())}")
            return AGENT_INSTANCES[v]  # Substitute str with an Agent instance
        return v

    @model_validator(mode='after')
    def check_verbose_yield_combination(self):
        if self.verbose and self.yield_messages:
            raise ValueError("Verbose mode is not compatible with yield_messages=True")
        return self
    
class AgencyRequestStreaming(BaseModel):
    message: str
    message_files: List[str] = None
    recipient_agent: str = None # Will be automatically converted to the Agent instance
    additional_instructions: str = None
    attachments: List[Attachment] = []
    tool_choice: dict = None
    response_format: dict = None

    @field_validator('recipient_agent')
    def validate_recipient_agent(cls, v):
        if v is not None:
            if v not in AGENT_INSTANCES:
                raise ValueError(f"Invalid agent name. Available agents: {list(AGENT_INSTANCES.keys())}")
            return AGENT_INSTANCES[v]  # Substitute str with an Agent instance
        return v