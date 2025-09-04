# File Storage System Implementation

**Implementation Date:** July 28, 2025 12:37 CEST  
**Version:** 0.1.7  
**Author:** AI Assistant  
**Status:** Completed and Tested

## Overview

The Agent Framework now includes a comprehensive file storage system that provides persistent file management capabilities beyond the previous in-memory-only approach. This system supports multiple storage backends, file metadata management, agent-generated file tracking, and seamless integration with the existing framework architecture.

## What Was Implemented

### 1. Core File Storage Architecture

#### 1.1 Abstract File Storage Interface (`FileStorageInterface`)
- **Location:** `agent_framework/file_storage.py`
- **Purpose:** Provides a unified interface for all storage backends
- **Key Methods:**
  - `initialize()`: Backend initialization
  - `store_file()`: Store files with metadata
  - `retrieve_file()`: Retrieve files and metadata
  - `delete_file()`: Remove files
  - `list_files()`: List files with filtering
  - `update_metadata()`: Update file metadata
  - `file_exists()`: Check file existence
  - `get_file_metadata()`: Get metadata only

#### 1.2 File Metadata Management (`FileMetadata`)
- **Comprehensive metadata tracking:**
  - File ID, filename, MIME type
  - Size, creation/update timestamps
  - User ID, session ID, agent ID associations
  - Generated vs uploaded file distinction
  - Custom tags and metadata
  - Storage backend and path information

### 2. Storage Backend Implementations

#### 2.1 Local File Storage (`LocalFileStorage`)
- **Location:** `agent_framework/local_file_storage.py`
- **Features:**
  - Filesystem-based storage
  - JSON metadata persistence
  - Automatic directory creation
  - Error handling and recovery

#### 2.2 AWS S3 Storage (`S3FileStorage`)
- **Location:** `agent_framework/s3_file_storage.py`
- **Features:**
  - AWS S3 integration with boto3
  - Object metadata storage
  - Bucket access validation
  - Error handling for network issues
  - **Optional dependency:** Requires `boto3` installation

#### 2.3 MinIO Storage (`MinIOFileStorage`)
- **Location:** `agent_framework/minio_file_storage.py`
- **Features:**
  - MinIO/S3-compatible storage
  - Self-hosted storage support
  - Bucket auto-creation
  - **Optional dependency:** Requires `minio` package

### 3. Multi-Storage Management System

#### 3.1 File Storage Manager (`FileStorageManager`)
- **Location:** `agent_framework/file_storage_manager.py`
- **Capabilities:**
  - Multiple backend registration
  - Intelligent routing rules based on MIME types
  - Cross-backend file discovery
  - Unified API for all operations
  - Backend fallback support

#### 3.2 File Storage Factory (`FileStorageFactory`)
- **Location:** `agent_framework/file_storage_factory.py`
- **Features:**
  - Environment-based configuration
  - Automatic backend detection and registration
  - Routing rule setup
  - Configuration templates

### 4. Agent Integration Components

#### 4.1 Enhanced Agent Interface
- **Location:** `agent_framework/agent_interface.py`
- **New Components:**
  - `FileReferenceInputPart`: References to stored files in input
  - `FileReferenceOutputPart`: References to stored files in output
  - Enhanced `AgentInputPartUnion` and `AgentOutputPartUnion`

#### 4.2 File Output Processor (`FileOutputProcessor`)
- **Location:** `agent_framework/file_output_processor.py`
- **Functions:**
  - Converts agent-generated `FileContentOutputPart` to persistent storage
  - Creates `FileReferenceOutputPart` for stored files
  - Resolves file references back to content for backward compatibility
  - Session file statistics and cleanup

### 5. Server Integration

#### 5.1 FastAPI Endpoints
- **Location:** `agent_framework/server.py`
- **New Endpoints:**
  - `POST /files/upload`: Upload files to storage
  - `GET /files/{file_id}/download`: Download files
  - `GET /files/{file_id}/metadata`: Get file metadata
  - `GET /files`: List files with filtering
  - `DELETE /files/{file_id}`: Delete files
  - `GET /files/stats`: Get storage statistics

#### 5.2 Lifespan Integration
- File storage manager initialization during server startup
- Automatic backend detection and configuration
- Graceful error handling for missing optional dependencies

## Key Features and Benefits

### 1. **Persistent File Storage**
- Files survive beyond request/response cycles
- Proper file lifecycle management
- Multiple storage backend support

### 2. **Generated File Tracking**
- Distinguishes between user-uploaded and agent-generated files
- Automatic metadata tagging
- Session-based file organization

### 3. **Multi-Storage Architecture**
- Route different file types to appropriate storage systems
- Fallback mechanisms for reliability
- Easy addition of new storage backends

### 4. **Comprehensive Metadata**
- Track file ownership and associations
- Support for custom tags and metadata
- Full audit trail with timestamps

### 5. **Backward Compatibility**
- Existing `FileContentOutputPart` continues to work
- Seamless conversion between content and references
- No breaking changes to existing APIs

### 6. **Environment-Based Configuration**
- Simple environment variable configuration
- Optional backend dependencies
- Production and development configurations

## Configuration

### Environment Variables

