# Enhanced File Processing Guide

This guide covers the enhanced file processing capabilities implemented in the Agent Framework, including dual file storage, comprehensive metadata reporting, enhanced error handling, and multimodal image analysis.

## Overview

The enhanced file processing system provides:

- **Dual File Storage**: Stores both original files and markdown-converted versions
- **Comprehensive Metadata Reporting**: Detailed processing status and capability information
- **Enhanced Error Handling**: User-friendly error messages and graceful degradation
- **Multimodal Image Analysis**: AI-powered image analysis capabilities
- **ImageAnalysisTool Integration**: On-demand image analysis for agents

## Key Features

### 1. Enhanced `process_file_inputs` Function

The core file processing function has been enhanced with comprehensive capabilities:

```python
from agent_framework.file_system_management import process_file_inputs

# Enhanced file processing with comprehensive reporting
processed_input, uploaded_files = await process_file_inputs(
    agent_input=agent_input,
    file_storage_manager=file_storage_manager,
    user_id="user123",
    session_id="session456",
    store_files=True,
    include_text_content=True,
    convert_to_markdown=True,
    enable_multimodal_processing=True  # New: Enable image analysis
)
```

#### Enhanced File Metadata

Each processed file now includes comprehensive metadata:

```python
file_info = {
    # Basic file information
    'filename': 'document.pdf',
    'mime_type': 'application/pdf',
    'size_bytes': 1024000,
    
    # Storage information
    'file_id': 'uuid-original-file',
    'markdown_file_id': 'uuid-markdown-version',  # If conversion succeeded
    'storage_backend': 'local',
    
    # Processing status
    'conversion_status': 'success',  # success/failed/disabled/not_attempted
    'conversion_success': True,
    'conversion_reason': None,  # Error reason if failed
    
    # Multimodal information
    'has_visual_content': False,
    'multimodal_capabilities': [],
    'multimodal_info': {},
    
    # User feedback
    'user_message': 'Successfully processed document.pdf - stored original - converted to markdown',
    'capabilities_available': ['file_storage', 'markdown_content', 'text_analysis'],
    'limitations': [],
    
    # Processing metadata
    'processing_errors': [],
    'processing_warnings': [],
    'processing_time_ms': 150.5,
    'versions_available': {'original': True, 'markdown': True}
}
```

### 2. ImageAnalysisTool Integration

The `ImageAnalysisTool` provides on-demand image analysis capabilities:

```python
from agent_framework.multimodal_tools import ImageAnalysisTool

# Initialize image analysis tool
image_tool = ImageAnalysisTool(file_storage_manager)

# Analyze an image
result = await image_tool.analyze_image(file_id, "Describe this image in detail")
print(result.user_friendly_summary)

# Get image description
description = await image_tool.describe_image(file_id)

# Answer questions about image
answer = await image_tool.answer_about_image(file_id, "What colors are in this image?")

# Extract text from image (OCR)
text = await image_tool.extract_text_from_image(file_id)

# Check available capabilities
capabilities = await image_tool.get_image_capabilities(file_id)
```

### 3. Enhanced Agent Integration

Agents can now leverage enhanced file processing and image analysis:

```python
class EnhancedAgent(AgentInterface):
    def __init__(self):
        self.file_storage_manager = None
        self.image_analysis_tool = None
    
    async def initialize(self):
        self.file_storage_manager = await FileStorageFactory.create_storage_manager()
        self.image_analysis_tool = ImageAnalysisTool(self.file_storage_manager)
    
    async def handle_message(self, session_id: str, agent_input: StructuredAgentInput):
        # Process files with enhanced capabilities
        processed_input, uploaded_files = await self.process_file_inputs(
            agent_input,
            session_id=session_id,
            enable_multimodal_processing=True
        )
        
        # Handle image files
        for file_info in uploaded_files:
            if file_info.get('has_visual_content'):
                # Automatically describe uploaded images
                description = await self.image_analysis_tool.describe_image(
                    file_info['file_id']
                )
                print(f"Image description: {description}")
```

## Configuration

### Environment Variables

```bash
# Enable multimodal analysis
ENABLE_MULTIMODAL_ANALYSIS=true

# File storage configuration
LOCAL_STORAGE_PATH=./file_storage
AWS_S3_BUCKET=my-bucket
MINIO_ENDPOINT=localhost:9000

# Routing for AI-generated content
AI_IMAGE_STORAGE_BACKEND=s3
AI_TEXT_STORAGE_BACKEND=local
```

### Multimodal Capabilities Check

```python
from agent_framework.multimodal_tools import get_multimodal_capabilities_summary

capabilities = get_multimodal_capabilities_summary()
print(f"Multimodal enabled: {capabilities['multimodal_enabled']}")
print(f"Supported formats: {capabilities['supported_image_types']}")
print(f"Available capabilities: {capabilities['available_capabilities']}")
```

## Error Handling

The enhanced system provides comprehensive error handling:

### Graceful Degradation

- Files are stored even if markdown conversion fails
- Processing continues even if individual files fail
- Clear error messages explain what went wrong

### User-Friendly Feedback

```python
# Example error handling
for file_info in uploaded_files:
    if file_info.get('processing_errors'):
        print(f"Errors: {file_info['processing_errors']}")
        print(f"User message: {file_info['user_message']}")
        print(f"Limitations: {file_info['limitations']}")
```

