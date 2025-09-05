from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


# ===== Base Models =====
class BaseResponse(BaseModel):
    """Base response model for API calls."""

    model_config = ConfigDict(extra="ignore")


class PaginatedResponse(BaseModel):
    """Generic paginated response model."""

    model_config = ConfigDict(extra="ignore")

    data: List[Any] = Field(description="Response data items")
    has_more: bool = Field(description="Whether more pages are available")
    limit: int = Field(description="Items per page limit")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")


# ===== Processing Rules =====
class PreProcessingRule(BaseModel):
    """Preprocessing rule configuration."""

    model_config = ConfigDict(extra="ignore")

    id: Literal["remove_extra_spaces", "remove_urls_emails"] = Field(
        description="Rule ID"
    )
    enabled: bool = Field(description="Whether the rule is enabled")


class Segmentation(BaseModel):
    """Text segmentation configuration."""

    model_config = ConfigDict(extra="ignore")

    separator: str = Field(default="\n", description="Segment separator")
    max_tokens: int = Field(default=1000, description="Maximum tokens per segment")


class SubchunkSegmentation(BaseModel):
    """Subchunk segmentation configuration for hierarchical mode."""

    model_config = ConfigDict(extra="ignore")

    separator: str = Field(default="***", description="Subchunk separator")
    max_tokens: int = Field(description="Maximum tokens per subchunk")
    chunk_overlap: Optional[int] = Field(None, description="Chunk overlap size")


class ProcessRuleConfig(BaseModel):
    """Custom process rule configuration."""

    model_config = ConfigDict(extra="ignore")

    pre_processing_rules: List[PreProcessingRule] = Field(
        description="Preprocessing rules"
    )
    segmentation: Segmentation = Field(description="Segmentation configuration")
    parent_mode: Optional[Literal["full-doc", "paragraph"]] = Field(
        None, description="Parent chunk recall mode"
    )
    subchunk_segmentation: Optional[SubchunkSegmentation] = Field(
        None, description="Subchunk segmentation config"
    )


class ProcessRule(BaseModel):
    """Processing rules for document indexing."""

    model_config = ConfigDict(extra="ignore")

    mode: Literal["automatic", "custom", "hierarchical"] = Field(
        description="Processing mode"
    )
    rules: Optional[ProcessRuleConfig] = Field(
        None, description="Custom processing rules"
    )


# ===== Retrieval Models =====
class RerankingModel(BaseModel):
    """Reranking model configuration."""

    model_config = ConfigDict(extra="ignore")

    reranking_provider_name: str = Field(description="Rerank model provider")
    reranking_model_name: str = Field(description="Rerank model name")


