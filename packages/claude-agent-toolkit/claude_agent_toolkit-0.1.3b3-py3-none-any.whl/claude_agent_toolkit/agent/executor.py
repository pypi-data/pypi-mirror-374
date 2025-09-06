#!/usr/bin/env python3
# executor.py - Container execution and result parsing

import json
import sys
import uuid
from typing import Any, Dict, Optional

import docker

from ..logging import get_logger
from ..exceptions import ConfigurationError, ConnectionError, ExecutionError
from ..constants import DOCKER_HOST_GATEWAY, CONTAINER_NAME_PREFIX, CONTAINER_UUID_LENGTH
from .response_handler import ResponseHandler

logger = get_logger('agent')


class ContainerExecutor:
    """Handles Docker container execution and result parsing."""
    
    def __init__(self, docker_client: docker.DockerClient, image_name: str):
        """
        Initialize container executor.
        
        Args:
            docker_client: Docker client instance
            image_name: Docker image to use for execution
        """
        self.docker_client = docker_client
        self.image_name = image_name
    
    def execute(self, prompt: str, oauth_token: str, tool_urls: Dict[str, str], system_prompt: Optional[str] = None, verbose: bool = False, model: Optional[str] = None) -> str:
        """
        Execute prompt in Docker container with connected tools.
        
        Args:
            prompt: The instruction for Claude
            oauth_token: Claude Code OAuth token
            tool_urls: Dictionary of tool_name -> url mappings
            system_prompt: Optional system prompt to customize agent behavior
            verbose: If True, enable verbose output in container
            model: Optional model to use for this execution
            
        Returns:
            Response string from Claude
            
        Raises:
            ConfigurationError: If OAuth token or configuration is invalid
            ConnectionError: If Docker connection fails
            ExecutionError: If container execution fails
        """
        from ..constants import MODEL_ID_MAPPING
        
        logger.info("Running with prompt: %s...", prompt[:100])
        
        # Prepare environment variables
        environment = {
            'CLAUDE_CODE_OAUTH_TOKEN': oauth_token,
            'AGENT_PROMPT': prompt,
            'AGENT_VERBOSE': '1' if verbose else '0'
        }
        
        # Add system prompt if provided
        if system_prompt:
            environment['AGENT_SYSTEM_PROMPT'] = system_prompt
        
        # Add model if provided - apply model ID mapping if needed
        if model:
            # Apply model ID mapping if model is a known alias
            mapped_model = MODEL_ID_MAPPING.get(model, model)
            environment['ANTHROPIC_MODEL'] = mapped_model
        
        # Add all connected tools as separate environment variables
        if tool_urls:
            # Pass tools as JSON for easier parsing in entrypoint
            environment['MCP_TOOLS'] = json.dumps(tool_urls)
            logger.info("Connected tools: %s", list(tool_urls.keys()))
        
        if not oauth_token:
            raise ConfigurationError("OAuth token is required")
        
        try:
            # Run container with streaming
            container_name = f"{CONTAINER_NAME_PREFIX}{uuid.uuid4().hex[:CONTAINER_UUID_LENGTH]}"
            
            logger.debug("Starting container %s", container_name)
            
            container = self.docker_client.containers.run(
                image=self.image_name,
                name=container_name,
                command="python /app/entrypoint.py",
                environment=environment,
                extra_hosts={'host.docker.internal': DOCKER_HOST_GATEWAY},
                stdout=True,
                stderr=True,
                stream=True,
                detach=False,
                remove=True
            )
            
            handler = ResponseHandler()
            
            # Process stream
            for chunk in container:
                if chunk:
                    chunk_text = chunk.decode('utf-8')
                    for line in chunk_text.splitlines():
                        result = handler.handle(line, verbose)
                        if result:
                            logger.info("Execution completed successfully")
                            return result  # Return string directly
                        
            # If we get here, no ResultMessage was received
            if handler.text_responses:
                logger.info("Execution completed with text responses")
                return '\n'.join(handler.text_responses)
            else:
                raise ExecutionError("No response received from Claude")
                
        except docker.errors.ContainerError as e:
            stderr = e.stderr.decode('utf-8') if e.stderr else str(e)
            logger.error("Container failed: %s", stderr)
            raise ExecutionError(f"Container failed: {stderr}") from e
            
        except docker.errors.DockerException as e:
            logger.error("Docker connection failed: %s", e)
            raise ConnectionError(f"Docker connection failed: {e}") from e
            
        except Exception as e:
            if isinstance(e, (ConfigurationError, ConnectionError, ExecutionError)):
                raise  # Re-raise our exceptions
            logger.error("Unexpected error: %s", e)
            raise ExecutionError(f"Unexpected error: {e}") from e
