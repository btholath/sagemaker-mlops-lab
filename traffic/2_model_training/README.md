
```bash
Before concat:
y_train        X_train
--------       ----------------------
[0, 1, 0]       [[5.1, 3.5], [6.2, 2.8], [5.9, 3.0]]


After concat:

train_data:
incident | feature1 | feature2
-------- | -------- | --------
   0     |   5.1    |   3.5
   1     |   6.2    |   2.8
   0     |   5.9    |   3.0
```

# You trained a smart AI model to predict traffic incidents.
The model looked at past traffic data (like number of vehicles, speed, and weather) and learned patterns to guess if an incident might happen.

The training finished quickly and successfully — AWS SageMaker did all the heavy lifting for you in the cloud.

- Algorithm:
   - You used Amazon SageMaker’s built-in XGBoost (v1.3) container for a binary classification task (objective='binary:logistic').

- Dataset: 
   - 697 records ingested from SageMaker Feature Store (retrieved using Athena).

- Training Details:
   - 557 records used (likely after split or filtering).
   - Model trained using 100 boosting rounds (as seen in num_round=100).
   - Training log shows monotonic reduction in logloss, confirming proper learning and convergence.

- Output: The trained model is stored in the specified S3 bucket (s3://{bucket}/{prefix}/output).

```bash
(.venv) @btholath ➜ /workspaces/sagemaker-mlops-lab/traffic/2_model_training (main) $ python xgb_train_from_featurestore.py 
sagemaker.config INFO - Not applying SDK defaults from location: /etc/xdg/sagemaker/config.yaml
sagemaker.config INFO - Not applying SDK defaults from location: /home/codespace/.config/sagemaker/config.yaml
SELECT * FROM "traffic_feature_group_local_1750179378"
📊 Records retrieved from Feature Store: 697
🧾 Columns in dataframe: ['timestamp', 'sensor_id', 'vehicle_count', 'avg_speed', 'weather_condition', 'incident', 'write_time', 'api_invocation_time', 'is_deleted']
INFO:sagemaker:Creating training-job with name: sagemaker-xgboost-2025-06-17-17-08-58-270
2025-06-17 17:09:00 Starting - Starting the training job...
2025-06-17 17:09:14 Starting - Preparing the instances for training...
2025-06-17 17:09:37 Downloading - Downloading input data...
2025-06-17 17:10:23 Downloading - Downloading the training image...
2025-06-17 17:11:04 Training - Training image download completed. Training in progress..[2025-06-17 17:11:08.882 ip-10-0-167-69.ec2.internal:8 INFO utils.py:28] RULE_JOB_STOP_SIGNAL_FILENAME: None
[2025-06-17 17:11:08.913 ip-10-0-167-69.ec2.internal:8 INFO profiler_config_parser.py:111] User has disabled profiler.
[2025-06-17:17:11:08:INFO] Imported framework sagemaker_xgboost_container.training
[2025-06-17:17:11:08:INFO] Failed to parse hyperparameter objective value binary:logistic to Json.
Returning the value itself
[2025-06-17:17:11:08:INFO] No GPUs detected (normal if no gpus installed)
[2025-06-17:17:11:08:INFO] Running XGBoost Sagemaker in algorithm mode
[2025-06-17:17:11:08:INFO] Determined delimiter of CSV input is ','
[2025-06-17:17:11:08:INFO] files path: /opt/ml/input/data/train
[2025-06-17:17:11:08:INFO] Determined delimiter of CSV input is ','
[2025-06-17:17:11:08:INFO] Single node training.
[2025-06-17:17:11:08:INFO] Train matrix has 557 rows and 8 columns
[2025-06-17 17:11:08.973 ip-10-0-167-69.ec2.internal:8 INFO json_config.py:92] Creating hook from json_config at /opt/ml/input/config/debughookconfig.json.
[2025-06-17 17:11:08.974 ip-10-0-167-69.ec2.internal:8 INFO hook.py:207] tensorboard_dir has not been set for the hook. SMDebug will not be exporting tensorboard summaries.
[2025-06-17 17:11:08.975 ip-10-0-167-69.ec2.internal:8 INFO hook.py:259] Saving to /opt/ml/output/tensors
[2025-06-17 17:11:08.975 ip-10-0-167-69.ec2.internal:8 INFO state_store.py:77] The checkpoint config file /opt/ml/input/config/checkpointconfig.json does not exist.
[2025-06-17:17:11:08:INFO] Debug hook created from config
[17:11:08] WARNING: ../src/learner.cc:1061: Starting in XGBoost 1.3.0, the default evaluation metric used with the objective 'binary:logistic' was changed from 'error' to 'logloss'. Explicitly set eval_metric if you'd like to restore the old behavior.
[0]#011train-logloss:0.48764
[2025-06-17 17:11:08.980 ip-10-0-167-69.ec2.internal:8 INFO hook.py:428] Monitoring the collections: metrics
[2025-06-17 17:11:08.983 ip-10-0-167-69.ec2.internal:8 INFO hook.py:491] Hook is writing from the hook with pid: 8
[1]#011train-logloss:0.37600
[2]#011train-logloss:0.30255
[3]#011train-logloss:0.25567
[4]#011train-logloss:0.21902
[5]#011train-logloss:0.19335
[6]#011train-logloss:0.17345
[7]#011train-logloss:0.15992
[8]#011train-logloss:0.14582
[9]#011train-logloss:0.13566
[10]#011train-logloss:0.12557
[11]#011train-logloss:0.11993
[12]#011train-logloss:0.11308
[13]#011train-logloss:0.10798
[14]#011train-logloss:0.10269
[15]#011train-logloss:0.09902
[16]#011train-logloss:0.09587
[17]#011train-logloss:0.09212
[18]#011train-logloss:0.09029
[19]#011train-logloss:0.08776
[20]#011train-logloss:0.08437
[21]#011train-logloss:0.08175
[22]#011train-logloss:0.07898
[23]#011train-logloss:0.07591
[24]#011train-logloss:0.07393
[25]#011train-logloss:0.07158
[26]#011train-logloss:0.06949
[27]#011train-logloss:0.06773
[28]#011train-logloss:0.06619
[29]#011train-logloss:0.06397
[30]#011train-logloss:0.06278
[31]#011train-logloss:0.06140
[32]#011train-logloss:0.05958
[33]#011train-logloss:0.05812
[34]#011train-logloss:0.05621
[35]#011train-logloss:0.05527
[36]#011train-logloss:0.05415
[37]#011train-logloss:0.05328
[38]#011train-logloss:0.05249
[39]#011train-logloss:0.05155
[40]#011train-logloss:0.05056
[41]#011train-logloss:0.04920
[42]#011train-logloss:0.04859
[43]#011train-logloss:0.04767
[44]#011train-logloss:0.04656
[45]#011train-logloss:0.04555
[46]#011train-logloss:0.04467
[47]#011train-logloss:0.04385
[48]#011train-logloss:0.04312
[49]#011train-logloss:0.04242
[50]#011train-logloss:0.04174
[51]#011train-logloss:0.04102
[52]#011train-logloss:0.04018
[53]#011train-logloss:0.03957
[54]#011train-logloss:0.03907
[55]#011train-logloss:0.03845
[56]#011train-logloss:0.03790
[57]#011train-logloss:0.03733
[58]#011train-logloss:0.03684
[59]#011train-logloss:0.03640
[60]#011train-logloss:0.03599
[61]#011train-logloss:0.03564
[62]#011train-logloss:0.03528
[63]#011train-logloss:0.03476
[64]#011train-logloss:0.03438
[65]#011train-logloss:0.03393
[66]#011train-logloss:0.03368
[67]#011train-logloss:0.03313
[68]#011train-logloss:0.03285
[69]#011train-logloss:0.03264
[70]#011train-logloss:0.03224
[71]#011train-logloss:0.03184
[72]#011train-logloss:0.03161
[73]#011train-logloss:0.03126
[74]#011train-logloss:0.03097
[75]#011train-logloss:0.03073
[76]#011train-logloss:0.03054
[77]#011train-logloss:0.03015
[78]#011train-logloss:0.02992
[79]#011train-logloss:0.02975
[80]#011train-logloss:0.02954
[81]#011train-logloss:0.02926
[82]#011train-logloss:0.02892
[83]#011train-logloss:0.02863
[84]#011train-logloss:0.02845
[85]#011train-logloss:0.02829
[86]#011train-logloss:0.02804
[87]#011train-logloss:0.02780
[88]#011train-logloss:0.02765
[89]#011train-logloss:0.02751
[90]#011train-logloss:0.02730
[91]#011train-logloss:0.02713
[92]#011train-logloss:0.02695
[93]#011train-logloss:0.02673
[94]#011train-logloss:0.02661
[95]#011train-logloss:0.02638
[96]#011train-logloss:0.02625
[97]#011train-logloss:0.02612
[98]#011train-logloss:0.02590
[99]#011train-logloss:0.02575

2025-06-17 17:11:27 Uploading - Uploading generated training model
2025-06-17 17:11:27 Completed - Training job completed
Training seconds: 110
Billable seconds: 110
✅ Model training completed.
(.venv) @btholath ➜ /workspaces/sagemaker-mlops-lab/traffic/2_model_training (main) $ 
```      

```bash
(.venv) @btholath ➜ /workspaces/sagemaker-mlops-lab/traffic/2_model_training (main) $ python validate_model_from_csv.py 
📄 Loaded 557 records from train.csv
✅ Accuracy: 0.9285714285714286
✅ Confusion Matrix:
 [[103   1]
 [  7   1]]
✅ Classification Report:
               precision    recall  f1-score   support

           0       0.94      0.99      0.96       104
           1       0.50      0.12      0.20         8

    accuracy                           0.93       112
   macro avg       0.72      0.56      0.58       112
weighted avg       0.91      0.93      0.91       112

(.venv) @btholath ➜ /workspaces/sagemaker-mlops-lab/traffic/2_model_training (main) $
```

Your model validation script has successfully run, and here’s what the results indicate:

📊 Results Summary
Metric	Value	Meaning
Accuracy	0.93	93% of total predictions are correct. Overall performance is strong.
Confusion Matrix	[[103, 1], [7, 1]]	Of the 104 actual “0” cases (no incident), 103 were predicted correctly; of the 8 actual “1” cases (incident), only 1 was predicted correctly.
Precision (Class 1)	0.50	When the model predicted an incident, it was correct only 50% of the time.
Recall (Class 1)	0.12	The model only caught 12% of actual incidents — misses most incidents.
F1 Score (Class 1)	0.20	Indicates poor performance for detecting incidents, despite high overall accuracy.

⚠️ What's Going On?
This is a classic case of imbalanced data — too many "0" (no incident) vs very few "1" (incident) labels.

The model learns to predict the majority class ("0") very well.

But it struggles with the minority class ("1"), which may be crucial in a traffic use case