# Dify Knowledge SDK 示例集合

本目录包含了 Dify Knowledge SDK 的各种使用示例，从基础用法到高级应用场景。

## 📁 示例文件概览

### 基础示例
- **[basic_usage.py](basic_usage.py)** - 基础用法示例
  - 数据集创建和管理
  - 文档上传和更新
  - 基础检索功能
  - 元数据管理

- **[advanced_usage.py](advanced_usage.py)** - 高级用法示例
  - 自定义处理规则
  - 文件上传功能
  - 批量操作
  - 复杂工作流程

### 专题示例

#### 🏷️ 知识标签管理
- **[knowledge_tag_management.py](knowledge_tag_management.py)**
  - 创建标签分类系统
  - 数据集与标签绑定
  - 标签查询和过滤
  - 标签批量操作

#### 📚 批量文档处理
- **[batch_document_processing.py](batch_document_processing.py)**
  - 并行文档上传
  - 批量索引监控
  - 批量元数据更新
  - 处理结果分析

#### 🔍 高级检索分析
- **[advanced_retrieval_analysis.py](advanced_retrieval_analysis.py)**
  - 多种检索策略对比
  - 检索性能分析
  - 参数优化建议
  - 检索质量评估

#### 🛡️ 错误处理和监控
- **[error_handling_and_monitoring.py](error_handling_and_monitoring.py)**
  - 异常处理最佳实践
  - 自动重试机制
  - 系统健康检查
  - 性能监控和日志

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install dify-knowledge-sdk
```

### 2. 配置API密钥
在运行示例之前，请将代码中的 `YOUR_API_KEY_HERE` 替换为你的实际API密钥：

```python
api_key = "your_actual_api_key_here"
base_url = "https://api.dify.ai"  # 或你的私有部署地址
```

### 3. 运行示例
```bash
# 基础示例
python examples/basic_usage.py

# 高级示例
python examples/advanced_usage.py

# 专题示例
python examples/knowledge_tag_management.py
python examples/batch_document_processing.py
python examples/advanced_retrieval_analysis.py
python examples/error_handling_and_monitoring.py
```

## 📖 示例详解

### 基础用法示例
适合初学者，展示了SDK的基本功能：
- ✅ 创建和管理数据集
- ✅ 上传和更新文档
- ✅ 基础检索操作
- ✅ 元数据字段管理

### 知识标签管理示例
演示企业级标签分类系统的构建：
- 🏷️ 多层级标签体系
- 🔗 数据集标签绑定
- 🎯 基于标签的过滤查询
- 📊 标签使用统计

### 批量文档处理示例
展示大规模文档处理的最佳实践：
- ⚡ 并行上传优化
- 📈 实时进度监控
- 📝 批量元数据管理
- 📊 处理结果报告

### 高级检索分析示例
深入探索检索功能的优化：
- 🔍 多种检索算法对比
- ⚡ 性能基准测试
- 🎯 参数调优建议
- 📈 检索质量评估

### 错误处理和监控示例
构建生产级的健壮应用：
- 🛡️ 全面异常处理
- 🔄 智能重试机制
- 🏥 系统健康监控
- 📊 性能指标追踪

## 💡 最佳实践建议

### 1. 错误处理
- 使用适当的异常捕获
- 实现重试机制
- 记录详细的错误日志

### 2. 性能优化
- 合理设置请求间隔
- 使用并行处理提高效率
- 监控API调用频率

### 3. 数据管理
- 规划好数据集结构
- 设计合理的标签体系
- 定期清理无用数据

### 4. 监控运维
- 实施健康检查
- 监控关键指标
- 设置告警机制

## 🤝 贡献指南

欢迎贡献更多示例！请确保：
- 代码清晰易懂
- 包含详细注释
- 提供使用说明
- 遵循最佳实践

## 📞 获取帮助

如果你在使用示例时遇到问题：
1. 检查API密钥是否正确配置
2. 确认网络连接正常
3. 查看错误日志信息
4. 参考官方文档

## 📝 更新日志

- **v1.0.0** - 初始版本，包含基础和高级示例
- **v1.1.0** - 新增知识标签管理示例
- **v1.2.0** - 新增批量处理和检索分析示例
- **v1.3.0** - 新增错误处理和监控示例

---

> 💡 **提示**: 这些示例旨在展示SDK的各种功能和最佳实践。在生产环境中使用时，请根据实际需求进行调整和优化。