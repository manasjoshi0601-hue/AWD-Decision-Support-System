from datetime import date, timedelta
def calculate_days_after_transplanting(farmer_data):
    """
    Calculates the number of days after transplanting.
    """

    today = date.today()

    transplant_date = farmer_data["transplant_date"]

    days = (today - transplant_date).days

    return days

def get_crop_stage(days_after_transplanting):
    """
    Determines the crop growth stage based on
    days after transplanting.
    """

    if days_after_transplanting <= 15:
        return "Establishment"

    elif days_after_transplanting <= 45:
        return "Vegetative"

    elif days_after_transplanting <= 75:
        return "Reproductive"

    else:
        return "Ripening"
    

def get_crop_coefficient(crop_stage):
    """
    Returns the FAO crop coefficient (Kc)
    for the current crop stage.
    """

    kc_values = {

        "Establishment": 1.05,

        "Vegetative": 1.15,

        "Reproductive": 1.20,

        "Ripening": 0.90

    }

    return kc_values[crop_stage]


def calculate_potential_etc(weather_data, kc):
    """
    Calculates potential crop evapotranspiration.
    """

    eto = weather_data["eto"]

    return eto * kc


def get_field_status(sensor_data):
    """
    Determines the current field status using
    weighted sensor scoring.
    """

    water_level = sensor_data["water_level"]
    soil_tension = sensor_data["soil_tension"]
    soil_moisture = sensor_data["soil_moisture"]

    score = 0

    # ---------------------------------
    # Water Level (Primary Indicator)
    # ---------------------------------

    if water_level <= -15:
        score += 6

    elif water_level <= -10:
        score += 3

    # ---------------------------------
    # Soil Tension
    # ---------------------------------

    if soil_tension >= 20:
        score += 2

    elif soil_tension >= 15:
        score += 1

    # ---------------------------------
    # Soil Moisture
    # ---------------------------------

    if soil_moisture < 20:
        score += 2

    elif soil_moisture <= 25:
        score += 1

    # ---------------------------------
    # Final Status
    # ---------------------------------

    if score >= 6:

        return {
            "status": "CRITICAL",
            "reason": "Field has reached the irrigation threshold.",
            "score": score
        }

    elif score >= 3:

        return {
            "status": "ATTENTION",
            "reason": "Field is approaching the irrigation threshold.",
            "score": score
        }

    else:

        return {
            "status": "SAFE",
            "reason": "Field is within a safe operating range.",
            "score": score
        }


def analyze_rainfall(weather_data, potential_etc):
    """
    Checks whether forecast rainfall is sufficient
    to offset crop water use over the next 3 days.
    """

    forecast = weather_data["forecast"]

    total_effective_rainfall = 0

    for day in ["day1", "day2", "day3"]:

        # Assume 80% of rainfall is effective
        total_effective_rainfall += forecast[day] * 0.8

    # Total crop water requirement for 3 days
    total_crop_water_use = potential_etc * 3

    if total_effective_rainfall >= total_crop_water_use:

        return {
            "rain_helped": True
        }

    else:

        return {
            "rain_helped": False
        }

