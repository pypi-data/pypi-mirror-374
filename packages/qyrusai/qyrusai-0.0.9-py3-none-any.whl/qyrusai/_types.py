from pydantic import BaseModel, Field, model_validator
from typing import List, Optional, Dict, Union, Any, Literal
from enum import Enum


# Pydantic for Input and Response
class Scenario(BaseModel):
    test_script_name: str
    test_script_objective: str
    reason_to_test: str
    criticality_description: str
    criticality_score: int


class CreateScenariosResponse(BaseModel):
    ok: bool
    message: str
    scenarios: Optional[List[Scenario]] = None


class JiraDetails(BaseModel):
    jira_endpoint: str
    jira_api_token: str
    jira_username: str
    jira_id: str


class UserDescription(BaseModel):
    user_description: str


class ApiBuilderResponse(BaseModel):
    swagger_dictionary: dict


class DataAmplifierResponse(BaseModel):
    data: Optional[Dict] = None
    status: bool
    message: str


class AssertionHeaderRequest(BaseModel):
    headers: Union[List, Dict, str]


# class AssertionHeaderResponse(BaseModel):
#     assertions: Union[List, Dict, str]
class AssertionResponseRequest(BaseModel):
    response: Union[List, Dict, str]


class AssertionAllRequest(BaseModel):
    headers: Union[List, Dict, str]
    response: Union[List, Dict, str]


# LLM Evaluator Models
class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW = "REVIEW"


# Common fields for both RAG and MCP requests
class EvaluationRequest(BaseModel):
    app_name: str = Field(..., description="Application name")
    qid: str = Field(..., description="Query ID")
    question: str = Field(..., description="The question being asked")
    answer: str = Field(..., description="The generated answer")
    citations: Optional[List[int]] = Field(default=None,
                                           description="Citation indices")
    gold_answers: Optional[List[str]] = Field(
        default=None, description="Gold standard answers")
    gold_passages: Optional[List[str]] = Field(
        default=None, description="Gold standard passages")
    params: Optional[Dict[str, Any]] = Field(default=None,
                                             description="Model parameters")
    meta: Optional[Dict[str, Any]] = Field(default=None,
                                           description="Metadata")


# RAG-specific data models
class RetrievedChunk(BaseModel):
    doc_id: str = Field(..., description="Document ID")
    text: str = Field(..., description="Chunk text")
    meta: Optional[Dict[str, Any]] = Field(default=None,
                                           description="Chunk metadata")
    score: Optional[float] = Field(default=None, description="Relevance score")


class SubRun(BaseModel):
    sub_qid: str = Field(..., description="Sub-query ID")
    question: str = Field(..., description="Sub-question")
    retrieved: Optional[List[RetrievedChunk]] = Field(
        default=None, description="Retrieved chunks")
    reranked: Optional[List[RetrievedChunk]] = Field(
        default=None, description="Reranked chunks")
    answer: str = Field(..., description="Sub-answer")
    citations: Optional[List[int]] = Field(default=None,
                                           description="Citation indices")


class RAGRequest(EvaluationRequest):
    retrieved: Optional[List[RetrievedChunk]] = Field(
        default=None, description="Retrieved chunks")
    reranked: Optional[List[RetrievedChunk]] = Field(
        default=None, description="Reranked chunks")
    decomposed: Optional[List[str]] = Field(default=None,
                                            description="Decomposed questions")
    subruns: Optional[List[SubRun]] = Field(
        default=None, description="Sub-runs for decomposed queries")


# MCP-specific data models
class ToolResultChunk(BaseModel):
    doc_id: str = Field(..., description="Document ID")
    text: str = Field(..., description="Chunk text")


class MCPTool(BaseModel):
    name: str = Field(..., description="Tool name")
    args: Dict[str, Any] = Field(..., description="Tool arguments")
    args_valid: Optional[bool] = Field(
        default=None,
        description=
        "Whether arguments are valid (user-provided, or auto-inferred if schema is provided)"
    )
    status: str = Field(..., description="Tool execution status")
    latency_ms: float = Field(..., description="Tool execution latency")
    result_text: Optional[str] = Field(default=None,
                                       description="Tool result text")
    result_chunks: Optional[List[ToolResultChunk]] = Field(
        default=None, description="Tool result chunks")


class MCPRequest(EvaluationRequest):
    tools: List[MCPTool]
    tool_schemas: Optional[Dict[str, Dict[str, Any]]] = None
    expected_tools: Optional[List[str]] = None

    @model_validator(mode='after')
    def check_args_validity_source(self):
        if not self.tool_schemas:
            for tool in self.tools:
                if tool.args_valid is None:
                    raise ValueError(
                        f"For tool '{tool.name}', 'args_valid' must be provided if 'tool_schemas' is not set."
                    )
        return self


