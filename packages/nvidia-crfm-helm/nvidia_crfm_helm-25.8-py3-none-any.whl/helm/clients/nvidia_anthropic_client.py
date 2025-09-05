# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Custom NVIDIA Anthropic client that includes NVIDIA-specific headers and fields.
"""

import os
import json
import requests
from typing import Any, Dict, List, Optional, cast
from helm.clients.anthropic_client import AnthropicMessagesClient
from helm.common.cache import CacheConfig
from helm.common.request import Request, RequestResult, wrap_request_time
from helm.tokenizers.tokenizer import Tokenizer
from anthropic import Anthropic
from anthropic.types import MessageParam
from helm.common.token_manager import create_token_on_error


class NvidiaAnthropicClient(AnthropicMessagesClient):
    """
    Custom NVIDIA Anthropic client that includes NVIDIA-specific headers and fields.
    This client adds the required 'dataClassification' header and 'anthropic_version' field
    that the NVIDIA endpoint expects.
    """

    def __init__(
        self,
        tokenizer: Tokenizer,
        tokenizer_name: str,
        cache_config: CacheConfig,
        thinking_budget_tokens: Optional[int] = None,
        anthropic_model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        stream: Optional[bool] = None,
        base_url: Optional[str] = None,
    ):
        # Don't call the parent constructor to avoid setting up the wrong client
        super().__init__(
            tokenizer=tokenizer,
            tokenizer_name=tokenizer_name,
            cache_config=cache_config,
            thinking_budget_tokens=thinking_budget_tokens,
            anthropic_model_name=anthropic_model_name,
            api_key=api_key,
            stream=stream,
            base_url=None,  # Don't pass base_url to parent
        )
        # Store the base_url for direct HTTP requests
        self.nvidia_base_url = base_url
        self.api_key = api_key

    def make_request(self, request: Request) -> RequestResult:
        """Override to add NVIDIA-specific headers and fields."""
        if request.max_tokens > self.MAX_OUTPUT_TOKENS:
            raise Exception(
                f"Request.max_tokens must be <= {self.MAX_OUTPUT_TOKENS}"
            )

        messages: List[MessageParam] = []
        system_message: Optional[MessageParam] = None

        if request.messages is not None:
            request.validate()
            messages = cast(List[MessageParam], request.messages)
            if messages[0]["role"] == "system":
                system_message = messages[0]
                messages = messages[1:]
        else:
            messages = [{"role": "user", "content": request.prompt}]

        # Create the raw request
        raw_request: Dict[str, Any] = {
            "messages": messages,
            "stop_sequences": request.stop_sequences,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "top_k": request.top_k_per_token,
        }
        
        if system_message is not None:
            raw_request["system"] = cast(str, system_message["content"])
        if self.thinking_budget_tokens:
            raw_request["thinking"] = {
                "type": "enabled",
                "budget_tokens": self.thinking_budget_tokens,
            }
            # Avoid error when thinking is enabled
            del raw_request["top_k"]

        # Add anthropic_version to the request payload
        raw_request["anthropic_version"] = "bedrock-2023-05-31"

        completions = []

        # `num_completions` is not supported, so instead make `num_completions` separate requests.
        for completion_index in range(request.num_completions):

            def do_it() -> Dict[str, Any]:
                try:
                    # Use the correct base URL
                    url = self.nvidia_base_url
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "dataClassification": "confidential"
                    }
                    
                    # Create payload with the correct format
                    payload = raw_request.copy()
                    
                    response = requests.post(url, headers=headers, json=payload)
                    
                    # Check for authentication error and try token refresh
                    if response.status_code == 401:
                        current_token = self.api_key
                        new_token = create_token_on_error(response.text, service_name="claude")
                        if new_token and new_token != current_token:
                            # Update the token and retry once
                            self.api_key = new_token
                            os.environ["ANTHROPIC_API_KEY"] = new_token
                            headers["Authorization"] = f"Bearer {new_token}"
                            response = requests.post(url, headers=headers, json=payload)
                    
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    # Handle the NVIDIA response format
                    if "content" in result and result["content"]:
                        # Check if content is a list with text blocks
                        if isinstance(result["content"], list) and len(result["content"]) > 0:
                            content_item = result["content"][0]
                            if isinstance(content_item, dict) and "text" in content_item:
                                # This is the expected format
                                return result
                    
                    # If we get here, the response format is unexpected
                    raise Exception(f"Unexpected response format: {result}")
                    
                except requests.exceptions.RequestException as e:
                    raise Exception(f"HTTP request failed: {str(e)}")
                except json.JSONDecodeError as e:
                    raise Exception(f"Invalid JSON response: {str(e)}")
                except Exception as e:
                    raise Exception(f"Request failed: {str(e)}")

            try:
                cache_key = self.make_cache_key(
                    {
                        "completion_index": completion_index,
                        **raw_request,
                    },
                    request,
                )
                raw_response, cached = self.cache.get(cache_key, wrap_request_time(do_it))

            except Exception as e:
                return RequestResult(
                    success=False,
                    cached=False,
                    error=str(e),
                    completions=[],
                    embedding=[],
                )

            # Process the response - handle the NVIDIA format
            response_text: Optional[str] = None
            response_thinking: Optional[str] = None
            
            # Extract text from the NVIDIA response format
            if "content" in raw_response and raw_response["content"]:
                for content_item in raw_response["content"]:
                    if isinstance(content_item, dict) and content_item.get("type") == "text":
                        response_text = content_item.get("text", "")
                        break
            
            if response_text is None:
                raise Exception("Anthropic response did not contain text block")
                
            from helm.common.request import GeneratedOutput, Token
            from helm.clients.client import truncate_and_tokenize_response_text
            
            completion = truncate_and_tokenize_response_text(
                response_text, request, self.tokenizer, self.tokenizer_name, original_finish_reason=""
            )
            
            if response_thinking is not None:
                from helm.common.request import Thinking
                import dataclasses
                completion = dataclasses.replace(completion, thinking=Thinking(text=response_thinking))
                
            completions.append(completion)

        return RequestResult(
            success=True,
            cached=cached,
            request_time=raw_response.get("request_time", 0),
            request_datetime=raw_response.get("request_datetime", ""),
            completions=completions,
            embedding=[],
        ) 