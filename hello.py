# pollution_data.py
import requests
import json

def get_pollution_data():
    url = (
        "https://namek.airparif.fr/geoserver/prev_horair/wms?"
        "SERVICE=WMS&VERSION=1.1.1&REQUEST=GetFeatureInfo&"
        "QUERY_LAYERS=prev_horair%3Aindice%2Cprev_horair%3AO3%2Cprev_horair%3ANO2%2Cprev_horair%3APM10%2Cprev_horair%3APM25%2Cprev_horair%3AcommunesIDF&"
        "LAYERS=prev_horair%3Aindice%2Cprev_horair%3AO3%2Cprev_horair%3ANO2%2Cprev_horair%3APM10%2Cprev_horair%3APM25%2Cprev_horair%3AcommunesIDF&"
        "INFO_FORMAT=application/json&FEATURE_COUNT=50&Y=50&X=70&SRS=EPSG%3A27572&WIDTH=101&HEIGHT=101&"
        "BBOX=595114.0466738944%2C2419223.466502076%2C595214.0466738944%2C2419323.466502076"
    )

    pollution_data = {
        'indice': 'Non disponible',
        'O3': 'Non disponible',
        'NO2': 'Non disponible',
        'PM10': 'Non disponible',
        'PM25': 'Non disponible'
    }

    try:
        # Fetch data from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP status codes

        # Load the response content as JSON
        data = response.json()

        # Extract values and populate the dictionary
        gray_index_values = []
        for feature in data.get("features", []):
            properties = feature.get("properties", {})
            gray_index = properties.get("GRAY_INDEX")
            if gray_index is not None:
                gray_index_values.append(gray_index)

        # Update the pollution data dictionary with extracted values
        pollution_types = ['indice', 'O3', 'NO2', 'PM10', 'PM25']
        for i, value in enumerate(gray_index_values):
            if i < len(pollution_types):
                pollution_data[pollution_types[i]] = value

    except requests.RequestException as e:
        print(f"HTTP Request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")

    return pollution_data

# Example usage
if __name__ == "__main__":
    data = get_pollution_data()
    print("Pollution Data:")
    print(data)