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

import json
import pathlib
import re

from nvidia_eval_commons.api.api_dataclasses import EvaluationResult, MetricResult, Score, TaskResult


def parse_output(output_dir: str) -> EvaluationResult:
    # Recursively search for stats.json in the output directory
    stats_files = list(pathlib.Path(output_dir).rglob("stats.json"))
    if not stats_files:
        raise FileNotFoundError(f"No stats.json found in {output_dir} or its subdirectories")
    if len(stats_files) > 1:
        raise ValueError(
            f"Multiple stats.json files found in {output_dir}. Please specify a more specific output directory."
        )
    
    stats_file = stats_files[0]
    with open(stats_file) as f:
        stats = json.load(f)

    # Extract task name from the output directory path
    # The directory structure is typically: output_dir/runs/suite/task_name:params/
    # We need to extract the task name part before the colon
    output_path = pathlib.Path(output_dir)
    
    # Find the run directory by looking for the directory containing stats.json
    # and then get its parent (the suite directory) and then the run directory
    run_dir = stats_file.parent
    suite_dir = run_dir.parent
    runs_dir = suite_dir.parent
    
    # The run directory name contains the task name and parameters
    # Extract task name from the directory name (remove parameters after colon)
    task_name = run_dir.name.split(":")[0]
    
    # Define metrics to filter out for readability
    filtered_metrics = {
        "batch_size",
        "bits_per_byte", 
        "num_bytes",
        "prompt_truncated",
        "num_train_instances",
        "num_train_trials",
        "num_references",
        "logprob_per_byte"
    }
    
    scores = {}
    
    # Process each stat entry
    for stat in stats:
        name = stat["name"]["name"]
        
        # Skip filtered metrics
        if name in filtered_metrics:
            print(f"Skipping metric: {name}")
            continue
        
        # Handle cases where count is 0 and mean/stddev fields are not present
        if stat.get("count", 0) == 0:
            # For stats with count 0, use 0 as the value and empty stats dict
            score_value = 0.0
            stats_dict = {}
        else:
            # For stats with count > 0, use mean and stddev if available
            score_value = stat.get("mean", 0.0)
            stats_dict = {"stddev": stat.get("stddev", 0.0)}
        
        scores[name] = Score(
            value=score_value,
            stats=stats_dict
        )

    metric_result = MetricResult(scores=scores)
    
    task_result = TaskResult(metrics={"score": metric_result})
    
    return EvaluationResult(
        tasks={task_name: task_result},
        groups={task_name: {"metrics": {"score": metric_result}}}
    )
