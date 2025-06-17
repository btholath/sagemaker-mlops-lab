
# ✅ Step-by-Step: Validate SageMaker Feature Store Ingestion
- 1. Login to AWS Console
- Go to https://console.aws.amazon.com/
- Select the correct region: us-east-1 (from your .env file)

# 2. Navigate to Amazon SageMaker
 - In the search bar, type SageMaker and click on Amazon SageMaker.
 - In the left sidebar, scroll down and click on Feature Store → Feature groups.

# 3. Validate Your Feature Group
 - Look for the Feature Group: traffic-feature-group-local
 - Click on it to open the details page.
 - On the Feature Group page, verify the following:
 - Status: Should say Created

    Offline Store S3 URI: Should match s3://sagemaker-traffic-prediction-bucket/traffic-pipeline/feature-store/ingest/

    IAM Role ARN: Should match the role you created (SageMakerExecutionRole-TrafficML)
    Record identifier: incident
    Event time feature: timestamp

# 4. Check Feature Definitions
 On the same page, scroll to Feature definitions.
 You should see all columns from your CSV (e.g., timestamp, incident, etc.)
 Confirm data types are as expected (e.g., String, Integral, Fractional).

# 5. Query Data with Athena (Offline Store)
 If Offline Store is enabled:
 Go to the Athena console: https://console.aws.amazon.com/athena/
 Select the appropriate database (usually starts with sagemaker_featurestore_)
 Run a query like:
    SELECT * FROM "your_table_name" LIMIT 10;

# 6. Check S3 Bucket for Offline Store
Go to S3 Console
Find the bucket: sagemaker-traffic-prediction-bucket
Navigate to: traffic-pipeline/feature-store/ingest/
You should see parquet or data files — evidence of data being stored for the offline store.

# ✅ Bonus Checks (Optional but Useful)
    - A. CloudTrail Audit
    - Go to AWS CloudTrail → Event history
    - Filter by Event name: CreateFeatureGroup
    - You can see when the resource was created and by which IAM user/role.
