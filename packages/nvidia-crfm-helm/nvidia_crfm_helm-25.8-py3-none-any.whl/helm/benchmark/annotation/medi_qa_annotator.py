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

from typing import Dict, Optional, Set

from helm.benchmark.annotation.model_as_judge import AnnotatorModelInfo, LLMAsJuryAnnotator
from helm.clients.auto_client import AutoClient


PROMPT_TEMPLATE = """You are a medical expert tasked with evaluating the quality of a
response to a consumer health question.
Your goal is to assess how well the generated response answers the medical question,
and how it compares to the gold response in terms of accuracy, completeness, and clarity.

The question will be provided in these tags:
<question>
{{QUESTION}}
</question>

The response will be provided in these tags:
<response>
{{RESPONSE}}
</response>

The reference answer will be provided in these tags:
<gold_response>
{{GOLD_RESPONSE}}
</gold_response>

Carefully analyze the <response> compared to the <gold_response> and the original <question>.
For each of the following criteria, rate the response on a scale of 1 to 5 (1 = very poor, 5 = excellent),
and provide a short justification for your score.

Evaluation Criteria:
Accuracy (1-5)
- Is the medical information correct?

Completeness (1-5)
- Does the response fully answer the question and include important medical details?

Clarity (1-5)
- Is the response easy for consumers to understand?

Output Format:
Output the evaluation as a single valid JSON object matching the following structure:
{
    "accuracy": {
        "score": 0,
        "explanation": "Explain why this score was given."
    },
    "completeness": {
        "score": 0,
        "explanation": "Explain why this score was given."
    },
    "clarity": {
        "score": 0,
        "explanation": "Explain why this score was given."
    }
}

Ensure the output is valid JSON:
- Use **double quotes** (") for all keys and string values.
- When quoting text or sections inside the explanations, use escaped double quotes (\") to
  maintain valid JSON formatting.
- Do not include any additional information in the output.
"""

ANNOTATION_CRITERIA: Dict[str, Set[str]] = {
    "accuracy": {"score", "explanation"},
    "completeness": {"score", "explanation"},
    "clarity": {"score", "explanation"},
}

ANNOTATOR_MODELS: Dict[str, AnnotatorModelInfo] = {
    "gpt": AnnotatorModelInfo(
        model_name="nvidia/gpt4o-judge",
        model_deployment="nvidia/gpt4o",
    ),
    "llama": AnnotatorModelInfo(
        model_name="nvdev/meta/llama-3.3-70b-instruct-judge",
        model_deployment="nvdev/meta/llama-3.3-70b-instruct",
    ),
    "claude": AnnotatorModelInfo(
        model_name="nvidia/claude-3-7-sonnet-20250219-judge",
        model_deployment="nvidia/claude-3-7-sonnet-20250219",
    ),
}


class MediQAAnnotator(LLMAsJuryAnnotator):
    """The MediQA autograder."""

    name = "medi_qa"

    def __init__(self, auto_client: AutoClient, template_name: Optional[str] = None):
        super().__init__(
            auto_client=auto_client,
            prompt_template=PROMPT_TEMPLATE,
            annotation_criteria=ANNOTATION_CRITERIA,
            annotator_models=ANNOTATOR_MODELS,
        )
