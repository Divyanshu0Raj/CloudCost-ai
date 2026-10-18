import pandas as pd

from cloudcost_ai.utils.logger import get_logger
from cloudcost_ai.utils.exception import CustomException

logger = get_logger(__name__)


def analyze_costs(df: pd.DataFrame) -> dict:
    try:
        required_columns = [
            "timestamp",
            "service",
            "department",
            "cost",
            "resource_id",
            "resource_status",
            "utilization_efficiency_pct",
        ]

        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        if df.empty:
            raise ValueError("Billing data is empty")

        data = df.copy()
        data["timestamp"] = pd.to_datetime(data["timestamp"], errors="raise")
        data["cost"] = pd.to_numeric(data["cost"], errors="raise")
        data["utilization_efficiency_pct"] = pd.to_numeric(
            data["utilization_efficiency_pct"], errors="raise"
        )

        monthly_cost = (
            data.assign(month=data["timestamp"].dt.to_period("M").astype(str))
            .groupby("month", as_index=False)["cost"]
            .sum()
            .sort_values("month")
        )

        service_cost = (
            data.groupby("service", as_index=False)["cost"]
            .sum()
            .sort_values(by="cost", ascending=False)
        )

        department_cost = (
            data.groupby("department", as_index=False)["cost"]
            .sum()
            .sort_values(by="cost", ascending=False)
        )

        stopped_resources = data[
            (data["resource_status"].str.lower() == "stopped")
            & (data["cost"] > 0)
        ].sort_values(by="cost", ascending=False)

        low_utilization_resources = data[
            data["utilization_efficiency_pct"] < 30
        ].sort_values(by="cost", ascending=False)

        result = {
            "monthly_cost": monthly_cost,
            "service_cost": service_cost,
            "department_cost": department_cost,
            "stopped_resources": stopped_resources,
            "low_utilization_resources": low_utilization_resources,
        }

        logger.info(
            "Cost analysis completed successfully: %s records, total cost %.2f",
            len(data),
            data["cost"].sum(),
        )

        return result

    except Exception as error:
        logger.exception("Cost analysis failed")
        raise CustomException(error) from error