# Machine-Learning-Model

# Import Dependencies
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import statsmodels.api as sm
import db_connections


def load_indego_weather_data():
    """
    Load MongoDB collection into a DataFrame.
    """
    db = db_connections.mogodb_client["Final_Project"]
    collection = db["indego_weather"]

    records = list(collection.find({}, {"_id": 0}))
    df = pd.DataFrame(records)

    return df


def prepare_daily_model_data():
    """
    Convert trip-level data into day-level data
    Target = number of bikes rented on that day
    Features = daily avg temp_f, humidity, wind_speed
    """
    df = load_indego_weather_data()

    if df.empty:
        return pd.DataFrame()

    # Make sure start_date is usable
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")

    # Convert weather columns to numeric
    for col in ["temp_f", "humidity", "wind_speed"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows missing key fields
    df = df.dropna(subset=["start_date", "temp_f", "humidity", "wind_speed"])

    # Aggregate to day level
    daily_df = (
        df.groupby(df["start_date"].dt.date)
        .agg(
            bikes_rented=("bike_id", "count"),
            temp_f=("temp_f", "mean"),
            humidity=("humidity", "mean"),
            wind_speed=("wind_speed", "mean")
        )
        .reset_index()
        .rename(columns={"start_date": "date"})
    )

    return daily_df


def get_correlation_table():
    """
    Create a correlation table for display in HTML.
    """
    daily_df = prepare_daily_model_data()

    if daily_df.empty:
        return pd.DataFrame()

    corr_df = daily_df[["bikes_rented", "temp_f", "humidity", "wind_speed"]].corr()

    return corr_df


def train_bike_rental_model():
    """
    Train a linear regression model on daily data.
    """
    daily_df = prepare_daily_model_data()
    
    # Check size of daily_df
    print(daily_df.describe())
    print(daily_df.shape)

    if daily_df.empty:
        return None, None, None, None

    X = daily_df[["temp_f", "humidity", "wind_speed"]]
    y = daily_df["bikes_rented"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LinearRegression()
    model.fit(X_scaled, y)

    predictions = model.predict(X_scaled)

    # Calculateing P-Value
    X_ols = sm.add_constant(X_scaled)
    ols_model = sm.OLS(y, X_ols).fit()

    # Extract p-values
    p_values = {
        "intercept": ols_model.pvalues[0],
        "temp_f": ols_model.pvalues[1],
        "humidity": ols_model.pvalues[2],
        "wind_speed": ols_model.pvalues[3]
    }

    metrics = {
        "r2": r2_score(y, predictions),
        "mae": mean_absolute_error(y, predictions),
        "intercept": model.intercept_,
        "coefficients": dict(zip(X.columns, model.coef_)),
        "p_values": p_values
    }

    # Check metrics
    print(metrics)

    return model, scaler, daily_df, metrics


def predict_bikes_rented(temp_f, humidity, wind_speed):
    """
    Predict bikes rented for a given set of weather inputs.
    """
    model, scaler, _, _ = train_bike_rental_model()

    if model is None:
        return None

    input_df = pd.DataFrame([{
        "temp_f": temp_f,
        "humidity": humidity,
        "wind_speed": wind_speed
    }])

    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)[0]

    # Keep prediction realistic
    return max(0, round(prediction))


def get_daily_preview():
    """
    Optional preview table for sanity checking.
    """
    daily_df = prepare_daily_model_data()
    return daily_df.head(10)