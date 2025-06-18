"""
Send sample predictions to the deployed endpoint using Boto3 Predictor.
"""

import boto3
import sagemaker
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(dotenv_path="traffic/.env")

endpoint_name = os.getenv("ENDPOINT_NAME")

session = sagemaker.Session()
predictor = sagemaker.predictor.Predictor(
    endpoint_name=endpoint_name,
    sagemaker_session=session
)

# Load test input
validation_df = pd.read_csv("traffic/2_model_training/validation.csv")
test_sample = validation_df.iloc[:5].values

# Send predictions
preds = predictor.predict(test_sample)
print("📈 Predictions:")
print(preds)
