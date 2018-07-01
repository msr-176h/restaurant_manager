#! /usr/bin/env python
# -*- coding: utf-8 -*-

# import from generic libraries.
import re
import geocoder
import os.path
import folium
import validators
from datetime import datetime

# import from own programs.
import configs

def address2map_info(address):
    """
    get latitude and longitude from address.

    Parameters
    ----------
    address: str

    Returns
    ----------
    latitude: float
    longitude: float

    """
    #address = '東京都秋葉原'
    g = geocoder.google(address)
    if g:
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        return latitude, longitude
    else:
        return 0, 0

def request2store_info(request):
    """
    covert user's input to store_info format

    Parameters
    ----------
    request: dict

    Returns
    ----------
    store_info: dict

    """
    store_info = {}
    print(request)
    store_info['store_name'] = request['store_name']
    store_info['tel'] = request['tel']
    store_info['experience'] = {'num': 0, 'experiences': []}
    store_info['evaluation'] = {'average': 0, 'evaluations': []}
    store_info['registered_date'] = datetime.now().strftime('%Y-%m-%d')
    store_info['last_visited'] = ''
    store_info['average_fee'] = 0
    store_info['map'] = {}
    store_info['map']['address'] = request['address']
    if store_info['map']['address'] == '':
        store_info['map']['latitude'] = 0
        store_info['map']['longitude'] = 0
        store_info['map']['save_dir'] = ''
    else:
        store_info['map']['latitude'], store_info['map']['longitude'] = address2map_info(request['address'])
        file_name = store_info['store_name'] + '_' + store_info['registered_date'] + '.html'
        store_info['map']['save_dir'] = os.path.join(configs.MAP_DIR, file_name)
    store_info['links'] = []
    dict_tmp = {}
    dict_tmp['url'] = request['url']
    dict_tmp['url_note'] = request['url_note']
    store_info['links'].append(dict_tmp)
    store_info['note'] = request['note']
    store_info['tags'] = []
    for k, v in request.items():
        if k in ['tag1', 'tag2', 'tag3']:
            store_info['tags'].append(v)

    return store_info

def validate_store_information(store_info):
    """
    validate input about store inforamtion.

    Parameters
    ----------
    store_info: dict
        store inforamtion

    Returns
    ----------
    True: bool (in case input is correct)
    False: bool (in case input is incorrect)
    errors: list of str
        if input is correct, it will be empty list.
        if not, occured errors are listed.

    Notes
    ----------
    input:
        - store_name: str (len < 256)
        - experience: dict
        - evaluation: dict
        - registered_date: datetime 
        - map: dict
        - links: list of dict
        - note: str (len < 256)
        - tags: list

    sample:
        {
        'store_name': 'udon shop',
        'links': [
                 ]
        }

    """
    errors = []

    # store_name: str (len < 256)
    if store_info['store_name'] == '':
        errors.append('store_name is needed.')
    elif type(store_info['store_name']) != str:
        errors.append('type of store_name must be strings.')
    if len(store_info['store_name']) > 256:
        errors.append('length of store_name must be shorter than 256.')

    # experience: dict
    if type(store_info['experience']) != dict:
        errors.append('type of experience must be dictionary.')

    # evaluation: dict
    if type(store_info['evaluation']) != dict:
        errors.append('type of evaluation must be dictionary.')

    # registered_date: datetime 
    try:
        d = datetime.strptime(store_info['registered_date'], '%Y-%m-%d')
    except:
        errors.append('registered_date is invalid format.')

    # map: dict
    if type(store_info['map']) != dict:
        errors.append('type of map must be dict.')
    if len(store_info['map']['address']) > 256:
        errors.append('length of address must be shorter than 256.')

    # links: list of dict
    if type(store_info['links']) != list:
        errors.append('type of links must be list.')
    for link in store_info['links']:
        if type(link) != dict:
            errors.append('type of link must be dictionary.')
            continue
        if not validators.url(link['url']) and link['url'] != '':
            errors.append('url is invalid format.')
        if len(link['url_note']) > 256:
            errors.append('note of link must be shorter than 256 (%s...)' % link['note'][:5])

    # note: str (len < 256)
    if store_info['note'] == '' and type(store_info['note']) != str:
        errors.append('type of note must be strings.')
    if len(store_info['note']) > 256:
        errors.append('length of note must be shorter than 256.')

    # tags: list
    if type(store_info['tags']) != list:
        errors.append('type of tags must be list.')
    for tag in store_info['tags']:
        if len(tag) > 256:
            errors.append('tag must be shorter than 256 (%s...)' % tag[:5])

    if len(errors) == 0:
        return True, errors
    else:
        return False, errors


