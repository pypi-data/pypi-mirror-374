"""
Batch Document Processing Example

Demonstrates how to use the Dify Knowledge SDK for batch document processing, including:
- Batch document upload
- Batch processing and indexing monitoring
- Batch metadata management
- Batch retrieval and analysis
"""

import concurrent.futures
import json
import time
from pathlib import Path
from typing import Any, Dict, List

from dify_dataset_sdk import DifyDatasetClient
from dify_dataset_sdk.models import ProcessRule


class BatchDocumentProcessor:
    """Batch Document Processor"""

    def __init__(self, api_key: str, base_url: str = "https://api.dify.ai"):
        self.client = DifyDatasetClient(api_key=api_key, base_url=base_url)
        self.processing_results = {}
        self.failed_operations = []

    def create_sample_documents(self, count: int = 5) -> List[Path]:
        """Create sample document files"""
        print(f"📝 Creating {count} sample documents...")

        documents = []
        sample_dir = Path("sample_documents")
        sample_dir.mkdir(exist_ok=True)

        document_templates = [
            {
                "name": "Technical Specification Document",
                "content": """
# Technical Specification Document

## 1. Overview
This document defines the technical specifications and implementation standards for the system.

## 2. Architecture Design
The system adopts a microservices architecture, including the following core components:
- API Gateway
- Business Service Layer
- Data Storage Layer
- Cache Layer

## 3. Technology Stack
- Backend: Python/Django
- Frontend: React/TypeScript
- Database: PostgreSQL
- Cache: Redis

## 4. Deployment Requirements
- Containerized deployment (Docker/Kubernetes)
- Support for horizontal scaling
- Monitoring and logging system integration
                """,
            },
            {
                "name": "User Operation Manual",
                "content": """
# User Operation Manual

## Quick Start
Welcome to our system! This manual will help you get started quickly.

### System Login
1. Open your browser and navigate to the system URL
2. Enter your username and password
3. Click the "Login" button

### Basic Operations
- Create new project: Click the "New" button
- Edit project: Select a project and click "Edit"
- Delete project: Select a project and click "Delete"

### Advanced Features
- Batch data import
- Custom report generation
- Permission management settings

### Frequently Asked Questions
Q: What to do if I forget my password?
A: Click the "Forgot Password" link on the login page

Q: How to modify personal information?
A: Go to the "Personal Settings" page to make changes
                """,
            },
            {
                "name": "API Interface Documentation",
                "content": """
# API Interface Documentation

## Authentication
The API uses Bearer Token authentication.

```
Authorization: Bearer your_token_here
```

## User Management API

### Get User List
```
GET /api/users
```

Parameters:
- page: Page number (optional, default 1)
- limit: Items per page (optional, default 20)

Response:
```json
{
  "code": 200,
  "data": {
    "users": [...],
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

### Create User
```
POST /api/users
```

Request Body:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

### Update User
```
PUT /api/users/{id}
```

### Delete User
```
DELETE /api/users/{id}
```

## Error Handling
The API returns standard HTTP status codes:
- 200: Success
- 400: Bad request parameters
- 401: Unauthorized
- 403: Insufficient permissions
- 404: Resource not found
- 500: Internal server error
                """,
            },
            {
                "name": "Project Requirements Document",
                "content": """
# Project Requirements Document

## Project Background
With rapid business growth, the existing system can no longer meet the increasing business demands, requiring the construction of a new system platform.

## Business Requirements

### Functional Requirements
1. **User Management System**
   - User registration, login, permission management
   - Multi-role support (Administrator, Regular User, Reviewer)
   - Single Sign-On (SSO) support

2. **Content Management System**
   - Document creation, editing, version management
   - Multimedia file support
   - Full-text search functionality

3. **Workflow Management**
   - Custom approval processes
   - Task assignment and tracking
   - Notification reminder mechanism

### Non-Functional Requirements
- **Performance Requirements**: System response time not exceeding 2 seconds
- **Concurrency Requirements**: Support for 1000 concurrent users
- **Availability Requirements**: System availability of 99.9%
- **Security Requirements**: Encrypted data storage, operation log recording

## Technical Requirements
- Support for mobile access
- Multi-browser compatibility
- Internationalization support
- Scalable architecture design

## Project Timeline
- Requirements Analysis: 2 weeks
- System Design: 3 weeks
- Development Implementation: 12 weeks
- Testing and Acceptance: 4 weeks
- Deployment and Launch: 1 week
                """,
            },
            {
                "name": "Test Case Documentation",
                "content": """
# Test Case Documentation

## Testing Strategy
This document describes the testing strategy, methods, and specific test cases for the system.

## Functional Test Cases

### Login Function Test
**Test Case ID**: TC001
**Test Description**: Verify user login functionality
**Preconditions**: System deployed, user account created
**Test Steps**:
1. Open login page
2. Enter correct username and password
3. Click login button

**Expected Result**: Successful login, redirect to main page

**Test Case ID**: TC002
**Test Description**: Verify incorrect password login
**Test Steps**:
1. Open login page
2. Enter correct username, incorrect password
3. Click login button

**Expected Result**: Display "Incorrect username or password" message

### Document Management Test
**Test Case ID**: TC003
**Test Description**: Verify document creation functionality
**Test Steps**:
1. Login to system
2. Navigate to document management page
3. Click "New Document"
4. Fill in document title and content
5. Click save

**Expected Result**: Document created successfully, displayed in document list

## Performance Test Cases

### Load Testing
**Test Objective**: Verify system performance under normal load
**Test Method**: Simulate 100 concurrent users accessing the system
**Performance Metrics**:
- Response time < 2 seconds
- Throughput > 500 TPS
- CPU usage < 70%
- Memory usage < 80%

### Stress Testing
**Test Objective**: Determine maximum load capacity of the system
**Test Method**: Gradually increase concurrent users until system responds abnormally
**Key Metrics**:
- Maximum concurrent users
- System crash threshold
- Recovery time

## Security Test Cases

### SQL Injection Test
**Test Description**: Verify system's protection against SQL injection attacks
**Test Method**: Input SQL injection code in input fields
**Expected Result**: System can protect against SQL injection attacks

### XSS Attack Test
**Test Description**: Verify system's protection against cross-site scripting attacks
**Test Method**: Input JavaScript code in text input fields
**Expected Result**: System can filter and escape malicious scripts
                """,
            },
        ]

        for i in range(count):
            template = document_templates[i % len(document_templates)]
            filename = f"{template['name']}_{i + 1}_{int(time.time())}.md"
            file_path = sample_dir / filename

            content = (
                template["content"]
                + f"\n\n<!-- Document ID: DOC-{i + 1:03d} -->\n<!-- Created: {time.strftime('%Y-%m-%d %H:%M:%S')} -->"
            )
            file_path.write_text(content, encoding="utf-8")
            documents.append(file_path)

        print(f"  ✅ Created {len(documents)} sample documents")
        return documents

    def batch_upload_documents(
        self, dataset_id: str, file_paths: List[Path], max_workers: int = 3
    ) -> Dict[str, Any]:
        """Batch upload documents (parallel processing)"""
        print(f"\n📤 Batch uploading {len(file_paths)} documents...")

        results = {"successful": [], "failed": [], "batches": []}

        # Create custom processing rules
        process_rule = ProcessRule(
            mode="custom",
            rules={
                "pre_processing_rules": [
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": True},
                ],
                "segmentation": {"separator": "\\n\\n", "max_tokens": 800},
            },
        )

        def upload_single_document(file_path: Path) -> Dict[str, Any]:
            """Upload a single document"""
            try:
                doc_response = self.client.create_document_by_file(
                    dataset_id=dataset_id,
                    file_path=file_path,
                    process_rule=process_rule,
                    indexing_technique="high_quality",
                )
                return {
                    "status": "success",
                    "file_path": str(file_path),
                    "document_id": doc_response.document.id,
                    "document_name": doc_response.document.name,
                    "batch_id": doc_response.batch,
                }
            except Exception as e:
                return {
                    "status": "failed",
                    "file_path": str(file_path),
                    "error": str(e),
                }

        # Use thread pool for parallel upload
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(upload_single_document, fp): fp for fp in file_paths
            }

            for future in concurrent.futures.as_completed(future_to_file):
                result = future.result()
                if result["status"] == "success":
                    results["successful"].append(result)
                    results["batches"].append(result["batch_id"])
                    print(f"  ✅ Upload successful: {Path(result['file_path']).name}")
                else:
                    results["failed"].append(result)
                    print(
                        f"  ❌ Upload failed: {Path(result['file_path']).name} - {result['error']}"
                    )

                time.sleep(0.5)  # Avoid too frequent requests

        print(
            f"\n📊 Upload results: {len(results['successful'])} successful, {len(results['failed'])} failed"
        )
        return results

    def monitor_batch_indexing(
        self, dataset_id: str, batch_ids: List[str], max_attempts: int = 50
    ) -> Dict[str, str]:
        """Monitor batch document indexing progress"""
        print(f"\n⏳ Monitoring indexing progress for {len(batch_ids)} batches...")

        batch_status = dict.fromkeys(batch_ids, "pending")
        completed_batches = set()

        for attempt in range(max_attempts):
            if len(completed_batches) == len(batch_ids):
                break

            for batch_id in batch_ids:
                if batch_id in completed_batches:
                    continue

                try:
                    status = self.client.get_document_indexing_status(
                        dataset_id, batch_id
                    )
                    if status.data:
                        info = status.data[0]
                        batch_status[batch_id] = info.indexing_status

                        if info.indexing_status in ["completed", "error", "paused"]:
                            completed_batches.add(batch_id)
                            if info.indexing_status == "completed":
                                print(
                                    f"  ✅ Batch {batch_id[:8]}... indexing completed"
                                )
                            else:
                                print(
                                    f"  ❌ Batch {batch_id[:8]}... indexing failed: {info.indexing_status}"
                                )
                        else:
                            progress = (
                                f"{info.completed_segments}/{info.total_segments}"
                            )
                            print(f"  ⏳ Batch {batch_id[:8]}... progress: {progress}")

                except Exception as e:
                    print(f"  ❌ Failed to check batch {batch_id[:8]}... status: {e}")
                    batch_status[batch_id] = "error"
                    completed_batches.add(batch_id)

            if attempt < max_attempts - 1:
                time.sleep(3)  # Wait 3 seconds before next check

        # Summary results
        completed_count = sum(
            1 for status in batch_status.values() if status == "completed"
        )
        print(
            f"\n📈 Indexing results: {completed_count}/{len(batch_ids)} batches completed"
        )

        return batch_status

    def batch_create_metadata_schema(self, dataset_id: str) -> List[Any]:
        """Batch create metadata schema"""
        print("\n🏗️  Creating batch metadata schema...")

        metadata_fields = [
            {"type": "string", "name": "document_type"},
            {"type": "string", "name": "author"},
            {"type": "string", "name": "department"},
            {"type": "string", "name": "version"},
            {"type": "string", "name": "status"},
            {"type": "number", "name": "priority"},
            {"type": "time", "name": "created_date"},
            {"type": "time", "name": "last_modified"},
        ]

        created_fields = []
        for field_config in metadata_fields:
            try:
                field = self.client.create_metadata_field(
                    dataset_id=dataset_id,
                    field_type=field_config["type"],
                    name=field_config["name"],
                )
                created_fields.append(field)
                print(f"  ✅ Created metadata field: {field.name} ({field.type})")
                time.sleep(0.3)
            except Exception as e:
                print(f"  ❌ Failed to create field {field_config['name']}: {e}")

        return created_fields

    def batch_update_document_metadata(
        self,
        dataset_id: str,
        documents: List[Dict[str, Any]],
        metadata_fields: List[Any],
    ) -> bool:
        """Batch update document metadata"""
        print(f"\n📝 Batch updating metadata for {len(documents)} documents...")

        # Create metadata field mapping
        field_mapping = {field.name: field.id for field in metadata_fields}

        # Prepare batch metadata update data
        metadata_operations = []

        for i, doc in enumerate(documents):
            document_id = doc["document_id"]
            doc_name = doc["document_name"]

            # Determine document type based on document name
            doc_type = "unknown"
            if "Technical Specification" in doc_name:
                doc_type = "technical_spec"
            elif "User Operation" in doc_name:
                doc_type = "user_manual"
            elif "API" in doc_name:
                doc_type = "api_doc"
            elif "Requirements" in doc_name:
                doc_type = "requirement"
            elif "Test" in doc_name:
                doc_type = "test_case"

            metadata_list = []

            # Add metadata
            if "document_type" in field_mapping:
                metadata_list.append(
                    {
                        "id": field_mapping["document_type"],
                        "value": doc_type,
                        "name": "document_type",
                    }
                )

            if "author" in field_mapping:
                metadata_list.append(
                    {
                        "id": field_mapping["author"],
                        "value": f"Author_{i + 1}",
                        "name": "author",
                    }
                )

            if "department" in field_mapping:
                dept = (
                    "Engineering"
                    if doc_type in ["technical_spec", "api_doc"]
                    else "Product"
                )
                metadata_list.append(
                    {
                        "id": field_mapping["department"],
                        "value": dept,
                        "name": "department",
                    }
                )

            if "version" in field_mapping:
                metadata_list.append(
                    {"id": field_mapping["version"], "value": "v1.0", "name": "version"}
                )

            if "status" in field_mapping:
                metadata_list.append(
                    {
                        "id": field_mapping["status"],
                        "value": "published",
                        "name": "status",
                    }
                )

            if "priority" in field_mapping:
                priority = 1 if doc_type in ["technical_spec", "api_doc"] else 2
                metadata_list.append(
                    {
                        "id": field_mapping["priority"],
                        "value": str(priority),
                        "name": "priority",
                    }
                )

            metadata_operations.append(
                {"document_id": document_id, "metadata_list": metadata_list}
            )

        try:
            self.client.update_document_metadata(dataset_id, metadata_operations)
            print(
                f"  ✅ Successfully updated metadata for {len(metadata_operations)} documents"
            )
            return True
        except Exception as e:
            print(f"  ❌ Batch metadata update failed: {e}")
            return False

    def batch_retrieve_test(
        self, dataset_id: str, queries: List[str]
    ) -> Dict[str, Any]:
        """Batch retrieval test"""
        print(f"\n🔍 Executing {len(queries)} retrieval tests...")

        results = {"queries": [], "total_results": 0, "avg_response_time": 0}

        total_time = 0

        for i, query in enumerate(queries):
            start_time = time.time()
            try:
                response = self.client.retrieve(
                    dataset_id=dataset_id,
                    query=query,
                    retrieval_model={
                        "search_method": "hybrid_search",
                        "reranking_enable": True,
                        "top_k": 5,
                        "score_threshold_enabled": True,
                        "score_threshold": 0.5,
                    },
                )

                end_time = time.time()
                response_time = end_time - start_time
                total_time += response_time

                result_count = (
                    len(response.records) if hasattr(response, "records") else 0
                )
                results["total_results"] += result_count

                query_result = {
                    "query": query,
                    "result_count": result_count,
                    "response_time": response_time,
                    "top_scores": [],
                }

                # Extract scores from top 3 results
                if hasattr(response, "records"):
                    for record in response.records[:3]:
                        if isinstance(record, dict) and "score" in record:
                            query_result["top_scores"].append(record["score"])

                results["queries"].append(query_result)
                print(
                    f"  ✅ Query {i + 1}: '{query[:30]}...' - {result_count} results ({response_time:.2f}s)"
                )

            except Exception as e:
                print(f"  ❌ Query {i + 1} failed: {e}")
                results["queries"].append(
                    {
                        "query": query,
                        "error": str(e),
                        "response_time": 0,
                        "result_count": 0,
                    }
                )

        results["avg_response_time"] = total_time / len(queries) if queries else 0

        print("\n📊 Retrieval Statistics:")
        print(f"  - Average response time: {results['avg_response_time']:.2f}s")
        print(f"  - Total retrieval results: {results['total_results']} items")
        print(
            f"  - Average per query: {results['total_results'] / len(queries):.1f} results"
        )

        return results

    def generate_batch_report(
        self, dataset_id: str, processing_results: Dict[str, Any]
    ) -> str:
        """Generate batch processing report"""
        print("\n📋 Generating batch processing report...")

        report = {
            "dataset_id": dataset_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_documents": len(processing_results.get("successful", []))
                + len(processing_results.get("failed", [])),
                "successful_uploads": len(processing_results.get("successful", [])),
                "failed_uploads": len(processing_results.get("failed", [])),
                "success_rate": 0,
            },
            "details": processing_results,
        }

        if report["summary"]["total_documents"] > 0:
            report["summary"]["success_rate"] = (
                report["summary"]["successful_uploads"]
                / report["summary"]["total_documents"]
                * 100
            )

        # Save report to file
        report_file = Path(f"batch_processing_report_{int(time.time())}.json")
        report_file.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        print(f"  ✅ Report saved to: {report_file}")
        print(f"  📊 Success rate: {report['summary']['success_rate']:.1f}%")

        return str(report_file)

    def cleanup_sample_files(self):
        """Clean up sample files"""
        sample_dir = Path("sample_documents")
        if sample_dir.exists():
            for file in sample_dir.glob("*"):
                file.unlink()
            sample_dir.rmdir()
            print("🧹 Sample files cleaned up")

    def close(self):
        """Close client connection"""
        self.client.close()


