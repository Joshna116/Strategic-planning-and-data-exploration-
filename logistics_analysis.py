import pandas as pd
import numpy as np

def load_and_prepare(path="logistics_orders.csv"):
    df = pd.read_csv(path)
    date_cols = ["Order_Date", "Promised_Date", "Delivery_Date"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if {"Delivery_Date", "Order_Date"}.issubset(df.columns):
        df["Delivery_Days"] = (df["Delivery_Date"] - df["Order_Date"]).dt.days

    if {"Delivery_Date", "Promised_Date"}.issubset(df.columns):
        df["Delay_Days"] = (df["Delivery_Date"] - df["Promised_Date"]).dt.days
        df["On_Time"] = np.where(df["Delay_Days"] <= 0, 1, 0)

    if {"Inventory_Available", "Quantity"}.issubset(df.columns):
        df["Stockout"] = np.where(df["Inventory_Available"] < df["Quantity"], 1, 0)

    return df

def calculate_kpis(df):
    result = {}
    if "On_Time" in df:
        result["on_time_delivery_rate"] = round(df["On_Time"].mean() * 100, 2)
    if "Delivery_Days" in df:
        result["average_delivery_days"] = round(df["Delivery_Days"].mean(), 2)
    if "Stockout" in df:
        result["stockout_rate"] = round(df["Stockout"].mean() * 100, 2)
    if "Delivery_Cost" in df:
        result["average_delivery_cost"] = round(df["Delivery_Cost"].mean(), 2)
    return result

def warehouse_summary(df):
    required = {"Warehouse_ID", "On_Time", "Delivery_Days", "Stockout"}
    if not required.issubset(df.columns):
        return pd.DataFrame()

    summary = (
        df.groupby("Warehouse_ID")
          .agg(On_Time_Rate=("On_Time", "mean"),
               Avg_Delivery_Days=("Delivery_Days", "mean"),
               Stockout_Rate=("Stockout", "mean"))
          .reset_index()
    )
    summary["On_Time_Rate"] *= 100
    summary["Stockout_Rate"] *= 100
    return summary.sort_values("On_Time_Rate")

if __name__ == "__main__":
    # Replace with the actual public/internship dataset path.
    df = load_and_prepare("logistics_orders.csv")
    print("Overall KPIs:", calculate_kpis(df))
    print("\nWarehouse summary:")
    print(warehouse_summary(df))