class MetadataCondition(BaseModel):
    """Metadata filtering condition."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(description="Metadata field name")
    comparison_operator: Literal[
        "contains",
        "not contains",
        "start with",
        "end with",
        "is",
        "is not",
        "empty",
        "not empty",
        "=",
        "≠",
        ">",
        "<",
        "≥",
        "≤",
        "before",
        "after",
    ] = Field(description="Comparison operator")
    value: Optional[Union[str, int, float]] = Field(
        None, description="Comparison value"
    )


class MetadataFilteringConditions(BaseModel):
    """Metadata filtering configuration."""

    model_config = ConfigDict(extra="ignore")

    logical_operator: Literal["and", "or"] = Field(description="Logical operator")
    conditions: List[MetadataCondition] = Field(description="Filtering conditions")


class RetrievalModel(BaseModel):
    """Retrieval model configuration."""

    model_config = ConfigDict(extra="ignore")

    search_method: Literal[
        "hybrid_search", "semantic_search", "full_text_search", "keyword_search"
    ] = Field(description="Search method")
    reranking_enable: Optional[bool] = Field(None, description="Enable reranking")
    reranking_mode: Optional[Literal["weighted_score", "reranking_model"]] = Field(
        None, description="Reranking mode"
    )
    reranking_model: Optional[RerankingModel] = Field(
        None, description="Reranking model config"
    )
    weights: Optional[float] = Field(None, description="Semantic search weight")
    top_k: Optional[int] = Field(None, description="Number of results to return")
    score_threshold_enabled: Optional[bool] = Field(
        None, description="Enable score threshold"
    )
    score_threshold: Optional[float] = Field(None, description="Score threshold")
    metadata_filtering_conditions: Optional[MetadataFilteringConditions] = Field(
        None, description="Metadata filtering"
    )


# ===== Core Data Models =====
class DataSourceInfo(BaseModel):
    """Information about the data source for a document."""

    model_config = ConfigDict(extra="ignore")

    upload_file_id: Optional[str] = Field(None, description="ID of uploaded file")


class Document(BaseModel):
    """Document information in a dataset."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Document ID")
    position: int = Field(description="Document position")
    data_source_type: str = Field(description="Data source type")
    data_source_info: Optional[DataSourceInfo] = Field(
        None, description="Data source info"
    )
    dataset_process_rule_id: Optional[str] = Field(None, description="Process rule ID")
    name: str = Field(description="Document name")
    created_from: str = Field(description="Creation source")
    created_by: str = Field(description="Creator ID")
    created_at: int = Field(description="Creation timestamp")
    tokens: Optional[int] = Field(None, description="Token count")
    indexing_status: str = Field(description="Indexing status")
    error: Optional[str] = Field(None, description="Error message")
    enabled: bool = Field(description="Whether document is enabled")
    disabled_at: Optional[int] = Field(None, description="Disabled timestamp")
    disabled_by: Optional[str] = Field(None, description="User who disabled")
    archived: bool = Field(description="Whether document is archived")
    display_status: Optional[str] = Field(None, description="Display status")
    word_count: Optional[int] = Field(None, description="Word count")
    hit_count: int = Field(description="Hit count")
    doc_form: str = Field(description="Document form")


class Dataset(BaseModel):
    """Dataset information."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Dataset ID")
    name: str = Field(description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    provider: Optional[str] = Field(None, description="Provider type")
    permission: str = Field(description="Permission level")
    data_source_type: Optional[str] = Field(None, description="Data source type")
    indexing_technique: Optional[str] = Field(None, description="Indexing technique")
    app_count: int = Field(description="Number of apps using this dataset")
    document_count: int = Field(description="Number of documents")
    word_count: int = Field(description="Total word count")
    created_by: str = Field(description="Creator ID")
    created_at: int = Field(description="Creation timestamp")
    updated_by: str = Field(description="Updater ID")
    updated_at: int = Field(description="Update timestamp")
    embedding_model: Optional[str] = Field(None, description="Embedding model name")
    embedding_model_provider: Optional[str] = Field(
        None, description="Embedding model provider"
    )
    embedding_available: Optional[bool] = Field(
        None, description="Whether embedding is available"
    )
    retrieval_model: Optional[RetrievalModel] = Field(
        None, description="Retrieval model configuration"
    )
    external_knowledge_api_id: Optional[str] = Field(
        None, description="External knowledge API ID"
    )
    external_knowledge_id: Optional[str] = Field(
        None, description="External knowledge ID"
    )


class Segment(BaseModel):
    """Document segment information."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Segment ID")
    position: int = Field(description="Segment position")
    document_id: str = Field(description="Document ID")
    content: str = Field(description="Segment content")
    answer: Optional[str] = Field(None, description="Answer content for Q&A mode")
    word_count: int = Field(description="Word count")
    tokens: int = Field(description="Token count")
    keywords: Optional[List[str]] = Field(None, description="Keywords")
    index_node_id: str = Field(description="Index node ID")
    index_node_hash: str = Field(description="Index node hash")
    hit_count: int = Field(description="Hit count")
    enabled: bool = Field(description="Whether segment is enabled")
    disabled_at: Optional[int] = Field(None, description="Disabled timestamp")
    disabled_by: Optional[str] = Field(None, description="User who disabled")
    status: str = Field(description="Segment status")
    created_by: str = Field(description="Creator ID")
    created_at: int = Field(description="Creation timestamp")
    indexing_at: int = Field(description="Indexing timestamp")
    completed_at: Optional[int] = Field(None, description="Completion timestamp")
    error: Optional[str] = Field(None, description="Error message")
    stopped_at: Optional[int] = Field(None, description="Stop timestamp")


