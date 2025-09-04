"""
A LlamaIndex FunctionAgent integrated into the AgentFramework with File Storage capabilities.

This example demonstrates how to use the new file storage system with agents,
including storing files, retrieving files, and managing file metadata.
"""
from typing import Any, Dict, Optional, List, AsyncGenerator, Tuple
import asyncio
import json
import re
import logging
import os
import base64
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from agent_framework.agent_interface import (
    AgentInterface,
    StructuredAgentInput,
    StructuredAgentOutput,
    TextOutputPart,
    TextOutputStreamPart,
    OptionsBlockOutputPart,
    FormDefinitionOutputPart,
    FileContentOutputPart,
    FileReferenceOutputPart,
    FileDataInputPart,
    TextInputPart,
)
from agent_framework.model_config import model_config
from agent_framework import create_basic_agent_server
from agent_framework.file_system_management import FileStorageFactory, FileStorageManager
from agent_framework.multimodal_tools import ImageAnalysisTool, get_multimodal_capabilities_summary

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Keep file storage logs at INFO level for production
file_storage_logger = logging.getLogger('agent_framework.file_system_management')
file_storage_logger.setLevel(logging.INFO)

# --- LlamaIndex Imports ---
try:
    from llama_index.core.agent.workflow import FunctionAgent
    from llama_index.llms.openai import OpenAI
    from llama_index.core.llms.llm import BaseLLM
    from llama_index.core.workflow import Context
    from llama_index.core.agent.workflow import AgentStream, ToolCallResult, AgentOutput
except ImportError:
    raise ImportError(
        "LlamaIndex dependencies are not installed. Please run 'pip install llama-index' to install the required packages."
    )

def parse_special_blocks_from_text(text: str) -> tuple[str, list]:
    """
    Parse optionsblock and formDefinition code blocks from text and return cleaned text + parts.
    
    Args:
        text: The text content to parse
        
    Returns:
        tuple: (cleaned_text, list_of_parsed_parts)
    """
    if not text:
        return text, []
    
    special_parts = []
    cleaned_text = text
    
    # Pattern to match ```json blocks with formDefinition
    json_formdefinition_pattern = r'```json\s*\n(.*?)\n```'
    json_matches = re.findall(json_formdefinition_pattern, text, re.DOTALL)
    
    for match in json_matches:
        try:
            # Parse the JSON content
            json_data = json.loads(match.strip())
            
            # Check if it contains formDefinition
            if isinstance(json_data, dict) and "formDefinition" in json_data:
                # Create a FormDefinitionOutputPart
                form_part = FormDefinitionOutputPart(definition=json_data["formDefinition"])
                special_parts.append(form_part)
                
                logger.info(f"Successfully parsed formDefinition: {json_data['formDefinition']}")
            else:
                # This JSON block doesn't contain formDefinition, leave it in the text
                continue
                
        except json.JSONDecodeError as e:
            # Invalid JSON, leave it in the text
            continue
        
        
    # Pattern to match ```optionsblock...``` blocks
    optionsblock_pattern = r'```optionsblock\s*\n(.*?)\n```'
    optionsblock_matches = re.findall(optionsblock_pattern, text, re.DOTALL)
    
    for match in optionsblock_matches:
        try:
            # Parse the JSON content
            options_data = json.loads(match.strip())
            
            # Create an OptionsBlockOutputPart
            options_part = OptionsBlockOutputPart(definition=options_data)
            special_parts.append(options_part)
            
            logger.info(f"Successfully parsed optionsblock: {options_data}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse optionsblock JSON: {e}")
            logger.error(f"Invalid JSON content: {match}")
            continue
    
    # Remove all optionsblock code blocks from the text
    cleaned_text = re.sub(optionsblock_pattern, '', cleaned_text, flags=re.DOTALL)
    
    # Remove JSON blocks that contain formDefinition
    for match in json_matches:
        try:
            json_data = json.loads(match.strip())
            if isinstance(json_data, dict) and "formDefinition" in json_data:
                # Remove this specific JSON block
                block_pattern = r'```json\s*\n' + re.escape(match) + r'\n```'
                cleaned_text = re.sub(block_pattern, '', cleaned_text, flags=re.DOTALL)
        except json.JSONDecodeError:
            continue
    
    # Clean up any extra whitespace left behind
    cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text, special_parts


