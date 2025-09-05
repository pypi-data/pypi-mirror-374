# Dify Dataset SDK API 完整参考文档

本文档详细介绍了 Dify Dataset SDK 的所有 39 个 API 方法，涵盖数据集管理、文档处理、片段管理、元数据操作、知识标签和高级检索等功能，并提供完整的参数说明和高级使用示例。

## 目录

- [Dify Dataset SDK API 完整参考文档](#dify-dataset-sdk-api-完整参考文档)
  - [目录](#目录)
  - [1. 简介](#1-简介)
    - [核心特性](#核心特性)
    - [支持的文件格式](#支持的文件格式)
  - [2. 快速开始](#2-快速开始)
    - [安装](#安装)
    - [基本使用](#基本使用)
  - [3. API 分类概览](#3-api-分类概览)
  - [4. 数据集管理 (5 个 API)](#4-数据集管理-5-个-api)
    - [4.1 创建数据集](#41-创建数据集)
    - [4.2 获取数据集列表](#42-获取数据集列表)
    - [4.3 获取数据集详情](#43-获取数据集详情)
    - [4.4 更新数据集](#44-更新数据集)
    - [4.5 删除数据集](#45-删除数据集)
  - [5. 文档管理 (9 个 API)](#5-文档管理-9-个-api)
    - [5.1 从文本创建文档](#51-从文本创建文档)
    - [5.2 从文件创建文档](#52-从文件创建文档)
    - [5.3 获取文档列表](#53-获取文档列表)
    - [5.4 获取文档详情](#54-获取文档详情)
    - [5.5 通过文本更新文档](#55-通过文本更新文档)
    - [5.6 获取文档索引状态](#56-获取文档索引状态)
    - [5.7 删除文档](#57-删除文档)
    - [5.8 通过文件更新文档](#58-通过文件更新文档)
    - [5.9 删除文档](#59-删除文档)
  - [6. 文档批量操作 (1 个 API)](#6-文档批量操作-1-个-api)
    - [6.1 批量更新文档状态](#61-批量更新文档状态)
  - [7. 片段管理 (5 个 API)](#7-片段管理-5-个-api)
    - [7.1 创建片段](#71-创建片段)
    - [7.2 获取片段列表](#72-获取片段列表)
    - [7.3 获取片段详情](#73-获取片段详情)
    - [7.4 更新片段](#74-更新片段)
    - [7.5 删除片段](#75-删除片段)
  - [8. 子片段管理 (4 个 API)](#8-子片段管理-4-个-api)
    - [8.1 创建子片段](#81-创建子片段)
    - [8.2 获取子片段列表](#82-获取子片段列表)
    - [8.3 更新子片段](#83-更新子片段)
    - [8.4 删除子片段](#84-删除子片段)
  - [9. 知识库检索 (1 个 API)](#9-知识库检索-1-个-api)
    - [9.1 检索知识库内容](#91-检索知识库内容)
  - [10. 文件管理 (1 个 API)](#10-文件管理-1-个-api)
    - [10.1 获取上传文件信息](#101-获取上传文件信息)
  - [11. 元数据管理 (6 个 API)](#11-元数据管理-6-个-api)
    - [11.1 创建元数据字段](#111-创建元数据字段)
    - [11.2 获取元数据字段列表](#112-获取元数据字段列表)
    - [11.3 更新元数据字段](#113-更新元数据字段)
    - [11.4 删除元数据字段](#114-删除元数据字段)
    - [11.5 更新文档元数据](#115-更新文档元数据)
    - [11.6 切换内置元数据字段](#116-切换内置元数据字段)
  - [12. 知识标签管理 (7 个 API)](#12-知识标签管理-7-个-api)
    - [12.1 创建知识标签](#121-创建知识标签)
    - [12.2 绑定数据集到标签](#122-绑定数据集到标签)
    - [12.3 获取知识标签列表](#123-获取知识标签列表)
    - [12.4 更新知识标签](#124-更新知识标签)
    - [12.5 删除知识标签](#125-删除知识标签)
    - [12.6 解绑数据集标签](#126-解绑数据集标签)
    - [12.7 获取数据集标签](#127-获取数据集标签)
  - [13. 嵌入模型管理 (1 个 API)](#13-嵌入模型管理-1-个-api)
    - [13.1 获取可用的嵌入模型列表](#131-获取可用的嵌入模型列表)
  - [14. 错误处理](#14-错误处理)
    - [高级错误处理](#高级错误处理)
  - [15. 性能优化建议](#15-性能优化建议)
    - [并发处理示例](#并发处理示例)
  - [16. 最佳实践](#16-最佳实践)
    - [16.1 客户端管理](#161-客户端管理)
    - [16.2 批量操作优化](#162-批量操作优化)
    - [16.3 高级检索配置](#163-高级检索配置)
    - [16.4 监控和日志](#164-监控和日志)
  - [17. 高级应用场景](#17-高级应用场景)
    - [17.1 企业知识库构建](#171-企业知识库构建)
    - [17.2 智能问答系统](#172-智能问答系统)
    - [17.3 内容审核与质量控制](#173-内容审核与质量控制)
  - [总结](#总结)

## 1. 简介

Dify Dataset SDK 是一个功能强大的 Python SDK，用于与 Dify 知识库 API 进行交互。该 SDK 提供了完整的知识库管理能力，包括数据集创建、文档上传处理、智能分片、元数据管理、标签组织和高级检索等功能。

### 核心特性

- 📚 **完整的 API 覆盖**：支持 Dify 知识库的所有 39 个 API 端点
- 🔒 **类型安全**：基于 Pydantic 的完整类型提示
- 🛡️ **错误处理**：全面的异常处理和重试机制
- ⚡ **高性能**：基于 httpx 的异步 HTTP 客户端
- 📄 **多格式支持**：支持文本、PDF、DOCX、Markdown 等多种文档格式
- 🔍 **高级检索**：语义搜索、全文搜索、混合搜索
- 🏷️ **标签管理**：知识库标签化组织
- 📊 **元数据管理**：自定义元数据字段和文档关联

### 支持的文件格式

- 文本文件：`.txt`, `.md`
- 文档文件：`.pdf`, `.docx`
- 数据文件：`.xlsx`, `.csv`
- 网页文件：`.html`

## 2. 快速开始

### 安装

```bash
pip install dify-dataset-sdk
```

### 基本使用

```python
from dify_dataset_sdk import DifyDatasetClient

# 初始化客户端
client = DifyDatasetClient(
    api_key="your-api-key-here",
    base_url="https://api.dify.ai",  # 可选，默认值
    timeout=30.0  # 可选，默认 30 秒
)

# 创建数据集
dataset = client.create_dataset(
    name="我的知识库",
    description="用于存储技术文档",
    permission="only_me"
)

# 创建文档
doc_response = client.create_document_by_text(
    dataset_id=dataset.id,
    name="示例文档",
    text="这是一个示例文档内容。",
    indexing_technique="high_quality"
)

# 关闭客户端连接
client.close()
```

## 3. API 分类概览

| 分类         | API 数量 | 主要功能                           |
| ------------ | -------- | ---------------------------------- |
| 数据集管理   | 5        | 创建、列表、查看、更新、删除数据集 |
| 文档管理     | 9        | 文档创建、更新、删除、状态查询     |
| 文档批量操作 | 1        | 批量更新文档状态                   |
| 片段管理     | 5        | 文档片段的增删改查                 |
| 子片段管理   | 4        | 分层片段的管理                     |
| 知识库检索   | 1        | 智能检索和搜索                     |
| 文件管理     | 1        | 上传文件信息查询                   |
| 元数据管理   | 6        | 自定义字段和文档元数据             |
| 知识标签管理 | 7        | 标签创建、绑定、解绑               |
| 嵌入模型管理 | 1        | 可用模型列表查询                   |
| **总计**     | **39**   | **完整的知识库管理功能**           |

## 4. 数据集管理 (5 个 API)

### 4.1 创建数据集

**方法签名：**

```python
def create_dataset(
    name: str,                                    # 数据集名称 (必需)
    description: Optional[str] = None,            # 数据集描述
    indexing_technique: Optional[Literal["high_quality", "economy"]] = None,  # 索引技术
    permission: Optional[Literal["only_me", "all_team_members", "partial_members"]] = "only_me",  # 权限
    provider: Optional[Literal["vendor", "external"]] = "vendor",             # 提供商类型
    external_knowledge_api_id: Optional[str] = None,      # 外部知识API ID
    external_knowledge_id: Optional[str] = None,          # 外部知识ID
    embedding_model: Optional[str] = None,                # 嵌入模型名称
    embedding_model_provider: Optional[str] = None,       # 嵌入模型提供商
    retrieval_model: Optional[RetrievalModel] = None,     # 检索模型配置
    partial_member_list: Optional[List[str]] = None,      # 部分成员列表
) -> Dataset
```

**参数说明：**

- `name` (str): 数据集名称 **(必需)**
- `description` (str, 可选): 数据集描述
- `indexing_technique` (str, 可选): 索引技术 - "high_quality" 或 "economy"
- `permission` (str, 可选): 权限级别，默认 "only_me"
- `provider` (str, 可选): 提供商类型，"vendor" 或 "external"
- `embedding_model` (str, 可选): 嵌入模型名称
- `embedding_model_provider` (str, 可选): 嵌入模型提供商
- `retrieval_model` (RetrievalModel, 可选): 检索模型配置

**基本使用示例：**

```python
# 基本创建
dataset = client.create_dataset(
    name="技术文档库",
    description="存储所有技术相关文档"
)

# 高级配置
from dify_dataset_sdk.models import RetrievalModel, RerankingModel

# 配置重排序模型
reranking_model = RerankingModel(
    reranking_provider_name="cohere",
    reranking_model_name="rerank-english-v2.0"
)

# 配置高级检索模型
retrieval_config = RetrievalModel(
    search_method="hybrid_search",
    reranking_enable=True,
    reranking_mode="reranking_model",
    reranking_model=reranking_model,
    weights=0.3,  # 语义搜索权重
    top_k=20,
    score_threshold_enabled=True,
    score_threshold=0.5
)

# 创建企业级数据集
enterprise_dataset = client.create_dataset(
    name="企业知识库",
    description="包含公司所有技术文档和流程",
    indexing_technique="high_quality",
    permission="all_team_members",
    embedding_model="text-embedding-ada-002",
    embedding_model_provider="openai",
    retrieval_model=retrieval_config
)
```

### 4.2 获取数据集列表

**方法签名：**

```python
def list_datasets(
    keyword: Optional[str] = None,
    tag_ids: Optional[List[str]] = None,
    page: int = 1,
    limit: int = 20,
    include_all: bool = False,
) -> PaginatedResponse
```

**参数说明：**

- `keyword` (str, 可选): 搜索关键词
- `tag_ids` (List[str], 可选): 标签 ID 列表，用于过滤
- `page` (int): 页码，默认 1
- `limit` (int): 每页数量，默认 20
- `include_all` (bool): 是否包含所有数据集

**使用示例：**

```python
# 获取所有数据集
datasets = client.list_datasets()
print(f"总数据集数: {datasets.total}")

# 搜索特定关键词
tech_datasets = client.list_datasets(keyword="技术", limit=10)

# 按标签过滤
tagged_datasets = client.list_datasets(tag_ids=["tag_id_1", "tag_id_2"])

# 分页获取
for page in range(1, 6):  # 获取前5页
    page_datasets = client.list_datasets(page=page, limit=10)
    print(f"第{page}页: {len(page_datasets.data)}个数据集")
```

### 4.3 获取数据集详情

**方法签名：**

```python
def get_dataset(dataset_id: str) -> Dataset
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**

**使用示例：**

```python
# 获取数据集详情
dataset = client.get_dataset("dataset_id")
print(f"数据集名称: {dataset.name}")
print(f"文档数量: {dataset.document_count}")
print(f"字符数: {dataset.character_count}")
print(f"创建时间: {dataset.created_at}")
```

### 4.4 更新数据集

**方法签名：**

```python
def update_dataset(
    dataset_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    indexing_technique: Optional[Literal["high_quality", "economy"]] = None,
    permission: Optional[Literal["only_me", "all_team_members", "partial_members"]] = None,
    retrieval_model: Optional[RetrievalModel] = None,
    partial_member_list: Optional[List[str]] = None,
) -> Dataset
```

**使用示例：**

```python
# 更新数据集基本信息
updated_dataset = client.update_dataset(
    dataset_id="dataset_id",
    name="更新后的数据集名称",
    description="更新后的描述"
)

# 更新权限设置
client.update_dataset(
    dataset_id="dataset_id",
    permission="all_team_members"
)

# 更新检索配置
new_retrieval_config = RetrievalModel(
    search_method="semantic_search",
    top_k=15,
    score_threshold_enabled=True,
    score_threshold=0.6
)

client.update_dataset(
    dataset_id="dataset_id",
    retrieval_model=new_retrieval_config
)
```

### 4.5 删除数据集

**方法签名：**

```python
def delete_dataset(dataset_id: str) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**

**使用示例：**

```python
# 删除数据集（注意：这是不可逆操作）
result = client.delete_dataset("dataset_id")
print(f"删除结果: {result}")

# 安全删除（先检查后删除）
try:
    dataset = client.get_dataset("dataset_id")
    if dataset.document_count == 0:
        result = client.delete_dataset("dataset_id")
        print("空数据集删除成功")
    else:
        print(f"数据集包含 {dataset.document_count} 个文档，请先清空")
except Exception as e:
    print(f"删除失败: {e}")
```

## 5. 文档管理 (9 个 API)

### 5.1 从文本创建文档

**方法签名：**

```python
def create_document_by_text(
    dataset_id: str,                              # 数据集ID (必需)
    name: str,                                    # 文档名称 (必需)
    text: str,                                    # 文档内容 (必需)
    indexing_technique: Optional[Literal["high_quality", "economy"]] = "high_quality",  # 索引技术
    doc_form: Optional[Literal["text_model", "hierarchical_model", "qa_model"]] = None,  # 文档形式
    doc_language: Optional[str] = None,           # 文档语言
    process_rule: Optional[ProcessRule] = None,   # 处理规则
    retrieval_model: Optional[RetrievalModel] = None,  # 检索模型配置
    embedding_model: Optional[str] = None,        # 嵌入模型名称
    embedding_model_provider: Optional[str] = None,  # 嵌入模型提供商
) -> DocumentResponse
```

**ProcessRule 配置详解：**

```python
from dify_dataset_sdk.models import (
    ProcessRule,
    ProcessRuleConfig,
    PreProcessingRule,
    Segmentation,
    SubchunkSegmentation
)

# 自定义预处理规则
pre_processing_rules = [
    PreProcessingRule(id="remove_extra_spaces", enabled=True),
    PreProcessingRule(id="remove_urls_emails", enabled=True)
]

# 分段配置
segmentation = Segmentation(
    separator="\n\n",    # 段落分隔符
    max_tokens=1000        # 每段最大token数
)

# 子分段配置（用于分层模式）
subchunk_segmentation = SubchunkSegmentation(
    separator="***",
    max_tokens=300,
    chunk_overlap=50
)

# 完整处理规则配置
process_rule_config = ProcessRuleConfig(
    pre_processing_rules=pre_processing_rules,
    segmentation=segmentation,
    parent_mode="full-doc",  # 或 "paragraph"
    subchunk_segmentation=subchunk_segmentation
)

# 自定义处理规则
custom_process_rule = ProcessRule(
    mode="custom",
    rules=process_rule_config
)
```

**使用示例：**

```python
# 基本文档创建
doc_response = client.create_document_by_text(
    dataset_id="dataset_id",
    name="API文档",
    text="这是一个详细的API使用说明文档...",
    indexing_technique="high_quality"
)

print(f"文档ID: {doc_response.document.id}")
print(f"批次ID: {doc_response.batch}")

# 创建问答模式文档
qa_doc_response = client.create_document_by_text(
    dataset_id="dataset_id",
    name="FAQ文档",
    text="问：什么是Python？\n答：Python是一种高级编程语言...",
    doc_form="qa_model",
    indexing_technique="high_quality"
)

# 使用嵌入模型和检索配置
from dify_dataset_sdk.models import RetrievalModel

retrieval_config = RetrievalModel(
    search_method="hybrid_search",
    top_k=10,
    score_threshold_enabled=True,
    score_threshold=0.7
)

advanced_doc_response = client.create_document_by_text(
    dataset_id="dataset_id",
    name="技术规范文档",
    text="长篇技术文档内容...",
    indexing_technique="high_quality",
    doc_form="text_model",
    embedding_model="text-embedding-ada-002",
    embedding_model_provider="openai",
    retrieval_model=retrieval_config,
    process_rule=custom_process_rule
)
```

### 5.2 从文件创建文档

**方法签名：**

```python
def create_document_by_file(
    dataset_id: str,                              # 数据集ID (必需)
    file_path: Union[str, Path],                  # 文件路径 (必需)
    original_document_id: Optional[str] = None,   # 原始文档ID (可选)
    indexing_technique: Optional[Literal["high_quality", "economy"]] = "high_quality",
    doc_form: Optional[Literal["text_model", "hierarchical_model", "qa_model"]] = None,  # 文档形式
    doc_language: Optional[str] = None,           # 文档语言
    process_rule: Optional[ProcessRule] = None,
    retrieval_model: Optional[RetrievalModel] = None,  # 检索模型配置
    embedding_model: Optional[str] = None,        # 嵌入模型名称
    embedding_model_provider: Optional[str] = None,  # 嵌入模型提供商
) -> DocumentResponse
```

**支持的文件格式：**

```python
SUPPORTED_FILE_TYPES = {
    '.txt': 'text/plain',
    '.md': 'text/markdown',
    '.pdf': 'application/pdf',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.csv': 'text/csv',
    '.html': 'text/html'
}
```

**使用示例：**

```python
# 上传PDF文档
doc_response = client.create_document_by_file(
    dataset_id="dataset_id",
    file_path="./documents/manual.pdf",
    indexing_technique="high_quality"
)

# 使用原始文档ID更新文档
update_response = client.create_document_by_file(
    dataset_id="dataset_id",
    file_path="./documents/updated_manual.pdf",
    original_document_id="existing_doc_id",
    indexing_technique="high_quality"
)

# 使用完整参数配置
from dify_dataset_sdk.models import ProcessRule, RetrievalModel

process_rule = ProcessRule(mode="custom")
retrieval_model = RetrievalModel(
    search_method="semantic_search",
    top_k=15
)

advanced_doc = client.create_document_by_file(
    dataset_id="dataset_id",
    file_path="./documents/technical_spec.docx",
    doc_form="hierarchical_model",
    doc_language="Chinese",
    process_rule=process_rule,
    retrieval_model=retrieval_model,
    embedding_model="text-embedding-ada-002",
    embedding_model_provider="openai"
)

# 批量文件上传示例
import os
from pathlib import Path

def batch_upload_documents(client, dataset_id, folder_path):
    """批量上传文件夹中的文档"""
    folder = Path(folder_path)
    supported_extensions = ['.txt', '.md', '.pdf', '.docx', '.xlsx', '.csv', '.html']

    for file_path in folder.iterdir():
        if file_path.suffix.lower() in supported_extensions:
            try:
                print(f"上传文件: {file_path.name}")
                doc_response = client.create_document_by_file(
                    dataset_id=dataset_id,
                    file_path=file_path,
                    indexing_technique="high_quality"
                )
                print(f"✅ 成功上传: {doc_response.document.id}")

            except Exception as e:
                print(f"❌ 上传失败 {file_path.name}: {e}")

# 使用示例
batch_upload_documents(client, "dataset_id", "./documents/")
```

### 5.3 获取文档列表

**方法签名：**

```python
def list_documents(
    dataset_id: str,
    keyword: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> PaginatedResponse
```

**使用示例：**

```python
# 获取所有文档
documents = client.list_documents("dataset_id")

# 搜索文档
search_docs = client.list_documents(
    dataset_id="dataset_id",
    keyword="API",
    limit=10
)

# 分页获取
page_docs = client.list_documents(
    dataset_id="dataset_id",
    page=2,
    limit=20
)
```

### 5.4 获取文档详情

**方法签名：**

```python
def get_document(
    dataset_id: str,
    document_id: str,
    metadata: Literal["all", "only", "without"] = "all",  # 元数据过滤条件
) -> Document
```

**使用示例：**

```python
document = client.get_document("dataset_id", "document_id")
print(f"文档名称: {document.name}")
print(f"字符数: {document.character_count}")
print(f"状态: {document.status}")
```

### 5.5 通过文本更新文档

**方法签名：**

```python
def update_document_by_text(
    dataset_id: str,
    document_id: str,
    name: Optional[str] = None,
    text: Optional[str] = None,
    process_rule: Optional[ProcessRule] = None,
) -> DocumentResponse
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `document_id` (str): 文档 ID **(必需)**
- `name` (str, 可选): 更新后的文档名称
- `text` (str, 可选): 更新后的文档文本内容
- `process_rule` (ProcessRule, 可选): 处理规则

**使用示例：**

```python
# 更新文档名称和内容
updated_doc = client.update_document_by_text(
    dataset_id="dataset_id",
    document_id="document_id",
    name="更新后的文档名称",
    text="这是更新后的文档内容。包含更多详细信息..."
)
print(f"更新批次ID: {updated_doc.batch}")

# 仅更新文档名称
client.update_document_by_text(
    dataset_id="dataset_id",
    document_id="document_id",
    name="新的文档标题"
)

# 使用自定义处理规则更新
from dify_dataset_sdk.models import ProcessRule

process_rule = ProcessRule(mode="custom")
client.update_document_by_text(
    dataset_id="dataset_id",
    document_id="document_id",
    text="更新后的内容",
    process_rule=process_rule
)
```

### 5.6 获取文档索引状态

**方法签名：**

```python
def get_document_indexing_status(
    dataset_id: str,
    batch: str
) -> IndexingStatusResponse
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `batch` (str): 文档创建时返回的批次 ID **(必需)**

**使用示例：**

```python
import time

# 创建文档后监控索引进度
doc_response = client.create_document_by_text(
    dataset_id="dataset_id",
    name="测试文档",
    text="测试内容"
)

# 等待索引完成
while True:
    status = client.get_document_indexing_status(
        "dataset_id", doc_response.batch
    )

    if status.data[0].indexing_status == "completed":
        print("文档索引完成")
        break
    elif status.data[0].indexing_status == "error":
        print(f"索引失败: {status.data[0].error}")
        break

    print(f"索引进度: {status.data[0].indexing_status}")
    time.sleep(2)

# 检查索引详情
def monitor_indexing_progress(client, dataset_id, batch_id, timeout=300):
    """监控文档索引进度"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            status = client.get_document_indexing_status(dataset_id, batch_id)
            if status.data:
                indexing_info = status.data[0]
                print(f"状态: {indexing_info.indexing_status}")
                print(f"进度: {indexing_info.processing_started_at}")

                if indexing_info.indexing_status == "completed":
                    print("✅ 索引完成")
                    return True
                elif indexing_info.indexing_status in ["error", "paused"]:
                    print(f"❌ 索引失败: {indexing_info.error}")
                    return False

            time.sleep(2)
        except Exception as e:
            print(f"检查状态时出错: {e}")
            time.sleep(5)

    print("⏰ 索引超时")
    return False

# 使用示例
monitor_indexing_progress(client, "dataset_id", doc_response.batch)
```

### 5.7 删除文档

**方法签名：**

```python
def delete_document(dataset_id: str, document_id: str) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `document_id` (str): 文档 ID **(必需)**

**使用示例：**

```python
# 删除文档
result = client.delete_document("dataset_id", "document_id")
print(f"删除结果: {result}")

# 安全删除（先检查后删除）
try:
    document = client.get_document("dataset_id", "document_id")
    if document.status == "completed":
        result = client.delete_document("dataset_id", "document_id")
        print("文档删除成功")
    else:
        print(f"文档状态为 {document.status}，请等待处理完成")
except Exception as e:
    print(f"删除失败: {e}")
```

### 5.8 通过文件更新文档

**方法签名：**

```python
def update_document_by_file(
    dataset_id: str,
    document_id: str,
    file_path: Union[str, Path],
    name: Optional[str] = None,
    process_rule: Optional[ProcessRule] = None,
) -> DocumentResponse
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `document_id` (str): 文档 ID **(必需)**
- `file_path` (Union[str, Path]): 新文件路径 **(必需)**
- `name` (str, 可选): 更新后的文档名称
- `process_rule` (ProcessRule, 可选): 处理规则

**使用示例：**

```python
# 通过文件更新文档
updated_doc = client.update_document_by_file(
    dataset_id="dataset_id",
    document_id="document_id",
    file_path="./updated_document.pdf",
    name="更新后的文档名称"
)
print(f"更新批次ID: {updated_doc.batch}")

# 使用自定义处理规则更新
from dify_dataset_sdk.models import ProcessRule

process_rule = ProcessRule(mode="automatic")
updated_doc = client.update_document_by_file(
    dataset_id="dataset_id",
    document_id="document_id",
    file_path="./new_version.docx",
    process_rule=process_rule
)
```

### 5.9 删除文档

**方法签名：**

```python
def delete_document(dataset_id: str, document_id: str) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `document_id` (str): 文档 ID **(必需)**

**使用示例：**

```python
# 删除文档
result = client.delete_document("dataset_id", "document_id")
print(f"删除结果: {result}")

# 安全删除（先检查后删除）
try:
    document = client.get_document("dataset_id", "document_id")
    if document.status == "completed":
        result = client.delete_document("dataset_id", "document_id")
        print("文档删除成功")
    else:
        print(f"文档状态为 {document.status}，请等待处理完成")
except Exception as e:
    print(f"删除失败: {e}")
```

## 6. 文档批量操作 (1 个 API)

### 6.1 批量更新文档状态

**方法签名：**

```python
def batch_update_document_status(
    dataset_id: str,
    action: Literal["enable", "disable", "archive", "un_archive"],
    document_ids: List[str],
) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `action` (str): 操作类型 - "enable", "disable", "archive", "un_archive"
- `document_ids` (List[str]): 文档 ID 列表 **(必需)**

**使用示例：**

```python
# 批量禁用文档
document_ids = ["doc_1", "doc_2", "doc_3"]
result = client.batch_update_document_status(
    dataset_id="dataset_id",
    action="disable",
    document_ids=document_ids
)

# 批量启用文档
client.batch_update_document_status(
    dataset_id="dataset_id",
    action="enable",
    document_ids=document_ids
)

# 批量归档文档
client.batch_update_document_status(
    dataset_id="dataset_id",
    action="archive",
    document_ids=document_ids
)
```

## 7. 片段管理 (5 个 API)

### 7.1 创建片段

**方法签名：**

```python
def create_segments(
    dataset_id: str,
    document_id: str,
    segments: List[Dict[str, Any]],
) -> SegmentResponse
```

**不同模式的片段创建：**

```python
# 1. 文本模式片段
text_segments = [
    {
        "content": "Python是一种高级编程语言，以其简洁的语法和强大的库生态系统而闻名。",
        "keywords": ["Python", "编程语言", "语法", "库"]
    },
    {
        "content": "面向对象编程是Python的核心特性之一，支持类、继承、封装和多态。",
        "keywords": ["面向对象", "类", "继承", "封装", "多态"]
    }
]

# 2. 问答模式片段
qa_segments = [
    {
        "content": "什么是Python的主要特点？",
        "answer": "Python的主要特点包括：简洁易读的语法、强大的标准库、跨平台兼容性、丰富的第三方库、支持多种编程范式等。",
        "keywords": ["Python", "特点", "语法", "标准库", "跨平台"]
    },
    {
        "content": "如何在Python中定义一个类？",
        "answer": "在Python中使用class关键字定义类，基本语法为：class ClassName: 然后在类体中定义属性和方法。",
        "keywords": ["Python", "类", "class", "定义", "语法"]
    }
]

# 3. 分层模式片段（包含子片段）
hierarchical_segments = [
    {
        "content": "Python数据结构详解",
        "answer": "Python提供了多种内置数据结构，包括列表、元组、字典、集合等，每种都有其特定的用途和特性。",
        "keywords": ["Python", "数据结构", "列表", "元组", "字典", "集合"],
        "child_chunks": [
            {
                "content": "列表(List)是有序、可变的数据集合，使用方括号[]定义。"
            },
            {
                "content": "元组(Tuple)是有序、不可变的数据集合，使用圆括号()定义。"
            },
            {
                "content": "字典(Dict)是无序的键值对集合，使用花括号{}定义。"
            }
        ]
    }
]
```

**使用示例：**

```python
# 创建不同类型的片段
text_result = client.create_segments("dataset_id", "doc_id", text_segments)
qa_result = client.create_segments("dataset_id", "doc_id", qa_segments)
hierarchical_result = client.create_segments("dataset_id", "doc_id", hierarchical_segments)

print(f"创建了 {len(text_result.data)} 个文本片段")
```

### 7.2 获取片段列表

**方法签名：**

```python
def list_segments(
    dataset_id: str,
    document_id: str,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> SegmentResponse
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `document_id` (str): 文档 ID **(必需)**
- `keyword` (str, 可选): 搜索关键词
- `status` (str, 可选): 搜索状态，如 'completed'
- `page` (int): 页码，默认 1
- `limit` (int): 每页数量，范围 1-100，默认 20

**使用示例：**

```python
# 获取文档的所有片段
segments = client.list_segments("dataset_id", "document_id")

# 搜索片段
search_segments = client.list_segments(
    "dataset_id", "document_id",
    keyword="Python",
    limit=10
)

# 按状态过滤
completed_segments = client.list_segments(
    "dataset_id", "document_id",
    status="completed"
)

for segment in segments.data:
    print(f"片段ID: {segment.id}")
    print(f"内容: {segment.content}")
    print(f"状态: {segment.status}")
```

### 7.3 获取片段详情

**方法签名：**

```python
def get_segment(
    dataset_id: str,
    document_id: str,
    segment_id: str,
) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `document_id` (str): 文档 ID **(必需)**
- `segment_id` (str): 片段 ID **(必需)**

**使用示例：**

```python
# 获取片段详情
segment = client.get_segment(
    dataset_id="dataset_id",
    document_id="document_id",
    segment_id="segment_id"
)
print(f"片段内容: {segment['content']}")
print(f"片段状态: {segment['enabled']}")
```

### 7.4 更新片段

**方法签名：**

```python
def update_segment(
    dataset_id: str,
    document_id: str,
    segment_id: str,
    segment_data: Dict[str, Any],
) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `document_id` (str): 文档 ID **(必需)**
- `segment_id` (str): 片段 ID **(必需)**
- `segment_data` (Dict[str, Any]): 片段数据 **(必需)**
  - `content` (str): 文本内容/问题内容 (必需)
  - `answer` (str): 答案内容 (可选, 问答模式下)
  - `keywords` (List[str]): 关键词 (可选)
  - `enabled` (bool): 是否启用片段 (可选)
  - `regenerate_child_chunks` (bool): 是否重新生成子片段 (可选)

**使用示例：**

```python
# 更新片段内容
segment_data = {
    "content": "更新后的片段内容",
    "keywords": ["Python", "更新", "编程"],
    "enabled": True
}

updated_segment = client.update_segment(
    dataset_id="dataset_id",
    document_id="document_id",
    segment_id="segment_id",
    segment_data=segment_data
)

# 更新问答模式片段
qa_segment_data = {
    "content": "什么是Python的主要特点？",
    "answer": "Python的主要特点包括简洁易读的语法、强大的标准库、跨平台兼容性等。",
    "keywords": ["Python", "特点", "语法"]
}

client.update_segment(
    dataset_id="dataset_id",
    document_id="document_id",
    segment_id="segment_id",
    segment_data=qa_segment_data
)
```

### 7.5 删除片段

**方法签名：**

```python
def delete_segment(
    dataset_id: str,
    document_id: str,
    segment_id: str
) -> Dict[str, Any]
```

## 8. 子片段管理 (4 个 API)

### 8.1 创建子片段

**方法签名：**

```python
def create_child_chunk(
    dataset_id: str,
    document_id: str,
    segment_id: str,
    content: str,
) -> Dict[str, Any]
```

**使用示例：**

```python
# 创建子片段
child_chunk = client.create_child_chunk(
    dataset_id="dataset_id",
    document_id="document_id",
    segment_id="segment_id",
    content="这是一个子片段的内容。"
)
```

### 8.2 获取子片段列表

**方法签名：**

```python
def list_child_chunks(
    dataset_id: str,
    document_id: str,
    segment_id: str,
    keyword: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
) -> ChildChunkResponse
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `document_id` (str): 文档 ID **(必需)**
- `segment_id` (str): 父片段 ID **(必需)**
- `keyword` (str, 可选): 搜索关键词
- `page` (int): 页码，默认 1
- `limit` (int): 每页数量，最大 100，默认 20

**使用示例：**

```python
# 获取所有子片段
child_chunks = client.list_child_chunks(
    dataset_id="dataset_id",
    document_id="document_id",
    segment_id="segment_id"
)

# 搜索子片段
search_chunks = client.list_child_chunks(
    dataset_id="dataset_id",
    document_id="document_id",
    segment_id="segment_id",
    keyword="Python",
    limit=10
)

for chunk in child_chunks.data:
    print(f"子片段ID: {chunk.id}")
    print(f"内容: {chunk.content}")
```

### 8.3 更新子片段

**方法签名：**

```python
def update_child_chunk(
    dataset_id: str,
    document_id: str,
    segment_id: str,
    child_chunk_id: str,
    content: str,
) -> Dict[str, Any]
```

### 8.4 删除子片段

**方法签名：**

```python
def delete_child_chunk(
    dataset_id: str,
    document_id: str,
    segment_id: str,
    child_chunk_id: str,
) -> Dict[str, Any]
```

## 9. 知识库检索 (1 个 API)

### 9.1 检索知识库内容

**方法签名：**

```python
def retrieve(
    dataset_id: str,
    query: str,
    retrieval_model: Optional[RetrievalModel] = None,
    external_retrieval_model: Optional[Dict[str, Any]] = None,
) -> RetrievalResponse
```

**完整检索配置示例：**

```python
from dify_dataset_sdk.models import (
    RetrievalModel,
    RerankingModel,
    MetadataFilteringConditions,
    MetadataCondition
)

# 1. 语义搜索配置
semantic_search = RetrievalModel(
    search_method="semantic_search",
    top_k=10,
    score_threshold_enabled=True,
    score_threshold=0.7
)

# 2. 全文搜索配置
fulltext_search = RetrievalModel(
    search_method="full_text_search",
    top_k=15,
    score_threshold_enabled=False
)

# 3. 混合搜索配置
hybrid_search = RetrievalModel(
    search_method="hybrid_search",
    weights=0.3,  # 语义搜索权重 (0.0-1.0)
    top_k=20,
    score_threshold_enabled=True,
    score_threshold=0.5,
    reranking_enable=True,
    reranking_mode="weighted_score"  # 或 "reranking_model"
)

# 4. 带重排序模型的高级检索
reranking_model = RerankingModel(
    reranking_provider_name="cohere",
    reranking_model_name="rerank-multilingual-v2.0"
)

advanced_retrieval = RetrievalModel(
    search_method="hybrid_search",
    weights=0.4,
    top_k=30,
    reranking_enable=True,
    reranking_mode="reranking_model",
    reranking_model=reranking_model
)

# 5. 带元数据过滤的检索
metadata_conditions = [
    MetadataCondition(
        name="author",
        comparison_operator="is",
        value="张三"
    ),
    MetadataCondition(
        name="publish_date",
        comparison_operator="after",
        value="2024-01-01"
    ),
    MetadataCondition(
        name="version",
        comparison_operator="≥",
        value=2.0
    )
]

metadata_filter = MetadataFilteringConditions(
    logical_operator="and",  # 或 "or"
    conditions=metadata_conditions
)

filtered_retrieval = RetrievalModel(
    search_method="semantic_search",
    top_k=10,
    metadata_filtering_conditions=metadata_filter
)

# 执行不同类型的检索
semantic_results = client.retrieve("dataset_id", "Python编程", semantic_search)
hybrid_results = client.retrieve("dataset_id", "机器学习算法", hybrid_search)
filtered_results = client.retrieve("dataset_id", "API文档", filtered_retrieval)
```

**基本使用示例：**

```python
# 基本检索
results = client.retrieve(
    dataset_id="dataset_id",
    query="什么是人工智能？"
)

for result in results.data:
    print(f"内容: {result.content}")
    print(f"相关度: {result.score}")
    print(f"文档: {result.document_name}")

# 高级检索配置
retrieval_config = RetrievalModel(
    search_method="hybrid_search",
    reranking_enable=True,
    top_k=5,
    score_threshold=0.7,
    weights=0.5  # 语义搜索权重
)

advanced_results = client.retrieve(
    dataset_id="dataset_id",
    query="人工智能应用",
    retrieval_model=retrieval_config
)
```

## 10. 文件管理 (1 个 API)

### 10.1 获取上传文件信息

**方法签名：**

```python
def get_upload_file(dataset_id: str, document_id: str) -> Dict[str, Any]
```

**使用示例：**

```python
# 获取上传文件信息
file_info = client.get_upload_file("dataset_id", "document_id")
print(f"文件名: {file_info['name']}")
print(f"文件大小: {file_info['size']}")
print(f"MIME类型: {file_info['mime_type']}")
```

## 11. 元数据管理 (6 个 API)

### 11.1 创建元数据字段

**方法签名：**

```python
def create_metadata_field(
    dataset_id: str,
    field_type: str,
    name: str,
) -> Metadata
```

**使用示例：**

```python
# 创建不同类型的元数据字段
string_field = client.create_metadata_field(
    dataset_id="dataset_id",
    field_type="string",
    name="作者"
)

number_field = client.create_metadata_field(
    dataset_id="dataset_id",
    field_type="number",
    name="版本号"
)

time_field = client.create_metadata_field(
    dataset_id="dataset_id",
    field_type="time",
    name="发布时间"
)
```

### 11.2 获取元数据字段列表

**方法签名：**

```python
def list_metadata_fields(dataset_id: str) -> MetadataListResponse
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**

**使用示例：**

```python
# 获取数据集的所有元数据字段
metadata_fields = client.list_metadata_fields("dataset_id")

for field in metadata_fields.data:
    print(f"字段ID: {field.id}")
    print(f"字段名称: {field.name}")
    print(f"字段类型: {field.type}")
```

### 11.3 更新元数据字段

**方法签名：**

```python
def update_metadata_field(
    dataset_id: str,
    metadata_id: str,
    name: str,
) -> Metadata
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `metadata_id` (str): 元数据字段 ID **(必需)**
- `name` (str): 更新后的字段名称 **(必需)**

**使用示例：**

```python
# 更新元数据字段名称
updated_field = client.update_metadata_field(
    dataset_id="dataset_id",
    metadata_id="metadata_id",
    name="更新后的作者字段"
)
print(f"更新成功: {updated_field.name}")
```

### 11.4 删除元数据字段

**方法签名：**

```python
def delete_metadata_field(
    dataset_id: str,
    metadata_id: str,
) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `metadata_id` (str): 元数据字段 ID **(必需)**

**使用示例：**

```python
# 删除元数据字段(注意：这是不可逆操作)
result = client.delete_metadata_field(
    dataset_id="dataset_id",
    metadata_id="metadata_id"
)
print(f"删除结果: {result}")

# 安全删除（先检查是否有文档使用）
try:
    # 检查该元数据字段是否被使用
    metadata_fields = client.list_metadata_fields("dataset_id")
    field_exists = any(field.id == "metadata_id" for field in metadata_fields.data)

    if field_exists:
        result = client.delete_metadata_field("dataset_id", "metadata_id")
        print("元数据字段删除成功")
    else:
        print("元数据字段不存在")
except Exception as e:
    print(f"删除失败: {e}")
```

### 11.5 更新文档元数据

**方法签名：**

```python
def update_document_metadata(
    dataset_id: str,
    operation_data: List[Dict[str, Any]],
) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `operation_data` (List[Dict[str, Any]]): 操作数据列表 **(必需)**
  - 每个操作包含：
    - `document_id` (str): 文档 ID
    - `metadata_list` (List[Dict]): 元数据列表
      - `id` (str): 元数据字段 ID
      - `value` (Any): 元数据值
      - `name` (str): 元数据字段名称

**批量元数据更新示例：**

```python
# 先创建元数据字段
author_field = client.create_metadata_field("dataset_id", "string", "作者")
version_field = client.create_metadata_field("dataset_id", "number", "版本")
date_field = client.create_metadata_field("dataset_id", "time", "发布日期")

# 准备批量元数据更新数据
metadata_operations = [
    {
        "document_id": "doc_1",
        "metadata_list": [
            {"id": author_field.id, "value": "张三", "name": "作者"},
            {"id": version_field.id, "value": "1.0", "name": "版本"},
            {"id": date_field.id, "value": "2024-01-15", "name": "发布日期"}
        ]
    },
    {
        "document_id": "doc_2",
        "metadata_list": [
            {"id": author_field.id, "value": "李四", "name": "作者"},
            {"id": version_field.id, "value": "2.0", "name": "版本"},
            {"id": date_field.id, "value": "2024-02-20", "name": "发布日期"}
        ]
    }
]

# 执行批量更新
result = client.update_document_metadata("dataset_id", metadata_operations)
print(f"更新结果: {result}")

# 单个文档元数据更新
single_update = [
    {
        "document_id": "doc_3",
        "metadata_list": [
            {"id": author_field.id, "value": "王五", "name": "作者"},
            {"id": version_field.id, "value": "3.0", "name": "版本"}
        ]
    }
]

result = client.update_document_metadata("dataset_id", single_update)
```

### 11.6 切换内置元数据字段

**方法签名：**

```python
def toggle_built_in_metadata_field(
    dataset_id: str,
    action: Literal["disable", "enable"],
) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `action` (str): 操作类型 - "disable" 或 "enable" **(必需)**

**使用示例：**

```python
# 启用内置元数据字段
result = client.toggle_built_in_metadata_field(
    dataset_id="dataset_id",
    action="enable"
)
print(f"启用结果: {result}")

# 禁用内置元数据字段
result = client.toggle_built_in_metadata_field(
    dataset_id="dataset_id",
    action="disable"
)
print(f"禁用结果: {result}")
```

## 12. 知识标签管理 (7 个 API)

### 12.1 创建知识标签

**方法签名：**

```python
def create_knowledge_tag(name: str) -> KnowledgeTag
```

**参数说明：**

- `name` (str): 标签名称，最大 50 个字符 **(必需)**

**使用示例：**

```python
# 创建单个标签
tech_tag = client.create_knowledge_tag("技术文档")
print(f"创建标签ID: {tech_tag.id}")
print(f"标签名称: {tech_tag.name}")

# 批量创建标签
tag_names = ["人工智能", "Web开发", "移动开发", "数据库", "云计算"]
created_tags = []

for tag_name in tag_names:
    try:
        tag = client.create_knowledge_tag(tag_name)
        created_tags.append(tag)
        print(f"✅ 创建成功: {tag.name}")
    except Exception as e:
        print(f"❌ 创建失败 {tag_name}: {e}")

print(f"成功创建 {len(created_tags)} 个标签")
```

### 12.2 绑定数据集到标签

**方法签名：**

```python
def bind_dataset_to_tag(dataset_id: str, tag_ids: List[str]) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `tag_ids` (List[str]): 标签 ID 列表 **(必需)**

**标签管理最佳实践：**

```python
# 创建分类标签体系
def setup_tag_system(client):
    """设置标签分类体系"""

    # 创建主要分类标签
    tech_tag = client.create_knowledge_tag("技术文档")
    business_tag = client.create_knowledge_tag("业务文档")
    process_tag = client.create_knowledge_tag("流程规范")

    # 创建技术子分类
    ai_tag = client.create_knowledge_tag("人工智能")
    web_tag = client.create_knowledge_tag("Web开发")
    mobile_tag = client.create_knowledge_tag("移动开发")

    # 创建优先级标签
    high_priority = client.create_knowledge_tag("高优先级")
    medium_priority = client.create_knowledge_tag("中优先级")
    low_priority = client.create_knowledge_tag("低优先级")

    return {
        "categories": [tech_tag, business_tag, process_tag],
        "tech_subcategories": [ai_tag, web_tag, mobile_tag],
        "priorities": [high_priority, medium_priority, low_priority]
    }

# 使用标签组织数据集
tags = setup_tag_system(client)

# 为AI相关数据集绑定标签
ai_dataset_tags = [
    tags["categories"][0].id,      # 技术文档
    tags["tech_subcategories"][0].id,  # 人工智能
    tags["priorities"][0].id       # 高优先级
]

client.bind_dataset_to_tag("ai_dataset_id", ai_dataset_tags)

# 查询特定标签的数据集
ai_datasets = client.list_datasets(tag_ids=[tags["tech_subcategories"][0].id])
```

**使用示例：**

```python
# 创建标签
tech_tag = client.create_knowledge_tag("技术文档")
ai_tag = client.create_knowledge_tag("人工智能")

# 绑定数据集到多个标签
client.bind_dataset_to_tag(
    dataset_id="dataset_id",
    tag_ids=[tech_tag.id, ai_tag.id]
)

# 获取数据集的标签
dataset_tags = client.get_dataset_tags("dataset_id")
for tag in dataset_tags:
    print(f"标签: {tag.name}")
```

### 12.3 获取知识标签列表

**方法签名：**

```python
def list_knowledge_tags() -> List[KnowledgeTag]
```

**使用示例：**

```python
# 获取所有标签
tags = client.list_knowledge_tags()
print(f"总共 {len(tags)} 个标签")

for tag in tags:
    print(f"ID: {tag.id}, 名称: {tag.name}")

# 按名称搜索标签
def find_tag_by_name(client, tag_name):
    """按名称查找标签"""
    tags = client.list_knowledge_tags()
    for tag in tags:
        if tag.name == tag_name:
            return tag
    return None

# 查找特定标签
ai_tag = find_tag_by_name(client, "人工智能")
if ai_tag:
    print(f"找到标签: {ai_tag.name} (ID: {ai_tag.id})")
else:
    print("未找到指定标签")
```

### 12.4 更新知识标签

**方法签名：**

```python
def update_knowledge_tag(tag_id: str, name: str) -> KnowledgeTag
```

**参数说明：**

- `tag_id` (str): 标签 ID **(必需)**
- `name` (str): 新标签名称，最大 50 个字符 **(必需)**

**使用示例：**

```python
# 更新标签名称
updated_tag = client.update_knowledge_tag(
    tag_id="tag_id",
    name="更新后的标签名称"
)
print(f"更新成功: {updated_tag.name}")

# 批量更新标签
tag_updates = [
    {"id": "tag_1", "name": "AI & 机器学习"},
    {"id": "tag_2", "name": "前端开发"},
    {"id": "tag_3", "name": "后端开发"}
]

for update in tag_updates:
    try:
        updated_tag = client.update_knowledge_tag(
            tag_id=update["id"],
            name=update["name"]
        )
        print(f"✅ 更新成功: {updated_tag.name}")
    except Exception as e:
        print(f"❌ 更新失败 {update['name']}: {e}")
```

### 12.5 删除知识标签

**方法签名：**

```python
def delete_knowledge_tag(tag_id: str) -> Dict[str, Any]
```

**参数说明：**

- `tag_id` (str): 标签 ID **(必需)**

**使用示例：**

```python
# 删除标签(注意：这是不可逆操作)
result = client.delete_knowledge_tag("tag_id")
print(f"删除结果: {result}")

# 安全删除（先检查后删除）
def safe_delete_tag(client, tag_id):
    """安全删除标签"""
    try:
        # 检查标签是否存在
        tags = client.list_knowledge_tags()
        tag_exists = any(tag.id == tag_id for tag in tags)

        if not tag_exists:
            print("标签不存在")
            return False

        # 检查是否有数据集使用该标签
        datasets_with_tag = client.list_datasets(tag_ids=[tag_id])
        if datasets_with_tag.total > 0:
            print(f"警告: 有 {datasets_with_tag.total} 个数据集使用该标签")
            return False

        # 执行删除
        result = client.delete_knowledge_tag(tag_id)
        print("标签删除成功")
        return True

    except Exception as e:
        print(f"删除失败: {e}")
        return False

# 使用安全删除
safe_delete_tag(client, "tag_id")
```

### 12.6 解绑数据集标签

**方法签名：**

```python
def unbind_dataset_from_tag(dataset_id: str, tag_id: str) -> Dict[str, Any]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**
- `tag_id` (str): 标签 ID **(必需)**

**使用示例：**

```python
# 解绑单个标签
result = client.unbind_dataset_from_tag(
    dataset_id="dataset_id",
    tag_id="tag_id"
)
print(f"解绑结果: {result}")

# 批量解绑标签
def unbind_multiple_tags(client, dataset_id, tag_ids):
    """批量解绑数据集标签"""
    success_count = 0

    for tag_id in tag_ids:
        try:
            result = client.unbind_dataset_from_tag(dataset_id, tag_id)
            print(f"✅ 解绑成功: {tag_id}")
            success_count += 1
        except Exception as e:
            print(f"❌ 解绑失败 {tag_id}: {e}")

    print(f"成功解绑 {success_count}/{len(tag_ids)} 个标签")
    return success_count

# 使用示例
tag_ids_to_unbind = ["tag_1", "tag_2", "tag_3"]
unbind_multiple_tags(client, "dataset_id", tag_ids_to_unbind)
```

### 12.7 获取数据集标签

**方法签名：**

```python
def get_dataset_tags(dataset_id: str) -> List[KnowledgeTag]
```

**参数说明：**

- `dataset_id` (str): 数据集 ID **(必需)**

**使用示例：**

```python
# 获取数据集的所有标签
dataset_tags = client.get_dataset_tags("dataset_id")
print(f"数据集共有 {len(dataset_tags)} 个标签")

for tag in dataset_tags:
    print(f"- {tag.name} (ID: {tag.id})")

# 批量查询多个数据集的标签
def get_multiple_dataset_tags(client, dataset_ids):
    """批量获取数据集标签"""
    dataset_tags_map = {}

    for dataset_id in dataset_ids:
        try:
            tags = client.get_dataset_tags(dataset_id)
            dataset_tags_map[dataset_id] = tags
            print(f"✅ 数据集 {dataset_id}: {len(tags)} 个标签")
        except Exception as e:
            print(f"❌ 获取失败 {dataset_id}: {e}")
            dataset_tags_map[dataset_id] = []

    return dataset_tags_map

# 使用示例
dataset_ids = ["dataset_1", "dataset_2", "dataset_3"]
tags_map = get_multiple_dataset_tags(client, dataset_ids)

# 分析标签使用情况
all_tags = []
for tags in tags_map.values():
    all_tags.extend(tags)

# 统计最常用的标签
from collections import Counter
tag_usage = Counter(tag.name for tag in all_tags)
print("\n最常用的标签:")
for tag_name, count in tag_usage.most_common(5):
    print(f"- {tag_name}: {count} 次")
```

## 13. 嵌入模型管理 (1 个 API)

### 13.1 获取可用的嵌入模型列表

**方法签名：**

```python
def list_embedding_models() -> EmbeddingModelResponse
```

**使用示例：**

```python
# 获取可用的嵌入模型
models = client.list_embedding_models()
print(f"共有 {len(models.data)} 个可用模型")

for model in models.data:
    print(f"模型名称: {model.model_name}")
    print(f"提供商: {model.model_provider}")
    print(f"维度: {model.dimensions}")
    print(f"最大tokens: {model.max_tokens}")
    print("-" * 40)

# 按提供商分类模型
def group_models_by_provider(models):
    """按提供商分类模型"""
    provider_groups = {}

    for model in models.data:
        provider = model.model_provider
        if provider not in provider_groups:
            provider_groups[provider] = []
        provider_groups[provider].append(model)

    return provider_groups

# 分类显示
models = client.list_embedding_models()
provider_groups = group_models_by_provider(models)

for provider, provider_models in provider_groups.items():
    print(f"\n{provider} 提供商 ({len(provider_models)} 个模型):")
    for model in provider_models:
        print(f"  - {model.model_name} (维度: {model.dimensions})")

# 选择最适合的模型
def recommend_model(models, requirements=None):
    """根据需求推荐模型"""
    if not requirements:
        requirements = {"language": "chinese", "dimension_preference": "high"}

    suitable_models = []

    for model in models.data:
        # 简单的推荐逻辑
        if "chinese" in requirements.get("language", "").lower():
            if "chinese" in model.model_name.lower() or "multilingual" in model.model_name.lower():
                suitable_models.append(model)
        elif requirements.get("dimension_preference") == "high":
            if model.dimensions >= 1024:
                suitable_models.append(model)

    return suitable_models[:3]  # 返回前3个推荐

# 获取推荐模型
recommended = recommend_model(models, {"language": "chinese"})
print("\n推荐的中文模型:")
for model in recommended:
    print(f"- {model.model_name} ({model.model_provider})")
```

## 14. 错误处理

SDK 提供了完整的异常处理机制：

```python
from dify_dataset_sdk.exceptions import (
    DifyAPIError,
    DifyNotFoundError,
    DifyValidationError,
    DifyAuthenticationError,
    DifyConnectionError,
    DifyTimeoutError
)

try:
    dataset = client.create_dataset(name="测试数据集")
except DifyValidationError as e:
    print(f"参数验证错误: {e}")
except DifyAuthenticationError as e:
    print(f"认证失败: {e}")
except DifyNotFoundError as e:
    print(f"资源未找到: {e}")
except DifyAPIError as e:
    print(f"API错误: {e}")
```

### 高级错误处理

```python
import time
import logging
from dify_dataset_sdk.exceptions import *

def robust_document_creation(client, dataset_id, documents, max_retries=3):
    """带重试机制的文档创建"""

    successful_docs = []
    failed_docs = []

    for doc_data in documents:
        retries = 0
        while retries < max_retries:
            try:
                doc_response = client.create_document_by_text(
                    dataset_id=dataset_id,
                    name=doc_data["name"],
                    text=doc_data["content"]
                )

                # 等待索引完成
                if wait_for_indexing(client, dataset_id, doc_response.batch):
                    successful_docs.append({
                        "name": doc_data["name"],
                        "document_id": doc_response.document.id
                    })
                    break
                else:
                    raise Exception("索引超时")

            except DifyValidationError as e:
                logging.error(f"参数验证错误 {doc_data['name']}: {e}")
                failed_docs.append({"name": doc_data["name"], "error": str(e)})
                break  # 验证错误不重试

            except DifyTimeoutError as e:
                logging.warning(f"超时错误 {doc_data['name']}: {e}")
                retries += 1
                time.sleep(2 ** retries)  # 指数退避

            except DifyAPIError as e:
                if "rate limit" in str(e).lower():
                    logging.warning(f"速率限制 {doc_data['name']}: {e}")
                    time.sleep(60)  # 等待1分钟
                    retries += 1
                else:
                    logging.error(f"API错误 {doc_data['name']}: {e}")
                    failed_docs.append({"name": doc_data["name"], "error": str(e)})
                    break

            except Exception as e:
                logging.error(f"未知错误 {doc_data['name']}: {e}")
                retries += 1
                time.sleep(5)

        if retries >= max_retries:
            failed_docs.append({
                "name": doc_data["name"],
                "error": f"重试{max_retries}次后仍然失败"
            })

    return successful_docs, failed_docs

def wait_for_indexing(client, dataset_id, batch, timeout=300):
    """等待文档索引完成"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            status = client.get_document_indexing_status(dataset_id, batch)
            if status.data:
                indexing_status = status.data[0].indexing_status
                if indexing_status == "completed":
                    return True
                elif indexing_status in ["error", "paused"]:
                    return False
            time.sleep(2)
        except Exception as e:
            logging.warning(f"检查索引状态时出错: {e}")
            time.sleep(5)

    return False  # 超时
```

## 15. 性能优化建议

### 并发处理示例

```python
import asyncio
import concurrent.futures
from typing import List, Dict, Any

# 并发处理示例
def concurrent_document_processing(client, dataset_id, documents: List[Dict], max_workers=5):
    """并发处理多个文档"""

    def process_single_document(doc_data):
        try:
            return client.create_document_by_text(
                dataset_id=dataset_id,
                name=doc_data["name"],
                text=doc_data["content"]
            )
        except Exception as e:
            return {"error": str(e), "doc_name": doc_data["name"]}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_doc = {
            executor.submit(process_single_document, doc): doc
            for doc in documents
        }

        results = []
        for future in concurrent.futures.as_completed(future_to_doc):
            doc_data = future_to_doc[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "doc_name": doc_data["name"]
                })

        return results

# 分批处理大量文档
def batch_process_large_dataset(client, dataset_id, documents: List[Dict], batch_size=10):
    """分批处理大量文档"""

    total_docs = len(documents)
    processed = 0
    all_results = []

    for i in range(0, total_docs, batch_size):
        batch = documents[i:i + batch_size]
        print(f"处理批次 {i//batch_size + 1}: {len(batch)} 个文档")

        batch_results = concurrent_document_processing(
            client, dataset_id, batch, max_workers=min(5, len(batch))
        )

        all_results.extend(batch_results)
        processed += len(batch)

        print(f"已处理: {processed}/{total_docs}")

        # 批次间休息，避免过载
        if i + batch_size < total_docs:
            time.sleep(1)

    return all_results
```

## 16. 最佳实践

### 16.1 客户端管理

```python
# 使用上下文管理器自动关闭连接
from dify_dataset_sdk import DifyDatasetClient

with DifyDatasetClient(api_key="your-api-key") as client:
    # 执行操作
    dataset = client.create_dataset(name="测试")
    # 客户端会自动关闭

# 手动管理连接
client = DifyDatasetClient(api_key="your-api-key")
try:
    # 执行操作
    dataset = client.create_dataset(name="测试")
finally:
    client.close()  # 确保连接关闭
```

### 16.2 批量操作优化

```python
# 批量处理文档
import time

def process_documents_batch(client, dataset_id, documents):
    """批量处理文档的示例"""
    for doc_data in documents:
        try:
            doc_response = client.create_document_by_text(
                dataset_id=dataset_id,
                name=doc_data["name"],
                text=doc_data["content"]
            )

            # 监控索引状态
            while True:
                status = client.get_document_indexing_status(
                    dataset_id, doc_response.batch
                )

                if status.data[0].indexing_status == "completed":
                    print(f"文档 {doc_data['name']} 索引完成")
                    break
                elif status.data[0].indexing_status == "error":
                    print(f"文档 {doc_data['name']} 索引失败")
                    break

                time.sleep(2)  # 等待2秒后再次检查

        except Exception as e:
            print(f"处理文档 {doc_data['name']} 时出错: {e}")
```

### 16.3 高级检索配置

```python
from dify_dataset_sdk.models import (
    RetrievalModel,
    MetadataFilteringConditions,
    MetadataCondition
)

# 配置高级检索
metadata_filter = MetadataFilteringConditions(
    logical_operator="and",
    conditions=[
        MetadataCondition(
            name="作者",
            comparison_operator="is",
            value="张三"
        ),
        MetadataCondition(
            name="版本号",
            comparison_operator="≥",
            value=2.0
        )
    ]
)

advanced_retrieval = RetrievalModel(
    search_method="hybrid_search",
    reranking_enable=True,
    top_k=10,
    score_threshold_enabled=True,
    score_threshold=0.5,
    metadata_filtering_conditions=metadata_filter
)

results = client.retrieve(
    dataset_id="dataset_id",
    query="搜索查询",
    retrieval_model=advanced_retrieval
)
```

### 16.4 监控和日志

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def monitor_dataset_operations(client, dataset_id):
    """监控数据集操作"""

    # 获取数据集基本信息
    dataset = client.get_dataset(dataset_id)
    logging.info(f"数据集 {dataset.name} 包含 {dataset.document_count} 个文档")

    # 获取文档列表
    documents = client.list_documents(dataset_id)
    logging.info(f"获取到 {len(documents.data)} 个文档")

    # 检查文档状态
    for doc in documents.data:
        if doc.status != "completed":
            logging.warning(f"文档 {doc.name} 状态异常: {doc.status}")

    # 检查嵌入模型
    models = client.list_embedding_models()
    logging.info(f"可用嵌入模型: {len(models.data)} 个")
```

## 17. 高级应用场景

### 17.1 企业知识库构建

```python
import time
from pathlib import Path
from typing import Dict, List, Any

def build_enterprise_knowledge_base(client, config: Dict[str, Any]):
    """构建企业级知识库"""

    # 1. 创建分类数据集
    datasets = {}
    dataset_configs = [
        {
            "name": "公司政策与制度",
            "description": "包含公司各类政策、制度和规范",
            "tags": ["政策", "制度", "规范"]
        },
        {
            "name": "技术文档与教程",
            "description": "技术开发相关文档和教程",
            "tags": ["技术", "开发", "教程"]
        },
        {
            "name": "产品运营知识",
            "description": "产品设计、运营相关知识",
            "tags": ["产品", "运营", "设计"]
        }
    ]

    # 创建所有数据集
    for config in dataset_configs:
        dataset = client.create_dataset(
            name=config["name"],
            description=config["description"],
            permission="all_team_members",
            indexing_technique="high_quality"
        )
        datasets[config["name"]] = dataset
        print(f"✅ 创建数据集: {dataset.name}")

        # 创建和绑定标签
        tag_ids = []
        for tag_name in config["tags"]:
            try:
                tag = client.create_knowledge_tag(tag_name)
                tag_ids.append(tag.id)
            except:
                # 标签可能已存在
                tags = client.list_knowledge_tags()
                for existing_tag in tags:
                    if existing_tag.name == tag_name:
                        tag_ids.append(existing_tag.id)
                        break

        if tag_ids:
            client.bind_dataset_to_tag(dataset.id, tag_ids)

    return datasets

def batch_import_documents(client, dataset_id: str, doc_folder: Path):
    """批量导入文档"""

    supported_extensions = ['.txt', '.md', '.pdf', '.docx', '.xlsx', '.csv', '.html']
    imported_docs = []
    failed_docs = []

    for file_path in doc_folder.rglob('*'):
        if file_path.suffix.lower() in supported_extensions:
            try:
                print(f"导入文件: {file_path.name}")

                # 创建文档
                doc_response = client.create_document_by_file(
                    dataset_id=dataset_id,
                    file_path=file_path,
                    indexing_technique="high_quality"
                )

                # 等待索引完成
                if wait_for_indexing_complete(client, dataset_id, doc_response.batch):
                    imported_docs.append({
                        "file": file_path.name,
                        "document_id": doc_response.document.id
                    })
                    print(f"✅ 导入成功: {file_path.name}")
                else:
                    failed_docs.append({"file": file_path.name, "error": "索引超时"})

            except Exception as e:
                failed_docs.append({"file": file_path.name, "error": str(e)})
                print(f"❌ 导入失败 {file_path.name}: {e}")

            # 避免过于频繁的请求
            time.sleep(1)

    return imported_docs, failed_docs

def wait_for_indexing_complete(client, dataset_id: str, batch_id: str, timeout: int = 300) -> bool:
    """等待文档索引完成"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            status = client.get_document_indexing_status(dataset_id, batch_id)
            if status.data and len(status.data) > 0:
                indexing_status = status.data[0].indexing_status
                if indexing_status == "completed":
                    return True
                elif indexing_status in ["error", "paused"]:
                    return False
            time.sleep(2)
        except Exception:
            time.sleep(5)

    return False
```

### 17.2 智能问答系统

```python
from dify_dataset_sdk.models import RetrievalModel, MetadataFilteringConditions, MetadataCondition

class IntelligentQASystem:
    """智能问答系统"""

    def __init__(self, client, dataset_configs: Dict[str, str]):
        self.client = client
        self.dataset_configs = dataset_configs  # {"category": "dataset_id"}

    def intelligent_search(self, query: str, category: str = None, filters: Dict = None) -> List[Dict]:
        """智能搜索"""

        # 选择数据集
        dataset_ids = [self.dataset_configs[category]] if category else list(self.dataset_configs.values())

        all_results = []

        for dataset_id in dataset_ids:
            # 构建检索配置
            retrieval_config = self._build_retrieval_config(filters)

            try:
                results = self.client.retrieve(
                    dataset_id=dataset_id,
                    query=query,
                    retrieval_model=retrieval_config
                )

                for result in results.data:
                    all_results.append({
                        "content": result.content,
                        "score": result.score,
                        "source": result.document_name,
                        "dataset": dataset_id,
                        "metadata": getattr(result, 'metadata', {})
                    })

            except Exception as e:
                print(f"搜索数据集 {dataset_id} 失败: {e}")

        # 按相关度排序
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:10]  # 返回前10个结果

    def _build_retrieval_config(self, filters: Dict = None) -> RetrievalModel:
        """构建检索配置"""

        config = RetrievalModel(
            search_method="hybrid_search",
            weights=0.4,  # 语义搜索权重
            top_k=20,
            score_threshold_enabled=True,
            score_threshold=0.3,
            reranking_enable=True,
            reranking_mode="weighted_score"
        )

        # 添加元数据过滤
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(MetadataCondition(
                    name=key,
                    comparison_operator="is",
                    value=value
                ))

            if conditions:
                config.metadata_filtering_conditions = MetadataFilteringConditions(
                    logical_operator="and",
                    conditions=conditions
                )

        return config

    def answer_question(self, question: str, context_limit: int = 3) -> Dict[str, Any]:
        """回答问题"""

        # 搜索相关内容
        search_results = self.intelligent_search(question)

        if not search_results:
            return {
                "answer": "抱歉，没有找到相关信息。",
                "confidence": 0.0,
                "sources": []
            }

        # 选择最相关的内容
        top_results = search_results[:context_limit]

        # 组合上下文
        context = "\n\n".join([result["content"] for result in top_results])

        # 计算置信度
        avg_score = sum(result["score"] for result in top_results) / len(top_results)
        confidence = min(avg_score, 1.0)

        return {
            "context": context,
            "confidence": confidence,
            "sources": [{
                "title": result["source"],
                "score": result["score"]
            } for result in top_results],
            "total_results": len(search_results)
        }

# 使用示例
qa_system = IntelligentQASystem(client, {
    "policy": "policy_dataset_id",
    "tech": "tech_dataset_id",
    "product": "product_dataset_id"
})

# 智能问答
result = qa_system.answer_question("公司的请假政策是什么？")
print(f"置信度: {result['confidence']:.2f}")
print(f"参考源: {[s['title'] for s in result['sources']]}")
```

### 17.3 内容审核与质量控制

```python
import re
from typing import List, Dict, Tuple

class ContentQualityController:
    """内容质量控制器"""

    def __init__(self, client):
        self.client = client
        self.quality_rules = {
            "min_content_length": 50,
            "max_content_length": 10000,
            "forbidden_patterns": [
                r"\b(\w)\1{5,}\b",  # 连续重复字符
                r"(\b\w+\b)\s+\1\s+\1",  # 重复词语
            ],
            "required_keywords_ratio": 0.02  # 关键词密度
        }

    def validate_document(self, content: str, keywords: List[str] = None) -> Tuple[bool, List[str]]:
        """验证文档质量"""

        issues = []

        # 1. 检查内容长度
        if len(content) < self.quality_rules["min_content_length"]:
            issues.append(f"内容过短，少于 {self.quality_rules['min_content_length']} 个字符")

        if len(content) > self.quality_rules["max_content_length"]:
            issues.append(f"内容过长，超过 {self.quality_rules['max_content_length']} 个字符")

        # 2. 检查禁止模式
        for pattern in self.quality_rules["forbidden_patterns"]:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"内容包含不允许的模式: {pattern}")

        # 3. 检查关键词密度
        if keywords:
            total_words = len(content.split())
            keyword_count = sum(content.lower().count(kw.lower()) for kw in keywords)
            keyword_ratio = keyword_count / total_words if total_words > 0 else 0

            if keyword_ratio < self.quality_rules["required_keywords_ratio"]:
                issues.append(f"关键词密度过低: {keyword_ratio:.3f}")

        return len(issues) == 0, issues

    def audit_dataset_quality(self, dataset_id: str) -> Dict[str, Any]:
        """审核数据集质量"""

        documents = self.client.list_documents(dataset_id, limit=100)
        quality_report = {
            "total_documents": len(documents.data),
            "passed": 0,
            "failed": 0,
            "issues": []
        }

        for doc in documents.data:
            try:
                # 获取文档详情
                doc_detail = self.client.get_document(dataset_id, doc.id)

                # 获取文档片段
                segments = self.client.list_segments(dataset_id, doc.id)

                for segment in segments.data:
                    is_valid, issues = self.validate_document(
                        segment.content,
                        getattr(segment, 'keywords', [])
                    )

                    if is_valid:
                        quality_report["passed"] += 1
                    else:
                        quality_report["failed"] += 1
                        quality_report["issues"].append({
                            "document": doc.name,
                            "segment_id": segment.id,
                            "issues": issues
                        })

            except Exception as e:
                quality_report["issues"].append({
                    "document": doc.name,
                    "error": str(e)
                })

        quality_report["pass_rate"] = quality_report["passed"] / (quality_report["passed"] + quality_report["failed"]) if (quality_report["passed"] + quality_report["failed"]) > 0 else 0

        return quality_report

    def auto_fix_common_issues(self, dataset_id: str, document_id: str) -> bool:
        """自动修复常见问题"""

        try:
            segments = self.client.list_segments(dataset_id, document_id)
            fixed_count = 0

            for segment in segments.data:
                original_content = segment.content
                fixed_content = original_content

                # 移除多余空格
                fixed_content = re.sub(r'\s+', ' ', fixed_content)

                # 移除重复句子
                sentences = fixed_content.split('.')
                unique_sentences = []
                for sentence in sentences:
                    if sentence.strip() not in [s.strip() for s in unique_sentences]:
                        unique_sentences.append(sentence)
                fixed_content = '.'.join(unique_sentences)

                # 如果内容有变化，更新片段
                if fixed_content != original_content:
                    self.client.update_segment(
                        dataset_id=dataset_id,
                        document_id=document_id,
                        segment_id=segment.id,
                        segment_data={"content": fixed_content}
                    )
                    fixed_count += 1

            return fixed_count > 0

        except Exception as e:
            print(f"自动修复失败: {e}")
            return False

# 使用示例
quality_controller = ContentQualityController(client)

# 审核数据集质量
report = quality_controller.audit_dataset_quality("dataset_id")
print(f"质量报告: 通过率 {report['pass_rate']:.2%}")
print(f"发现 {len(report['issues'])} 个问题")

# 自动修复
for issue in report['issues']:
    if 'document' in issue:
        quality_controller.auto_fix_common_issues(
            "dataset_id",
            issue['document']
        )
```

---

## 总结

本文档提供了 Dify Dataset SDK 所有 39 个 API 的完整参考，包括：

- 📚 **5 个数据集管理 API**：创建、查询、更新、删除数据集
- 📄 **8 个文档管理 API**：文档的完整生命周期管理
- 🔄 **1 个批量操作 API**：高效的批量文档状态管理
- ✂️ **5 个片段管理 API**：精细化的内容片段控制
- 🌳 **4 个子片段管理 API**：分层内容结构支持
- 🔍 **1 个检索 API**：强大的语义和混合搜索
- 📁 **1 个文件管理 API**：上传文件信息查询
- 🏷️ **6 个元数据管理 API**：自定义元数据字段和关联
- 🔖 **7 个知识标签管理 API**：标签化知识组织
- 🤖 **1 个嵌入模型管理 API**：模型信息查询

SDK 提供了完整的类型安全、错误处理、性能优化和最佳实践指南，能够满足从简单到复杂的各种知识库管理需求。

---

📝 **注意**: 本文档基于 Dify Dataset SDK v0.3.0 版本编写。建议查看最新的 [GitHub 仓库](https://github.com/LeekJay/dify-dataset-sdk) 获取最新功能和更新。

🔗 **相关链接**:

- [SDK GitHub 仓库](https://github.com/LeekJay/dify-dataset-sdk)
- [Dify 官方文档](https://docs.dify.ai/)
- [PyPI 包页面](https://pypi.org/project/dify-dataset-sdk/)
- [问题反馈](https://github.com/LeekJay/dify-dataset-sdk/issues)