class ChildChunk(BaseModel):
    """Child chunk information for hierarchical segments."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Child chunk ID")
    content: str = Field(description="Child chunk content")
    position: int = Field(description="Position in parent segment")
    word_count: int = Field(description="Word count")
    tokens: Optional[int] = Field(None, description="Token count")
    created_at: int = Field(description="Creation timestamp")
    updated_at: int = Field(description="Update timestamp")


class IndexingStatus(BaseModel):
    """Document indexing status information."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Document ID")
    indexing_status: str = Field(description="Indexing status")
    processing_started_at: Optional[float] = Field(
        None, description="Processing start time"
    )
    parsing_completed_at: Optional[float] = Field(
        None, description="Parsing completion time"
    )
    cleaning_completed_at: Optional[float] = Field(
        None, description="Cleaning completion time"
    )
    splitting_completed_at: Optional[float] = Field(
        None, description="Splitting completion time"
    )
    completed_at: Optional[float] = Field(None, description="Overall completion time")
    paused_at: Optional[float] = Field(None, description="Pause time")
    error: Optional[str] = Field(None, description="Error message")
    stopped_at: Optional[float] = Field(None, description="Stop time")
    completed_segments: int = Field(description="Number of completed segments")
    total_segments: int = Field(description="Total number of segments")


class Metadata(BaseModel):
    """Metadata field information."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Metadata field ID")
    type: str = Field(description="Field type")
    name: str = Field(description="Field name")
    use_count: Optional[int] = Field(None, description="Usage count")


class MetadataValue(BaseModel):
    """Metadata value information."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Metadata field ID")
    value: str = Field(description="Metadata value")
    name: str = Field(description="Field name")


class DocumentMetadata(BaseModel):
    """Document metadata association."""

    model_config = ConfigDict(extra="ignore")

    document_id: str = Field(description="Document ID")
    metadata_list: List[MetadataValue] = Field(description="Metadata values")


class RetrievalResult(BaseModel):
    """Knowledge base retrieval result."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Segment ID")
    content: str = Field(description="Segment content")
    score: float = Field(description="Relevance score")
    document_id: str = Field(description="Document ID")
    document_name: str = Field(description="Document name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")


class KnowledgeTag(BaseModel):
    """Knowledge base tag information."""

    model_config = ConfigDict(extra="ignore")

    id: str = Field(description="Tag ID")
    name: str = Field(description="Tag name")
    color: Optional[str] = Field(None, description="Tag color")
    created_at: Optional[int] = Field(None, description="Creation timestamp")
    updated_at: Optional[int] = Field(None, description="Update timestamp")
    binding_count: Optional[int] = Field(None, description="Number of bindings")


# ===== Request Models =====
class CreateDatasetRequest(BaseModel):
    """Request model for creating a new dataset."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    indexing_technique: Optional[Literal["high_quality", "economy"]] = Field(
        None, description="Indexing technique"
    )
    permission: Optional[Literal["only_me", "all_team_members", "partial_members"]] = (
        Field("only_me", description="Permission level")
    )
    provider: Optional[Literal["vendor", "external"]] = Field(
        "vendor", description="Provider type"
    )
    external_knowledge_api_id: Optional[str] = Field(
        None, description="External knowledge API ID"
    )
    external_knowledge_id: Optional[str] = Field(
        None, description="External knowledge ID"
    )
    embedding_model: Optional[str] = Field(None, description="Embedding model name")
    embedding_model_provider: Optional[str] = Field(
        None, description="Embedding model provider"
    )
    retrieval_model: Optional[RetrievalModel] = Field(
        None, description="Retrieval model config"
    )
    partial_member_list: Optional[List[str]] = Field(
        None, description="Partial member list"
    )


