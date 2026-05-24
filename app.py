# Import Dependencies
from flask import Flask, render_template, request
import plotly
import plotly.express as px
import json
import pandas as pd
import ml_model


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    error_message = None

    form_values = {
        "temp_f": "",
        "humidity": "",
        "wind_speed": ""
    }

    # Build correlation table
    corr_df = ml_model.get_correlation_table()
    corr_table = corr_df.round(3).to_html(
        classes="table table-striped table-bordered",
        index=True
    ) if not corr_df.empty else "<p>No correlation data available.</p>"

    # Train model and get metrics
    model, scaler, daily_df, metrics = ml_model.train_bike_rental_model()


    # Get observed input ranges from training data
    input_ranges = None

    if daily_df is not None and not daily_df.empty:
        input_ranges = {
            "temp_f_min": round(daily_df["temp_f"].min(), 2),
            "temp_f_max": round(daily_df["temp_f"].max(), 2),
            "humidity_min": round(daily_df["humidity"].min(), 2),
            "humidity_max": round(daily_df["humidity"].max(), 2),
            "wind_speed_min": round(daily_df["wind_speed"].min(), 3),
            "wind_speed_max": round(daily_df["wind_speed"].max(), 3),
        }

    if request.method == "POST":
        try:
            temp_f = float(request.form["temp_f"])
            humidity = float(request.form["humidity"])
            wind_speed = float(request.form["wind_speed"])

            form_values["temp_f"] = temp_f
            form_values["humidity"] = humidity
            form_values["wind_speed"] = wind_speed

            if model is None or scaler is None:
                error_message = "The model is not available yet. Please check your MongoDB data."
            else:
                # Warning for out-of-range values
                if input_ranges:
                    if not (input_ranges["temp_f_min"] <= temp_f <= input_ranges["temp_f_max"]):
                        error_message = "Temperature is outside the observed training range. Prediction may be unreliable."
                    elif not (input_ranges["humidity_min"] <= humidity <= input_ranges["humidity_max"]):
                        error_message = "Humidity is outside the observed training range. Prediction may be unreliable."
                    elif not (input_ranges["wind_speed_min"] <= wind_speed <= input_ranges["wind_speed_max"]):
                        error_message = "Wind speed is outside the observed training range. Prediction may be unreliable."

                prediction = ml_model.predict_bikes_rented(
                    temp_f=temp_f,
                    humidity=humidity,
                    wind_speed=wind_speed
                )

        except ValueError:
            prediction = "Invalid input. Please enter numeric values."

    return render_template(
        "index.html",
        corr_table=corr_table,
        prediction=prediction,
        metrics=metrics,
        form_values=form_values,
        input_ranges=input_ranges,
        error_message=error_message
    )

