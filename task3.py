import os

import folium
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request
from geopy.geocoders import Nominatim

import task2

print(load_dotenv('mysite/.env'))
# print(load_dotenv('venv/.env'))
app = Flask('UCU labs', template_folder='mysite/templates')
# app = Flask('UCU labs', template_folder='templates')


@app.route('/')
def root() -> str:
    """
    Returns base html page when user enters the site
    """
    return render_template("index.html")


@app.route('/map')
def get_map() -> str:
    """
    Returns html page with a map on it with markers - friends
    of user passed as a parameter
    """
    try:
        return get_map_for_user(request.args.get('username'))
    except ValueError as e:
        return render_template('index.html', error_content=e.__str__())


def get_location_from_geopy(location: str) -> tuple:
    """
    Gets location coordinates using geopy
    """
    geo_locator = Nominatim(user_agent="UCU FP2022 Lab2")
    location = geo_locator.geocode(location, timeout=None)
    if location is None:
        return None
    else:
        return float(location.latitude), float(location.longitude)


def build_map(locations_data: list) -> str:
    """
    Generates folium map placing markers at provided spots
    returns string - html file with the map
    """
    folium_map = folium.Map(location=[0, 0], zoom_start=4)
    feature_group = folium.FeatureGroup(name='friends')
    for friend in locations_data:
        location = get_location_from_geopy(friend['location'])
        if location is None:
            continue
        feature_group.add_child(folium.Marker(
            location=list(location),
            popup=friend['name'],
            icon=folium.Icon(color='green')
        ))
    folium_map.add_child(feature_group)
    return folium_map.get_root().render()


def get_user_id(username: str) -> int:
    """
    Returns user id of user by username
    """
    header = {"authorization": f"Bearer {os.getenv('twitter_token')}"}
    user_response = requests.get(f'https://api.twitter.com'
                                 f'/2/users/by/username/{username}',
                                 headers=header)

    if user_response.status_code != 200:
        raise ValueError(f'ERROR! Returned code: {user_response.status_code}')
    try:
        raise ValueError(task2.get_field_from_json(json_str=user_response.text,
                                                   path_to_field=['errors', 0,
                                                                  'detail']))
    except KeyError:
        pass

    return task2.get_field_from_json(json_str=user_response.text,
                                     path_to_field=['data', 'id'])


def get_locations_by_id(user_id: int) -> requests.Response:
    """
    Gets locations response by user id
    """
    header = {"authorization": f"Bearer {os.getenv('twitter_token')}"}
    follows_response = requests.get('https://api.twitter.com'
                                    f'/2/users/{user_id}/following',
                                    headers=header,
                                    params={'user.fields': 'location'})

    if follows_response.status_code != 200:
        raise ValueError(f'Returned code: {follows_response.status_code}')
    try:
        raise ValueError(task2.get_field_from_json(
            json_str=follows_response.text,
            path_to_field=['errors',
                           0, 'detail']))
    except KeyError:
        pass

    return follows_response


def get_map_for_user(username: str):
    """
    Gets folium for provided username
    """
    print(f'Someone wants to know about {username}')

    user_id = get_user_id(username)
    follows_response = get_locations_by_id(user_id)

    amount = task2.get_field_from_json(json_str=follows_response.text,
                                       path_to_field=['meta', 'result_count'])
    locations_data = []
    for idx in range(amount):
        try:
            name = task2.get_field_from_json(json_str=follows_response.text,
                                             path_to_field=['data', idx,
                                                            'name'])
            location = task2.get_field_from_json(json_str=follows_response.text,
                                                 path_to_field=['data', idx,
                                                                'location'])
            locations_data += [{"name": name, "location": location}]
        except KeyError:
            pass

    return build_map(locations_data)


if __name__ == '__main__':
    app.run(port=8080)