# Judge output models - Evidence model for function calling
class JudgeEvidenceResponse(BaseModel):
    idx: int = Field(..., description="Source index")
    text: str = Field(..., description="Evidence text")


# Pydantic model for function calling schema (matches judge output exactly)
class JudgeEvaluationResponse(BaseModel):
    faithfulness: float = Field(...,
                                ge=0.0,
                                le=1.0,
                                description="Faithfulness score 0-1")
    relevance: float = Field(...,
                             ge=0.0,
                             le=1.0,
                             description="Relevance score 0-1")
    coverage: float = Field(...,
                            ge=0.0,
                            le=1.0,
                            description="Coverage score 0-1")
    citation_use: float = Field(...,
                                ge=0.0,
                                le=1.0,
                                description="Citation use score 0-1")
    hallucination_flags: List[str] = Field(
        default=[], description="List of hallucination flags")
    rationale: str = Field(..., description="Brief rationale for scores")
    evidence_spans: List[JudgeEvidenceResponse] = Field(
        default=[], description="Evidence spans from sources")


# Judge result model for internal use
class JudgeEvidence(BaseModel):
    idx: int = Field(..., description="Source index")
    text: str = Field(..., description="Evidence text")


class JudgeResult(BaseModel):
    faithfulness: Optional[float] = Field(default=None,
                                          description="Faithfulness score 0-1")
    relevance: Optional[float] = Field(default=None,
                                       description="Relevance score 0-1")
    coverage: Optional[float] = Field(default=None,
                                      description="Coverage score 0-1")
    citation_use: Optional[float] = Field(default=None,
                                          description="Citation use score 0-1")
    hallucination_flags: List[str] = Field(default=[],
                                           description="Hallucination flags")
    rationale: str = Field(..., description="Judge rationale")
    evidence_spans: List[JudgeEvidence] = Field(default=[],
                                                description="Evidence spans")


# Metrics output models
class Metrics(BaseModel):
    # Judge
    faithfulness: Optional[float] = None
    relevance: Optional[float] = None
    coverage: Optional[float] = None
    citation_use: Optional[float] = None
    # Embedding
    attribution_rate: Optional[float] = None
    answer_source_overlap: Optional[float] = None
    rerank_alignment_score: Optional[float] = None
    # Retrieval
    recall_at_10: Optional[float] = None
    precision_at_10: Optional[float] = None
    ndcg_at_10: Optional[float] = None
    # MCP health
    args_valid_rate: Optional[float] = None
    tool_error_rate: Optional[float] = None
    tool_retry_rate: Optional[float] = None
    tool_latency_p50: Optional[float] = None
    tool_latency_p75: Optional[float] = None
    # NEW MCP signals
    tool_relevance_max: Optional[float] = None
    tool_selection_quality: Optional[float] = None
    step_faithfulness: Optional[float] = None
    # NEW general
    answer_gold_similarity: Optional[float] = None


# Response models
class ScoreResponse(BaseModel):
    qid: str
    status: Status
    metrics: Metrics
    judge: Optional[JudgeResult] = None
    saved: bool
    diagnostics: Optional[Dict[str, Any]] = None


class BatchScoreResponse(BaseModel):
    results: List[Union[ScoreResponse,
                        Dict[str, Any]]] = Field(...,
                                                 description="Batch results")
    total: int = Field(..., description="Total items processed")
    successful: int = Field(..., description="Successfully processed items")
    failed: int = Field(..., description="Failed items")


# Summary models
class AppSummary(BaseModel):
    app_name: str = Field(..., description="Application name")
    window: str = Field(..., description="Time window")
    total_queries: int = Field(..., description="Total queries")
    metrics_summary: Dict[str,
                          Dict[str,
                               float]] = Field(...,
                                               description="Metrics summary")
    top_risk_queries: List[Dict[str,
                                Any]] = Field(...,
                                              description="High-risk queries")


class EvaluationItem(BaseModel):
    evaluation_type: str  # "RAG" or "MCP"
    data: Union[RAGRequest, MCPRequest]


class EvaluationDataset(BaseModel):
    dataset_type: str  # "RAG", "MCP", or "MIXED"
    items: List[EvaluationItem]


# Union type for requests
EvaluationRequestUnion = Union[RAGRequest, MCPRequest]