class UpdateDatasetRequest(BaseModel):
    """Request model for updating dataset."""

    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = Field(None, description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    indexing_technique: Optional[Literal["high_quality", "economy"]] = Field(
        None, description="Indexing technique"
    )
    permission: Optional[Literal["only_me", "all_team_members", "partial_members"]] = (
        Field(None, description="Permission level")
    )
    embedding_model_provider: Optional[str] = Field(
        None, description="Embedding model provider"
    )
    embedding_model: Optional[str] = Field(None, description="Embedding model")
    retrieval_model: Optional[RetrievalModel] = Field(
        None, description="Retrieval parameters"
    )
    partial_member_list: Optional[List[str]] = Field(
        None, description="Partial member list"
    )


class CreateDocumentByTextRequest(BaseModel):
    """Request model for creating document by text."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(description="Document name")
    text: str = Field(description="Document content")
    indexing_technique: Optional[Literal["high_quality", "economy"]] = Field(
        "high_quality", description="Indexing technique"
    )
    doc_form: Optional[Literal["text_model", "hierarchical_model", "qa_model"]] = Field(
        None, description="Document form"
    )
    doc_language: Optional[str] = Field(
        None, description="Document language for Q&A mode"
    )
    process_rule: Optional[ProcessRule] = Field(None, description="Processing rules")
    retrieval_model: Optional[RetrievalModel] = Field(
        None, description="Retrieval model config"
    )
    embedding_model: Optional[str] = Field(None, description="Embedding model name")
    embedding_model_provider: Optional[str] = Field(
        None, description="Embedding model provider"
    )


class CreateDocumentByFileData(BaseModel):
    """Data payload for file upload."""

    model_config = ConfigDict(extra="ignore")

    original_document_id: Optional[str] = Field(
        None, description="Original document ID for update"
    )
    indexing_technique: Optional[Literal["high_quality", "economy"]] = Field(
        "high_quality", description="Indexing technique"
    )
    doc_form: Optional[Literal["text_model", "hierarchical_model", "qa_model"]] = Field(
        None, description="Document form"
    )
    doc_language: Optional[str] = Field(
        None, description="Document language for Q&A mode"
    )
    process_rule: Optional[ProcessRule] = Field(None, description="Processing rules")
    retrieval_model: Optional[RetrievalModel] = Field(
        None, description="Retrieval model config"
    )
    embedding_model: Optional[str] = Field(None, description="Embedding model name")
    embedding_model_provider: Optional[str] = Field(
        None, description="Embedding model provider"
    )


class UpdateDocumentByTextRequest(BaseModel):
    """Request model for updating document by text."""

    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = Field(None, description="Document name")
    text: Optional[str] = Field(None, description="Document content")
    process_rule: Optional[ProcessRule] = Field(None, description="Processing rules")


class UpdateDocumentByFileData(BaseModel):
    """Data payload for file update."""

    model_config = ConfigDict(extra="ignore")

    name: Optional[str] = Field(None, description="Document name")
    process_rule: Optional[ProcessRule] = Field(None, description="Processing rules")


class BatchDocumentStatusRequest(BaseModel):
    """Request model for batch document status update."""

    model_config = ConfigDict(extra="ignore")

    document_ids: List[str] = Field(description="Document ID list")


class CreateSegmentRequest(BaseModel):
    """Request model for creating segments."""

    model_config = ConfigDict(extra="ignore")

    segments: List[Dict[str, Any]] = Field(description="Segment data list")


class UpdateSegmentRequest(BaseModel):
    """Request model for updating segment."""

    model_config = ConfigDict(extra="ignore")

    segment: Dict[str, Any] = Field(description="Segment data")


class CreateChildChunkRequest(BaseModel):
    """Request model for creating child chunk."""

    model_config = ConfigDict(extra="ignore")

    content: str = Field(description="Child chunk content")


class UpdateChildChunkRequest(BaseModel):
    """Request model for updating child chunk."""

    model_config = ConfigDict(extra="ignore")

    content: str = Field(description="Child chunk content")


class RetrievalRequest(BaseModel):
    """Request model for knowledge base retrieval."""

    model_config = ConfigDict(extra="ignore")

    query: str = Field(description="Search query")
    retrieval_model: Optional[RetrievalModel] = Field(
        None, description="Retrieval parameters"
    )
    external_retrieval_model: Optional[Dict[str, Any]] = Field(
        None, description="External retrieval model"
    )


class CreateMetadataRequest(BaseModel):
    """Request model for creating metadata field."""

    model_config = ConfigDict(extra="ignore")

    type: str = Field(description="Metadata type")
    name: str = Field(description="Metadata name")


class UpdateMetadataRequest(BaseModel):
    """Request model for updating metadata field."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(description="Metadata name")


class UpdateDocumentMetadataRequest(BaseModel):
    """Request model for updating document metadata."""

    model_config = ConfigDict(extra="ignore")

    operation_data: List[DocumentMetadata] = Field(
        description="Document metadata operations"
    )


class CreateKnowledgeTagRequest(BaseModel):
    """Request model for creating knowledge tag."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(description="Tag name", max_length=50)


class UpdateKnowledgeTagRequest(BaseModel):
    """Request model for updating knowledge tag."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(description="Tag name", max_length=50)
    tag_id: str = Field(description="Tag ID")


class DeleteKnowledgeTagRequest(BaseModel):
    """Request model for deleting knowledge tag."""

    model_config = ConfigDict(extra="ignore")

    tag_id: str = Field(description="Tag ID")


class BindDatasetToTagRequest(BaseModel):
    """Request model for binding dataset to knowledge tag."""

    model_config = ConfigDict(extra="ignore")

    tag_ids: List[str] = Field(description="Tag ID list")
    target_id: str = Field(description="Dataset ID")


class UnbindDatasetFromTagRequest(BaseModel):
    """Request model for unbinding dataset from knowledge tag."""

    model_config = ConfigDict(extra="ignore")

    tag_id: str = Field(description="Tag ID")
    target_id: str = Field(description="Dataset ID")


# ===== Response Models =====
class DocumentResponse(BaseModel):
    """Response model for document operations."""

    model_config = ConfigDict(extra="ignore")

    document: Document = Field(description="Document information")
    batch: str = Field(description="Batch ID for tracking")


class SegmentResponse(BaseModel):
    """Response model for segment operations."""

    model_config = ConfigDict(extra="ignore")

    data: List[Segment] = Field(description="Segment list")
    doc_form: str = Field(description="Document form")


class ChildChunkResponse(BaseModel):
    """Response model for child chunk operations."""

    model_config = ConfigDict(extra="ignore")

    data: List[ChildChunk] = Field(description="Child chunk list")


class MetadataListResponse(BaseModel):
    """Response model for metadata list."""

    model_config = ConfigDict(extra="ignore")

    doc_metadata: List[Metadata] = Field(description="Metadata fields")
    built_in_field_enabled: bool = Field(description="Built-in field enabled status")


class IndexingStatusResponse(BaseModel):
    """Response model for indexing status."""

    model_config = ConfigDict(extra="ignore")

    data: List[IndexingStatus] = Field(description="Indexing status list")


class RetrievalResponse(BaseModel):
    """Response model for retrieval operations."""

    model_config = ConfigDict(extra="ignore")

    query: Dict[str, Any] = Field(description="Search query object")
    retrieval_model: Optional[Dict[str, Any]] = Field(
        None, description="Retrieval model used"
    )
    records: List[Dict[str, Any]] = Field(description="Retrieved records")


class EmbeddingModelResponse(BaseModel):
    """Response model for embedding model list."""

    model_config = ConfigDict(extra="ignore")

    data: List[Dict[str, Any]] = Field(description="Embedding model list")


class SuccessResponse(BaseModel):
    """Standard success response model."""

    model_config = ConfigDict(extra="ignore")

    result: Literal["success"] = Field("success", description="Operation result status")


class ErrorResponse(BaseModel):
    """Standard error response model."""

    model_config = ConfigDict(extra="ignore")

    code: str = Field(description="Error code")
    status: int = Field(description="HTTP status code")
    message: str = Field(description="Error message")
