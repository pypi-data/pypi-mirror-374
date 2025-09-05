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


PROMPT_TEMPLATE = """You are a medical expert responsible for evaluating a proposed treatment plan
based on provided patient information.

Your goal is to assess whether the treatment plan uses the patient's medical history,
medications, symptoms, and other relevant details appropriately, follows clinical best practices,
and aligns with the gold standard response in accuracy, completeness, and clarity.

The patient's information will be provided in these tags:
<patient_information>
{{QUESTION}}
</patient_information>

The proposed treatment plan will be provided in these tags:
<response>
{{RESPONSE}}
</response>

The gold standard treatment plan will be provided in these tags:
<gold_response>
{{GOLD_RESPONSE}}
</gold_response>

Carefully review the <response> based on the <patient_information> and compare it to the <gold_response> when needed.

For each category below, rate the response on a scale of 1 to 5 (1 = very poor, 5 = excellent) and
provide a brief explanation for your score:

Evaluation Criteria:
Accuracy (1-5)
- Does the treatment plan provide correct medical advice based on clinical guidelines?

Completeness (1-5)
Does the treatment plan include all important medical details?

Clarity (1-5)
- Is the treatment plan written clearly so clinicians can easily understand it?

Output Format:
Generate a valid JSON object with the following structure:
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


class MTSamplesReplicateAnnotator(LLMAsJuryAnnotator):
    """The MTSamplesReplicate autograder."""

    name = "mtsamples_replicate"

    def __init__(self, auto_client: AutoClient, template_name: Optional[str] = None):
        super().__init__(
            auto_client=auto_client,
            prompt_template=PROMPT_TEMPLATE,
            annotation_criteria=ANNOTATION_CRITERIA,
            annotator_models=ANNOTATOR_MODELS,
        )
