# Lyceum CLI

Command-line interface for Lyceum Cloud Execution API - Execute code, run inference, and manage batch processing in the cloud.

## Features

- **Code Execution**: Run Python scripts and Docker containers on powerful cloud infrastructure
- **AI Inference**: Synchronous and batch inference with various AI models
- **Batch Processing**: OpenAI-compatible batch API for large-scale AI workloads
- **Resource Management**: List available machine types and monitor running jobs
- **S3 Storage**: Built-in file management with S3 backend

## Installation

```bash
pip install lyceum-cli
```

## Quick Start

1. **Login** with your API key:
```bash
lyceum login --api-key your-api-key-here
```

2. **Run Python code**:
```bash
lyceum run-python "print('Hello from the cloud!')"
```

3. **List available resources**:
```bash
lyceum machine-types
```

## Batch Processing

Upload and process large batches of AI requests:

```bash
# Upload a JSONL file
lyceum batch upload requests.jsonl

# Create batch job
lyceum batch create file_abc123 --endpoint /v1/chat/completions

# Monitor progress
lyceum batch get batch_xyz789

# Download results
lyceum batch download file_output123
```

## Command Structure

### Legacy Commands (for compatibility)
- `lyceum login` / `lyceum logout` / `lyceum status`
- `lyceum run-python` / `lyceum run-docker`
- `lyceum machine-types` / `lyceum list-jobs` / `lyceum abort`

### New Modular Commands
- `lyceum auth login` / `lyceum auth logout` / `lyceum auth status`
- `lyceum python run` / `lyceum docker run`
- `lyceum workloads list` / `lyceum workloads abort` / `lyceum workloads history`
- `lyceum batch upload` / `lyceum batch create` / `lyceum batch list`
- `lyceum resources machine-types`

## Configuration

Configuration is stored in `~/.lyceum/config.json`:

```json
{
  "api_key": "your-api-key",
  "base_url": "https://api.lyceum.technology"
}
```

## Support

- Documentation: https://docs.lyceum.technology
- Support: support@lyceum.technology
- Issues: https://github.com/lyceum/lyceum-cli/issues