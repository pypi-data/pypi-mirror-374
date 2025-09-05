from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from .base_client import BaseClient
from .models import (
    BatchDocumentStatusRequest,
    BindDatasetToTagRequest,
    ChildChunkResponse,
    CreateChildChunkRequest,
    CreateDatasetRequest,
    CreateDocumentByFileData,
    CreateDocumentByTextRequest,
    CreateKnowledgeTagRequest,
    CreateMetadataRequest,
    CreateSegmentRequest,
    Dataset,
    DeleteKnowledgeTagRequest,
    Document,
    DocumentResponse,
    EmbeddingModelResponse,
    IndexingStatusResponse,
    KnowledgeTag,
    Metadata,
    MetadataListResponse,
    PaginatedResponse,
    ProcessRule,
    RetrievalModel,
    RetrievalRequest,
    RetrievalResponse,
    SegmentResponse,
    UnbindDatasetFromTagRequest,
    UpdateChildChunkRequest,
    UpdateDatasetRequest,
    UpdateDocumentByFileData,
    UpdateDocumentByTextRequest,
    UpdateDocumentMetadataRequest,
    UpdateKnowledgeTagRequest,
    UpdateMetadataRequest,
    UpdateSegmentRequest,
)


class DifyDatasetClient(BaseClient):
    """Dify Knowledge Base API client for comprehensive knowledge management.

    This client provides access to all Dify Knowledge Base API endpoints including:
    - Dataset management (CRUD operations)
    - Document management (text/file upload, update, delete)
    - Segment management (create, update, delete, query)
    - Child chunk management (hierarchical segments)
    - Metadata management (field definition, document association)
    - Knowledge base retrieval and search
    - Knowledge tags management
    """

    def __init__(
        self, api_key: str, base_url: str = "https://api.dify.ai", timeout: float = 30.0
    ):
        """Initialize the Dify Knowledge client.

        Args:
            api_key: Dify API key for authentication
            base_url: Base URL for Dify API (default: https://api.dify.ai)
            timeout: Request timeout in seconds (default: 30.0)
        """
        super().__init__(api_key, base_url, timeout)

    # ===== Dataset Management =====
    def create_dataset(
        self,
        name: str,
        description: Optional[str] = None,
        indexing_technique: Optional[Literal["high_quality", "economy"]] = None,
        permission: Optional[
            Literal["only_me", "all_team_members", "partial_members"]
        ] = "only_me",
        provider: Optional[Literal["vendor", "external"]] = "vendor",
        external_knowledge_api_id: Optional[str] = None,
        external_knowledge_id: Optional[str] = None,
        embedding_model: Optional[str] = None,
        embedding_model_provider: Optional[str] = None,
        retrieval_model: Optional[RetrievalModel] = None,
        partial_member_list: Optional[List[str]] = None,
    ) -> Dataset:
        """Create an empty dataset.

        Args:
            name: Dataset name (required)
            description: Dataset description (optional)
            indexing_technique: Indexing mode - 'high_quality' or 'economy' (optional)
            permission: Permission level (optional, default: 'only_me')
            provider: Provider type (optional, default: 'vendor')
            external_knowledge_api_id: External knowledge API ID (optional)
            external_knowledge_id: External knowledge ID (optional)
            embedding_model: Embedding model name (optional)
            embedding_model_provider: Embedding model provider (optional)
            retrieval_model: Retrieval model configuration (optional)
            partial_member_list: Partial member list (optional)

        Returns:
            Created dataset information

        Raises:
            DifyAPIError: For API errors
        """
        request = CreateDatasetRequest(
            name=name,
            description=description,
            indexing_technique=indexing_technique,
            permission=permission,
            provider=provider,
            external_knowledge_api_id=external_knowledge_api_id,
            external_knowledge_id=external_knowledge_id,
            embedding_model=embedding_model,
            embedding_model_provider=embedding_model_provider,
            retrieval_model=retrieval_model,
            partial_member_list=partial_member_list,
        )
        response = self.post("/v1/datasets", json=request.model_dump(exclude_none=True))
        return Dataset(**response)

    def list_datasets(
        self,
        keyword: Optional[str] = None,
        tag_ids: Optional[List[str]] = None,
        page: int = 1,
        limit: int = 20,
        include_all: bool = False,
    ) -> PaginatedResponse:
        """Get paginated list of datasets.

        Args:
            keyword: Search keyword (optional)
            tag_ids: Tag ID list (optional)
            page: Page number, starting from 1 (default: 1)
            limit: Items per page, max 100 (default: 20)
            include_all: Include all datasets (only for owners) (default: False)

        Returns:
            Paginated response containing dataset list

        Raises:
            DifyAPIError: For API errors
        """
        params = {"page": page, "limit": limit, "include_all": include_all}
        if keyword:
            params["keyword"] = keyword
        if tag_ids:
            params["tag_ids"] = tag_ids

        response = self.get("/v1/datasets", params=params)
        return PaginatedResponse(**response)

    def get_dataset(self, dataset_id: str) -> Dataset:
        """Get dataset details.

        Args:
            dataset_id: Dataset ID

        Returns:
            Dataset information

        Raises:
            DifyNotFoundError: If dataset not found
            DifyAPIError: For other API errors
        """
        response = self.get(f"/v1/datasets/{dataset_id}")
        return Dataset(**response)

    def update_dataset(
        self,
        dataset_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        indexing_technique: Optional[Literal["high_quality", "economy"]] = None,
        permission: Optional[
            Literal["only_me", "all_team_members", "partial_members"]
        ] = None,
        embedding_model_provider: Optional[str] = None,
        embedding_model: Optional[str] = None,
        retrieval_model: Optional[RetrievalModel] = None,
        partial_member_list: Optional[List[str]] = None,
    ) -> Dataset:
        """Update dataset details.

        Args:
            dataset_id: Dataset ID
            name: Dataset name (optional)
            description: Dataset description (optional)
            indexing_technique: Indexing mode (optional)
            permission: Permission level (optional)
            embedding_model_provider: Embedding model provider (optional)
            embedding_model: Embedding model (optional)
            retrieval_model: Retrieval parameters (optional)
            partial_member_list: Partial member list (optional)

        Returns:
            Updated dataset information

        Raises:
            DifyNotFoundError: If dataset not found
            DifyAPIError: For other API errors
        """
        request = UpdateDatasetRequest(
            name=name,
            description=description,
            indexing_technique=indexing_technique,
            permission=permission,
            embedding_model_provider=embedding_model_provider,
            embedding_model=embedding_model,
            retrieval_model=retrieval_model,
            partial_member_list=partial_member_list,
        )
        response = self.patch(
            f"/v1/datasets/{dataset_id}", json=request.model_dump(exclude_none=True)
        )
        return Dataset(**response)

    def delete_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Delete a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If dataset not found
            DifyAPIError: For other API errors
        """
        return self.delete(f"/v1/datasets/{dataset_id}")

    # ===== Document Management =====
    def create_document_by_text(
        self,
        dataset_id: str,
        name: str,
        text: str,
        indexing_technique: Optional[
            Literal["high_quality", "economy"]
        ] = "high_quality",
        doc_form: Optional[
            Literal["text_model", "hierarchical_model", "qa_model"]
        ] = None,
        doc_language: Optional[str] = None,
        process_rule: Optional[ProcessRule] = None,
        retrieval_model: Optional[RetrievalModel] = None,
        embedding_model: Optional[str] = None,
        embedding_model_provider: Optional[str] = None,
    ) -> DocumentResponse:
        """Create a document from text content.

        Args:
            dataset_id: Dataset ID
            name: Document name
            text: Document text content
            indexing_technique: Indexing technique (default: 'high_quality')
            doc_form: Document form (optional)
            doc_language: Document language for Q&A mode (optional)
            process_rule: Processing rules (optional)
            retrieval_model: Retrieval model config (optional)
            embedding_model: Embedding model name (optional)
            embedding_model_provider: Embedding model provider (optional)

        Returns:
            Created document information with batch ID

        Raises:
            DifyValidationError: If parameters are invalid
            DifyAPIError: For other API errors
        """
        request = CreateDocumentByTextRequest(
            name=name,
            text=text,
            indexing_technique=indexing_technique,
            doc_form=doc_form,
            doc_language=doc_language,
            process_rule=process_rule,
            retrieval_model=retrieval_model,
            embedding_model=embedding_model,
            embedding_model_provider=embedding_model_provider,
        )
        response = self.post(
            f"/v1/datasets/{dataset_id}/document/create-by-text",
            json=request.model_dump(exclude_none=True),
        )
        return DocumentResponse(**response)

    def create_document_by_file(
        self,
        dataset_id: str,
        file_path: Union[str, Path],
        original_document_id: Optional[str] = None,
        indexing_technique: Optional[
            Literal["high_quality", "economy"]
        ] = "high_quality",
        doc_form: Optional[
            Literal["text_model", "hierarchical_model", "qa_model"]
        ] = None,
        doc_language: Optional[str] = None,
        process_rule: Optional[ProcessRule] = None,
        retrieval_model: Optional[RetrievalModel] = None,
        embedding_model: Optional[str] = None,
        embedding_model_provider: Optional[str] = None,
    ) -> DocumentResponse:
        """Create a document from file upload.

        Args:
            dataset_id: Dataset ID
            file_path: Path to the file to upload
            original_document_id: Original document ID for update (optional)
            indexing_technique: Indexing technique (default: 'high_quality')
            doc_form: Document form (optional)
            doc_language: Document language for Q&A mode (optional)
            process_rule: Processing rules (optional)
            retrieval_model: Retrieval model config (optional)
            embedding_model: Embedding model name (optional)
            embedding_model_provider: Embedding model provider (optional)

        Returns:
            Created document information with batch ID

        Raises:
            FileNotFoundError: If file doesn't exist
            DifyValidationError: If file type not supported or too large
            DifyAPIError: For other API errors
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        data_payload = CreateDocumentByFileData(
            original_document_id=original_document_id,
            indexing_technique=indexing_technique,
            doc_form=doc_form,
            doc_language=doc_language,
            process_rule=process_rule,
            retrieval_model=retrieval_model,
            embedding_model=embedding_model,
            embedding_model_provider=embedding_model_provider,
        )

        json_data = data_payload.model_dump_json(exclude_none=True)

        with open(file_path, "rb") as file_handle:
            files = {
                "file": (file_path.name, file_handle, "application/octet-stream"),
                "data": ("", json_data, "application/json"),
            }
            response = self.post(
                f"/v1/datasets/{dataset_id}/document/create-by-file", files=files
            )

        return DocumentResponse(**response)

    def list_documents(
        self,
        dataset_id: str,
        keyword: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> PaginatedResponse:
        """Get list of documents in a dataset.

        Args:
            dataset_id: Dataset ID
            keyword: Search keyword for document names (optional)
            page: Page number (default: 1)
            limit: Items per page, range 1-100 (default: 20)

        Returns:
            Paginated list of documents

        Raises:
            DifyNotFoundError: If dataset not found
            DifyAPIError: For other API errors
        """
        params = {"page": page, "limit": limit}
        if keyword:
            params["keyword"] = keyword

        response = self.get(f"/v1/datasets/{dataset_id}/documents", params=params)
        return PaginatedResponse(**response)

    def get_document(
        self,
        dataset_id: str,
        document_id: str,
        metadata: Literal["all", "only", "without"] = "all",
    ) -> Document:
        """Get document details.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            metadata: Metadata filter condition (default: 'all')

        Returns:
            Document information

        Raises:
            DifyNotFoundError: If dataset or document not found
            DifyAPIError: For other API errors
        """
        params = {"metadata": metadata}
        response = self.get(
            f"/v1/datasets/{dataset_id}/documents/{document_id}", params=params
        )
        return Document(**response)

    def update_document_by_text(
        self,
        dataset_id: str,
        document_id: str,
        name: Optional[str] = None,
        text: Optional[str] = None,
        process_rule: Optional[ProcessRule] = None,
    ) -> DocumentResponse:
        """Update a document with text content.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            name: Updated document name (optional)
            text: Updated document text content (optional)
            process_rule: Processing rules (optional)

        Returns:
            Updated document information

        Raises:
            DifyNotFoundError: If dataset or document not found
            DifyAPIError: For other API errors
        """
        request = UpdateDocumentByTextRequest(
            name=name,
            text=text,
            process_rule=process_rule,
        )
        response = self.post(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/update-by-text",
            json=request.model_dump(exclude_none=True),
        )
        return DocumentResponse(**response)

    def update_document_by_file(
        self,
        dataset_id: str,
        document_id: str,
        file_path: Union[str, Path],
        name: Optional[str] = None,
        process_rule: Optional[ProcessRule] = None,
    ) -> DocumentResponse:
        """Update a document with file content.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            file_path: Path to the new file
            name: Updated document name (optional)
            process_rule: Processing rules (optional)

        Returns:
            Updated document information

        Raises:
            FileNotFoundError: If file doesn't exist
            DifyNotFoundError: If dataset or document not found
            DifyValidationError: If file type not supported or too large
            DifyAPIError: For other API errors
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        data_payload = UpdateDocumentByFileData(
            name=name,
            process_rule=process_rule,
        )

        json_data = data_payload.model_dump_json(exclude_none=True)

        with open(file_path, "rb") as file_handle:
            files = {
                "file": (file_path.name, file_handle, "application/octet-stream"),
                "data": ("", json_data, "application/json"),
            }
            response = self.post(
                f"/v1/datasets/{dataset_id}/documents/{document_id}/update-by-file",
                files=files,
            )

        return DocumentResponse(**response)

    def delete_document(self, dataset_id: str, document_id: str) -> Dict[str, Any]:
        """Delete a document.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If dataset or document not found
            DifyAPIError: For other API errors
        """
        return self.delete(f"/v1/datasets/{dataset_id}/documents/{document_id}")

    def get_document_indexing_status(
        self, dataset_id: str, batch: str
    ) -> IndexingStatusResponse:
        """Get document indexing status (progress).

        Args:
            dataset_id: Dataset ID
            batch: Upload batch number from document creation

        Returns:
            Indexing status information

        Raises:
            DifyNotFoundError: If dataset or batch not found
            DifyAPIError: For other API errors
        """
        response = self.get(
            f"/v1/datasets/{dataset_id}/documents/{batch}/indexing-status"
        )
        return IndexingStatusResponse(**response)

    def batch_update_document_status(
        self,
        dataset_id: str,
        action: Literal["enable", "disable", "archive", "un_archive"],
        document_ids: List[str],
    ) -> Dict[str, Any]:
        """Update status of multiple documents.

        Args:
            dataset_id: Dataset ID
            action: Action to perform - 'enable', 'disable', 'archive', 'un_archive'
            document_ids: List of document IDs

        Returns:
            Success response

        Raises:
            DifyValidationError: If action is invalid
            DifyNotFoundError: If dataset not found
            DifyAPIError: For other API errors
        """
        request = BatchDocumentStatusRequest(document_ids=document_ids)
        response = self.patch(
            f"/v1/datasets/{dataset_id}/documents/status/{action}",
            json=request.model_dump(),
        )
        return response

    # ===== Segment Management =====
    def create_segments(
        self,
        dataset_id: str,
        document_id: str,
        segments: List[Dict[str, Any]],
    ) -> SegmentResponse:
        """Create new segments for a document.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segments: List of segment data, each containing:
                - content (str): Text content/question content (required)
                - answer (str): Answer content (optional, for Q&A mode)
                - keywords (list): Keywords (optional)

        Returns:
            Created segments information

        Raises:
            DifyNotFoundError: If dataset or document not found
            DifyValidationError: If segment data is invalid
            DifyAPIError: For other API errors
        """
        request = CreateSegmentRequest(segments=segments)
        response = self.post(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/segments",
            json=request.model_dump(),
        )
        return SegmentResponse(**response)

    def list_segments(
        self,
        dataset_id: str,
        document_id: str,
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> SegmentResponse:
        """Get list of segments in a document.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            keyword: Search keyword (optional)
            status: Search status, e.g., 'completed' (optional)
            page: Page number (default: 1)
            limit: Items per page, range 1-100 (default: 20)

        Returns:
            List of segments

        Raises:
            DifyNotFoundError: If dataset or document not found
            DifyAPIError: For other API errors
        """
        params = {"page": page, "limit": limit}
        if keyword:
            params["keyword"] = keyword
        if status:
            params["status"] = status

        response = self.get(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/segments", params=params
        )
        return SegmentResponse(**response)

    def get_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
    ) -> Dict[str, Any]:
        """Get document segment details.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segment_id: Segment ID

        Returns:
            Segment details

        Raises:
            DifyNotFoundError: If dataset, document, or segment not found
            DifyAPIError: For other API errors
        """
        return self.get(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"
        )

    def update_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        segment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a document segment.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segment_id: Segment ID
            segment_data: Updated segment data containing:
                - content (str): Text content/question content (required)
                - answer (str): Answer content (optional, for Q&A mode)
                - keywords (list): Keywords (optional)
                - enabled (bool): Whether segment is enabled (optional)
                - regenerate_child_chunks (bool): Whether to regenerate child segments (optional)

        Returns:
            Updated segment information

        Raises:
            DifyNotFoundError: If dataset, document, or segment not found
            DifyValidationError: If segment data is invalid
            DifyAPIError: For other API errors
        """
        request = UpdateSegmentRequest(segment=segment_data)
        response = self.post(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}",
            json=request.model_dump(),
        )
        return response

    def delete_segment(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
    ) -> Dict[str, Any]:
        """Delete a document segment.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segment_id: Segment ID

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If dataset, document, or segment not found
            DifyAPIError: For other API errors
        """
        return self.delete(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"
        )

    # ===== Child Chunk Management (Hierarchical Segments) =====
    def create_child_chunk(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """Create a new child chunk for a document segment.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segment_id: Parent segment ID
            content: Child chunk content

        Returns:
            Created child chunk information

        Raises:
            DifyNotFoundError: If dataset, document, or segment not found
            DifyValidationError: If content is invalid
            DifyAPIError: For other API errors
        """
        request = CreateChildChunkRequest(content=content)
        return self.post(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks",
            json=request.model_dump(),
        )

    def list_child_chunks(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        keyword: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> ChildChunkResponse:
        """Get list of child chunks for a document segment.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segment_id: Parent segment ID
            keyword: Search keyword (optional)
            page: Page number (default: 1)
            limit: Items per page, max 100 (default: 20)

        Returns:
            List of child chunks

        Raises:
            DifyNotFoundError: If dataset, document, or segment not found
            DifyAPIError: For other API errors
        """
        params = {"page": page, "limit": limit}
        if keyword:
            params["keyword"] = keyword

        response = self.get(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks",
            params=params,
        )
        return ChildChunkResponse(**response)

    def update_child_chunk(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        child_chunk_id: str,
        content: str,
    ) -> Dict[str, Any]:
        """Update a document child chunk.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segment_id: Parent segment ID
            child_chunk_id: Child chunk ID
            content: Updated child chunk content

        Returns:
            Updated child chunk information

        Raises:
            DifyNotFoundError: If dataset, document, segment, or child chunk not found
            DifyValidationError: If content is invalid
            DifyAPIError: For other API errors
        """
        request = UpdateChildChunkRequest(content=content)
        return self.patch(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks/{child_chunk_id}",
            json=request.model_dump(),
        )

    def delete_child_chunk(
        self,
        dataset_id: str,
        document_id: str,
        segment_id: str,
        child_chunk_id: str,
    ) -> Dict[str, Any]:
        """Delete a document child chunk.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID
            segment_id: Parent segment ID
            child_chunk_id: Child chunk ID

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If dataset, document, segment, or child chunk not found
            DifyAPIError: For other API errors
        """
        return self.delete(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}/child_chunks/{child_chunk_id}"
        )

    # ===== Knowledge Base Retrieval =====
    def retrieve(
        self,
        dataset_id: str,
        query: str,
        retrieval_model: Optional[RetrievalModel] = None,
        external_retrieval_model: Optional[Dict[str, Any]] = None,
    ) -> RetrievalResponse:
        """Retrieve knowledge base content.

        Args:
            dataset_id: Dataset ID
            query: Search query
            retrieval_model: Retrieval parameters (optional)
            external_retrieval_model: External retrieval model (optional)

        Returns:
            Retrieval results

        Raises:
            DifyNotFoundError: If dataset not found
            DifyValidationError: If query is invalid
            DifyAPIError: For other API errors
        """
        request = RetrievalRequest(
            query=query,
            retrieval_model=retrieval_model,
            external_retrieval_model=external_retrieval_model,
        )
        response = self.post(
            f"/v1/datasets/{dataset_id}/retrieve",
            json=request.model_dump(exclude_none=True),
        )
        return RetrievalResponse(**response)

    # ===== File Management =====
    def get_upload_file(
        self,
        dataset_id: str,
        document_id: str,
    ) -> Dict[str, Any]:
        """Get uploaded file information.

        Args:
            dataset_id: Dataset ID
            document_id: Document ID

        Returns:
            File information

        Raises:
            DifyNotFoundError: If dataset or document not found
            DifyAPIError: For other API errors
        """
        return self.get(
            f"/v1/datasets/{dataset_id}/documents/{document_id}/upload-file"
        )

    # ===== Metadata Management =====
    def create_metadata_field(
        self,
        dataset_id: str,
        field_type: str,
        name: str,
    ) -> Metadata:
        """Create a metadata field for a dataset.

        Args:
            dataset_id: Dataset ID
            field_type: Metadata type (string, number, time)
            name: Field name

        Returns:
            Created metadata field information

        Raises:
            DifyNotFoundError: If dataset not found
            DifyValidationError: If field data is invalid
            DifyAPIError: For other API errors
        """
        request = CreateMetadataRequest(type=field_type, name=name)
        response = self.post(
            f"/v1/datasets/{dataset_id}/metadata", json=request.model_dump()
        )
        return Metadata(**response)

    def update_metadata_field(
        self,
        dataset_id: str,
        metadata_id: str,
        name: str,
    ) -> Metadata:
        """Update a metadata field.

        Args:
            dataset_id: Dataset ID
            metadata_id: Metadata field ID
            name: Updated field name

        Returns:
            Updated metadata field information

        Raises:
            DifyNotFoundError: If dataset or metadata field not found
            DifyValidationError: If field data is invalid
            DifyAPIError: For other API errors
        """
        request = UpdateMetadataRequest(name=name)
        response = self.patch(
            f"/v1/datasets/{dataset_id}/metadata/{metadata_id}",
            json=request.model_dump(),
        )
        return Metadata(**response)

    def delete_metadata_field(
        self,
        dataset_id: str,
        metadata_id: str,
    ) -> Dict[str, Any]:
        """Delete a metadata field.

        Args:
            dataset_id: Dataset ID
            metadata_id: Metadata field ID

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If dataset or metadata field not found
            DifyAPIError: For other API errors
        """
        return self.delete(f"/v1/datasets/{dataset_id}/metadata/{metadata_id}")

    def toggle_built_in_metadata_field(
        self,
        dataset_id: str,
        action: Literal["disable", "enable"],
    ) -> Dict[str, Any]:
        """Enable or disable built-in metadata fields.

        Args:
            dataset_id: Dataset ID
            action: Action to perform - 'disable' or 'enable'

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If dataset not found
            DifyValidationError: If action is invalid
            DifyAPIError: For other API errors
        """
        return self.post(f"/v1/datasets/{dataset_id}/metadata/built-in/{action}")

    def update_document_metadata(
        self,
        dataset_id: str,
        operation_data: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Update document metadata values.

        Args:
            dataset_id: Dataset ID
            operation_data: List of document metadata operations, each containing:
                - document_id (str): Document ID
                - metadata_list (list): Metadata list with id, value, name

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If dataset not found
            DifyValidationError: If metadata is invalid
            DifyAPIError: For other API errors
        """
        request = UpdateDocumentMetadataRequest(operation_data=operation_data)
        return self.post(
            f"/v1/datasets/{dataset_id}/documents/metadata", json=request.model_dump()
        )

    def list_metadata_fields(self, dataset_id: str) -> MetadataListResponse:
        """Get list of metadata fields for a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            List of metadata fields

        Raises:
            DifyNotFoundError: If dataset not found
            DifyAPIError: For other API errors
        """
        response = self.get(f"/v1/datasets/{dataset_id}/metadata")
        return MetadataListResponse(**response)

    # ===== Knowledge Tags Management =====
    def create_knowledge_tag(self, name: str) -> KnowledgeTag:
        """Create a new knowledge type tag.

        Args:
            name: Tag name (max 50 characters)

        Returns:
            Created tag information

        Raises:
            DifyValidationError: If name is invalid or too long
            DifyAPIError: For other API errors
        """
        request = CreateKnowledgeTagRequest(name=name)
        response = self.post("/v1/datasets/tags", json=request.model_dump())
        return KnowledgeTag(**response)

    def list_knowledge_tags(self) -> List[KnowledgeTag]:
        """Get list of knowledge type tags.

        Returns:
            List of knowledge tags

        Raises:
            DifyAPIError: For API errors
        """
        response = self.get("/v1/datasets/tags")
        # Handle both list and dict response formats
        if isinstance(response, list):
            return [KnowledgeTag(**tag) for tag in response]
        else:
            return [KnowledgeTag(**tag) for tag in response.get("data", [])]

    def update_knowledge_tag(self, tag_id: str, name: str) -> KnowledgeTag:
        """Update knowledge type tag name.

        Args:
            tag_id: Tag ID
            name: New tag name (max 50 characters)

        Returns:
            Updated tag information

        Raises:
            DifyNotFoundError: If tag not found
            DifyValidationError: If name is invalid
            DifyAPIError: For other API errors
        """
        request = UpdateKnowledgeTagRequest(name=name, tag_id=tag_id)
        response = self.patch("/v1/datasets/tags", json=request.model_dump())
        return KnowledgeTag(**response)

    def delete_knowledge_tag(self, tag_id: str) -> Dict[str, Any]:
        """Delete a knowledge type tag.

        Args:
            tag_id: Tag ID

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If tag not found
            DifyAPIError: For other API errors
        """

        request = DeleteKnowledgeTagRequest(tag_id=tag_id)
        return self.delete("/v1/datasets/tags", json=request.model_dump())

    def bind_dataset_to_tag(
        self,
        dataset_id: str,
        tag_ids: List[str],
    ) -> Dict[str, Any]:
        """Bind dataset to knowledge type tags.

        Args:
            dataset_id: Dataset ID
            tag_ids: List of tag IDs

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If dataset or tags not found
            DifyValidationError: If tag IDs are invalid
            DifyAPIError: For other API errors
        """
        request = BindDatasetToTagRequest(tag_ids=tag_ids, target_id=dataset_id)
        return self.post("/v1/datasets/tags/binding", json=request.model_dump())

    def unbind_dataset_from_tag(
        self,
        dataset_id: str,
        tag_id: str,
    ) -> Dict[str, Any]:
        """Unbind dataset from knowledge type tag.

        Args:
            dataset_id: Dataset ID
            tag_id: Tag ID

        Returns:
            Success response

        Raises:
            DifyNotFoundError: If dataset or tag not found
            DifyAPIError: For other API errors
        """
        request = UnbindDatasetFromTagRequest(tag_id=tag_id, target_id=dataset_id)
        return self.post("/v1/datasets/tags/unbinding", json=request.model_dump())

    def get_dataset_tags(self, dataset_id: str) -> List[KnowledgeTag]:
        """Get tags bound to a dataset.

        Args:
            dataset_id: Dataset ID

        Returns:
            List of bound tags

        Raises:
            DifyNotFoundError: If dataset not found
            DifyAPIError: For other API errors
        """
        response = self.get(f"/v1/datasets/{dataset_id}/tags")
        # Handle both list and dict response formats
        if isinstance(response, list):
            return [KnowledgeTag(**tag) for tag in response]
        else:
            return [KnowledgeTag(**tag) for tag in response.get("data", [])]

    # ===== Embedding Models =====
    def list_embedding_models(self) -> EmbeddingModelResponse:
        """Get list of available text embedding models.

        Returns:
            List of available embedding models

        Raises:
            DifyAPIError: For API errors
        """
        response = self.get("/v1/workspaces/current/models/model-types/text-embedding")
        return EmbeddingModelResponse(**response)
