from typing import Dict, Any, List


plot_properties: Dict[str, Dict[str, str]] = {
    'Avg_CO2_lowpass': {
        'label': 'Average CO2 lowpass',
        'color': '#039BE5',
        'marker': 'D',
    },
    'Avg_H2S': {
        'label': 'Average H2S',
        'color': '#F44336',
        'marker': '^',
    },
    'Avg_SO2': {
        'label': 'Average SO2',
        'color': '#8BC34A',
        'marker': '*',
    },
    'Avg_CO2_H2S_ratio': {
        'label': 'Average CO2/H2S Ratio',
        'color': '#B00020',
        'marker': 'o',
    },
    'Avg_H2O_CO2_ratio': {
        'label': 'Average H2O/CO2 Ratio',
        'color': '#4527A0',
        'marker': 'o',
    },
    'Avg_H2S_SO2_ratio': {
        'label': 'Average H2S/SO2 Ratio',
        'color': '#1B5E20',
        'marker': 'o',
    },
    'Avg_CO2_SO2_ratio': {
        'label': 'Average CO2/SO2 Ratio',
        'color': '#F57F17',
        'marker': 'o',
    },
    'Avg_CO2_S_tot_ratio': {
        'label': 'Average CO2/S_Total Ratio',
        'color': '#006064',
        'marker': 'o',
    },
}

wind_direction_4: List[Dict[str, Any]] = [
    {
        "direction": "North",
        "code": "N",
        "degree": 0,
        "min_degree": 315,
        "max_degree": 360,
        "range_degree": "315 - 45"
    },
    {
        "direction": "North",
        "code": "N",
        "degree": 0,
        "min_degree": 0,
        "max_degree": 45,
        "range_degree": "315 - 45"
    },
    {
        "direction": "East",
        "code": "E",
        "degree": 90,
        "min_degree": 45,
        "max_degree": 135,
        "range_degree": "45 - 135"
    },
    {
        "direction": "South",
        "code": "S",
        "degree": 180,
        "min_degree": 135,
        "max_degree": 225,
        "range_degree": "135 - 225"
    },
    {
        "direction": "West",
        "code": "W",
        "degree": 270,
        "min_degree": 225,
        "max_degree": 315,
        "range_degree": "225 - 315"
    },
]

wind_direction_8: List[Dict[str, Any]] = [
    {
        "direction": "North",
        "code": "N",
        "degree": 0,
        "min_degree": 337.5,
        "max_degree": 360,
        "range_degree": "337.5 - 22.25"
    },
    {
        "direction": "North",
        "code": "N",
        "degree": 0,
        "min_degree": 0,
        "max_degree": 22.25,
        "range_degree": "337.5 - 22.25"
    },
    {
        "direction": "Northeast",
        "code": "NE",
        "degree": 45,
        "min_degree": 22.25,
        "max_degree": 67.5,
        "range_degree": "22.25 - 67.5"
    },
    {
        "direction": "East",
        "code": "E",
        "degree": 90,
        "min_degree": 67.5,
        "max_degree": 112.5,
        "range_degree": "67.5 - 112.5"
    },
    {
        "direction": "Southeast",
        "code": "SE",
        "degree": 135,
        "min_degree": 112.5,
        "max_degree": 157.5,
        "range_degree": "112.5 - 157.5"
    },
    {
        "direction": "South",
        "code": "S",
        "degree": 180,
        "min_degree": 157.5,
        "max_degree": 202.5,
        "range_degree": "157.5 - 202.5"
    },
    {
        "direction": "Southwest",
        "code": "SW",
        "degree": 225,
        "min_degree": 202.5,
        "max_degree": 247.5,
        "range_degree": "202.5 - 247.5"
    },
    {
        "direction": "West",
        "code": "W",
        "degree": 270,
        "min_degree": 247.5,
        "max_degree": 292.5,
        "range_degree": "247.5 - 292.5"
    },
    {
        "direction": "Northwest",
        "code": "NW",
        "degree": 315,
        "min_degree": 292.5,
        "max_degree": 337.5,
        "range_degree": "292.5 - 337.5"
    },
]