def generate_map(latitude, longitude, save_dir, zoom_start=30, popup=''):
    """
    generate map from latitude and longitude by folium library.

    Parameters
    ----------
    latitude: float
    longitude: float
    save_dir: str
        generated map (.html) is saved in "save_dir"
    zoom_start, default 15: int
        diameter of map
    popup, default '', str
        description written in popup

    Returns
    ----------
    True: bool
    False: bool

    """
    loc = [latitude, longitude]
    map_obj = folium.Map(location=loc, zoom_start=zoom_start)
    #map_obj.simple_marker(loc, popup=popup)
    folium.Marker(loc, popup=popup).add_to(map_obj)
    map_obj.save(save_dir)
    return True


def generate_store_map(store_info):
    """
    generate store map from store_info. 

    Parameters
    ----------
    store_info: dict
        map-related information is needed as follows:
        - latitude = store_info['map']['latitude']
        - longitude = store_info['map']['longitude']
        - save_dir = store_info['map']['save_dir']
        - save_dir = store_info['store_name']

    Returns
    ----------
    True: bool
    False: bool

    See Also
    ----------
    generate_map()

    """
    latitude = store_info['map']['latitude']
    longitude = store_info['map']['longitude']
    save_dir = store_info['map']['save_dir']
    popup = store_info['store_name']
    res = generate_map(latitude, longitude, save_dir, popup=popup)
    return res


def request2store_evaluation(request):
    """
    covert user's input to store_evaluation format

    Parameters
    ----------
    request: dict

    Returns
    ----------
    store_evaluation: dict

    """
    store_evaluation = {}
    store_evaluation['user'] = request['user']
    store_evaluation['visited_date'] = request['visited_date']
    store_evaluation['score'] = float(request['score'])
    try:
        store_evaluation['fee'] = int(request['fee'])
    except:
        store_evaluation['fee'] = request['fee']
    store_evaluation['note'] = request['note']
    return store_evaluation

def validate_store_evaluation(store_evaluation):
    """
    validate input about store evaluation.

    Parameters
    ----------
    store_evaluation: dict

    Returns
    ----------
    True: bool (in case input is correct)
    False: bool (in case input is incorrect)
    errors: list of str
        if input is correct, it will be empty list.
        if not, occured errors are listed.

    Notes
    ----------
    input:
        - user: str (len < 256)
        - visited_date: datetime
        - score: float (0.0 - 5.0, 0.5 devided)
        - fee: int
        - note: str (len < 256)

    """
    errors = []
    # user: str (len < 256)
    if store_evaluation['user'] == '':
        errors.append('user is needed.')
    else:
        if type(store_evaluation['user']) != str:
            errors.append('type of user must be strings.')
        if len(store_evaluation['user']) > 256:
            errors.append('length of user must be shorter than 256.')

    # score: float
    score_candidate = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    if store_evaluation['score'] not in score_candidate:
        errors.append('invalid score.')

    # visited_date: datetime 
    try:
        d = datetime.strptime(store_evaluation['visited_date'], '%Y-%m-%d')
    except:
        errors.append('visited_date is invalid format.')

    # fee: int
    if store_evaluation['fee'] == '':
        errors.append('fee is needed.')
    else:
        if type(store_evaluation['fee']) != int:
            errors.append('type of fee must be int.')
        elif store_evaluation['fee'] < 0:
            errors.append('fee must be upper than 0.')

    # note: str (len < 256)
    if store_evaluation['note'] == '' and type(store_evaluation['note']) != str:
        errors.append('type of note must be strings.')
    if len(store_evaluation['note']) > 256:
        errors.append('length of note must be shorter than 256.')

    if len(errors) == 0:
        return True, errors
    else:
        return False, errors

if __name__ == '__main__':
    latitude, longitude = address2map_info('test')
    print(latitude, longitude)
