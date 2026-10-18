# from pathlib import Path

# import joblib
# import pandas as pd
# import plotly.express as px
# import streamlit as st

# from src.cloudcost_ai.config import PROJECT_ROOT
# from src.cloudcost_ai.cost_analyzer import analyze_costs
# from src.cloudcost_ai.anomaly_detector import (
#     NUMERIC_FEATURES,
#     CATEGORICAL_FEATURES
# )


# DATA_PATH = PROJECT_ROOT / "data" / "raw" / "cloudcost_billing_50000.csv"
# MODEL_PATH = PROJECT_ROOT / "models" / "anomaly_detector.joblib"

# st.set_page_config(
#     page_title="CloudCost AI",
#     page_icon="☁️",
#     layout="wide"
# )

# st.title("CloudCost AI")
# st.caption("Cloud FinOps Intelligence | Cost Analytics and Anomaly Detection")

# @st.cache_data
# def load_data(path):
#     return pd.read_csv(path)

# @st.cache_resource
# def load_model(path):
#     return joblib.load(path)

# if not DATA_PATH.exists():
#     st.error("Trained model not found. train the anomaly detector dirst.")
#     st.code("PYTHONPATH=src python3 -m cloudost_ai.anomaly_detector")
#     st.stop()


# try:
#     df=load_data(str(DATA_PATH))
#     model=load_model(str(MODEL_PATH))

#     df["timestamp"]=pd.to_datetime(df["timestamp"],errors="coerce")
#     df["cost"]=pd.to_numeric(df["cost"],errors="coerce").fillna(0)

#     analysis=analyze_costs(df)

#     features=df[NUMERIC_FEATURES+CATEGORICAL_FEATURES].copy()
#     df["anomaly_probobility"]=model.predict_proba(features)[:,1]
#     df["predicted_anomaly"]=model.predict(features).astype(int)

# except Exception as error:
#     st.error(f"unable to load dashboard data: {error}")
#     st.stop()

# st.sidebar.header("Filters")

# services = ["All"] + sorted(df["service"].dropna().unique().tolist())
# selected_service = st.sidebar.selectbox("Service", services)

# departments = ["All"] + sorted(df["department"].dropna().unique().tolist())
# selected_department = st.sidebar.selectbox("Department", departments)

# filtered = df.copy()

# if selected_service != "All":
#     filtered = filtered[filtered["service"] == selected_service]

# if selected_department != "All":
#     filtered = filtered[filtered["department"] == selected_department]
# total_cost=filtered["cost"].sum()
# record_count=len(filtered)
# anomaly_count=int(filtered["predicted_anomaly"].sum())

# st.subheader("Exective Overview")
# c1,c2,c3,c4=st.columns(4)
# c1.metric("Total Cloud Spend",f"${total_cost:,.2f}")
# c2.metric("Billing Records",f"{record_count:,}")
# c3.metric("Predicted Anomalies",f"{anomaly_count:,}")

# c4.metric("Stopped Records with Cost",
#           f"{len(filtered[(filtered["resource_status"].str.lower()=="stopped") & (filtered["cost"]>0)]):,}")

# st.divider()

# left,right=st.columns(2)

# with left:
#     st.subheader("Monthly Cloud Spend")
#     monthly=(filtered.dropna(subset=["timestamp"])
#              .assign(month=lambda x:x["timestamp"].dt.to_period("M").astype(str))
#              .groupby("month",as_index=False)["cost"]
#              .sum().sort_values("Month"))

#     fig=px.line(monthly,x="month",y="cost",markers=True,title="Monthly Spending Trend",labels={"month":"Month","cost":"Spend($)"})

#     st.plotly_chart(fig,use_container_width=True)

# with right:
#     st.subheader("Spend by Service")
#     service_cost=(filtered.groupby("service",as_index=False)["cost"]
#                   .sum().sort_values("cost", ascending=False).head(10))

#     fig=px.bar(service_cost,x="cost",y="service",orientation="h",title="Top 10 Services",labels={"cost":"Spend ($)","service":"Service"})
#     fig.update_layout(yaxis={"categoryorder":"total ascending"})
#     st.plotly_chart(fig,use_container_width=True)



# left,right=st.columns(2)

# with left:
#     st.subheader("Spend By Department")
#     department_cost=(filtered.groupby("department",as_index=False)["cost"]
#                      .sum().sort_values("cost",ascending=False))

#     fig=px.bar(department_cost,x="department",y="cost",title="Department Spending",labels={"department":"department","cost":"Spend {$}"})