### Error Types

- **Storage Errors**: File storage system unavailable
- **Conversion Errors**: Markdown conversion failed
- **Multimodal Errors**: Image analysis not available
- **Processing Errors**: General file processing failures

## Usage Examples

### Basic Enhanced File Processing

```python
import asyncio
from agent_framework.file_system_management import process_file_inputs, FileStorageFactory
from agent_framework.agent_interface import StructuredAgentInput, FileDataInputPart

async def process_files():
    # Initialize storage
    storage_manager = await FileStorageFactory.create_storage_manager()
    
    # Create agent input with files
    agent_input = StructuredAgentInput(
        query="Process these files",
        parts=[
            FileDataInputPart(
                filename="document.pdf",
                content_base64="base64_content_here",
                mime_type="application/pdf"
            )
        ]
    )
    
    # Process with enhanced capabilities
    processed_input, files = await process_file_inputs(
        agent_input,
        storage_manager,
        user_id="user123",
        session_id="session456",
        enable_multimodal_processing=True
    )
    
    # Check results
    for file_info in files:
        print(f"File: {file_info['filename']}")
        print(f"Status: {file_info['user_message']}")
        print(f"Capabilities: {file_info['capabilities_available']}")

asyncio.run(process_files())
```

### Image Analysis Example

```python
async def analyze_uploaded_image():
    storage_manager = await FileStorageFactory.create_storage_manager()
    image_tool = ImageAnalysisTool(storage_manager)
    
    # Assume we have an image file stored with ID 'image_file_id'
    file_id = "image_file_id"
    
    # Get comprehensive analysis
    result = await image_tool.analyze_image(
        file_id, 
        "Analyze this image and describe what you see in detail"
    )
    
    if result.success:
        print(f"Description: {result.description}")
        print(f"Objects detected: {result.objects_detected}")
        print(f"Text detected: {result.text_detected}")
        print(f"Confidence scores: {result.confidence_scores}")
    else:
        print(f"Analysis failed: {result.error_message}")
```

### Agent Integration Example

See `examples/llamaindex_agent_with_file_storage.py` for a complete example of an agent with enhanced file processing and image analysis capabilities.

## Best Practices

### 1. Always Enable Enhanced Processing

```python
# Always use enhanced capabilities for best results
processed_input, files = await process_file_inputs(
    agent_input,
    file_storage_manager,
    convert_to_markdown=True,
    enable_multimodal_processing=True
)
```

### 2. Check File Capabilities

```python
# Check what capabilities are available for each file
for file_info in uploaded_files:
    capabilities = file_info.get('capabilities_available', [])
    if 'multimodal_image_analysis' in capabilities:
        # File supports image analysis
        pass
    if 'markdown_content' in capabilities:
        # File has markdown content available
        pass
```

### 3. Handle Errors Gracefully

```python
# Always check for processing errors
for file_info in uploaded_files:
    if file_info.get('processing_errors'):
        # Handle errors appropriately
        print(f"Processing failed: {file_info['user_message']}")
        # Provide alternative actions
    else:
        # Process successfully
        print(f"Success: {file_info['user_message']}")
```

### 4. Use Comprehensive Reporting

```python
from agent_framework.file_system_management import get_file_processing_summary

# Generate user-friendly summary
summary = get_file_processing_summary(uploaded_files)
print(summary)  # Shows comprehensive processing results
```

## Troubleshooting

### Multimodal Analysis Not Working

1. Check environment variable: `ENABLE_MULTIMODAL_ANALYSIS=true`
2. Verify image file types are supported
3. Check for any import errors in logs

### File Storage Issues

1. Verify file storage backends are configured
2. Check file permissions and storage paths
3. Review storage backend logs

### Conversion Failures

1. Check file format support in markitdown
2. Review conversion error messages
3. Verify file content is not corrupted

## Migration Guide

### From Basic to Enhanced Processing

1. Update `process_file_inputs` calls to include new parameters
2. Handle enhanced metadata in file processing logic
3. Add image analysis capabilities to agents
4. Update error handling to use new error information

### Example Migration

```python
# Before (basic processing)
processed_input, files = await process_file_inputs(
    agent_input, file_storage_manager
)

# After (enhanced processing)
processed_input, files = await process_file_inputs(
    agent_input, 
    file_storage_manager,
    convert_to_markdown=True,
    enable_multimodal_processing=True
)

# Handle enhanced metadata
for file_info in files:
    print(f"Processing result: {file_info['user_message']}")
    if file_info.get('has_visual_content'):
        # Handle image files
        pass
```

## Requirements Covered

This implementation covers the following requirements:

- **5.1**: Enhanced agent integration with comprehensive file information
- **5.2**: Detailed metadata reporting including conversion status
- **5.3**: Enhanced error handling with user-friendly feedback  
- **5.4**: Multimodal capabilities integration
- **5.5**: Comprehensive file processing workflow
- **3.1**: Multimodal image analysis when enabled
- **3.2**: Agent multimodal capabilities
- **7.1**: Structured error handling and user feedback
- **7.2**: Enhanced error messages and recovery suggestions

## See Also

- [Multimodal Tools Documentation](./multimodal_tools_guide.md)
- [File Storage System Guide](./file_storage_system_implementation.md)
- [Agent Integration Examples](../examples/)