AGENT_PROMPT = '''
You are an assistant helping with a user's requests. You have enhanced capabilities for file management, storage, and image analysis.

You can generate markdown, mermaid diagrams, charts and code blocks, forms and optionsblocks.
You also have powerful file storage capabilities that allow you to:
- Create and store text files
- Read existing files
- List files for the current user/session  
- Delete files when needed
- Generate reports and save them as files
- Analyze images with AI-powered multimodal capabilities

ALWAYS include option blocks in your answer especially when asking the user to select an option or continue with the conversation!!! 
ALWAYS include options blocks (OK, No Thanks) when saying something like: Let me know if you want to ... 

When working with files, you can:
1. Create text files with any content (reports, summaries, code, etc.)
2. Read back files that were previously stored
3. List all files to see what's available
4. Clean up by deleting files that are no longer needed
5. Analyze uploaded images to describe content, answer questions, or extract text

**File Storage Tools Available:**
- create_file(filename, content): Creates and stores a text file
- read_file(file_id): Reads a stored file by its ID  
- list_files(): Lists all files for the current user/session
- delete_file(file_id): Deletes a file by its ID

**Image Analysis Tools Available (when multimodal analysis is enabled):**
- analyze_image(file_id, analysis_prompt): Analyze an image with optional custom prompt
- describe_image(file_id): Get a detailed description of an image
- answer_about_image(file_id, question): Answer specific questions about an image
- extract_text_from_image(file_id): Extract text from images using OCR
- get_image_capabilities(file_id): Check what analysis capabilities are available for an image
- get_multimodal_status(): Check if multimodal analysis is enabled and configured

When users upload images, you can:
1. Describe what you see in the image
2. Answer specific questions about the image content
3. Extract any text visible in the image
4. Identify objects, people, or scenes in the image
5. Provide detailed analysis based on custom prompts

Note: Image analysis capabilities depend on the ENABLE_MULTIMODAL_ANALYSIS environment variable being set to true.

**Crucial for Display: Formatting Charts and Tables**
To ensure charts are displayed correctly as interactive graphics, you MUST format your chart output using a fenced code block explicitly marked as `chart`. The content of this block must be a JSON object with **EXACTLY** the following top-level structure:
```json
{
  "type": "chartjs",
  "chartConfig": { /* Your actual Chart.js configuration object goes here */ }
}
```
Inside the `chartConfig` object, you will then specify the Chart.js `type` (e.g., `bar`, `line`), `data`, and `options`.

**CRITICAL: NO JAVASCRIPT FUNCTIONS ALLOWED**
The `chartConfig` must be PURE JSON - NO JavaScript functions, callbacks, or executable code are allowed.

If you need to present a form to the user to gather structured information,
you MUST format your entire response as a single JSON string. 
This JSON object should contain a top-level key `"formDefinition"`, and its value should be an object describing the form.

If you need to ask a single question with a small, fixed set of answers, you can present these as clickable options to the user.
Use the ```optionsblock``` for this. The user's selection (the 'value' of the chosen option) will be sent back as their next message.
Format this block as a JSON object with the following structure:
- `question` (string, optional): The question text displayed to the user above the options.
- `options` (array of objects): Each object represents a clickable option.
  - `text` (string): The text displayed on the button for the user.
  - `value` (string): The actual value that will be sent back to you if this option is chosen.
- `id` (string, optional): A unique identifier for this set of options.

ALWAYS generate the optionsblock as the last thing in your response!!!! YOU MUST DO THIS!!!
'''


