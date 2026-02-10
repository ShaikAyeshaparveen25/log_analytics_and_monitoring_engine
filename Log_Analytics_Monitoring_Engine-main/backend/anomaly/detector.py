import pandas as pd


def detect_anomaly(log_df, z_threshold=3):
    log_df = log_df.rename(columns={
        "Timestamp": "timestamp",
        "Level": "level"
    })

    error_logs = log_df[log_df["level"] == "ERROR"]

    error_pd = error_logs.compute()
    if error_pd.empty:
        return pd.DataFrame()

    error_pd["timestamp"] = pd.to_datetime(error_pd["timestamp"])
    error_pd = error_pd.set_index("timestamp")

    error_counts = (
        error_pd
        .resample("1min")
        .size()
        .rename("error_count")
        .reset_index()
    )

    mean = error_counts["error_count"].mean()
    std = error_counts["error_count"].std()

    if std == 0 or pd.isna(std):
        return pd.DataFrame()

    error_counts["z_score"] = (error_counts["error_count"] - mean) / std
    error_counts["is_anomaly"] = error_counts["z_score"].abs() > z_threshold

    return error_counts[error_counts["is_anomaly"]]