wind_direction_16: List[Dict[str, Any]] = [
    {
        "direction": "North",
        "code": "N",
        "degree": 0,
        "min_degree": 348.75,
        "max_degree": 360,
        "range_degree": "348.75 - 11.25"
    },
    {
        "direction": "North",
        "code": "N",
        "degree": 0,
        "min_degree": 0,
        "max_degree": 11.25,
        "range_degree": "348.75 - 11.25"
    },
    {
        "direction": "North-Northeast",
        "code": "NNE",
        "degree": 22.5,
        "min_degree": 11.25,
        "max_degree": 33.75,
        "range_degree": "11.25 - 33.75"
    },
    {
        "direction": "Northeast",
        "code": "NE",
        "degree": 45,
        "min_degree": 33.75,
        "max_degree": 56.25,
        "range_degree": "33.75 - 56.25"

    },
    {
        "direction": "East-Northeast",
        "code": "ENE",
        "degree": 67.5,
        "min_degree": 56.25,
        "max_degree": 78.75,
        "range_degree": "56.25 - 78.75"
    },
    {
        "direction": "East",
        "code": "E",
        "degree": 90,
        "min_degree": 78.75,
        "max_degree": 101.25,
        "range_degree": "78.75 - 101.25"
    },
    {
        "direction": "East-Southeast",
        "code": "ESE",
        "degree": 112.5,
        "min_degree": 101.25,
        "max_degree": 123.75,
        "range_degree": "101.25 - 123.75"
    },
    {
        "direction": "Southeast",
        "code": "SE",
        "degree": 135,
        "min_degree": 123.75,
        "max_degree": 146.25,
        "range_degree": "123.75 - 146.25"
    },
    {
        "direction": "South-Southeast",
        "code": "SSE",
        "degree": 157.5,
        "min_degree": 146.25,
        "max_degree": 168.75,
        "range_degree": "146.25 - 168.75"
    },
    {
        "direction": "South",
        "code": "S",
        "degree": 180,
        "min_degree": 168.75,
        "max_degree": 191.25,
        "range_degree": "168.75 - 191.25"
    },
    {
        "direction": "South-Southwest",
        "code": "SSW",
        "degree": 202.5,
        "min_degree": 191.25,
        "max_degree": 213.75,
        "range_degree": "202.25 - 213.75"
    },
    {
        "direction": "Southwest",
        "code": "SW",
        "degree": 225,
        "min_degree": 213.75,
        "max_degree": 236.25,
        "range_degree": "213.75 - 236.25"
    },
    {
        "direction": "West-Southwest",
        "code": "WSW",
        "degree": 247.5,
        "min_degree": 236.25,
        "max_degree": 258.75,
        "range_degree": "236.25 - 258.75"
    },
    {
        "direction": "West",
        "code": "W",
        "degree": 270,
        "min_degree": 258.75,
        "max_degree": 281.25,
        "range_degree": "270.75 - 281.25"
    },
    {
        "direction": "West-Northwest",
        "code": "WNW",
        "degree": 292.5,
        "min_degree": 281.25,
        "max_degree": 303.75,
        "range_degree": "292.25 - 303.75"
    },
    {
        "direction": "Northwest",
        "code": "NW",
        "degree": 315,
        "min_degree": 303.75,
        "max_degree": 326.25,
        "range_degree": "315.75 - 326.25"
    },
    {
        "direction": "North-Northwest",
        "code": "NNW",
        "degree": 337.5,
        "min_degree": 326.25,
        "max_degree": 348.75,
        "range_degree": "337.5 - 348.75"
    }
]

wind_quadrant_4: List[Dict[str, Any]] = [
    {
        "direction": "Quadrant I",
        "code": "I",
        "degree": 45,
        "min_degree": 0,
        "max_degree": 90,
        "range_degree": "0 - 90"
    },
    {
        "direction": "Quadrant II",
        "code": "II",
        "degree": 135,
        "min_degree": 90,
        "max_degree": 180,
        "range_degree": "90 - 180"
    },
    {
        "direction": "Quadrant III",
        "code": "III",
        "degree": 225,
        "min_degree": 180,
        "max_degree": 270,
        "range_degree": "180 - 270"
    },
    {
        "direction": "Quadrant IV",
        "code": "IV",
        "degree": 315,
        "min_degree": 270,
        "max_degree": 360,
        "range_degree": "270 - 360"
    },
]

wind_quadrant_8: List[Dict[str, Any]] = [
    {
        "direction": "Quadrant I",
        "code": "I",
        "degree": 22.5,
        "min_degree": 0,
        "max_degree": 45,
        "range_degree": "0 - 45"
    },
    {
        "direction": "Quadrant II",
        "code": "II",
        "degree": 67.5,
        "min_degree": 45,
        "max_degree": 90,
        "range_degree": "45 - 90"
    },
    {
        "direction": "Quadrant III",
        "code": "III",
        "degree": 112.5,
        "min_degree": 90,
        "max_degree": 135,
        "range_degree": "90 - 135"
    },
    {
        "direction": "Quadrant IV",
        "code": "IV",
        "degree": 157.5,
        "min_degree": 135,
        "max_degree": 180,
        "range_degree": "135 - 180"
    },
    {
        "direction": "Quadrant V",
        "code": "V",
        "degree": 202.5,
        "min_degree": 180,
        "max_degree": 225,
        "range_degree": "180 - 225"
    },
    {
        "direction": "Quadrant VI",
        "code": "VI",
        "degree": 247.5,
        "min_degree": 225,
        "max_degree": 270,
        "range_degree": "225 - 270"
    },
    {
        "direction": "Quadrant VII",
        "code": "VII",
        "degree": 292.5,
        "min_degree": 270,
        "max_degree": 315,
        "range_degree": "270 - 315"
    },
    {
        "direction": "Quadrant VIII",
        "code": "VIII",
        "degree": 337.5,
        "min_degree": 315,
        "max_degree": 360,
        "range_degree": "315 - 360"
    },
]
