
import pandas as pd

df=pd.read_csv("data/raw/cloudcost_billing_50000.csv")

print(df.head()) 
print(df.columns.tolist(),df.isnull().sum(),df.describe())
print(df.duplicated().sum())
print(df["usage_id"].duplicated().sum())
print((df["cost"]<0).sum())
print((df["usage_quantity"]<0).sum())
print(df["cost"].describe())

df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce")

df["billing_month"]=df["timestamp"].dt.to_period("M")


monthly_cost=(
    df.groupby("billing_month")["cost"]
    .sum()
    .sort_index()
)

print("monthly cost\n",monthly_cost)

print("monthly cost spending:---\n",round(df["cost"].sum(),2))

print("monthly cost spending by service:---\n",df.groupby("service")["cost"].sum())

print("")

department_cost=(
    df.groupby("department")["cost"]
    .sum()
    .sort_values(ascending=False)
)

print("\ndepartment cost spending:---\n",department_cost.round(2))

environment_cost=(
    df.groupby("environment")["cost"]
    .sum()
    .sort_values(ascending=False)
)

print("\nenvironment cost spending:---\n",environment_cost.round(2))

print("Billing currency:---\n",df["billing_currency"].value_counts(dropna=False))


# Select records belonging to ML Platform
ml_df = df[df["department"] == "ML Platform"]

# Break down ML Platform cost by service
print("\n--- ML Platform Cost by Service ---")

ml_service_cost = (
    ml_df.groupby("service")["cost"]
    .sum()
    .sort_values(ascending=False)
)

print(ml_service_cost.round(2))

# Break down ML Platform cost by environment
print("\n--- ML Platform Cost by Environment ---")

ml_environment_cost = (
    ml_df.groupby("environment")["cost"]
    .sum()
    .sort_values(ascending=False)
)

print(ml_environment_cost.round(2))

# Check average CPU utilization by service
print("\n--- ML Platform CPU Utilization ---")

ml_cpu = (
    ml_df.groupby("service")["cpu_utilization_pct"]
    .mean()
    .sort_values(ascending=False)
)

print(ml_cpu.round(2))


print("\n-----Resource and utilization columns-----")

for column in df.columns:
    if any (
        word in column.lower()
        for word in ["utilization", "resource", "status", "age", "cost"]
    ):
        print(column)

print("\n-----Resource Status Counts-----")
print(df["resource_status"].value_counts(dropna=False))

print("\n Oldest ML Platform Resouces")

resource_age=(
    ml_df.groupby(["service","resource_id"])["resource_age_days"]
    .max()
    .sort_values(ascending=False)
)

print(resource_age.head(10))

print("\n----Top 10 Expensive Resources-------\n")

resource_cost=(
    df.groupby(
        ["department","service","resource_id","environment"]
    )
    .agg(
        total_cost=("cost","sum"),
        avg_cpu=("cpu_utilization_pct","mean"),
        avg_memory=("memory_utilization_pct","mean"),
        avg_efficiency=("utilization_efficiency_pct","mean"),
        age_days=("resource_age_days","max"),
        records=("usage_id","count")
    ).sort_values("total_cost",ascending=False)

)

print(resource_cost.head(10).round(2).to_string())
