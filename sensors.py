def get_sensor_data():
    """
    Returns sensor readings for the AWD model.

    Currently, values are entered manually.
    Later, these inputs will be replaced with
    real sensor readings from the hardware.
    """

    print("\nEnter Sensor Readings")
    print("----------------------")

    soil_moisture = float(
        input("Soil Moisture (%): ")
    )

    water_level = float(
        input("Water Level (cm): ")
    )

    soil_tension = float(
        input("Soil Water Tension (kPa): ")
    )

    return {

        "soil_moisture": soil_moisture,

        "water_level": water_level,

        "soil_tension": soil_tension

    }