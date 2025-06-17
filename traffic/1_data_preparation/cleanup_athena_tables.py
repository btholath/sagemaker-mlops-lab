import boto3

glue = boto3.client("glue")
database_name = "sagemaker_featurestore"
table_prefix = "traffic_feature_group_local_"

# List all tables in the sagemaker_featurestore database
paginator = glue.get_paginator("get_tables")
tables_to_delete = []

for page in paginator.paginate(DatabaseName=database_name):
    for table in page["TableList"]:
        table_name = table["Name"]
        if table_name.startswith(table_prefix):
            tables_to_delete.append(table_name)

# Delete matching tables
for table_name in tables_to_delete:
    print(f"🗑️ Deleting table: {table_name}")
    glue.delete_table(DatabaseName=database_name, Name=table_name)

print(f"✅ Deleted {len(tables_to_delete)} tables.")
