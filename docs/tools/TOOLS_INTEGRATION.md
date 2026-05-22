# Software Tools Integration

This document describes how tools from the software-tools knowledge base are integrated.

## Agent Protocols & Integrations

### Model Context Protocol (MCP)
- **Status**: Configured
- **Usage**: AI agents can query SBOM data via MCP server endpoints
- **Config**: MCP server defined in `.opencode/mcp.json`

### Agent Skills
- **Status**: Available
- **Usage**: Pre-built skills for SBOM analysis, firmware verification, and provenance tracing
- **Location**: `docs/tools/skills/`

### Desktop Extensions (DXT)
- **Status**: Packaged
- **Usage**: One-click MCP server installation for Claude Desktop and Codex Desktop

## AI Agents & Coding Assistants

### Claude Code
- **Config**: `.claude.json` with project context
- **Commands**: Automated SBOM creation, firmware verification, provenance tracing

### Claude Desktop
- **Extension**: MCP server for SBOM querying
- **Tools**: Firmware hash verification, vulnerability lookup

### Codex Desktop
- **Workspace**: Multi-agent parallel SBOM analysis
- **Agents**: SBOM creation agent, firmware verification agent

### Devin
- **Workflow**: Automated supply chain analysis
- **Integration**: API-based task delegation

### Hermes Agent
- **Scheduled Tasks**: Daily vulnerability scans, weekly SBOM reports
- **Channels**: Slack/Teams notifications for approval requests

## AI Evaluation & Observability

### Weights & Biases Weave
- **Tracing**: LLM API call tracing for AI-powered SBOM analysis
- **Evaluation**: SBOM quality scoring, firmware verification accuracy
- **Dataset**: SBOM validation results tracking

### OpenTelemetry
- **Instrumentation**: Automatic tracing of all API requests
- **Export**: Traces to configured OTLP endpoint

## Local AI & Model Serving

### Ollama
- **Models**: Local LLMs for SBOM analysis
- **API**: OpenAI-compatible endpoint for AI features

### llama.cpp
- **Inference**: On-device firmware analysis
- **Integration**: CLI tool for local hash verification

### vLLM / SGLang
- **Serving**: High-throughput model serving for batch SBOM processing
- **Optimization**: PagedAttention for large batch analysis

## Vector Databases & Retrieval

### Chroma
- **Status**: Default vector store
- **Usage**: SBOM semantic search, firmware similarity matching
- **Collection**: `sbom_embeddings`

### Qdrant
- **Status**: Alternative vector store
- **Usage**: High-scale SBOM retrieval
- **Config**: Set `VECTOR_DB_PROVIDER=qdrant`

### LanceDB / Milvus / Weaviate
- **Status**: Optional
- **Config**: Selectable via environment variable

## Data Lakehouse & Analytics

### Apache Iceberg
- **Usage**: SBOM data lake catalog
- **Integration**: PyIceberg for table management

### DuckDB
- **Usage**: Local SBOM analytics and reporting
- **Features**: In-process SQL queries over SBOM data

### Trino
- **Usage**: Federated queries across SBOM stores
- **Federation**: Join SBOM data with external databases

### Apache Arrow
- **Usage**: High-performance SBOM data interchange
- **Integration**: PyArrow for columnar data processing

### Apache DataFusion
- **Usage**: Custom SBOM analytics queries
- **Optimization**: Vectorized execution for large SBOM datasets

## Cloud-Native & Security

### Cilium Tetragon
- **Usage**: Runtime security monitoring
- **Monitoring**: eBPF-based process execution tracking

### Post-Quantum Cryptography
- **Libraries**: liboqs integration for quantum-resistant signatures
- **Usage**: Future-proof firmware signing

## Configuration

Vector store and AI model selection via environment variables:

```bash
# Vector DB
export VECTOR_DB_PROVIDER=chroma  # or qdrant, lancedb
export VECTOR_DB_URL=http://localhost:8001

# AI Models
export OLLAMA_BASE_URL=http://localhost:11434
export OPENAI_API_KEY=sk-...
```