@app.route("/passholder-analysis")
def trip_analysis():
    # Load data from MongoDB
    df = ml_model.load_indego_weather_data()

    # Convert key columns
    df["duration"] = pd.to_numeric(df["duration"], errors="coerce")

    # Drop rows missing important fields
    df = df.dropna(subset=[
        "passholder_type",
        "bike_type",
        "duration",
        "start_station",
        "end_station"
    ])

    # 1. Total trip duration by passholder type
    duration_counts = (
        df.groupby(["duration", "passholder_type"])
        .size()
        .reset_index(name="trip_count")
    )

    # Pivot into table format
    duration_table = duration_counts.pivot_table(
        index="duration",
        columns="passholder_type",
        values="trip_count",
        fill_value=0
    ).reset_index().sort_values("duration")

    # Convert dataframe to HTML table
    duration_table_html = duration_table.to_html(
        classes="table table-striped table-bordered",
        index=False
    )

    '''
    print(duration_counts.shape)
    print(duration_counts.head(10))

    # Create grouped bar chart
    fig1 = px.bar(
        duration_counts,
        x="duration",
        y="trip_count",
        color="passholder_type",
        barmode="group",
        title="Trip Duration by Passholder Type",
        labels={
            "duration_minutes": "Trip Duration (Minutes)",
            "trip_count": "Number of Bike Rentals",
            "passholder_type": "Passholder Type"
        }
    )
    '''

    # 2. Bike type rentals by passholder type
    bike_by_passholder = (
        df.groupby(["passholder_type", "bike_type"])
        .size()
        .reset_index(name="rental_count")
    )

    # Pivot into table format
    bike_by_passholder_table = bike_by_passholder.pivot_table(
        index="passholder_type",
        columns="bike_type",
        values="rental_count",
        fill_value=0
    ).reset_index()

    # Convert dataframe to HTML table
    bike_by_passholder_table_html = bike_by_passholder_table.to_html(
        classes="table table-striped table-bordered",
        index=False
    )

    '''
    print(bike_by_passholder.shape)
    print(bike_by_passholder.head(10))

    fig2 = px.bar(
        bike_by_passholder,
        x="passholder_type",
        y="rental_count",
        color="bike_type",
        barmode="group",
        title="Bike Type Rentals by Passholder Type",
        labels={
            "passholder_type": "Passholder Type",
            "rental_count": "Number of Rentals",
            "bike_type": "Bike Type"
        }
    )
    '''

    # 3. Start station usage by passholder type
    # Limit to top 10 stations so graph is readable
    top_start_stations = (
        df["start_station"]
        .value_counts()
        .head(10)
        .index
    )

    start_station_df = (
        df[df["start_station"].isin(top_start_stations)]
        .groupby(["start_station", "passholder_type"])
        .size()
        .reset_index(name="trip_count")
    )

    # Pivot into table format
    start_station_df_table = start_station_df.pivot_table(
        index="start_station",
        columns="passholder_type",
        values="trip_count",
        fill_value=0
    ).reset_index()

    # Convert dataframe to HTML table
    start_station_df_table_html = start_station_df_table.to_html(
        classes="table table-striped table-bordered",
        index=False
    )

    '''
    fig3 = px.bar(
        start_station_df,
        x="start_station",
        y="trip_count",
        color="passholder_type",
        barmode="group",
        title="Top 10 Start Stations by Passholder Type",
        labels={
            "start_station": "Start Station",
            "trip_count": "Number of Trips",
            "passholder_type": "Passholder Type"
        }
    )    
    '''


    # 4. End station usage by passholder type
    # Limit to top 10 stations so graph is readable
    top_end_stations = (
        df["end_station"]
        .value_counts()
        .head(10)
        .index
    )

    end_station_df = (
        df[df["end_station"].isin(top_end_stations)]
        .groupby(["end_station", "passholder_type"])
        .size()
        .reset_index(name="trip_count")
    )

    # Pivot into table format
    end_station_df_table = end_station_df.pivot_table(
        index="end_station",
        columns="passholder_type",
        values="trip_count",
        fill_value=0
    ).reset_index()

    # Convert dataframe to HTML table
    end_station_df_table_html = end_station_df_table.to_html(
        classes="table table-striped table-bordered",
        index=False
    )

    '''
    fig4 = px.bar(
        end_station_df,
        x="end_station",
        y="trip_count",
        color="passholder_type",
        barmode="group",
        title="Top 10 End Stations by Passholder Type",
        labels={
            "end_station": "End Station",
            "trip_count": "Number of Trips",
            "passholder_type": "Passholder Type"
        }
    )
    '''

    #graph1JSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    #graph2JSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    #graph3JSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    #graph4JSON = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        "passholder_analysis.html",
        duration_table=duration_table_html,
        bike_by_passholder_table = bike_by_passholder_table_html,
        start_station_df_table = start_station_df_table_html,
        end_station_df_table = end_station_df_table_html
        #graph1JSON=graph1JSON,
        #graph2JSON=graph2JSON,
        #graph3JSON=graph3JSON,
        #graph4JSON=graph4JSON
    )

if __name__ == "__main__":
    app.run(debug=True)