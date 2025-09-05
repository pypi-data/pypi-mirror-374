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

"""Token management utilities for automatic token creation and refresh."""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any

import requests
from dotenv import load_dotenv

from helm.common.hierarchical_logger import hlog, hwarn

load_dotenv()

def _mask_api_key(api_key: str) -> str:
    """Mask the API keys"""
    return "[API_KEY_REDACTED]"

if os.getenv("OPENAI_TOKEN_URL") is None:
    os.environ["OPENAI_TOKEN_URL"] = "https://prod.api.nvidia.com/oauth/api/v1/ssa/default/token"
    hlog(f"OPENAI_TOKEN_URL is not set, setting to default: {os.environ['OPENAI_TOKEN_URL']}")

if os.getenv("OPENAI_SCOPE") is None:
    os.environ["OPENAI_SCOPE"] = "awsanthropic-readwrite"
    hlog(f"OPENAI_SCOPE is not set, setting to default: {os.environ['OPENAI_SCOPE']}")

if os.getenv("OPENAI_MODEL_URL") is None:
    os.environ["OPENAI_MODEL_URL"] = "https://prod.api.nvidia.com/llm/v1/azure/"
    hlog(f"OPENAI_MODEL_URL is not set, setting to default: {os.environ['OPENAI_MODEL_URL']}")

if os.getenv("GPT_JUDGE_API_KEY") is None or os.getenv("GPT_JUDGE_API_KEY") == "":
    os.environ["GPT_JUDGE_API_KEY"] = os.getenv("OPENAI_API_KEY")
    hlog(f"GPT_JUDGE_API_KEY is not set, setting to OPENAI_API_KEY: {_mask_api_key(os.environ['GPT_JUDGE_API_KEY'])}")

if os.getenv("LLAMA_JUDGE_API_KEY") is None or os.getenv("LLAMA_JUDGE_API_KEY") == "":
    os.environ["LLAMA_JUDGE_API_KEY"] = os.getenv("OPENAI_API_KEY")
    hlog(f"LLAMA_JUDGE_API_KEY is not set, setting to OPENAI_API_KEY: {_mask_api_key(os.environ['LLAMA_JUDGE_API_KEY'])}")

if os.getenv("CLAUDE_JUDGE_API_KEY") is None or os.getenv("CLAUDE_JUDGE_API_KEY") == "":
    os.environ["CLAUDE_JUDGE_API_KEY"] = os.getenv("OPENAI_API_KEY")
    hlog(f"CLAUDE_JUDGE_API_KEY is not set, setting to OPENAI_API_KEY: {_mask_api_key(os.environ['CLAUDE_JUDGE_API_KEY'])}")

