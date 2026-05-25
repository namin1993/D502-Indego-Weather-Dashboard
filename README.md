## README

### Project Overview:
1.) Is there a correlation between weather variables such as temperature, wind speed, and humidity and the demand of Indego Bikes?

2.) Is there also any noticeable differences in maximum time duration and common start/end stations used between different passholders?

### Datasets
* **OpenWeather API**
	**URL:** https://openweathermap.org/
	**Description:** Daily historical weather data through REST API format.
	**Owner:** OpenWeather, a London-based weather intelligence company serving enterprises, developers, businesses, and researchers worldwide. Through its developer business, the company provides global weather data and forecasting services via fast, reliable APIs, delivering historical, current, and forecast weather data for any location worldwide.

* **Indego Bike Data**
	**URL:** https://www.rideindego.com/about/data/
	**Description:** CSV data for indego-trips-2025-q2.csv
	**Owner:** Office of Transportation and Infrastructure Systems (OTIS) in the City of Philadelphia. Indego itself is an initiative of the City of Philadelphia, which owns the bicycles and stations.

### API Key Requirements for config.py
* MongoDB Username, Password, and API Key
* OpenWeather API Key

### Project Deployment Instructions
1.) Clone the github repository:

```git clone https://github.com/namin1993/D502_Capstone_Project.git```

2.) Navigate to the directory through your terminal and create a virtual environment. 

* Using Conda (you can create a virutal environment and install all packages in the requirements.txt file at the same time)

```conda create --name <virtualenv_name> --file requirements.txt```
```conda activate <virtualenv_name>```

* Using Python:

```virtualenv -p /usr/bin/python3.7.13 virtualenv_name source virtualenv_name/bin/activate```
```pip install -r requirements.txt```

3.) Run the application locally

```python app.py```

### Correlation Analysis
The first row of the correlation table measures how strongly the total number of bikes rented per day (bikes_rented) is related to each weather variable: temperature in Fahrenheit (temp_f), humidity (humidity), and wind speed (wind_speed). A correlation value ranges from -1 to +1, where values closer to +1 indicate a strong positive relationship (as one variable increases, the other also increases), values closer to -1 indicate a strong negative relationship (as one increases, the other decreases), and values near 0 indicate little to no linear relationship. 

The value of 1.000 between bikes_rented and itself is expected because every variable has a perfect positive correlation with itself.

* bikes_rented and temp_f is **0.265**: Indicates a **weak positive relationship** between both variables. Warmer days may be associated with slightly higher bike usage, but temperature alone is not a strong predictor of demand.
* bikes_rented and humidity is **0.000**: Indicates a **no measurable linear relationship** between both variables. Humidity does not appear to significantly influence ridership patterns during this Q2 period.
* bikes_rented and wind_speed is **0.037**: Indicates a **very weak positive relationship** between both variables. Wind speed had little to no observable impact on daily bike rentals.

Overall, the table suggests that among the three weather features, temperature has the strongest influence on bike demand, but even that relationship is fairly weak, implying that other factors such as weekday vs. weekend travel, commuting habits, station location, or rider subscription type likely play a much larger role in predicting Indego bike usage.

### Linear Regression Analysis
A Linear Regression Model was selected for this project because the goal was to understand whether there was a measurable relationship between continuous weather variables—temperature, humidity, and wind speed—and the continuous target variable, daily Indego bike rentals. 

Linear regression is useful when the objective is not just prediction, but also interpretation. It allows us to clearly measure how much each weather factor increases or decreases bike demand through easily understandable coefficients, while also providing statistical metrics like R² and Mean Absolute Error to evaluate model performance.

* **R²: 0.2647** - Approximately 26.5% of the variation in daily bike rentals can be explained by these three weather variables alone, while the remaining 73.5% is influenced by other factors not included in the model.

* **Mean Absolute Error: 636.45** - On average, the model’s daily bike rental prediction is off by about 636 rentals per day. This is reasonable considering the average daily ridership is around 4,000 bikes and suggests the model is useful for identifying general trends rather than exact daily counts.

* **Intercept Value: 4018.52** - The model’s baseline prediction when all standardized weather variables are at their average values—in other words, under typical Q2 weather conditions, the model expects roughly 4,019 bike rentals per day.

* **Coefficients: How each weather variable affects ridership relative to that baseline.**
	* **Temp_f: 1050.176** - Warmer than average days are associated with higher bike rentals; as temperature increases, ridership tends to rise significantly

	* **Humidity: -149.150** - More humid days are associated with slightly fewer rentals, suggesting people may be less likely to bike in muggy conditions

	* **Wind Speed: -1004.721** - Stronger winds are linked to a substantial decrease in bike rentals, likely because windy conditions make biking less comfortable

Temperature has the strongest positive influence on demand. Wind speed has the strongest negative influence. Humidity having a smaller negative effect.

Additionally, linear regression works well as a strong baseline model because it is simpler, faster, and easier to explain compared to more complex models like Random Forest or XGBoost. It further supports the correlation analysis above by determining whether the relationship between weather and bike demand is positive, negative, or weak.

