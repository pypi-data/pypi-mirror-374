# Enhanced Markdown Converter

## Overview

The Enhanced Markdown Converter is a comprehensive file conversion system built on top of Microsoft's `markitdown` library. It provides robust error handling, user-friendly feedback, and support for a wide range of file formats.

## Key Features

### 🔧 Enhanced Error Handling
- **Detailed Error Classification**: Specific error types with appropriate severity levels
- **User-Friendly Messages**: Clear explanations of what went wrong and how to fix it
- **Actionable Suggestions**: Specific recommendations for each error type
- **Technical Details**: Detailed information for debugging when needed

### 📄 Comprehensive Format Support
Based on markitdown v0.1.0+, supports 28+ file formats across multiple categories:

#### Documents
- **PDF** (`application/pdf`, `application/x-pdf`)
- **Microsoft Word** (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`)

#### Spreadsheets
- **Excel XLSX** (`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)
- **Excel XLS** (`application/vnd.ms-excel`)

#### Presentations
- **PowerPoint PPTX** (`application/vnd.openxmlformats-officedocument.presentationml.presentation`)

#### Images (with OCR and metadata extraction)
- **JPEG** (`image/jpeg`)
- **PNG** (`image/png`)

#### Audio/Video (with transcription)
- **WAV** (`audio/x-wav`)
- **MP3** (`audio/mpeg`)
- **MP4** (`video/mp4`) - audio extraction

#### Web and Markup
- **HTML** (`text/html`)
- **XHTML** (`application/xhtml+xml`)

#### Data Formats
- **JSON** (`application/json`)
- **CSV** (`text/csv`, `application/csv`)
- **XML** (`application/xml`, `text/xml`)