class TokenManager:
    """Manages automatic token creation and refresh for different services."""
    
    def __init__(self):
        self.token_cache: Dict[str, Dict[str, Any]] = {}
        self.base_path = Path(__file__).parent.parent.parent
    
    def get_openai_token(self, force: bool = False) -> Optional[str]:
        """Get OpenAI OAuth token, creating it automatically if needed."""
        return self._get_oauth_token(
            service_name="openai",
            required_vars=["OPENAI_TOKEN_URL", "OPENAI_CLIENT_ID", "OPENAI_CLIENT_SECRET", "OPENAI_SCOPE"],
            scope="azureopenai-readwrite",  # Scope for GPT judges
            force=force
        )
    
    def get_claude_token(self, force: bool = False) -> Optional[str]:
        """Get Claude OAuth token, creating it automatically if needed."""
        return self._get_oauth_token(
            service_name="claude",
            required_vars=["OPENAI_TOKEN_URL", "OPENAI_CLIENT_ID", "OPENAI_CLIENT_SECRET", "OPENAI_SCOPE"],
            scope="awsanthropic-readwrite",  # Scope for Claude
            force=force
        )
    
    def get_token_with_scope(self, service_name: str, scope: str, force: bool = False) -> Optional[str]:
        """Get OAuth token with a specific scope."""
        return self._get_oauth_token(
            service_name=service_name,
            required_vars=["OPENAI_TOKEN_URL", "OPENAI_CLIENT_ID", "OPENAI_CLIENT_SECRET", "OPENAI_SCOPE"],
            scope=scope,
            force=force
        )
    
    def _get_oauth_token(
        self, 
        service_name: str, 
        required_vars: list, 
        scope: str, 
        force: bool = False
    ) -> Optional[str]:
        """Generic OAuth token getter with automatic creation and refresh."""
        
        # Check for required environment variables
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            hwarn(f"Missing environment variables for {service_name} token: {missing_vars}")
            return None
        
        token_url = os.environ.get("OPENAI_TOKEN_URL")
        client_id = os.environ.get("OPENAI_CLIENT_ID")
        client_secret = os.environ.get("OPENAI_CLIENT_SECRET")
        
        # Use provided scope or get from environment
        if scope:
            token_scope = scope
        else:
            token_scope = os.environ.get("OPENAI_SCOPE", "awsanthropic-readwrite")
        
        # Ensure we have all required values
        if not token_url or not client_id or not client_secret:
            hwarn(f"Missing required environment variables for {service_name} token")
            return None
        
        file_name = f"{service_name}_oauth_token.json"
        file_path = self.base_path / file_name
        
        try:
            # Check if the token is cached in memory
            if not force and service_name in self.token_cache:
                token = self.token_cache[service_name]
                if time.time() < token.get("expires_at", 0):
                    hlog(f"Using cached {service_name} token")
                    return token["access_token"]
            
            # Check if the token is cached on disk
            if not force and file_path.exists():
                with open(file_path, "r") as f:
                    token = json.load(f)
                    self.token_cache[service_name] = token
                    
                    # Check if the token is expired
                    if time.time() < token.get("expires_at", 0):
                        hlog(f"Using cached {service_name} token from disk")
                        return token["access_token"]
                    else:
                        hlog(f"{service_name} token expired, creating new one")
            
            # Create new token
            hlog(f"Creating new {service_name} OAuth token with scope: {token_scope}")
            response = requests.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": token_scope,
                },
                timeout=30
            )
            response.raise_for_status()
            token = response.json()
            token["expires_at"] = time.time() + token["expires_in"]
            
            # Cache the token
            self.token_cache[service_name] = token
            with open(file_path, "w") as f:
                json.dump(token, f)
            
            hlog(f"Successfully created new {service_name} token")
            return token["access_token"]
            
        except Exception as e:
            hwarn(f"Error creating {service_name} OAuth token: {e}")
            return None
    
    def refresh_token_if_needed(self, service_name: str) -> Optional[str]:
        """Refresh token if it's expired or about to expire."""
        if service_name == "openai":
            return self.get_openai_token(force=True)
        elif service_name == "claude":
            return self.get_claude_token(force=True)
        else:
            hwarn(f"Unknown service for token refresh: {service_name}")
            return None


# Global token manager instance
_token_manager = TokenManager()


def get_token_manager() -> TokenManager:
    """Get the global token manager instance."""
    return _token_manager


def create_token_on_error(error_message: str, service_name: str) -> Optional[str]:
    """Create a new token when an authentication error occurs."""
    error_lower = error_message.lower()
    
    # Check if this is an authentication/token error
    auth_keywords = [
        "authentication", "auth", "unauthorized", "invalid token", 
        "incorrect token", "token expired", "401", "403", "401 client error",
        "the token has expired", "unauthorized: the token has expired"
    ]
    
    is_auth_error = any(keyword in error_lower for keyword in auth_keywords)
    
    if is_auth_error:
        hlog(f"Authentication error detected for {service_name}, attempting to create new token")
        return _token_manager.refresh_token_if_needed(service_name)
    
    return None 