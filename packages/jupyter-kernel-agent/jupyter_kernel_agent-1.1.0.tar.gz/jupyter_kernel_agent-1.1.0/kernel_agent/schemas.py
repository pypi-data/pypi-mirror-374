# kernel_agent/schemas.py
from __future__ import annotations
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

# ---------- Jupyter-style outputs ----------

class StreamOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["stream"] = "stream"
    name: str = "stdout"
    text: str = ""

class ExecuteResultOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["execute_result"] = "execute_result"
    data: Dict[str, Any] = Field(default_factory=dict)
    execution_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DisplayDataOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["display_data"] = "display_data"
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ErrorOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    type: Literal["error"] = "error"
    ename: Optional[str] = None
    evalue: Optional[str] = None
    traceback: Optional[List[str]] = None

OutputItem = Union[StreamOutput, ExecuteResultOutput, DisplayDataOutput, ErrorOutput]


# ---------- POST / : request/response ----------

class RPCRequest(BaseModel):
    """
    Body of POST / for kernel actions.
    """
    model_config = ConfigDict(extra="ignore")
    action: str
    session_id: str = "default"
    code: Optional[str] = None
    execution_count: Optional[int] = None
    channel: Optional[str] = None   # <== NEW, only in request

class RPCResponse(BaseModel):
    """
    Jupyter cell-style envelope returned by POST /.
    """
    model_config = ConfigDict(extra="ignore")
    ok: bool = True
    outputs: List[OutputItem] = Field(default_factory=list)
    execution_count: Optional[int] = None
    session_id: str = "default"
    action: str = ""
    request_id: Optional[str] = None
    world_size: int = 1
    ranks: Optional[List[Dict[str, Any]]] = None
    channel: Optional[str] = None   # <== echoed back for traceability