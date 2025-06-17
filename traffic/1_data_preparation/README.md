
# Delete the existing Feature Group
```bash
(.venv) @btholath ➜ /workspaces/sagemaker-mlops-lab/traffic/1_data_preparation (main) $ 
aws sagemaker delete-feature-group --feature-group-name traffic-feature-group-local

(.venv) @btholath ➜ /workspaces/sagemaker-mlops-lab/traffic/1_data_preparation (main) $ 
python feature_store_ingest.py
sagemaker.config INFO - Not applying SDK defaults from location: /etc/xdg/sagemaker/config.yaml
sagemaker.config INFO - Not applying SDK defaults from location: /home/codespace/.config/sagemaker/config.yaml
0    1/1/23 0:00
1    1/1/23 1:00
2    1/1/23 2:00
3    1/1/23 3:00
4    1/1/23 4:00
Name: timestamp, dtype: object
⏳ Feature Group status: Creating
⏳ Feature Group status: Creating
⏳ Feature Group status: Created
✅ Feature Group 'traffic-feature-group-local' created successfully.
📥 Ingesting 697 records into Feature Store...
✅ Data ingestion completed successfully.
(.venv) @btholath ➜ /workspaces/sagemaker-mlops-lab/traffic/1_data_preparation (main) $ 
```