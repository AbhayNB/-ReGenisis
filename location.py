# importing modules
from geopy.geocoders import Nominatim
import geocoder

# Get the current location using the 'geocoder' library
location = geocoder.ip('me')

# Access latitude and longitude
user_latitude = location.latlng[0]
user_longitude = location.latlng[1]

print(f"Latitude: {user_latitude}")
print(f"Longitude: {user_longitude}")

# Create a Nominatim geocoder instance
geoLoc = Nominatim(user_agent="GetLoc")

# Reverse geocode the coordinates
location_info = geoLoc.reverse((user_latitude, user_longitude), exactly_one=True)

# Print the address/location name
if location_info:
    print("Address:", location_info.address)
else:
    print("Unable to retrieve location information.")
