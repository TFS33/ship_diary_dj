import requests
import json

# user_ip = "your_ip"
#
ABSTRACT_GEO_KEY = "API_KEY"
#
# response = requests.get(
#     "https://ipgeolocation.abstractapi.com/v1/?api_key=" + ABSTRACT_GEO_KEY + "&ip_address=" + user_ip)
#
# response = response.text
#
# tekstas = json.loads(response)
#
#
# # print(tekstas["city"])
# # print(tekstas)


def get_location():
    user_ip = "IP"
    ABSTRACT_GEO_KEY = "KEY"

    response = requests.get(
        f"https://ipgeolocation.abstractapi.com/v1/?api_key={ABSTRACT_GEO_KEY}&ip_address={user_ip}"
    )

    all_data = json.loads(response.text)
    print("Full API response:")
    print(json.dumps(all_data, indent=2))

    # Attempt to print specific fields if they exist
    print("\nAttempting to access specific fields:")
    print("City:", all_data.get("city", "Not found"))
    print("Longitude:", all_data.get("longitude", "Not found"))
    print("Latitude:", all_data.get("latitude", "Not found"))


get_location()