#     st.plotly_chart(fig,use_container_width=True)

# with right:
#     st.subheader("Predicted Anomaly Breakdown")
#     anomaly_summary = pd.DataFrame(
#         {
#             "Status": ["Predicted anomaly", "Not flagged"],
#             "Records": [
#                 int(filtered["predicted_anomaly"].sum()),
#                 int((filtered["predicted_anomaly"] == 0).sum()),
#             ],
#         }
#     )
#     fig = px.pie(
#         anomaly_summary,
#         names="Status",
#         values="Records",
#         hole=0.55,
#     )
#     st.plotly_chart(fig, use_container_width=True)

# st.divider()

# st.subheader("Anomaly Alerts")

# alerts = filtered[filtered["predicted_anomaly"] == 1].copy()
# alerts = alerts.sort_values("anomaly_probability", ascending=False)

# alert_columns = [
#     "usage_id",
#     "timestamp",
#     "service",
#     "department",
#     "resource_id",
#     "cost",
#     "utilization_efficiency_pct",
#     "anomaly_probability",
# ]

# available_alert_columns = [c for c in alert_columns if c in alerts.columns]
# display_alerts = alerts[available_alert_columns].copy()

# if "anomaly_probability" in display_alerts:
#     display_alerts["anomaly_probability"] = (
#         display_alerts["anomaly_probability"] * 100
#     ).round(2)

# st.caption("Anomaly probability is the model's estimated probability, not a confirmed incident.")
# st.dataframe(display_alerts, use_container_width=True, hide_index=True)

# st.download_button(
#     "Download anomaly alerts CSV",
#     data=alerts.to_csv(index=False).encode("utf-8"),
#     file_name="cloudcost_anomaly_alerts.csv",
#     mime="text/csv",
# )

# st.divider()

# st.subheader("Optimization Candidates")

# stopped = filtered[
#     (filtered["resource_status"].str.lower() == "stopped")
#     & (filtered["cost"] > 0)
# ].sort_values("cost", ascending=False)

# low_utilization = filtered[
#     filtered["utilization_efficiency_pct"] < 30
# ].sort_values("cost", ascending=False)

# tab1, tab2 = st.tabs(["Stopped Resources With Cost", "Low Utilization"])

# with tab1:
#     st.caption(
#         "Positive charges on stopped resources need investigation; they do not automatically prove waste."
#     )
#     st.dataframe(stopped, use_container_width=True, hide_index=True)

# with tab2:
#     st.caption(
#         "Low utilization is a review signal, not an automatic recommendation to shut down a resource."
#     )
#     st.dataframe(low_utilization, use_container_width=True, hide_index=True)

# st.caption(
#     "V1 uses the supplied billing dataset and labeled anomaly examples. "
#     "Validate alerts and estimated savings against real billing data before making financial claims."
# )

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

from cloudcost_ai.config import PROJECT_ROOT
from cloudcost_ai.cost_analyzer import analyze_costs
from cloudcost_ai.anomaly_detector import (
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "cloudcost_billing_50000.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "anomaly_detector.joblib"

st.set_page_config(
    page_title="CloudCost AI",
    page_icon="☁️",
    layout="wide",
)

st.title("CloudCost AI")
st.caption("Cloud FinOps Intelligence | Cost Analytics and Anomaly Detection")


@st.cache_data
def load_data(path):
    return pd.read_csv(path)


@st.cache_resource
def load_model(path):
    return joblib.load(path)


if not DATA_PATH.exists():
    st.error(f"Billing dataset not found: {DATA_PATH}")
    st.stop()

if not MODEL_PATH.exists():
    st.error(f"Trained model not found: {MODEL_PATH}")
    st.code("PYTHONPATH=src python3 -m cloudcost_ai.anomaly_detector")
    st.stop()


try:
    df = load_data(str(DATA_PATH))
    model = load_model(str(MODEL_PATH))

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce").fillna(0)

    analysis = analyze_costs(df)

    features = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES].copy()
    df["anomaly_probability"] = model.predict_proba(features)[:, 1]
    df["predicted_anomaly"] = model.predict(features).astype(int)

except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.stop()


st.sidebar.header("Filters")

services = ["All"] + sorted(df["service"].dropna().unique().tolist())
selected_service = st.sidebar.selectbox("Service", services)

departments = ["All"] + sorted(df["department"].dropna().unique().tolist())
selected_department = st.sidebar.selectbox("Department", departments)

filtered = df.copy()

