
from data_loader import load_billing_data_from_oci



df = load_billing_data_from_oci()

print("Successfully loaded billing data from OCI.")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("\nFirst 3 records:")
print(df.head(3).to_string(index=False))