```bash
# Local Storage (always enabled as fallback)
LOCAL_STORAGE_PATH=./file_storage

# AWS S3 Storage (optional)
AWS_S3_BUCKET=my-agent-files-bucket
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_FILE_PREFIX=agent-files/
S3_AS_DEFAULT=false

# MinIO Storage (optional)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=agent-files
MINIO_SECURE=false
MINIO_FILE_PREFIX=agent-files/
MINIO_AS_DEFAULT=false

# Routing Rules (optional)
IMAGE_STORAGE_BACKEND=s3
VIDEO_STORAGE_BACKEND=s3
PDF_STORAGE_BACKEND=local
TEXT_STORAGE_BACKEND=local

# Custom routing rules (optional)
FILE_ROUTING_RULES=image/:s3,video/:minio,application/pdf:local
```

### Optional Dependencies

```bash
# For AWS S3 support
pip install boto3

# For MinIO support  
pip install minio
```

## Usage Examples

### 1. Basic File Storage

```python
from agent_framework import FileStorageFactory

# Create storage manager
manager = await FileStorageFactory.create_storage_manager()

# Store a file
file_id = await manager.store_file(
    content=b"Hello, World!",
    filename="hello.txt",
    user_id="user-123",
    session_id="session-123",
    mime_type="text/plain"
)

# Retrieve the file
content, metadata = await manager.retrieve_file(file_id)
print(f"File: {metadata.filename}, Size: {metadata.size_bytes}")
```

### 2. Agent Output Processing

```python
from agent_framework import FileOutputProcessor

# Create processor
processor = FileOutputProcessor(file_manager)

# Process agent output with generated files
processed_output = await processor.process_agent_output(
    output=agent_output,
    user_id="user-123",
    session_id="session-123", 
    agent_id="agent-123"
)

# FileContentOutputPart is automatically converted to FileReferenceOutputPart
```

### 3. File Upload via API

```bash
curl -X POST "http://localhost:8000/files/upload" \
  -H "Authorization: Bearer your-token" \
  -F "file=@example.pdf" \
  -F "user_id=user-123" \
  -F "session_id=session-123"
```

### 4. File Download via API

```bash
curl -X GET "http://localhost:8000/files/{file_id}/download" \
  -H "Authorization: Bearer your-token" \
  -o downloaded_file.pdf
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Framework File Storage                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌──────────────────┐                   │
│  │   FastAPI       │    │  File Output     │                   │
│  │   Endpoints     │◄──►│  Processor       │                   │
│  └─────────────────┘    └──────────────────┘                   │
│           │                       │                            │
│           ▼                       ▼                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              File Storage Manager                       │   │
│  │                                                         │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │   Local     │  │     S3      │  │   MinIO     │     │   │
│  │  │  Storage    │  │  Storage    │  │  Storage    │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  │                                                         │   │
│  │  Routing Rules: MIME Type → Backend                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                     File Metadata                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ • File ID, Filename, MIME Type                          │   │
│  │ • User ID, Session ID, Agent ID                         │   │
│  │ • Created/Updated Timestamps                            │   │
│  │ • Generated vs Uploaded Flag                            │   │
│  │ • Custom Tags and Metadata                              │   │
│  │ • Storage Backend and Path                              │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Testing

The implementation includes comprehensive test coverage with 19 test cases covering:

- **Unit Tests:** Individual component testing
- **Integration Tests:** Cross-component functionality
- **File Operations:** Store, retrieve, delete, list operations
- **Metadata Management:** Create, read, update operations
- **Backend Registration:** Multi-backend setup and routing
- **Agent Integration:** File output processing and resolution
- **Error Handling:** Edge cases and failure scenarios

### Running Tests

```bash
# Run all file storage tests
uv run python -m pytest tests/test_file_storage.py -v

# Run specific test class
uv run python -m pytest tests/test_file_storage.py::TestLocalFileStorage -v
```

## Security Considerations

1. **Authentication:** All file endpoints require authentication
2. **User Isolation:** Files are isolated by user_id
3. **Access Control:** No cross-user file access
4. **Storage Security:** Backend-specific security (S3 IAM, etc.)
5. **Input Validation:** File size limits and MIME type validation

## Performance Considerations

1. **Async Operations:** All file operations are async
2. **Metadata Caching:** In-memory metadata caching for performance
3. **Streaming:** File downloads use streaming for large files
4. **Backend Selection:** Route large files to appropriate backends
5. **Error Recovery:** Graceful handling of backend failures

## Future Enhancements

1. **File Compression:** Optional compression for text files
2. **Versioning:** File version management
3. **Cleanup Jobs:** Automatic cleanup of old files
4. **Virus Scanning:** Integration with virus scanning services
5. **CDN Integration:** CloudFront or similar CDN support
6. **Encryption:** Client-side and server-side encryption options

## Migration Notes

This implementation is fully backward compatible. No changes are required for existing agents or API consumers. The system automatically converts between `FileContentOutputPart` and `FileReferenceOutputPart` as needed.

## Troubleshooting

### Common Issues

1. **Missing Dependencies:**
   ```
   ImportError: S3 storage requires boto3
   ```
   **Solution:** Install optional dependencies: `pip install boto3`

2. **Storage Initialization Failure:**
   ```
   RuntimeError: Failed to initialize local file storage
   ```
   **Solution:** Check file permissions and disk space

3. **File Not Found:**
   ```
   FileNotFoundError: File {file_id} not found
   ```
   **Solution:** Verify file ID and user permissions

### Debug Logging

Enable debug logging to see detailed file storage operations:

```python
import logging
logging.getLogger('agent_framework.file_storage').setLevel(logging.DEBUG)
```

## Conclusion

The file storage system provides a robust, scalable, and extensible solution for persistent file management in the Agent Framework. It maintains backward compatibility while adding powerful new capabilities for production deployments.

The implementation follows established patterns from the existing session storage system, ensuring consistency and maintainability across the framework. 