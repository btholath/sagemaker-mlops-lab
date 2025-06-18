import argparse
import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
import traceback

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

        # Load CSV from SageMaker input location
        input_dir = "/opt/ml/input/data/train"
        df = pd.read_csv(os.path.join(input_dir, "train.csv"))
        X = df.drop(columns=["incident"])
        y = df["incident"]

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)

        # Parameters from SageMaker
        params = {
            "objective": args.objective,
            "eval_metric": args.eval_metric,
            "eta": args.eta,
            "gamma": args.gamma,
            "max_depth": args.max_depth,
            "min_child_weight": args.min_child_weight,
            "subsample": args.subsample,
        }

        # Train
        xgb.train(
            params=params,
            dtrain=dtrain,
            num_boost_round=args.num_round,
            evals=[(dval, "validation")],
            verbose_eval=True
        )
    except Exception as e:
        print("❌ Exception occurred during training:")
        traceback.print_exc()
        raise e