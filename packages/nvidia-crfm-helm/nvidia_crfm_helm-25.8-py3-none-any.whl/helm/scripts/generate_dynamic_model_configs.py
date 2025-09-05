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

#!/usr/bin/env python3
"""
Script to generate model configuration files for HELM.
Generates model_deployments.yaml and model_metadata.yaml based on CLI parameters.
"""

import argparse
import yaml
import os
from datetime import datetime, date
from pathlib import Path


def generate_model_metadata(model_name: str) -> dict:
    """Generate model metadata configuration."""
    models = [
        {
            "name": model_name,
            "display_name": f"{model_name.split('/')[-1]} (Generated)",
            "description": f"Auto-generated model configuration for {model_name}. This is a placeholder description.",
            "creator_organization_name": "Generated",
            "access": "open",
            "num_parameters": 1000000000,
            "release_date": date.today(),
            "tags": ["TEXT_MODEL_TAG", "PARTIAL_FUNCTIONALITY_TEXT_MODEL_TAG"],
        },
        # Judge models for annotation (with unique names to avoid conflicts)
        {
            "name": "nvidia/gpt4o-judge",
            "display_name": "GPT-4o (NVIDIA Judge)",
            "description": "GPT-4o model hosted on NVIDIA's platform for annotation",
            "creator_organization_name": "NVIDIA",
            "access": "open",
            "num_parameters": 1000000000,
            "release_date": date.today(),
            "tags": ["TEXT_MODEL_TAG", "PARTIAL_FUNCTIONALITY_TEXT_MODEL_TAG"],
        },
        {
            "name": "nvdev/meta/llama-3.3-70b-instruct-judge",
            "display_name": "Llama-3.3-70B-Instruct (NVIDIA Judge)",
            "description": "Llama-3.3-70B-Instruct model hosted on NVIDIA's platform for annotation",
            "creator_organization_name": "NVIDIA",
            "access": "open",
            "num_parameters": 1000000000,
            "release_date": date.today(),
            "tags": ["TEXT_MODEL_TAG", "PARTIAL_FUNCTIONALITY_TEXT_MODEL_TAG"],
        },
        {
            "name": "nvidia/claude-3-7-sonnet-20250219-judge",
            "display_name": "Claude-3-7-Sonnet (NVIDIA Judge)",
            "description": "Claude-3-7-Sonnet model hosted on NVIDIA's platform for annotation",
            "creator_organization_name": "NVIDIA",
            "access": "open",
            "num_parameters": 1000000000,
            "release_date": date.today(),
            "tags": ["TEXT_MODEL_TAG", "PARTIAL_FUNCTIONALITY_TEXT_MODEL_TAG"],
        },
    ]
    return {"models": models}


def generate_model_deployments(model_name: str, base_url: str, openai_model_name: str) -> dict:
    """Generate model deployments configuration."""
    model_deployments = {
        "model_deployments": [
            {
                "name": model_name,
                "model_name": model_name,
                "tokenizer_name": "simple/tokenizer1",
                "max_sequence_length": 128000,
                "max_request_length": 128001,
                "client_spec": {
                    "class_name": "helm.clients.openai_client.OpenAIClient",
                    "args": {
                        "base_url": base_url,
                        "openai_model_name": openai_model_name,
                    },
                },
            },
            # Judge models for annotation (with unique names to avoid conflicts)
            {
                "name": "nvidia/gpt4o-judge",
                "model_name": "nvidia/gpt4o-judge",
                "tokenizer_name": "openai/cl100k_base",
                "max_sequence_length": 128000,
                "client_spec": {
                    "class_name": "helm.clients.openai_client.OpenAIClient",
                    "args": {
                        "base_url": "https://prod.api.nvidia.com/llm/v1/azure/",
                        "openai_model_name": "gpt-4o",
                    },
                },
            },
            {
                "name": "nvdev/meta/llama-3.3-70b-instruct-judge",
                "model_name": "nvdev/meta/llama-3.3-70b-instruct-judge",
                "tokenizer_name": "simple/tokenizer1",
                "max_sequence_length": 128000,
                "client_spec": {
                    "class_name": "helm.clients.openai_client.OpenAIClient",
                    "args": {
                        "base_url": "https://integrate.api.nvidia.com/v1",
                        "openai_model_name": "nvdev/meta/llama-3.3-70b-instruct",
                    },
                },
            },
            {
                "name": "nvidia/claude-3-7-sonnet-20250219-judge",
                "model_name": "nvidia/claude-3-7-sonnet-20250219-judge",
                "tokenizer_name": "anthropic/claude-3-7-sonnet-20250219",
                "max_sequence_length": 128000,
                "client_spec": {
                    "class_name": "helm.clients.nvidia_anthropic_client.NvidiaAnthropicClient",
                    "args": {
                        "base_url": "https://prod.api.nvidia.com/llm/v1/azure/",
                        "anthropic_model_name": "claude-3-7-sonnet-20250219",
                    },
                },
            },
        ]
    }
    return model_deployments


def write_yaml_file(data: dict, filepath: str):
    """Write data to YAML file with proper formatting."""
    with open(filepath, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate model configuration files for HELM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_dynamic_model_configs.py \\
    --model-name "myorg/mymodel" \\
    --base-url "https://api.myorg.com/v1" \\
    --openai-model-name "myorg/mymodel" \\
    --output-dir "./generated-configs"
        """
    )
    
    parser.add_argument(
        "--model-name",
        required=True,
        help="Model name (e.g., 'myorg/mymodel')"
    )
    
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL for the API endpoint"
    )
    
    parser.add_argument(
        "--openai-model-name",
        required=True,
        help="OpenAI model name for the client"
    )
    
    parser.add_argument(
        "--output-dir",
        default="./generated-configs",
        help="Output directory for generated files (default: ./generated-configs)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    model_metadata = generate_model_metadata(args.model_name)
    model_deployments = generate_model_deployments(
        args.model_name, 
        args.base_url, 
        args.openai_model_name
    )
    
    metadata_path = output_dir / "model_metadata.yaml"
    deployments_path = output_dir / "model_deployments.yaml"
    
    write_yaml_file(model_metadata, str(metadata_path))
    write_yaml_file(model_deployments, str(deployments_path))
    
    print(f"✅ Generated configuration files:")
    print(f"   📄 {metadata_path}")
    print(f"   📄 {deployments_path}")
    print(f"\n📋 Configuration summary:")
    print(f"   Model name: {args.model_name}")
    print(f"   Base URL: {args.base_url}")
    print(f"   OpenAI model name: {args.openai_model_name}")
    print(f"   Judge models included: GPT-4o, Llama-3.3-70B-Instruct, Claude-3-7-Sonnet")


if __name__ == "__main__":
    main()
