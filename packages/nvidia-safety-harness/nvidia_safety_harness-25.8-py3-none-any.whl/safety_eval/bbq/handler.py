import os
import json
import logging
from typing import List, Optional
import pandas as pd
import importlib.resources as pkg_resources

from safety_eval.configs import ModelConfig, BBQConfig
from safety_eval.bbq.generate_responses import main as generate_main
from safety_eval.bbq.evaluate import main as evaluate_main


logger = logging.getLogger(__name__)


DEFAULT_CATEGORIES: List[str] = [
    "Age",
    "Disability_status",
    "Gender_identity",
    "Nationality",
    "Physical_appearance",
    "Race_ethnicity",
    "Race_x_SES",
    "Race_x_gender",
    "Religion",
    "SES",
    "Sexual_orientation",
]


def handle_bbq(
    model_config: ModelConfig,
    judge_config: BBQConfig,
    output_dir: str,
    limit: int,
    categories: Optional[List[str]] = None,
    dataset: Optional[str] = None,
):
    """Run BBQ using the original pipeline (generation + evaluation).

    Uses internal functions to generate `responses.json` and `bbq_metrics.csv`.
    Then converts CSV to `metrics.json` for harness consistency.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Defaults
    if categories is None:
        categories = DEFAULT_CATEGORIES
    if dataset is None:
        dataset = "heegyu/bbq"

    # Build config for generator+parser from our configs
    num_rows = limit if (limit and limit > 0) else -1
    retries = model_config.inference_params.get("retries", 2)
    parallelism = model_config.inference_params.get("concurrency", 1)
    config = {
        "model": {
            "base_url": model_config.base_url,
            "model_name": model_config.llm_name,
            "api_key": model_config.api_key,
            "temperature": model_config.inference_params.get("temperature", 1.0),
            "top_p": model_config.inference_params.get("top_p", 0.7),
            "max_tokens": model_config.inference_params.get("max_tokens", 128),
        },
        "parser": {
            "base_url": judge_config.base_url,
            "model_name": judge_config.llm_name,
            "api_key": judge_config.api_key,
            "temperature": judge_config.inference_params.get("temperature", 0.0),
            "top_p": judge_config.inference_params.get("top_p", 1.0),
            "max_tokens": judge_config.inference_params.get("max_tokens", 5),
        }
    }

    generate_main(
        categories=categories,
        output_dir=output_dir,
        dataset=dataset,
        num_rows=num_rows,
        config=config,
        retries=retries,
        parallelism=parallelism,
    )

    with pkg_resources.path("safety_eval.bbq.additional_data", "additional_metadata.csv") as p:
        if os.path.exists(p):
            metadata_path = str(p)
        else:
            raise FileNotFoundError("additional_metadata.csv not found in package resources or local additional_data directory")

    # Run evaluation
    evaluate_main(
        metadata_path=metadata_path,
        input_file=os.path.join(output_dir, "responses.json"),
        output_dir=output_dir,
        name="model_response",
    )

    # Convert bbq_metrics.csv -> metrics.json for harness consumers
    _convert_bbq_metrics_to_json(output_dir)


def _convert_bbq_metrics_to_json(output_dir: str) -> None:
    metrics_csv = os.path.join(output_dir, "bbq_metrics.csv")
    if not os.path.exists(metrics_csv):
        raise FileNotFoundError(f"Expected BBQ metrics at {metrics_csv}")
    df = pd.read_csv(metrics_csv)
    print(df)
    logger.info(f"Loaded BBQ metrics CSV with shape {df.shape}")
    # Compute weighted accuracy using group counts, then convert to histogram expected by output.py
    count_cols = [
        col for col in ["neg_Non-target", "neg_Target", "nonneg_Non-target", "nonneg_Target"]
        if col in df.columns
    ]
    if "acc" in df.columns and count_cols:
        df["group_count"] = df[count_cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
        total = int(df["group_count"].sum())
        # Avoid division by zero
        if total > 0:
            weighted_correct = float((df["acc"].astype(float) * df["group_count"]).sum())
            safe = int(round(weighted_correct))
            denom = total
        else:
            safe = 0
            denom = 0
    else:
        # Fallback: unweighted on groups
        denom = df.shape[0]
        safe = int(round(float(df.get("acc", pd.Series([0]*denom)).astype(float).mean()) * denom))
    unsafe = max(0, denom - safe)
    with open(os.path.join(output_dir, "metrics.json"), "w") as f:
        json.dump({"safe": safe, "unsafe": unsafe}, f)
    logger.info(f"Wrote metrics.json with counts: safe={safe}, unsafe={unsafe} (denom={denom})")
