import earth_engine
import weather
import sensors
import farmer
import decision_engine

earth_engine.connect()

print("=" * 45)
print("      AWD Decision Support System")
print("=" * 45)

print(f"\nField Area: {earth_engine.get_field_area():.2f} hectares")

# -------------------------
# Sentinel-2
# -------------------------

collection = earth_engine.get_sentinel2_collection()

print(f"Number of Sentinel-2 Images: {collection.size().getInfo()}")

s2 = earth_engine.get_sentinel2_metadata()

print("\nSentinel-2")
print("----------------")
print("Date:", s2["date"])
print(f"Tile Cloud: {s2['tile_cloud']:.2f}%")
print(f"AOI Cloud: {s2['aoi_cloud']:.2f}%")

if s2["usable"]:
    print("Status: ✅ Usable")
    print(f"NDVI: {s2['ndvi']:.4f}")
    print(f"LSWI: {s2['lswi']:.4f}")
else:
    print("Status: ❌ Ignored (AOI too cloudy)")

# -------------------------
# Sentinel-1
# -------------------------
s1 = earth_engine.get_sentinel1_metadata()
print("\nSentinel-1")
print("----------------")
print("Date:", s1["date"])
print(f"VV: {s1['vv']:.4f}")
print(f"VH: {s1['vh']:.4f}")


print("\nWeather")
print("----------------")

weather_data = weather.get_weather_data()

print(f"Temperature: {weather_data['temperature']:.1f} °C")
print(f"ET₀: {weather_data['eto']:.2f} mm/day")

print("\nRain Forecast")

print(f"Day 1: {weather_data['forecast']['day1']:.2f} mm")
print(f"Day 2: {weather_data['forecast']['day2']:.2f} mm")
print(f"Day 3: {weather_data['forecast']['day3']:.2f} mm")

latitude, longitude = earth_engine.get_field_center()

print("\nField Center")
print("----------------")
print(f"Latitude : {latitude:.10f}")
print(f"Longitude: {longitude:.10f}")


sensor_data = sensors.get_sensor_data()

print("\nSensor Data")
print("----------------")
print(f"Soil Moisture : {sensor_data['soil_moisture']:.1f}%")
print(f"Water Level   : {sensor_data['water_level']:.1f} cm")
print(f"Soil Tension  : {sensor_data['soil_tension']:.1f} kPa")

farmer_data = farmer.get_farmer_data()

print("\nFarmer Data")
print("----------------")
print(
    "Transplant Date:",
    farmer_data["transplant_date"].strftime("%d-%m-%Y")
)
print("Rice Variety   :", farmer_data["rice_variety"])


days = decision_engine.calculate_days_after_transplanting(farmer_data)

crop_stage = decision_engine.get_crop_stage(days)

kc = decision_engine.get_crop_coefficient(crop_stage)

potential_etc = decision_engine.calculate_potential_etc(
    weather_data,
    kc
)
satellite = decision_engine.analyze_satellite_data(
    s2,
    s1,
    crop_stage
)

print("\nCrop Analysis")
print("----------------")
print(f"Days After Transplanting : {days}")
print(f"Crop Stage              : {crop_stage}")
print(f"Kc                      : {kc:.2f}")
print(f"Potential ETc           : {potential_etc:.2f} mm/day")

field_status = decision_engine.get_field_status(sensor_data)

print("\nField Status")
print("----------------")
print("Status     :", field_status["status"])
print("Risk Score :", field_status["score"])
print("Reason     :", field_status["reason"])

prediction = decision_engine.analyze_rainfall(
    weather_data,
    potential_etc
)

print("\nRainfall Analysis")
print("----------------")

if prediction["rain_helped"]:

    print("Forecast rainfall is sufficient.")

else:

    print("Forecast rainfall is NOT sufficient.")

decision = decision_engine.make_irrigation_decision(
    field_status,
    prediction,
    crop_stage
)

print("\nFinal Recommendation")
print("----------------")
print("Recommendation :", decision["recommendation"])
print("Reason         :", decision["reason"])
print("\nSatellite Observation")
print("----------------")
print("Observation :", satellite["observation"])