from datetime import datetime


def get_farmer_data():
    """
    Returns farmer and crop information.

    Currently, values are entered manually.
    Later, these inputs can come from a mobile app
    or web interface.
    """

    print("\nEnter Farmer Details")
    print("----------------------")

    transplant_date = input(
        "Transplant Date (DD-MM-YYYY): "
    )

    rice_variety = input(
        "Rice Variety: "
    
    )

    return {

        "transplant_date": datetime.strptime(
            transplant_date,
            "%d-%m-%Y"
        ).date(),

        "rice_variety": rice_variety,


    }