from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ValidationInfo, field_validator

from galileo_core.schemas.shared.workflows.node_type import NodeType


class TransactionLoggingMethod(str, Enum):
    py_langchain = "py_langchain"
    py_langchain_async = "py_langchain_async"
    py_logger = "py_logger"


class TransactionRecord(BaseModel):
    latency_ms: Optional[int] = None
    status_code: Optional[int] = None
    input_text: str
    redacted_input: Optional[str] = None
    output_text: Optional[str] = None
    redacted_output: Optional[str] = None
    tools: Optional[str] = None
    model: Optional[str] = None
    num_input_tokens: Optional[int] = None
    num_output_tokens: Optional[int] = None
    num_total_tokens: Optional[int] = None
    finish_reason: Optional[str] = None
    node_id: str
    chain_id: Optional[str] = None
    chain_root_id: Optional[str] = None
    output_logprobs: Optional[dict] = None
    created_at: str
    tags: Optional[list[str]] = None
    user_metadata: Optional[dict[str, Any]] = None
    temperature: Optional[float] = None
    node_type: NodeType
    node_name: Optional[str] = None
    has_children: bool = False
    time_to_first_token_ms: Optional[float] = None
    version: Optional[str] = None

    @field_validator("chain_id", mode="before")
    def validate_chain_id(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:
        if value == info.data.get("node_id"):
            raise ValueError("Chain ID cannot match node ID.")
        return value


class TransactionRecordBatch(BaseModel):
    records: list[TransactionRecord]
    logging_method: TransactionLoggingMethod
    client_version: Optional[str] = None
