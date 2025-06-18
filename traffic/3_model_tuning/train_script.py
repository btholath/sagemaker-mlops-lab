"""
s3://sagemaker-traffic-prediction-bucket/traffic-pipeline/train/train.csv
The train.csv is following columns.
incident	timestamp	sensor_id	vehicle_count	avg_speed	weather_condition	write_time	api_invocation_time	is_deleted
- remove last 3 columns such as write_time	api_invocation_time	is_deleted
-  Do categorical encoding (like LabelEncoder or OneHotEncoder)  for  weather_condition
"""
import argparse
import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import traceback


def preprocess(df):
    """Preprocess the input DataFrame for training."""
    # One-hot encode 'weather_condition'
    df = pd.get_dummies(df, columns=["weather_condition"], drop_first=True)

    # Separate target
    y = df["incident"]

    # Drop irrelevant timestamp-related columns and the target
    drop_columns = ["timestamp", "write_time", "api_invocation_time", "incident"]
    X = df.drop(columns=drop_columns, errors="ignore")

    return train_test_split(X, y, test_size=0.2, random_state=42)


if __name__ == "__main__":
    try:
        # Parse SageMaker hyperparameters
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

        # Load CSV from SageMaker input
        input_dir = "/opt/ml/input/data/train"
        input_file = os.path.join(input_dir, "train.csv")
        df = pd.read_csv(input_file, header=0)

        # Preprocess and split data
        X_train, X_val, y_train, y_val = preprocess(df)

        # Save validation set to /opt/ml/output/data/validation.csv
        val_df = pd.concat([y_val.reset_index(drop=True), X_val.reset_index(drop=True)], axis=1)
        val_output_path = "/opt/ml/output/data/validation.csv"
        val_df.to_csv(val_output_path, index=False)
        print(f"📁 Validation set saved to {val_output_path}")

        # Create DMatrix for XGBoost
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)

        # Define training parameters
        params = {
            "objective": args.objective,
            "eval_metric": args.eval_metric,
            "eta": args.eta,
            "gamma": args.gamma,
            "max_depth": args.max_depth,
            "min_child_weight": args.min_child_weight,
            "subsample": args.subsample,
        }

        # Train model
        xgb.train(
            params=params,
            dtrain=dtrain,
            num_boost_round=args.num_round,
            evals=[(dval, "validation")],
            verbose_eval=True
        )

        print("✅ Training completed successfully.")

    except Exception as e:
        print("❌ Exception occurred during training:")
        traceback.print_exc()
        raise e
