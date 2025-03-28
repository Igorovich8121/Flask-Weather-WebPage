from flask import Flask, render_template, request, redirect, url_for
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from peewee import SqliteDatabase, Model, FloatField, DateField

# Inicializē Flask un datubāzi
app = Flask(__name__)
DATABASE = "weather_data.db"
db = SqliteDatabase(DATABASE)

# Datubāzes modelis
class Weather(Model):
    date = DateField()
    temperature = FloatField()
    humidity = FloatField()
    wind_speed = FloatField()

    class Meta:
        database = db

# Izveido tabulu
db.connect()
db.create_tables([Weather], safe=True)

# Mājaslapa
@app.route('/')
def index():
    return render_template('index.html')

# CSV augšupielāde un datu saglabāšana datubāzē
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    df = pd.read_csv(file)
    for _, row in df.iterrows():
        Weather.create(
            date=row['date'],
            temperature=row['temperature'],
            humidity=row['humidity'],
            wind_speed=row['wind_speed']
        )

    return redirect(url_for('dashboard'))

# Datu vizualizācija
@app.route('/dashboard')
def dashboard():
    data = pd.DataFrame(list(Weather.select().dicts()))

    if not data.empty:
        # Izveido grafiku mapi
        os.makedirs("static/graphs", exist_ok=True)

        # Līniju grafiks (temperatūra)
        plt.figure(figsize=(8, 5))
        sns.lineplot(x=data['date'], y=data['temperature'], marker='o')
        plt.xticks(rotation=45)
        plt.title("Temperature Trends")
        plt.xlabel("Date")
        plt.ylabel("Temperature (°C)")
        plt.grid()
        plt.savefig("static/graphs/temp_chart.png")
        plt.close()

        # Histogramma
        plt.figure(figsize=(8, 5))
        sns.histplot(data['temperature'], bins=10, kde=True, color="blue")
        plt.title("Temperature Distribution")
        plt.xlabel("Temperature (°C)")
        plt.ylabel("Frequency")
        plt.grid()
        plt.savefig("static/graphs/histogram.png")
        plt.close()

        # Kastes diagramma
        plt.figure(figsize=(6, 5))
        sns.boxplot(y=data['humidity'], color="green")
        plt.title("Humidity Analysis")
        plt.ylabel("Humidity (%)")
        plt.grid()
        plt.savefig("static/graphs/boxplot.png")
        plt.close()

    return render_template("dashboard.html")

# Flask servera palaišana
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
