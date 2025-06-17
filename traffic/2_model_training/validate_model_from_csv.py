import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Define column names manually since no header in CSV
column_names = [
    "incident", "timestamp", "sensor_id", "vehicle_count", 
    "avg_speed", "weather_condition", "write_time", 
    "api_invocation_time", "is_deleted"
]

df = pd.read_csv("train.csv", names=column_names)
print(f"📄 Loaded {len(df)} records from train.csv")

# Drop non-numeric or irrelevant columns
df = df.drop(columns=["timestamp", "write_time", "api_invocation_time", "is_deleted"])

# Encode categorical column
df["weather_condition"] = df["weather_condition"].astype("category").cat.codes

# Prepare features and label
X = df.drop(columns=["incident"])
y = df["incident"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# XGBoost
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

params = {"objective": "binary:logistic", "eval_metric": "logloss", "verbosity": 0}
bst = xgb.train(params, dtrain, num_boost_round=100)

# Predictions and metrics
y_pred_prob = bst.predict(dtest)
y_pred = [1 if p > 0.5 else 0 for p in y_pred_prob]

print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("✅ Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("✅ Classification Report:\n", classification_report(y_test, y_pred))