if selected_service != "All":
    filtered = filtered[filtered["service"] == selected_service]

if selected_department != "All":
    filtered = filtered[filtered["department"] == selected_department]


total_cost = filtered["cost"].sum()
record_count = len(filtered)
anomaly_count = int(filtered["predicted_anomaly"].sum())

st.subheader("Executive Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Cloud Spend", f"${total_cost:,.2f}")
c2.metric("Billing Records", f"{record_count:,}")
c3.metric("Predicted Anomalies", f"{anomaly_count:,}")

stopped_count = len(
    filtered[
        (filtered["resource_status"].str.lower() == "stopped")
        & (filtered["cost"] > 0)
    ]
)

c4.metric("Stopped Records With Cost", f"{stopped_count:,}")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Monthly Cloud Spend")

    monthly = (
        filtered.dropna(subset=["timestamp"])
        .assign(month=lambda x: x["timestamp"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)["cost"]
        .sum()
        .sort_values("month")
    )

    fig = px.line(
        monthly,
        x="month",
        y="cost",
        markers=True,
        title="Monthly Spending Trend",
        labels={"month": "Month", "cost": "Spend ($)"},
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Spend by Service")

    service_cost = (
        filtered.groupby("service", as_index=False)["cost"]
        .sum()
        .sort_values("cost", ascending=False)
        .head(10)
    )

    fig = px.bar(
        service_cost,
        x="cost",
        y="service",
        orientation="h",
        title="Top 10 Services",
        labels={"cost": "Spend ($)", "service": "Service"},
    )

    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)


left, right = st.columns(2)

with left:
    st.subheader("Spend by Department")

    department_cost = (
        filtered.groupby("department", as_index=False)["cost"]
        .sum()
        .sort_values("cost", ascending=False)
    )

    fig = px.bar(
        department_cost,
        x="department",
        y="cost",
        title="Department Spending",
        labels={"department": "Department", "cost": "Spend ($)"},
    )

    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Predicted Anomaly Breakdown")

    anomaly_summary = pd.DataFrame(
        {
            "Status": ["Predicted anomaly", "Not flagged"],
            "Records": [
                anomaly_count,
                int((filtered["predicted_anomaly"] == 0).sum()),
            ],
        }
    )

    fig = px.pie(
        anomaly_summary,
        names="Status",
        values="Records",
        hole=0.55,
    )

    st.plotly_chart(fig, use_container_width=True)


st.divider()
st.subheader("Anomaly Alerts")

alerts = filtered[filtered["predicted_anomaly"] == 1].copy()
alerts = alerts.sort_values("anomaly_probability", ascending=False)

alert_columns = [
    "usage_id",
    "timestamp",
    "service",
    "department",
    "resource_id",
    "cost",
    "utilization_efficiency_pct",
    "anomaly_probability",
]

available_alert_columns = [
    column for column in alert_columns if column in alerts.columns
]

display_alerts = alerts[available_alert_columns].copy()

if "anomaly_probability" in display_alerts.columns:
    display_alerts["anomaly_probability"] = (
        display_alerts["anomaly_probability"] * 100
    ).round(2)

st.caption(
    "Anomaly probability is the model's estimated probability, not a confirmed incident."
)

st.dataframe(
    display_alerts,
    use_container_width=True,
    hide_index=True,
)

st.download_button(
    "Download Anomaly Alerts CSV",
    data=alerts.to_csv(index=False).encode("utf-8"),
    file_name="cloudcost_anomaly_alerts.csv",
    mime="text/csv",
)

st.divider()
st.subheader("Optimization Candidates")

stopped = filtered[
    (filtered["resource_status"].str.lower() == "stopped")
    & (filtered["cost"] > 0)
].sort_values("cost", ascending=False)

low_utilization = filtered[
    filtered["utilization_efficiency_pct"] < 30
].sort_values("cost", ascending=False)

tab1, tab2 = st.tabs(
    ["Stopped Resources With Cost", "Low Utilization"]
)

with tab1:
    st.caption(
        "Positive charges on stopped resources need investigation; "
        "they do not automatically prove waste."
    )
    st.dataframe(stopped, use_container_width=True, hide_index=True)

with tab2:
    st.caption(
        "Low utilization is a review signal, not an automatic recommendation "
        "to shut down a resource."
    )
    st.dataframe(
        low_utilization,
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "V1 uses the supplied billing dataset and labeled anomaly examples. "
    "Validate alerts and estimated savings against real billing data before "
    "making financial claims."
)
