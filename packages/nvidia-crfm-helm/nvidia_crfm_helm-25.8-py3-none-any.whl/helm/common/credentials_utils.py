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
#
# Original Copyright 2025 Stanford Center for Research on Foundation Models.
# For the original license and copyright information, see the LICENSE file in this repository.

"""Functions used for credentials."""

import os
from typing import Any, Mapping, Optional

from helm.common.hierarchical_logger import hlog, hwarn


def provide_api_key(
    credentials: Mapping[str, Any], host_organization: str, model: Optional[str] = None
) -> Optional[str]:
    # First check for environment variables for specific judge API keys
    if model:
        # Check for judge-specific environment variables
        # Look for GPT models (nvidia/gpt4o or variants)
        if "gpt4o" in model.lower():
            env_key = os.getenv("GPT_JUDGE_API_KEY")
            if env_key:
                hlog(f"Using GPT judge API key from environment variable for model: {model} (ends with: ...{env_key[-5:]})")
                return env_key
        
        # Look for Llama models (nvdev/meta/llama or variants)
        if "llama" in model.lower():
            env_key = os.getenv("LLAMA_JUDGE_API_KEY")
            if env_key:
                hlog(f"Using Llama judge API key from environment variable for model: {model} (ends with: ...{env_key[-5:]})")
                return env_key
        
        # Look for Claude models (nvidia/claude or variants)
        if "claude" in model.lower():
            env_key = os.getenv("CLAUDE_JUDGE_API_KEY")
            if env_key:
                hlog(f"Using Claude judge API key from environment variable for model: {model} (ends with: ...{env_key[-5:]})")
                return env_key
    
    # Fall back to the original logic
    api_key_name = host_organization + "ApiKey"
    if api_key_name in credentials:
        api_key = credentials[api_key_name]
        hlog(f"Using host_organization api key defined in credentials.conf: {api_key_name} (ends with: ...{api_key[-5:]})")
        return api_key
    if "deployments" not in credentials:
        hwarn(
            "Could not find key 'deployments' in credentials.conf, "
            f"therefore the API key {api_key_name} should be specified."
        )
        return None
    deployment_api_keys = credentials["deployments"]
    if host_organization in deployment_api_keys:
        api_key = deployment_api_keys[host_organization]
        hlog(f"Using host_organization api key defined in deployments: {host_organization} (ends with: ...{api_key[-5:]})")
        return api_key
    return None
