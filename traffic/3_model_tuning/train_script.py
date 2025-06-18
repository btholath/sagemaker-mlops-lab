"""
s3://sagemaker-traffic-prediction-bucket/traffic-pipeline/train/train.csv
- Remove columns: write_time, api_invocation_time, is_deleted
- One-hot encode weather_condition
"""
import argparse
import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import traceback
import boto3
import logging

# ---------------- Setup Logger ----------------
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------- Preprocessing ----------------
def preprocess(df):
    """Preprocess the input DataFrame for training."""
    logger.info("🔄 Starting preprocessing...")

    # One-hot encode 'weather_condition'
    df = pd.get_dummies(df, columns=["weather_condition"], drop_first=True)

    # Separate target
    y = df["incident"]

    # Drop irrelevant timestamp-related columns and the target
    drop_columns = ["timestamp", "write_time", "api_invocation_time", "is_deleted", "incident"]
    X = df.drop(columns=drop_columns, errors="ignore")

    logger.info("✅ Finished preprocessing. Data shape: %s", X.shape)
    return train_test_split(X, y, test_size=0.2, random_state=42)

# ---------------- Main Training ----------------
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--num_round", type=int, default=100)
        parser.add_argument("--eta", type=float, default=0.3)
        parser.add_argument("--gamma", type=float, default=0)
        parser.add_argument("--max_depth", type=int, default=6)
        parser.add_argument("--min_child_weight", type=int, default=1)
        parser.add_argument("--subsample", type=float, default=1.0)
        parser.add_argument("--objective", type=str, default="binary:logistic")
        parser.add_argument("--eval_metric", type=str, default="auc")
        args = parser.parse_args()

        logger.info("🚀 Starting training job...")
        input_dir = "/opt/ml/input/data/train"
        input_file = os.path.join(input_dir, "train.csv")
        df = pd.read_csv(input_file, header=0)

        logger.info("📄 Loaded training data: %d rows", len(df))

        # Preprocess
        X_train, X_val, y_train, y_val = preprocess(df)

        # Save validation set to S3
        val_df = pd.concat([y_val.reset_index(drop=True), X_val.reset_index(drop=True)], axis=1)
        val_output_path = "/opt/ml/output/data/validation.csv"
        val_df.to_csv(val_output_path, index=False)
        logger.info("💾 Saved validation set to %s", val_output_path)

        bucket = "sagemaker-traffic-prediction-bucket"
        key = "traffic-pipeline/validation/validation.csv"
        s3 = boto3.client("s3")
        s3.upload_file(val_output_path, bucket, key)
        logger.info("☁️ Uploaded validation.csv to s3://%s/%s", bucket, key)

        # Train model
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)
        params = {
            "objective": args.objective,
            "eval_metric": args.eval_metric,
            "eta": args.eta,
            "gamma": args.gamma,
            "max_depth": args.max_depth,
            "min_child_weight": args.min_child_weight,
            "subsample": args.subsample,
        }

        logger.info("⚙️ XGBoost training params: %s", params)
        xgb.train(
            params=params,
            dtrain=dtrain,
            num_boost_round=args.num_round,
            evals=[(dval, "validation")],
            verbose_eval=True
        )

        logger.info("✅ Training completed successfully.")

    except Exception as e:
        logger.exception("❌ Exception occurred during training:")
        raise
