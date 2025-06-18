import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.preprocessing import OneHotEncoder
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define column names manually
column_names = [
    "incident", "timestamp", "sensor_id", "vehicle_count", 
    "avg_speed", "weather_condition", "write_time", 
    "api_invocation_time", "is_deleted"
]

# Load data
df = pd.read_csv("train.csv", names=column_names)
logger.info(f"📄 Loaded {len(df)} records from train.csv")

# Drop unused columns
df.drop(columns=["timestamp", "write_time", "api_invocation_time", "is_deleted"], inplace=True)

# Convert numeric columns
numeric_cols = ["sensor_id", "vehicle_count", "avg_speed"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Drop rows with missing values
df.dropna(inplace=True)

# Prepare features and label
y = df["incident"].astype(int)  # Convert to int to match predicted labels
X = df.drop(columns=["incident"])

# One-hot encode weather_condition
encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
encoded_weather = encoder.fit_transform(X[["weather_condition"]])
encoded_weather_df = pd.DataFrame(encoded_weather, columns=encoder.get_feature_names_out(["weather_condition"]))

# Combine numeric and encoded categorical features
X.reset_index(drop=True, inplace=True)
encoded_weather_df.reset_index(drop=True, inplace=True)
X_final = pd.concat([X.drop(columns=["weather_condition"]), encoded_weather_df], axis=1)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X_final, y, test_size=0.2, random_state=42)

# XGBoost training
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

params = {
    "objective": "binary:logistic",
    "eval_metric": "logloss",
    "verbosity": 0
}
bst = xgb.train(params, dtrain, num_boost_round=100)

# Predictions
y_pred_prob = bst.predict(dtest)
y_pred = [1 if p > 0.5 else 0 for p in y_pred_prob]

# Evaluation
logger.info("✅ Accuracy: %.4f", accuracy_score(y_test, y_pred))
logger.info("✅ Confusion Matrix:\n%s", confusion_matrix(y_test, y_pred))
logger.info("✅ Classification Report:\n%s", classification_report(y_test, y_pred))