def make_irrigation_decision(field_status, prediction, crop_stage):
    """
    Generates the final irrigation recommendation.
    """

    status = field_status["status"]

    # ---------------------------------
    # SAFE
    # ---------------------------------

    if status == "SAFE":

        return {
            "recommendation": "NO IRRIGATION REQUIRED",
            "reason": "Field condition is normal. Continue routine monitoring."
        }

    # ---------------------------------
    # ATTENTION
    # ---------------------------------

    elif status == "ATTENTION":

        # Reproductive stage override
        if crop_stage == "Reproductive":

            return {
                "recommendation": "IRRIGATE SOON",
                "reason": (
                    "The crop is currently in the reproductive stage, "
                    "which is highly sensitive to water stress. "
                    "Avoid prolonged drying to protect grain yield."
                )
            }

        # Other growth stages

        if prediction["rain_helped"]:

            return {
                "recommendation": "WAIT FOR RAIN",
                "reason": (
                    "Forecast rainfall is expected to help replenish "
                    "soil moisture. Continue monitoring the field daily."
                )
            }

        else:

         today = date.today()

        start_date = today.strftime("%d %B")
        end_date = (today + timedelta(days=2)).strftime("%d %B")

        return {
 
              "recommendation": "IRRIGATION REQUIRED",

             "reason": (
             f"Recommended irrigation window: "
            f"{start_date} – {end_date}."
    )

            }
            

    # ---------------------------------
    # CRITICAL
    # ---------------------------------

    elif status == "CRITICAL":

        return {
            "recommendation": "IRRIGATE IMMEDIATELY",
            "reason": (
                "The field has reached the AWD irrigation threshold."
            )
        }

def analyze_satellite_data(s2_data, s1_data, crop_stage):
    """
    Analyses satellite data and generates
    a field-wide observation.
    """

    ndvi = s2_data["ndvi"]
    lswi = s2_data["lswi"]
    vv = s1_data["vv"]
    vh = s1_data["vh"]

    score = 0

    # -------------------------
    # NDVI (Vegetation)
    # -------------------------

    if crop_stage == "Establishment":

        if ndvi >= 0.20:
         score += 2
        elif ndvi >= 0.10:
         score += 1

    elif crop_stage == "Vegetative":

        if ndvi >= 0.50:
         score += 2
        elif ndvi >= 0.30:
         score += 1

    elif crop_stage == "Reproductive":

        if ndvi >= 0.65:
         score += 2
        elif ndvi >= 0.45:
         score += 1

    elif crop_stage == "Ripening":

        if ndvi >= 0.40:
         score += 2
        elif ndvi >= 0.20:
          score += 1

    # -------------------------
    # LSWI (Surface Moisture)
    # -------------------------

    if lswi > 0.20:
        score += 2

    elif lswi >= 0.00:
        score += 1

    # -------------------------
    # VV (Radar Moisture)
    # -------------------------

    if vv > -10:
        score += 2

    elif vv >= -15:
        score += 1

    # -------------------------
    # VH (Crop Structure)
    # -------------------------

    if vh > -22:
        score += 2

    elif vh >= -28:
        score += 1

    # -------------------------
    # Final Observation
    # -------------------------

    if score >= 7:

        observation = (
            "Satellite imagery indicates healthy crop "
            "growth and adequate field moisture."
        )

    elif score >= 4:

        observation = (
            "Satellite imagery indicates normal "
            "field conditions."
        )

    else:

        observation = (
            "Satellite imagery indicates drying "
            "field conditions."
        )

    return {

        "score": score,

        "observation": observation

    }
def run_model(
    farmer_data,
    sensor_data,
    weather_data,
    s2,
    s1,
    field_area,
    latitude,
    longitude
):
    """
    Runs the complete AWD decision model and
    returns all results required by the UI.
    """
    days = calculate_days_after_transplanting(
        farmer_data
    )

    crop_stage = get_crop_stage(days)

    kc = get_crop_coefficient(crop_stage)

    potential_etc = calculate_potential_etc(
        weather_data,
        kc
    )

    satellite = analyze_satellite_data(
        s2,
        s1,
        crop_stage
    )

    field_status = get_field_status(
        sensor_data
    )

    prediction = analyze_rainfall(
        weather_data,
        potential_etc
    )

    decision = make_irrigation_decision(
        field_status,
        prediction,
        crop_stage
    )

    return {

        "weather": weather_data,

        "field_area": field_area,

        "latitude": latitude,

        "longitude": longitude,

        "days": days,

        "crop_stage": crop_stage,

        "kc": kc,

        "potential_etc": potential_etc,

        "field_status": field_status,

        "prediction": prediction,

        "satellite": satellite,

        "decision": decision,

        "s2": s2,

        "s1": s1

    }
