# LlamaIndex Agent with File Storage

This example demonstrates how to integrate the new **File Storage System** with a LlamaIndex agent, providing persistent file management capabilities alongside the original mathematical tools.

## Files

- **`llamaindex_agent_with_file_storage.py`** - Enhanced LlamaIndex agent with file storage capabilities
- **`demo_file_storage_agent.py`** - Interactive demonstration script
- **`llamaindex_agent.py`** - Original agent (for comparison)

## Features

### 🗂️ File Storage Capabilities

The enhanced agent provides four new file management tools:

1. **`create_file(filename, content)`** - Create and store text files
2. **`read_file(file_id)`** - Read stored files by ID
3. **`list_files()`** - List all files with metadata
4. **`delete_file(file_id)`** - Delete files by ID

### 🧮 Original Math Tools

All original mathematical capabilities are preserved:

- **`add(a, b)`** - Addition
- **`subtract(a, b)`** - Subtraction  
- **`multiply(a, b)`** - Multiplication
- **`divide(a, b)`** - Division

### 💾 Storage Backends

The file storage system supports multiple backends:

- **Local Storage** - Filesystem-based (always available)
- **AWS S3** - Cloud storage (optional, requires `boto3`)
- **MinIO** - Self-hosted S3-compatible storage (optional, requires `minio`)

## Quick Start

### 1. Run the Enhanced Agent Server

```bash
# Install dependencies
uv pip install llama-index

# Set up environment
export OPENAI_API_KEY="your-api-key"
export AGENT_PORT="8001"  # Different port from original

# Run the enhanced agent
uv run python examples/llamaindex_agent_with_file_storage.py
```

The server will start on `http://localhost:8001` (default) with:
- Web UI: `http://localhost:8001/ui`
- Test interface: `http://localhost:8001/testapp`
- API docs: `http://localhost:8001/docs`

### 2. Run the Demo Script

```bash
# Run the interactive demonstration
uv run python examples/demo_file_storage_agent.py
```

This will demonstrate:
- Creating files with custom content
- Reading and summarizing file contents
- Listing files with metadata
- Combining math operations with file storage
- Cleaning up files

### 3. Try Interactive Examples

Once the server is running, try these example prompts:

#### File Creation
```
Create a file called 'meeting_notes.txt' with notes from today's team meeting including action items and deadlines.
```

#### File Reading
```
Read the meeting_notes.txt file and extract all the action items.
```

#### Combined Operations
```
Calculate the total budget (5000 + 3000 + 2000) and create a file called 'budget_summary.txt' with the calculation and breakdown.
```

#### File Management
```
List all my files and show their sizes and creation dates.
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional
AGENT_PORT=8001
OPENAI_API_MODEL=gpt-4o-mini

# File Storage (optional)
LOCAL_STORAGE_PATH=./file_storage
AWS_S3_BUCKET=my-agent-files
MINIO_ENDPOINT=localhost:9000
```

### Storage Backend Setup

#### Local Storage (Default)
No additional setup required. Files are stored in `./file_storage/`.

#### AWS S3 (Optional)
```bash
# Install boto3
uv pip install boto3

# Configure AWS
export AWS_S3_BUCKET=my-agent-files
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

#### MinIO (Optional)
```bash
# Install minio client
uv pip install minio

# Configure MinIO
export MINIO_ENDPOINT=localhost:9000
export MINIO_ACCESS_KEY=minioadmin
export MINIO_SECRET_KEY=minioadmin
export MINIO_BUCKET=agent-files
```

## API Examples

### File Upload via API

```bash
curl -X POST "http://localhost:8001/files/upload" \
  -H "Authorization: Bearer your-token" \
  -F "file=@example.txt" \
  -F "user_id=user-123" \
  -F "session_id=session-123"
```

### File Download via API

```bash
curl -X GET "http://localhost:8001/files/{file_id}/download" \
  -H "Authorization: Bearer your-token" \
  -o downloaded_file.txt
```

### List Files via API

```bash
curl -X GET "http://localhost:8001/files?user_id=user-123" \
  -H "Authorization: Bearer your-token"
```

## Key Differences from Original Agent

| Feature | Original Agent | Enhanced Agent |
|---------|---------------|----------------|
| **Tools** | 4 math tools | 8 tools (4 math + 4 file) |
| **Storage** | Memory only | Persistent file storage |
| **File Support** | Base64 in responses | Persistent with metadata |
| **Backends** | None | Local, S3, MinIO |
| **Port** | 8000 | 8001 |
| **Use Cases** | Math calculations | Math + document management |

## File Metadata

Each stored file includes comprehensive metadata:

```json
{
  "file_id": "uuid-here",
  "filename": "example.txt",
  "mime_type": "text/plain",
  "size_bytes": 1234,
  "created_at": "2025-07-28T12:37:33Z",
  "updated_at": "2025-07-28T12:37:33Z",
  "user_id": "user-123",
  "session_id": "session-123",
  "agent_id": "agent-456",
  "is_generated": true,
  "tags": ["agent-created", "text-file"],
  "storage_backend": "local"
}
```

## Use Cases

### 📊 Report Generation
- Create detailed reports and save them as files
- Generate summaries and export for later use
- Build documents with calculated data

### 📝 Note Taking
- Store meeting notes and action items
- Create persistent documentation
- Manage project files

### 🔄 Data Processing
- Process data and save results
- Create analysis files
- Export calculation results

### 📋 Document Management
- Organize files by session
- Search and retrieve documents
- Clean up old files

## Troubleshooting

### Common Issues

1. **File Not Found**
   - Check the file ID is correct
   - Ensure the file belongs to the current user/session

2. **Storage Backend Error**
   - Verify environment variables are set
   - Check network connectivity for S3/MinIO
   - Ensure proper permissions

3. **Large File Handling**
   - File size limits may apply
   - Consider using streaming for large files

### Debug Mode

Enable debug logging to see detailed file operations:

```python
import logging
logging.getLogger('agent_framework.file_storage').setLevel(logging.DEBUG)
```

## Advanced Usage

### Custom File Processors

You can extend the agent with custom file processing:

```python
async def process_csv_file(self, file_id: str) -> str:
    """Custom tool to process CSV files"""
    content, metadata = await self._file_storage_manager.retrieve_file(file_id)
    # Process CSV content...
    return "Processed CSV data"
```

### File Type Routing

Configure automatic routing based on file types:

```bash
# Route images to S3, documents to local
export FILE_ROUTING_RULES="image/:s3,text/:local"
```

## Contributing

To extend this example:

1. Add new file processing tools
2. Implement custom storage backends
3. Add file validation and processing
4. Extend metadata with custom fields

For the complete file storage documentation, see: [File Storage Implementation Guide](../docs/file_storage_system_implementation.md) 