class LlamaIndexAgentWithFileStorage(AgentInterface):
    """
    A LlamaIndex FunctionAgent integrated into the AgentFramework with File Storage capabilities.
    """
    
    def __init__(self):
        # Store configuration that can be overridden per session
        self._session_system_prompt = AGENT_PROMPT
        self._session_model_config = {}
        self._session_model_name = None
        self._state = None
        self._file_storage_manager: Optional[FileStorageManager] = None
        self._current_user_id = "default_user"  # This would normally come from authentication
        self._current_session_id = None
        self._image_analysis_tool: Optional[ImageAnalysisTool] = None
        self._ai_content_manager = None
        
        # Initialize file storage
        asyncio.create_task(self._initialize_file_storage())
        
        # Initialize LlamaIndex agent
        self._create_llamaindex_agent()

    async def _initialize_file_storage(self):
        """Initialize the file storage manager and related tools"""
        try:
            self._file_storage_manager = await FileStorageFactory.create_storage_manager()
            logger.info("File storage manager initialized successfully")
            
            # Initialize image analysis tool
            if self._file_storage_manager:
                self._image_analysis_tool = ImageAnalysisTool(self._file_storage_manager)
                logger.info("Image analysis tool initialized successfully")
                
                # Initialize AI content manager
                from agent_framework.ai_content_management import AIContentManager
                self._ai_content_manager = AIContentManager(self._file_storage_manager)
                logger.info("AI content manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize file storage: {e}")
            self._file_storage_manager = None
            self._image_analysis_tool = None
            self._ai_content_manager = None

    # ===== MATH TOOLS (Original) =====
    @staticmethod
    def add(a: float, b: float) -> float:
        """Add two numbers together."""
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        """Subtract one number from another."""
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers together."""
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        """Divide one number by another."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

    # ===== FILE HANDLING METHODS (Framework Integration) =====
    # This agent now uses the framework's built-in file processing capabilities
    # The process_file_inputs method is inherited from AgentInterface

    # ===== FILE STORAGE TOOLS (New) =====
    async def create_file(self, filename: str, content: str) -> str:
        """
        Create and store a text file with the given content.
        
        Args:
            filename: Name of the file to create
            content: Text content to store in the file
            
        Returns:
            String describing the result with file ID
        """
        try:
            if not self._file_storage_manager:
                return "Error: File storage system not available"
            
            # Convert string content to bytes
            content_bytes = content.encode('utf-8')
            
            # Store the file
            file_id = await self._file_storage_manager.store_file(
                content=content_bytes,
                filename=filename,
                user_id=self._current_user_id,
                session_id=self._current_session_id,
                mime_type="text/plain",
                is_generated=True,  # Mark as agent-generated
                tags=["agent-created", "text-file"]
            )
            
            logger.info(f"Created file {filename} with ID {file_id}")
            return f"Successfully created file '{filename}' with ID: {file_id}. The file contains {len(content)} characters."
            
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            return f"Error creating file: {str(e)}"

    async def read_file(self, file_id: str) -> str:
        """
        Read a stored file by its ID.
        
        Args:
            file_id: The ID of the file to read
            
        Returns:
            The file content as a string, or error message
        """
        try:
            if not self._file_storage_manager:
                return "Error: File storage system not available"
            
            # Retrieve the file
            content_bytes, metadata = await self._file_storage_manager.retrieve_file(file_id)
            
            # Convert bytes back to string
            content = content_bytes.decode('utf-8')
            
            logger.info(f"Read file {metadata.filename} (ID: {file_id})")
            return f"File '{metadata.filename}' content:\n\n{content}"
            
        except FileNotFoundError:
            return f"Error: File with ID {file_id} not found"
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return f"Error reading file: {str(e)}"

    async def list_files(self) -> str:
        """
        List all files for the current user/session.
        
        Returns:
            A formatted list of files with their metadata
        """
        try:
            if not self._file_storage_manager:
                return "Error: File storage system not available"
            
            # List files for current user and session
            files = await self._file_storage_manager.list_files(
                user_id=self._current_user_id,
                session_id=self._current_session_id
            )
            
            if not files:
                return "No files found for this session."
            
            # Format the file list
            file_list = []
            for file_meta in files:
                size_kb = file_meta.size_bytes / 1024
                created = file_meta.created_at.strftime("%Y-%m-%d %H:%M:%S")
                generated = "✓" if file_meta.is_generated else "✗"
                file_list.append(
                    f"• {file_meta.filename} (ID: {file_meta.file_id})\n"
                    f"  Size: {size_kb:.1f} KB | Created: {created} | Generated: {generated}"
                )
            
            return f"Found {len(files)} files:\n\n" + "\n\n".join(file_list)
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return f"Error listing files: {str(e)}"

    async def delete_file(self, file_id: str) -> str:
        """
        Delete a file by its ID.
        
        Args:
            file_id: The ID of the file to delete
            
        Returns:
            Success or error message
        """
        try:
            if not self._file_storage_manager:
                return "Error: File storage system not available"
            
            # Get metadata before deletion for confirmation
            metadata = await self._file_storage_manager.get_file_metadata(file_id)
            if not metadata:
                return f"Error: File with ID {file_id} not found"
            
            # Delete the file
            success = await self._file_storage_manager.delete_file(file_id)
            
            if success:
                logger.info(f"Deleted file {metadata.filename} (ID: {file_id})")
                return f"Successfully deleted file '{metadata.filename}' (ID: {file_id})"
            else:
                return f"Error: Failed to delete file {file_id}"
                
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return f"Error deleting file: {str(e)}"

    # ===== IMAGE ANALYSIS TOOLS (New) =====
    async def analyze_image(self, file_id: str, analysis_prompt: str = None) -> str:
        """
        Analyze an image using multimodal AI capabilities.
        
        Args:
            file_id: The ID of the image file to analyze
            analysis_prompt: Optional specific prompt for analysis
            
        Returns:
            String describing the analysis result
        """
        try:
            if not self._image_analysis_tool:
                return "Error: Image analysis tool not available. Make sure multimodal analysis is enabled."
            
            # Perform image analysis
            result = await self._image_analysis_tool.analyze_image(file_id, analysis_prompt)
            
            if result.success:
                return result.user_friendly_summary
            else:
                return f"Image analysis failed: {result.error_message}"
                
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return f"Error analyzing image: {str(e)}"

    async def describe_image(self, file_id: str) -> str:
        """
        Get a description of an image.
        
        Args:
            file_id: The ID of the image file to describe
            
        Returns:
            String description of the image
        """
        try:
            if not self._image_analysis_tool:
                return "Error: Image analysis tool not available. Make sure multimodal analysis is enabled."
            
            description = await self._image_analysis_tool.describe_image(file_id)
            return description
                
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return f"Error describing image: {str(e)}"

    async def answer_about_image(self, file_id: str, question: str) -> str:
        """
        Answer a specific question about an image.
        
        Args:
            file_id: The ID of the image file
            question: Question to answer about the image
            
        Returns:
            String answer to the question
        """
        try:
            if not self._image_analysis_tool:
                return "Error: Image analysis tool not available. Make sure multimodal analysis is enabled."
            
            answer = await self._image_analysis_tool.answer_about_image(file_id, question)
            return answer
                
        except Exception as e:
            logger.error(f"Error answering question about image: {e}")
            return f"Error answering question about image: {str(e)}"

    async def extract_text_from_image(self, file_id: str) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            file_id: The ID of the image file
            
        Returns:
            Extracted text content
        """
        try:
            if not self._image_analysis_tool:
                return "Error: Image analysis tool not available. Make sure multimodal analysis is enabled."
            
            text = await self._image_analysis_tool.extract_text_from_image(file_id)
            return text
                
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return f"Error extracting text from image: {str(e)}"

    async def get_image_capabilities(self, file_id: str) -> str:
        """
        Get available capabilities for an image file.
        
        Args:
            file_id: The ID of the image file
            
        Returns:
            String describing available capabilities
        """
        try:
            if not self._image_analysis_tool:
                return "Error: Image analysis tool not available. Make sure multimodal analysis is enabled."
            
            capabilities = await self._image_analysis_tool.get_image_capabilities(file_id)
            
            if capabilities:
                cap_names = [cap.value for cap in capabilities]
                return f"Available image analysis capabilities: {', '.join(cap_names)}"
            else:
                return "No image analysis capabilities available for this file."
                
        except Exception as e:
            logger.error(f"Error getting image capabilities: {e}")
            return f"Error getting image capabilities: {str(e)}"

    async def get_multimodal_status(self) -> str:
        """
        Get the current status of multimodal capabilities.
        
        Returns:
            String describing multimodal status and configuration
        """
        try:
            capabilities_summary = get_multimodal_capabilities_summary()
            
            status_parts = [
                f"Multimodal Analysis: {'✓ Enabled' if capabilities_summary['multimodal_enabled'] else '❌ Disabled'}",
                f"Supported Image Types: {len(capabilities_summary['supported_image_types'])} formats",
                f"Available Capabilities: {len(capabilities_summary['available_capabilities'])} features"
            ]
            
            if capabilities_summary['multimodal_enabled']:
                status_parts.append(f"Image Analysis Tool: {'✓ Available' if self._image_analysis_tool else '❌ Not initialized'}")
                status_parts.append(f"Capabilities: {', '.join(capabilities_summary['available_capabilities'])}")
            else:
                status_parts.append(f"To enable: Set {capabilities_summary['environment_variable']}=true")
            
            return "\n".join(status_parts)
                
        except Exception as e:
            logger.error(f"Error getting multimodal status: {e}")
            return f"Error getting multimodal status: {str(e)}"

    def _create_llamaindex_agent(self):
        """Create the LlamaIndex FunctionAgent with current configuration."""
        # Get all tools (math + file storage + image analysis)
        tools = [
            # Math tools
            self.add, 
            self.subtract, 
            self.multiply, 
            self.divide,
            # File storage tools
            self.create_file,
            self.read_file,
            self.list_files,
            self.delete_file,
            # Image analysis tools
            self.analyze_image,
            self.describe_image,
            self.answer_about_image,
            self.extract_text_from_image,
            self.get_image_capabilities,
            self.get_multimodal_status
        ]
        
        # Create LLM
        model_name = self._session_model_name or os.getenv("OPENAI_API_MODEL", "gpt-4o-mini")
        llm = OpenAI(model=model_name)
        
        # Create the agent
        self.llamaindex_agent = FunctionAgent(
            tools=tools,
            llm=llm,
            system_prompt=self._session_system_prompt,
            verbose=True
        )
        
        logger.info(f"LlamaIndex agent created with {len(tools)} tools (including file storage) and model {model_name}")

    async def configure_session(self, session_configuration: Dict[str, Any]) -> None:
        """
        Configure the agent with session-level settings.
        Called by AgentManager after agent creation but before state loading.
        """
        logger.info(f"LlamaIndexAgentWithFileStorage: Configuring session with: {session_configuration}")
        
        # Extract session-level configuration
        if "system_prompt" in session_configuration:
            self._session_system_prompt = session_configuration["system_prompt"]
            logger.info(f"LlamaIndexAgentWithFileStorage: Set system prompt to: {self._session_system_prompt[:100]}...")
        
        if "model_config" in session_configuration:
            self._session_model_config = session_configuration["model_config"]
            logger.info(f"LlamaIndexAgentWithFileStorage: Set model config to: {self._session_model_config}")
        
        if "model_name" in session_configuration:
            self._session_model_name = session_configuration["model_name"]
            logger.info(f"LlamaIndexAgentWithFileStorage: Set model name to: {self._session_model_name}")
        
        # Store session info for file operations
        if "session_id" in session_configuration:
            self._current_session_id = session_configuration["session_id"]
        
        if "user_id" in session_configuration:
            self._current_user_id = session_configuration["user_id"]
        
        # Ensure file storage and image analysis are initialized
        if not self._file_storage_manager:
            await self._initialize_file_storage()
        
        # Recreate the agent with new configuration
        self._create_llamaindex_agent()
        
        logger.info("LlamaIndexAgentWithFileStorage: Agent reconfigured with session settings")

    async def get_system_prompt(self) -> Optional[str]:
        """Return the current system prompt for this session."""
        return self._session_system_prompt

    async def get_current_model(self, session_id: str) -> Optional[str]:
        """Return the current model name for this session."""
        return self._session_model_name

    async def get_metadata(self) -> Dict[str, Any]:
        """Returns metadata about the agent."""
        tool_list = [
            # Math tools
            {
                "name": "add",
                "description": "Add two numbers together",
                "parameters": ["a: float", "b: float"],
                "type": "static",
                "category": "math"
            },
            {
                "name": "subtract", 
                "description": "Subtract one number from another",
                "parameters": ["a: float", "b: float"],
                "type": "static",
                "category": "math"
            },
            {
                "name": "multiply",
                "description": "Multiply two numbers together", 
                "parameters": ["a: float", "b: float"],
                "type": "static",
                "category": "math"
            },
            {
                "name": "divide",
                "description": "Divide one number by another",
                "parameters": ["a: float", "b: float"],
                "type": "static",
                "category": "math"
            },
            # File storage tools
            {
                "name": "create_file",
                "description": "Create and store a text file with given content",
                "parameters": ["filename: str", "content: str"],
                "type": "async",
                "category": "file_storage"
            },
            {
                "name": "read_file",
                "description": "Read a stored file by its ID",
                "parameters": ["file_id: str"],
                "type": "async",
                "category": "file_storage"
            },
            {
                "name": "list_files",
                "description": "List all files for the current user/session",
                "parameters": [],
                "type": "async",
                "category": "file_storage"
            },
            {
                "name": "delete_file",
                "description": "Delete a file by its ID",
                "parameters": ["file_id: str"],
                "type": "async",
                "category": "file_storage"
            },
            # Image analysis tools
            {
                "name": "analyze_image",
                "description": "Analyze an image using multimodal AI capabilities",
                "parameters": ["file_id: str", "analysis_prompt: str = None"],
                "type": "async",
                "category": "image_analysis"
            },
            {
                "name": "describe_image",
                "description": "Get a description of an image",
                "parameters": ["file_id: str"],
                "type": "async",
                "category": "image_analysis"
            },
            {
                "name": "answer_about_image",
                "description": "Answer a specific question about an image",
                "parameters": ["file_id: str", "question: str"],
                "type": "async",
                "category": "image_analysis"
            },
            {
                "name": "extract_text_from_image",
                "description": "Extract text from an image using OCR",
                "parameters": ["file_id: str"],
                "type": "async",
                "category": "image_analysis"
            },
            {
                "name": "get_image_capabilities",
                "description": "Get available capabilities for an image file",
                "parameters": ["file_id: str"],
                "type": "async",
                "category": "image_analysis"
            },
            {
                "name": "get_multimodal_status",
                "description": "Get the current status of multimodal capabilities",
                "parameters": [],
                "type": "async",
                "category": "image_analysis"
            }
        ]
        
        # Check multimodal capabilities
        multimodal_summary = get_multimodal_capabilities_summary()
        multimodal_enabled = multimodal_summary['multimodal_enabled']
        
        return {
            "name": "LlamaIndex Function Agent with Enhanced File Storage and Image Analysis",
            "description": "An agent that uses LlamaIndex FunctionAgent with mathematical tools, comprehensive file storage capabilities, and multimodal image analysis.",
            "welcome_message": f"Hello! I'm a LlamaIndex-powered agent that can help with mathematical calculations, file management, and {'image analysis' if multimodal_enabled else 'general assistance'}. I can create, read, list, and delete files for you{', and analyze images when multimodal analysis is enabled' if multimodal_enabled else ''}!",
            "capabilities": {
                "streaming": True,
                "tool_use": True,
                "reasoning": True,
                "multimodal": multimodal_enabled,
                "image_analysis": multimodal_enabled,
                "llamaindex_integration": True,
                "file_storage": True,
                "persistent_files": True,
                "dual_file_storage": True,
                "markdown_conversion": True
            },
            "defaultInputModes": ["text", "file"],
            "defaultOutputModes": ["text", "structured", "files"],
            "tools": tool_list,
            "tool_summary": {
                "total_tools": len(tool_list),
                "math_tools": 4,
                "file_storage_tools": 4,
                "image_analysis_tools": 6,
                "llamaindex_tools": len(tool_list)
            },
            "framework": "LlamaIndex",
            "agent_type": "FunctionAgent",
            "file_storage": {
                "enabled": True,
                "backends": ["local", "s3", "minio"],
                "supported_operations": ["create", "read", "list", "delete"],
                "file_types": ["text/plain", "application/json", "text/markdown", "image/*"],
                "dual_storage": True,
                "markdown_conversion": True
            },
            "multimodal": {
                "enabled": multimodal_enabled,
                "image_analysis": multimodal_enabled,
                "supported_formats": multimodal_summary['supported_image_types'] if multimodal_enabled else [],
                "capabilities": multimodal_summary['available_capabilities'] if multimodal_enabled else [],
                "environment_variable": multimodal_summary['environment_variable'],
                "current_setting": multimodal_summary['current_setting']
            }
        }

    async def handle_message(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> StructuredAgentOutput:
        """
        Handles a user message in non-streaming mode.
        """
        logger.info(f"Handling message for session {session_id}")
        
        # Log agent input with truncated query to avoid binary content in logs
        query_preview = agent_input.query[:100] + "..." if agent_input.query and len(agent_input.query) > 100 else agent_input.query
        logger.info(f"Original agent_input: query='{query_preview}', parts={len(agent_input.parts)}")
        
        # Log input parts summary (clean)
        file_parts = [p for p in agent_input.parts if hasattr(p, 'type') and p.type == 'file_data']
        text_parts = [p for p in agent_input.parts if hasattr(p, 'type') and p.type == 'text']
        logger.info(f"  Input: {len(text_parts)} text parts, {len(file_parts)} file parts")
        for file_part in file_parts:
            logger.info(f"    📁 File: {file_part.filename} ({file_part.mime_type})")
        
        # Update session info for file operations
        self._current_session_id = session_id
        
        # Ensure file storage is initialized before processing files
        if not self._file_storage_manager:
            logger.warning("File storage manager not initialized, initializing now...")
            await self._initialize_file_storage()
        
        # Process any uploaded files using the enhanced framework method
        processed_input, uploaded_files = await self.process_file_inputs(
            agent_input, 
            session_id=session_id,
            user_id=self._current_user_id,
            convert_to_markdown=True,  # Enable markdown conversion
            enable_multimodal_processing=True  # Enable multimodal processing
        )
        logger.info(f"Processed {len(uploaded_files)} uploaded files with enhanced capabilities")
        
        # Enrich context with markdown content for uploaded files
        enriched_context = self._build_enriched_context(agent_input, uploaded_files)
        logger.info(f"Enriched context: {enriched_context}")
        
        # Log enhanced file processing results
        if uploaded_files:
            for file_info in uploaded_files:
                if file_info.get('file_id'):
                    status_parts = [f"Stored: {file_info['filename']} ({file_info['size_bytes']} bytes) → {file_info['file_id']}"]
                    if file_info.get('markdown_file_id'):
                        status_parts.append(f"Markdown: {file_info['markdown_file_id']}")
                    if file_info.get('has_visual_content'):
                        cap_count = len(file_info.get('multimodal_capabilities', []))
                        status_parts.append(f"Visual ({cap_count} capabilities)")
                    logger.info(f"  ✅ {' | '.join(status_parts)}")
                else:
                    logger.error(f"  ❌ Failed to store: {file_info['filename']} - {file_info.get('user_message', 'Unknown error')}")
        else:
            logger.info("  ℹ️  No files processed")
        
        if not processed_input.query:
            return StructuredAgentOutput(
                response_text="Input query cannot be empty.", parts=[]
            )

        try:
            # Run the LlamaIndex agent
            from llama_index.core.workflow import JsonSerializer
            
            if(self._state is not None):
                ctx = self._state
                logger.info("STATE USED IN HANDLE_MESSAGE: FROM LOCAL VARIABLE")
            else:
                ctx = Context(self.llamaindex_agent)
                logger.info("STATE USED IN HANDLE_MESSAGE: FROM INITIALIZED")
            
            response = await self.llamaindex_agent.run(user_msg=enriched_context, ctx=ctx)
            response_text = str(response)
            
            # Save context as state for next interaction
            self._state = ctx

            # Parse special blocks (optionsblocks and formDefinition) from the response
            cleaned_text, special_parts = parse_special_blocks_from_text(response_text)
            
            # Build the parts list
            parts = [TextOutputPart(text=cleaned_text)]
            parts.extend(special_parts)

            # Create initial output
            output = StructuredAgentOutput(
                response_text=cleaned_text,
                parts=parts,
            )
            
            # Process AI-generated content if AI content manager is available
            if self._ai_content_manager:
                try:
                    # Process and store AI-generated content
                    enhanced_output = await self._ai_content_manager.process_agent_response(
                        output, 
                        session_id=session_id,
                        user_id=self._current_user_id
                    )
                    logger.info("✅ AI-generated content processed and stored")
                    output = enhanced_output
                except Exception as e:
                    logger.warning(f"⚠️ AI content management failed: {e}")
                    # Continue with original output if AI content management fails
            
            return output
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error_message = f"Sorry, I encountered an error: {str(e)}"
            return StructuredAgentOutput(
                response_text=error_message,
                parts=[TextOutputPart(text=error_message)],
            )

    async def handle_message_stream(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> AsyncGenerator[StructuredAgentOutput, None]:
        """
        Handles a user message by yielding responses as they are generated.
        Uses LlamaIndex's streaming capability.
        """
        logger.info(f"Handling streaming message for session {session_id}")
        
        # Update session info for file operations
        self._current_session_id = session_id
        
        # Ensure file storage is initialized before processing files
        if not self._file_storage_manager:
            logger.warning("File storage manager not initialized, initializing now...")
            await self._initialize_file_storage()
        
        # Process any uploaded files using the enhanced framework method
        processed_input, uploaded_files = await self.process_file_inputs(
            agent_input, 
            session_id=session_id,
            user_id=self._current_user_id,
            convert_to_markdown=True,  # Enable markdown conversion
            enable_multimodal_processing=True  # Enable multimodal processing
        )
        
        # Enrich context with markdown content for uploaded files
        enriched_context = self._build_enriched_context(agent_input, uploaded_files)
        
        if not processed_input.query:
            yield StructuredAgentOutput(
                response_text="Input query cannot be empty.", parts=[]
            )
            return

        try:
            from llama_index.core.workflow import JsonSerializer
            
            if(self._state is not None):
                ctx = self._state
                logger.info("STATE USED IN HANDLE_MESSAGE_STREAM: FROM LOCAL VARIABLE")
            else:
                ctx = Context(self.llamaindex_agent)
                logger.info("STATE USED IN HANDLE_MESSAGE_STREAM: FROM INITIALIZED")
            
            # Run the LlamaIndex agent with streaming
            handler = self.llamaindex_agent.run(user_msg=enriched_context, ctx=ctx)
            
            accumulated_text = ""
            
            # Stream events from LlamaIndex
            async for event in handler.stream_events():
                if isinstance(event, AgentStream):
                    # Stream text tokens
                    chunk_text = event.delta
                    if chunk_text:
                        accumulated_text += chunk_text
                        yield StructuredAgentOutput(
                            response_text="",
                            parts=[TextOutputStreamPart(text=f"__STREAM_CHUNK__{chunk_text}")]
                        )
                        
                elif isinstance(event, ToolCallResult):
                    # Tool execution results (including file operations)
                    activity_data = {
                        "type": "tool_result",
                        "source": "llamaindex_agent_with_file_storage",
                        "tool_name": event.tool_name,
                        "tool_kwargs": event.tool_kwargs,
                        "tool_output": str(event.tool_output),
                        "timestamp": str(datetime.now())
                    }
                    
                    # Add special handling for file operations
                    if event.tool_name in ["create_file", "read_file", "list_files", "delete_file"]:
                        activity_data["category"] = "file_storage"
                    elif event.tool_name in ["add", "subtract", "multiply", "divide"]:
                        activity_data["category"] = "math"
                    
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(activity_data)}")]
                    )
            
            # Get the final response
            response = await handler
            final_response_text = str(response)
            self._state = ctx
            
            # Parse special blocks from the final response
            cleaned_text, special_parts = parse_special_blocks_from_text(final_response_text)
            
            # Build the parts list
            parts = [TextOutputPart(text=cleaned_text)]
            parts.extend(special_parts)
            
            # Create initial output
            output = StructuredAgentOutput(
                response_text=cleaned_text,
                parts=parts
            )
            
            # Process AI-generated content if AI content manager is available
            if self._ai_content_manager:
                try:
                    # Process and store AI-generated content
                    enhanced_output = await self._ai_content_manager.process_agent_response(
                        output, 
                        session_id=session_id,
                        user_id=self._current_user_id
                    )
                    logger.info("✅ AI-generated content processed and stored (streaming)")
                    output = enhanced_output
                except Exception as e:
                    logger.warning(f"⚠️ AI content management failed (streaming): {e}")
                    # Continue with original output if AI content management fails
            
            # Send final answer
            yield output
                    
        except Exception as e:
            logger.error(f"Error processing streaming message: {e}")
            error_message = f"Sorry, I encountered an error: {str(e)}"
            yield StructuredAgentOutput(
                response_text=error_message,
                parts=[TextOutputPart(text=error_message)],
            )

    async def get_state(self) -> Dict[str, Any]:
        """Retrieves the serializable state of the agent."""
        from llama_index.core.workflow import JsonSerializer
        state_dict = None
        if self._state is not None:
            state_dict = self._state.to_dict(serializer=JsonSerializer())
            logger.info("STATE RETRIEVAL: FROM self._state")
            self._state = None
        else:
            state_dict = Context(self.llamaindex_agent).to_dict(serializer=JsonSerializer())
            logger.info("STATE RETRIEVAL: INITIALIZED CONTEXT")
        return state_dict

    async def load_state(self, state: Dict[str, Any]):
        """Loads the state into the agent."""
        from llama_index.core.workflow import JsonSerializer
        if state:
            try:
                self._state = Context.from_dict(self.llamaindex_agent, state, serializer=JsonSerializer())
                logger.info("STATE LOADING: FROM PERSISTENCE LAYER")
            except Exception as e:
                logger.error(f"STATE LOADING: ERROR: {e}. Starting fresh.")
                ctx = Context(self.llamaindex_agent)
                self._state = ctx.to_dict(serializer=JsonSerializer())

    def _build_enriched_context(self, agent_input: StructuredAgentInput, uploaded_files: List[Dict[str, Any]]) -> str:
        """
        Build enriched context for the LLM with markdown content from uploaded files
        
        Args:
            agent_input: Original agent input
            uploaded_files: List of processed file metadata
            
        Returns:
            Enriched context string for the LLM
        """
        context_parts = []
        
        # Add original user query
        if agent_input.query:
            context_parts.append(f"**User Query:** {agent_input.query}")
        
        # Add information about uploaded files
        if uploaded_files:
            context_parts.append("\n**📁 Uploaded Files:**")
            
            for file_info in uploaded_files:
                filename = file_info.get('filename', 'Unknown')
                file_id = file_info.get('file_id', 'No ID')
                mime_type = file_info.get('mime_type', 'Unknown type')
                size_bytes = file_info.get('size_bytes', 0)
                
                context_parts.append(f"\n**File:** {filename}")
                context_parts.append(f"**Storage ID:** {file_id}")
                context_parts.append(f"**Type:** {mime_type} ({size_bytes:,} bytes)")
                context_parts.append(f"**Status:** Available in file storage")
                
                # Add processing status and capabilities
                processing_status = []
                
                # Markdown conversion status
                markdown_content = file_info.get('markdown_content')
                conversion_success = file_info.get('conversion_success', False)
                markdown_file_id = file_info.get('markdown_file_id')
                
                if markdown_content and conversion_success:
                    processing_status.append("✓ Markdown converted")
                    if markdown_file_id:
                        processing_status.append(f"(Markdown ID: {markdown_file_id})")
                elif not conversion_success:
                    reason = file_info.get('conversion_reason', 'Unknown error')
                    processing_status.append(f"❌ Markdown conversion failed: {reason}")
                else:
                    processing_status.append("ℹ️ Markdown conversion not attempted")
                
                # Image analysis capabilities
                has_visual_content = file_info.get('has_visual_content', False)
                multimodal_capabilities = file_info.get('multimodal_capabilities', [])
                
                if has_visual_content:
                    if multimodal_capabilities:
                        cap_names = [cap.replace('_', ' ').title() for cap in multimodal_capabilities]
                        processing_status.append(f"🖼️ Image analysis available: {', '.join(cap_names)}")
                        processing_status.append(f"Use analyze_image('{file_id}') to analyze this image")
                    else:
                        processing_status.append("🖼️ Image detected (analysis not available)")
                
                # Available capabilities
                capabilities = file_info.get('capabilities_available', [])
                if capabilities:
                    cap_display = [cap.replace('_', ' ').title() for cap in capabilities]
                    processing_status.append(f"🔧 Capabilities: {', '.join(cap_display)}")
                
                # User message
                user_message = file_info.get('user_message', '')
                if user_message:
                    processing_status.append(f"📋 Status: {user_message}")
                
                if processing_status:
                    context_parts.append(f"**Processing Status:** {' | '.join(processing_status)}")
                
                # Add markdown content if available
                if markdown_content and conversion_success:
                    context_parts.append(f"\n**📝 Markdown Content:**")
                    context_parts.append("```markdown")
                    context_parts.append(markdown_content)
                    context_parts.append("```")
        
        # Add enhanced instructions for the LLM
        if uploaded_files:
            context_parts.append("\n**💡 Instructions:**")
            context_parts.append("- You can reference the uploaded files by their names and IDs")
            context_parts.append("- Use the markdown content to understand text-based file contents")
            context_parts.append("- For images with visual content, use image analysis tools:")
            context_parts.append("  • describe_image(file_id) - Get image description")
            context_parts.append("  • answer_about_image(file_id, question) - Ask specific questions")
            context_parts.append("  • extract_text_from_image(file_id) - Extract text via OCR")
            context_parts.append("  • analyze_image(file_id, prompt) - Custom analysis")
            context_parts.append("- Provide comprehensive analysis based on all available content")
            context_parts.append("- If processing failed, explain limitations and suggest alternatives")
            
            # Add specific guidance for image files
            image_files = [f for f in uploaded_files if f.get('has_visual_content')]
            if image_files:
                context_parts.append("\n**🖼️ Image Analysis Available:**")
                for img_file in image_files:
                    file_id = img_file.get('file_id', 'unknown')
                    filename = img_file.get('filename', 'unknown')
                    capabilities = img_file.get('multimodal_capabilities', [])
                    if capabilities:
                        context_parts.append(f"- {filename} (ID: {file_id}) - Ready for analysis")
                    else:
                        context_parts.append(f"- {filename} (ID: {file_id}) - Image detected but analysis not available")
        
        return "\n".join(context_parts)


def main():
    """Main function to start the LlamaIndex agent with file storage server."""
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Error: No OPENAI_API_KEY found!")
        logger.error("Please set OPENAI_API_KEY environment variable")
        return
    
    # Get port from environment variable or use 8001 as default (different from original)
    try:
        port = int(os.getenv("AGENT_PORT", "8001"))
    except ValueError:
        logger.warning("Invalid AGENT_PORT specified. Defaulting to 8001.")
        port = 8001

    logger.info("Starting LlamaIndex Agent with File Storage Server...")
    logger.info(f"Model: {os.getenv('OPENAI_API_MODEL', 'gpt-4o-mini')}")
    logger.info(f"File Storage: Enabled with Local, S3, and MinIO backend support")
    logger.info(f"Access at: http://localhost:{port}/testapp")
    logger.info(f"Access modern UI at: http://localhost:{port}/ui")
    
    create_basic_agent_server(
        agent_class=LlamaIndexAgentWithFileStorage,
        host="0.0.0.0", 
        port=port,
        reload=False
    )


if __name__ == "__main__":
    main() 