def main():
    """Main function - Demonstrates the complete batch document processing workflow"""
    # Configure API information
    api_key = "YOUR_API_KEY_HERE"  # Replace with your actual API key
    base_url = "https://api.dify.ai"  # Dify API address

    processor = BatchDocumentProcessor(api_key=api_key, base_url=base_url)

    try:
        print("🚀 Dify Knowledge SDK - Batch Document Processing Example")
        print("=" * 60)

        # 1. Create dataset
        print("📚 Creating test dataset...")
        timestamp = int(time.time())
        dataset = processor.client.create_dataset(
            name=f"Batch Processing Test Dataset_{timestamp}",
            description="Test dataset for batch document processing example",
            permission="only_me",
        )
        print(f"  ✅ Created dataset: {dataset.name}")
        dataset_id = dataset.id

        # 2. Create sample documents
        document_files = processor.create_sample_documents(count=5)

        # 3. Batch upload documents
        upload_results = processor.batch_upload_documents(
            dataset_id, document_files, max_workers=2
        )

        # 4. Monitor indexing progress
        if upload_results["batches"]:
            processor.monitor_batch_indexing(dataset_id, upload_results["batches"])

        # 5. Create metadata schema
        metadata_fields = processor.batch_create_metadata_schema(dataset_id)

        # 6. Batch update document metadata
        if upload_results["successful"] and metadata_fields:
            processor.batch_update_document_metadata(
                dataset_id, upload_results["successful"], metadata_fields
            )

        # 7. Batch retrieval test
        test_queries = [
            "technical architecture design",
            "user login operation",
            "API interface documentation",
            "project requirements analysis",
            "test case writing",
            "system deployment plan",
            "database design",
            "performance optimization suggestions",
        ]

        # Wait for indexing to complete before retrieval test
        if upload_results["successful"]:
            time.sleep(5)  # Wait for indexing to complete
            processor.batch_retrieve_test(dataset_id, test_queries)

        # 8. Generate processing report
        report_file = processor.generate_batch_report(dataset_id, upload_results)

        print("\n✅ Batch document processing example completed!")
        print("📝 Summary:")
        print(f"  - Created dataset: {dataset.name}")
        print(f"  - Uploaded documents: {len(upload_results['successful'])} successful")
        print(f"  - Metadata fields: {len(metadata_fields)} fields")
        print(f"  - Retrieval tests: {len(test_queries)} queries")
        print(f"  - Processing report: {report_file}")

        print("\n💡 Tips:")
        print("  - In production, consider adding error retry mechanisms")
        print("  - Adjust processing rules and metadata based on document types")
        print(
            "  - Monitor indexing queue to avoid submitting too many documents simultaneously"
        )

    except Exception as e:
        print(f"\n❌ Error occurred during batch processing: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Clean up sample files
        processor.cleanup_sample_files()

        # Close client
        processor.close()


if __name__ == "__main__":
    main()