### P-Value Analysis
The **intercept** in the linear regression model represents the model’s baseline prediction for the number of bikes rented when all predictor variables are at their standardized average values. Because the model uses `StandardScaler()`, the predictors (`temp_f`, `humidity`, and `wind_speed`) were transformed so that their averages are centered around zero. This means the intercept represents the estimated average daily bike rentals under “typical” weather conditions during the Q2 dataset period. The extremely small p-value for the intercept (`2.02 × 10⁻⁶⁴`) indicates that the intercept is statistically significant, meaning the baseline rental level is different from zero and is an important part of the regression equation.

The p-values for the weather variables determine whether each variable has a statistically significant relationship with the number of bikes rented per day. The threshold for significance in this experiment is **0.05**:

* **Temperature (`temp_f`)** has a p-value of `2.84 × 10⁻⁷`, which is far below 0.05. This means temperature has a **strong statistically significant relationship** with bike rentals. Warmer temperatures are very likely associated with changes in bike demand rather than the relationship occurring by random chance.
* **Humidity** has a p-value of `0.239`, which is greater than 0.05. This means humidity is **not statistically significant** in this model. Although humidity may still have a small effect on ridership, the model does not provide strong enough evidence to conclude that humidity meaningfully impacts bike rentals during this time period.
* **Wind speed** has a p-value of `2.89 × 10⁻⁵`, which is also far below 0.05. This indicates wind speed has a **statistically significant relationship** with bike demand. Since the regression coefficient for wind speed was negative, this suggests that stronger winds are associated with fewer bike rentals.

Overall, the statistical significance testing shows that among the three weather variables, **temperature and wind speed were significant predictors of Indego bike demand**, while humidity was not statistically significant in explaining variations in daily ridership for the Q2 2025 dataset.


### Analysis on Passholder's
Each of the 4 charts listed on the "/passholder-analytics" webpage depict certain differences in the behaviors of different Indego passholder's. 

Important Note: The reason that the information is presented in tabular format instead of as bar graphs is because when I attempted to present the data as a bar graph through plotly's library methods in the app.py code, the actual columns of the bar graph would either not appear at all or would display the data incorrectly despite the df.groupby() function having correct parameters.

#### **Chart 1: Trip Duration by Passholder Type**
---
The most popular amount of time in minutes spent on using an Indego bicycle according to each passholder are as follows: 
* Daypass: 1 minute
* Indego30: 7 minutes
* Indego365: 7 minutes
* IndegoFlex: 3 minutes
* Walk-Up: 10 minutes

In order to encourage longer rental periods, frequent bike usage, and an upgrade to certain passholder tiers, special discount rates might be applied depending on the minutes accrued per trip or cumulatively depending on the passholder type.

#### **Chart 2: Bike Type Rentals by Passholder Type**
---
The most popular type of Indego bicycle according to each passholder are as follows: 
* Daypass: Electric
* Indego30: Electric
* Indego365: Electric
* IndegoFlex: Standard
* Walk-Up: Electric

Across the board, with exception to 1 IndegoFlex rider, the Electric bike is preferred. Therefore, given the time period from April - July, more electric bikes should be available and maintained in order to guarantee an increase in the number of passholders using the Indego bike system.

#### **Chart 3: Top 10 Start Stations**
---
The most popular Start Station out of the top 10 Start Stations according to each passholder are as follows: 
* Daypass: 3185
* Indego30: 3010
* Indego365: 3010
* IndegoFlex: 3359
* Walk-Up: 3163

#### **Chart 4: Top 10 End Stations**
---
The most popular End Station out of the top 10 End Stations according to each passholder are as follows: 
* Daypass: 3000
* Indego30: 3000
* Indego365: 3020
* IndegoFlex: N/A
* Walk-Up: 3000

### File and Directory Descriptions
**Dataset:** Directory containing the Indego Q2 2025 CSV dataset.

**weather_cache_q2.json:** JSON file containing data from OpenWeather API data call in the "Indego - ETL Process.ipynb"

**Indego - ETL Process.ipynb:** Jupyter Notebook script for uploading OpenWeather API data and Indego Q2 2025 data onto the Cloud MongoDB account.

**db_connections.py:** Python script for connecting to the MongoDB account.

**ml_model.py:** Python script for creating a correlation table and a linear regression analysis from the dataset stored on MongoDB.

**app.py:** Flask script for creating the Indego-Weather application.

**templates:** Directory for html templates for the Flask application.

### Project Links
**Github Repository:** [D502-Indego-Weather-Dashboard](https://github.com/namin1993/D502-Indego-Weather-Dashboard)

**Webpage:**





start_lat & start_lon - 3 missing rows where start_station is 3000
end_lat & end_lon - missing 6139 where end_station is 3000

365760 rows

https://www.linkedin.com/pulse/exploratory-analysis-philadelphias-indego-bike-share-armstrong/

Jupyter Notebook:
> Extract Data
*Connect to Openweather API
*Convert Indego bike data to dataframe

> Transform Data
*Fill in blank values where station is 3000

* Seperate start time and end time columns as seperate start_date, start_time, end_date, end_time columns

* Use start_Longitude, start_Latitude, and start_date to call WeatherAPI data and make weather dataframe

* Combine weather data columns to Indego dataframe
23100 - 45 minutes



Can you create:
1.) Plotly bar graph measuring the total duration of each trip to the total number of each passholder_type
2.) Plotly bar graph comparing number of each passholder_type to the amount of bike_type rented for the entire months of the Q2 dataset
3.) Plotly graph measuring the total number of each passholder_type to each start_station
4.) Plotly graph measuring the total number of each passholder_type to each end_station
