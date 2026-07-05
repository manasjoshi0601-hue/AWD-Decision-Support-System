import streamlit as st
import decision_engine
import weather
import earth_engine


# -----------------------------------
# Connect Google Earth Engine
# -----------------------------------

earth_engine.connect()

# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="AWD Decision Support System",
    page_icon="🌾",
    layout="wide"
)

# -----------------------------------
# Title
# -----------------------------------

st.title("🌾 AWD Decision Support System")

st.caption(
    "AI-powered irrigation recommendation system using field sensors, "
    "weather forecasts and satellite observations."
)

# ===================================
# Sidebar
# ===================================

st.sidebar.header("🌾 Farmer Inputs")

transplant_date = st.sidebar.date_input(
    "Transplant Date"
)

rice_variety = st.sidebar.selectbox(
    "Rice Variety",
    [
        "PR-126",
        "PR-121",
        "Pusa-44"
    ]
)

soil_moisture = st.sidebar.slider(
    "Soil Moisture (%)",
    0,
    100,
    25
)

water_level = st.sidebar.slider(
    "Water Level (cm)",
    -20,
    5,
    -10
)

soil_tension = st.sidebar.slider(
    "Soil Water Tension (kPa)",
    0,
    40,
    15
)

generate = st.sidebar.button(
    "🚀 Generate Recommendation"
)

# ===================================
# Prepare Input Dictionaries
# ===================================

farmer_data = {

    "transplant_date": transplant_date,
    "rice_variety": rice_variety

}

sensor_data = {

    "soil_moisture": soil_moisture,
    "water_level": water_level,
    "soil_tension": soil_tension

}

# ===================================
# Backend
# ===================================

if generate:

    weather_data = weather.get_weather_data()

    field_area = earth_engine.get_field_area()

    latitude, longitude = earth_engine.get_field_center()

    s2 = earth_engine.get_sentinel2_metadata()

    s1 = earth_engine.get_sentinel1_metadata()

    results = decision_engine.run_model(
        farmer_data,
        sensor_data,
        weather_data,
        s2,
        s1,
        field_area,
        latitude,
        longitude
    )

# ===================================
# Dashboard
# ===================================

st.divider()

weather_col, satellite_col = st.columns(2)

# ===================================
# Weather
# ===================================

with weather_col:

    st.subheader("🌦 Weather")

    c1, c2, c3 = st.columns(3)

    if generate:

        c1.metric(
            "Temperature",
            f"{results['weather']['temperature']:.1f} °C"
        )

        c2.metric(
            "ET₀",
            f"{results['weather']['eto']:.2f} mm/day"
        )

        c3.metric(
            "ETc",
            f"{results['potential_etc']:.2f} mm/day"
        )

        st.write("### Rain Forecast")

        r1, r2, r3 = st.columns(3)

        forecast = results["weather"]["forecast"]

        r1.metric("Day 1", f"{forecast['day1']:.1f} mm")
        r2.metric("Day 2", f"{forecast['day2']:.1f} mm")
        r3.metric("Day 3", f"{forecast['day3']:.1f} mm")

    else:

        c1.metric("Temperature", "-- °C")
        c2.metric("ET₀", "--")
        c3.metric("ETc", "--")

# ===================================
# Satellite
# ===================================

with satellite_col:

    st.subheader("🛰 Satellite")

    if generate:

        a, b = st.columns(2)

        a.metric(
            "NDVI",
            f"{results['s2']['ndvi']:.3f}"
        )

        b.metric(
            "LSWI",
            f"{results['s2']['lswi']:.3f}"
        )

        c, d = st.columns(2)

        c.metric(
            "VV",
            f"{results['s1']['vv']:.2f}"
        )

        d.metric(
            "VH",
            f"{results['s1']['vh']:.2f}"
        )

    else:

        a, b = st.columns(2)

        a.metric("NDVI", "--")

        b.metric("LSWI", "--")

        c, d = st.columns(2)

        c.metric("VV", "--")

        d.metric("VH", "--")
# ===================================
# Sensor Readings
# ===================================

st.divider()

st.subheader("📟 Current Sensor Readings")

c1, c2, c3 = st.columns(3)

if generate:

    c1.metric(
        "Water Level",
        f"{sensor_data['water_level']} cm"
    )

    c2.metric(
        "Soil Moisture",
        f"{sensor_data['soil_moisture']} %"
    )

    c3.metric(
        "Soil Tension",
        f"{sensor_data['soil_tension']} kPa"
    )

else:

    c1.metric("Water Level", "-- cm")
    c2.metric("Soil Moisture", "-- %")
    c3.metric("Soil Tension", "-- kPa")

    # ===================================
# Crop Information
# ===================================

st.divider()

st.subheader("🌾 Crop Information")

if generate:

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Days After Transplanting",
        results["days"]
    )

    c2.metric(
        "Crop Stage",
        results["crop_stage"]
    )

    c3.metric(
        "Crop Coefficient",
        f"{results['kc']:.2f}"
    )

else:

    st.info("Generate a recommendation to view crop information.")

# ===================================
# Field Information
# ===================================

st.divider()

st.subheader("📍 Field Information")

if generate:

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Field Area",
        f"{results['field_area']:.2f} ha"
    )

    c2.metric(
        "Latitude",
        f"{results['latitude']:.4f}"
    )

    c3.metric(
        "Longitude",
        f"{results['longitude']:.4f}"
    )

else:

    st.info("Generate a recommendation to view field information.")

# ===================================
# Satellite Observation
# ===================================

st.divider()

st.subheader("🛰 Satellite Observation")

if generate:

    st.info(
        results["satellite"]["observation"]
    )

else:

    st.info("Generate a recommendation to view satellite observations.")

# ===================================
# Field Status
# ===================================

st.divider()

st.subheader("⚠️ Field Status")

if generate:

    status = results["field_status"]["status"]
    score = results["field_status"]["score"]
    reason = results["field_status"]["reason"]

    if status == "SAFE":

        st.success(
            f"🟢 SAFE\n\nRisk Score: {score}"
        )

    elif status == "ATTENTION":

        st.warning(
            f"🟡 ATTENTION\n\nRisk Score: {score}"
        )

    else:

        st.error(
            f"🔴 CRITICAL\n\nRisk Score: {score}"
        )

    st.write(reason)

else:

    st.info("Generate a recommendation to analyse field status.")

# ===================================
# Final Recommendation
# ===================================

st.divider()

st.subheader("🌾 Final Recommendation")

if generate:

    recommendation = results["decision"]["recommendation"]
    reason = results["decision"]["reason"]

    if recommendation == "NO IRRIGATION REQUIRED":

        st.success(recommendation)

    elif recommendation == "WAIT FOR RAIN":

        st.info(recommendation)

    elif recommendation == "IRRIGATION REQUIRED WITHIN 1–3 DAYS":

        st.warning(recommendation)

    elif recommendation == "IRRIGATE SOON":

        st.warning(recommendation)

    else:

        st.error(recommendation)

    st.write(reason)

else:

    st.info("Generate a recommendation to view the final decision.")