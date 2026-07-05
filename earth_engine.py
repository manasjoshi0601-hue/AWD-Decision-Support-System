import ee
from datetime import datetime, timedelta, timezone

# Connect to Google Earth Engine
def connect():
    ee.Initialize(project="awd-rice-cultivation")
    print("✅ Google Earth Engine connected successfully!")


# Return the field polygon
def get_field():
    return ee.Geometry.Polygon([
        [
             [74.88658200500413, 31.458207426754445],
             [74.88658200500413, 31.456582946319035],
             [74.88933931587144, 31.456514305680198],
             [74.88939296005174, 31.458134211341168]
        ]
    ])


# Calculate field area
def get_field_area():
    field = get_field()
    area = field.area().divide(10000)
    return area.getInfo()


# Get Sentinel-2 collection
def get_sentinel2_collection():
    """Returns Sentinel-2 images from the last 30 days."""

    field = get_field()

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(field)
        .filterDate(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
    )

    return collection


def get_latest_sentinel2():
    """Returns the latest Sentinel-2 image."""

    collection = get_sentinel2_collection()

    latest = collection.sort("system:time_start", False).first()

    return latest


def get_sentinel2_metadata():
    """
    Returns all Sentinel-2 information required
    for the AWD model.
    """

    image = get_latest_sentinel2()

    date = (
        ee.Date(image.get("system:time_start"))
        .format("YYYY-MM-dd HH:mm:ss")
        .getInfo()
    )

    tile_cloud = image.get("CLOUDY_PIXEL_PERCENTAGE").getInfo()

    aoi_cloud = get_aoi_cloud(image)

    data = {
        "date": date,
        "tile_cloud": tile_cloud,
        "aoi_cloud": aoi_cloud
    }

    if aoi_cloud > 20:
        data["usable"] = False
        data["ndvi"] = None
        data["lswi"] = None
    else:
        data["usable"] = True
        data["ndvi"] = calculate_ndvi(image)
        data["lswi"] = calculate_lswi(image)

    return data


def get_sentinel1_collection():
    """
    Returns Sentinel-1 images from the last 30 days.
    """

    field = get_field()

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=30)

    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filterBounds(field)
        .filterDate(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation",
                "VV"
            )
        )
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation",
                "VH"
            )
        )
    )

    return collection


def get_latest_sentinel1():
    """
    Returns the latest Sentinel-1 image.
    """

    collection = get_sentinel1_collection()

    return collection.sort("system:time_start", False).first()


def calculate_vv(image):
    """
    Calculates mean VV over the field.
    """

    field = get_field()

    value = image.select("VV").reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=field,
        scale=10,
        maxPixels=1e9
    ).get("VV")

    return ee.Number(value).getInfo()


def calculate_vh(image):
    """
    Calculates mean VH over the field.
    """

    field = get_field()

    value = image.select("VH").reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=field,
        scale=10,
        maxPixels=1e9
    ).get("VH")

    return ee.Number(value).getInfo()


def get_sentinel1_metadata():
    """
    Returns all Sentinel-1 information.
    """

    image = get_latest_sentinel1()

    date = (
        ee.Date(image.get("system:time_start"))
        .format("YYYY-MM-dd HH:mm:ss")
        .getInfo()
    )

    return {
        "date": date,
        "vv": calculate_vv(image),
        "vh": calculate_vh(image)
    }

    # Ignore Sentinel-2 if AOI is too cloudy
    if aoi_cloud > 20:
        data["usable"] = False
        data["ndvi"] = None
        data["lswi"] = None
    else:
        data["usable"] = True
        data["ndvi"] = calculate_ndvi()
        data["lswi"] = calculate_lswi()

    return data


def get_aoi_cloud(image):
    """
    Calculates AOI cloud percentage using the
    Sentinel-2 Scene Classification Layer (SCL).
    """

    field = get_field()

    scl = image.select("SCL")

    cloud_mask = (
        scl.eq(7)
        .Or(scl.eq(8))
        .Or(scl.eq(9))
        .Or(scl.eq(10))
    )

    cloud_percentage = (
        cloud_mask.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=field,
            scale=10,
            maxPixels=1e9
        ).get("SCL")
    )

    return ee.Number(cloud_percentage).multiply(100).getInfo()


def calculate_ndvi(image):
    """
    Calculates mean NDVI over the field.
    """

    field = get_field()

    ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")

    value = ndvi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=field,
        scale=10,
        maxPixels=1e9
    ).get("NDVI")

    return ee.Number(value).getInfo()


def calculate_lswi(image):
    """
    Calculates mean LSWI over the field.
    """

    field = get_field()

    lswi = image.normalizedDifference(["B8", "B11"]).rename("LSWI")

    value = lswi.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=field,
        scale=10,
        maxPixels=1e9
    ).get("LSWI")

    return ee.Number(value).getInfo()


def get_field_center():
    """
    Returns the centre coordinates of the field.
    """

    field = get_field()

    centroid = field.centroid()

    coordinates = centroid.coordinates().getInfo()

    longitude = coordinates[0]
    latitude = coordinates[1]

    return latitude, longitude