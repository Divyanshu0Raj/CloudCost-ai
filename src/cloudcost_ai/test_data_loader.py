from data_loader import load_billing_data

df = load_billing_data(
    bucket_name="cloudcost",
    object_name="cloudcost_billing_50000.csv",
)

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:", df.shape)
