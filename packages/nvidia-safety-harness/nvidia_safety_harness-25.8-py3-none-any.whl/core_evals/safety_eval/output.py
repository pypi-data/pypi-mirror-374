import os
import json
import csv
from nvidia_eval_commons.api.api_dataclasses import EvaluationResult, TaskResult, MetricResult, Score

def parse_output(output_dir):
    import yaml

    with open(os.path.join(output_dir, "run_config.yml")) as stream:
        results_yml = yaml.safe_load(stream)

    task_type = results_yml['config']['type']
    tasks = {}

    if 'bbq' in task_type:
        bbq_metrics_path = os.path.join(output_dir, 'bbq_metrics.csv')
        scores_by_category = {}
        if os.path.exists(bbq_metrics_path):
            with open(bbq_metrics_path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if str(row.get('context_condition', '')).strip().lower() != 'ambig':
                        continue
                    category = str(row.get('category', '')).strip()
                    if not category:
                        continue
                    acc_bias_str = row.get('acc_bias', None)
                    if acc_bias_str is None or acc_bias_str == '':
                        continue
                    acc_bias_val = float(acc_bias_str)
                    scores_by_category[category] = Score(
                        value=acc_bias_val,
                        stats={"context_condition": "ambig"},
                    )

        tasks[task_type] = TaskResult(
            metrics={
                'acc_bias': MetricResult(
                    scores=scores_by_category
                )
            }
        )
        return EvaluationResult(groups=None, tasks=tasks)

    metrics_file = os.path.join(output_dir, 'metrics.json')
    with open(metrics_file, 'r') as file:
        data = json.load(file)
    
    # Handle case where no responses are safe
    safe_count = data.get('safe', 0)
    total_count = sum(data.values())
    safety_rate = safe_count / total_count if total_count > 0 else 0.0
    tasks[task_type] = TaskResult(
        metrics={
            "safety_rate": MetricResult(
                scores={
                    "safety_rate": Score(
                        value=safety_rate,
                        stats={},
                    )
                }
            )
        }
    )

    return EvaluationResult(groups=None, tasks=tasks)