#### Text Formats (with prefix matching)
- **Plain Text** (`text/plain`)
- **Markdown** (`text/markdown`, `application/markdown`)
- **All text/* types** (JavaScript, CSS, Python, etc.)

#### E-books
- **EPUB** (`application/epub+zip`, `application/epub`, `application/x-epub+zip`)

#### Email
- **Outlook Messages** (`application/vnd.ms-outlook`)

#### Archives
- **ZIP** (`application/zip`) - iterates over contents

#### Code/Notebooks
- **Jupyter Notebooks** (`application/x-ipynb+json`)

### ⚠️ Partial Conversion Support
When full conversion fails, the system attempts to extract partial content:
- **Text files**: Direct text extraction with encoding handling
- **HTML files**: Basic tag removal and text extraction
- **Other formats**: File information and metadata

### 📊 Performance Tracking
- **Conversion timing**: Millisecond-precision timing
- **Content metrics**: Character counts, line counts, word estimates
- **Processing status**: Comprehensive status tracking

## Usage Examples

### Basic Conversion
```python
from agent_framework.markdown_converter import markdown_converter

# Convert a file
result = await markdown_converter.convert_to_markdown(
    content=file_bytes,
    filename="document.pdf",
    mime_type="application/pdf"
)

if result.success:
    print(f"✅ Converted successfully: {result.user_friendly_summary}")
    markdown_content = result.content
elif result.partial_content:
    print(f"⚠️ Partial conversion: {result.user_friendly_summary}")
    markdown_content = result.partial_content
else:
    print(f"❌ Conversion failed: {result.user_friendly_summary}")
    for issue in result.issues:
        print(f"  - {issue.user_message}")
        if issue.suggestions:
            print(f"    Suggestions: {', '.join(issue.suggestions)}")
```

### Legacy Compatibility
```python
# For backward compatibility
markdown_content = await markdown_converter.convert_to_markdown_legacy(
    content=file_bytes,
    filename="document.pdf", 
    mime_type="application/pdf"
)

# Or using the metadata method
result_dict = await markdown_converter.convert_file_with_metadata(
    content=file_bytes,
    filename="document.pdf",
    mime_type="application/pdf"
)
```

### Format Information
```python
# Check if a format is supported
is_supported = markdown_converter.is_supported_format("application/pdf")

# Get format information
format_info = markdown_converter.get_format_info("application/pdf")
print(f"Format: {format_info['name']} - {format_info['description']}")
print(f"Typical issues: {', '.join(format_info['typical_issues'])}")

# Get categorized format summary
categories = markdown_converter.get_supported_formats_summary()
for category, formats in categories.items():
    print(f"{category}: {len(formats)} formats")
```

## Error Types and Handling

### Error Classification
- **CRITICAL**: System-level issues (markitdown not available)
- **ERROR**: Conversion-blocking issues (unsupported format, file too large)
- **WARNING**: Quality issues (short content, encoding problems)
- **INFO**: Informational messages (format-specific notes)

### Common Error Types
1. **FORMAT_NOT_SUPPORTED**: File type not supported by markitdown
2. **FILE_TOO_LARGE**: File exceeds size limits
3. **MARKITDOWN_NOT_AVAILABLE**: Library not installed
4. **CONVERSION_FAILED**: General conversion error
5. **EMPTY_RESULT**: No content extracted
6. **FILE_CORRUPTED**: File appears damaged
7. **PERMISSION_ERROR**: System permission issues
8. **MEMORY_ERROR**: Insufficient memory
9. **TIMEOUT_ERROR**: Conversion took too long

### User-Friendly Suggestions
Each error type includes specific suggestions:
- Alternative file formats to try
- Steps to resolve the issue
- Workarounds when available
- Contact information for support

## Integration with File Storage

The enhanced converter integrates seamlessly with the file storage system:

### Automatic Conversion
```python
# Store file with automatic markdown conversion
original_file_id, markdown_file_id = await file_storage_manager.store_file_with_markdown_conversion(
    content=file_bytes,
    filename="document.pdf",
    user_id="user123",
    mime_type="application/pdf"
)
```

### Metadata Updates
The file storage system automatically updates metadata with:
- Conversion status (success/partial/failed)
- Processing time
- Error messages and warnings
- User-friendly feedback
- Suggestions for failed conversions

### Processing Summary
```python
# Get comprehensive processing information
summary = await file_storage_manager.get_file_processing_summary(file_id)
print(f"Conversion status: {summary['conversion_status']}")
print(f"Processing time: {summary['total_processing_time_ms']}ms")
if summary['processing_errors']:
    print(f"Errors: {', '.join(summary['processing_errors'])}")
if summary['processing_warnings']:
    print(f"Warnings: {', '.join(summary['processing_warnings'])}")
```

## Configuration

### Environment Variables
```bash
# Maximum file size for conversion (default: 50MB)
MAX_MARKDOWN_FILE_SIZE_MB=50

# Conversion timeout (default: 300 seconds)
MARKDOWN_CONVERSION_TIMEOUT_SECONDS=300

# Enable partial conversion attempts (default: true)
ENABLE_PARTIAL_CONVERSION=true
```

### Initialization Options
```python
converter = MarkdownConverter(
    max_file_size_mb=50,
    conversion_timeout_seconds=300,
    enable_partial_conversion=True
)
```

## Quality Analysis

The converter automatically analyzes conversion quality and provides warnings for:
- **Very short content**: Might indicate poor conversion or image-only documents
- **Encoding issues**: Unicode replacement characters detected
- **Repetitive content**: Highly repetitive text that might indicate conversion errors
- **Table detection**: Successfully converted tables with formatting notes

## Best Practices

### File Upload Handling
1. **Check format support** before attempting conversion
2. **Validate file size** against limits
3. **Handle partial conversions** gracefully
4. **Provide user feedback** with specific error messages
5. **Store original files** even if conversion fails

### Error Handling
1. **Display user-friendly messages** instead of technical errors
2. **Provide actionable suggestions** for each error type
3. **Log technical details** for debugging
4. **Offer alternatives** when conversion fails

### Performance Optimization
1. **Set appropriate timeouts** for large files
2. **Monitor conversion times** and adjust limits
3. **Use partial conversion** for better user experience
4. **Cache conversion results** when possible

## Troubleshooting

### Common Issues

#### "Markitdown not available"
- **Cause**: markitdown library not installed
- **Solution**: `pip install 'markitdown[all]'`
- **Alternative**: Install specific dependencies: `pip install 'markitdown[pdf,docx,pptx]'`

#### "Format not supported"
- **Cause**: File type not supported by markitdown
- **Solution**: Convert to supported format (PDF, DOCX, HTML, TXT)
- **Alternative**: Use the file in its original format

#### "File too large"
- **Cause**: File exceeds size limits
- **Solution**: Compress file or split into smaller parts
- **Alternative**: Increase `MAX_MARKDOWN_FILE_SIZE_MB` limit

#### "Conversion returned empty content"
- **Cause**: File might be image-only or corrupted
- **Solution**: Check file content, try OCR tools for images
- **Alternative**: Use partial conversion if available

### Debug Information
Enable debug logging to see detailed conversion information:
```python
import logging
logging.getLogger('agent_framework.markdown_converter').setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **OCR Integration**: Automatic text extraction from images
- **Language Detection**: Automatic language identification
- **Content Summarization**: AI-powered content summaries
- **Batch Processing**: Multiple file conversion
- **Custom Converters**: Plugin system for additional formats

### Extensibility
The converter is designed to be extensible:
- Add new MIME types to `SUPPORTED_MIME_TYPES`
- Implement custom error handlers
- Add format-specific quality analyzers
- Create custom partial conversion strategies

## Related Documentation
- [Enhanced File Management Guide](ENHANCED_FILE_MANAGEMENT_COMPLETE_GUIDE.md)
- [Agent Migration Guide](ENHANCED_AGENT_MIGRATION_GUIDE.md)
- [File Storage API Reference](../agent_framework/file_storages.py)
- [Markitdown Documentation](https://github.com/microsoft/markitdown)