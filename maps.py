import pandas as pd
import folium
from folium.plugins import HeatMap
import numpy as np
from unidecode import unidecode
from geopy.geocoders import Nominatim

def make_pinned_map(df, links=False, zoom=12):
    '''
    Creates and returns a Folium Map object with popup pins for each post.

    INPUT:
        - df (DataFrame): DataFrame from a MissedConn object (e.g. mc.df) or the
        'missedconn' table
        - links (boolean): If True, the popup text displays the post's title as
        a link to the original webpage. If False, the popup text displays the
        post title and content.
        - zoom (int): initial zoom factor for viewing the map (large int means
        higher magnification). Folium Map object supports mouse zoom & pan during
        viewing as well.
    '''
    df_temp = df.copy()
    df_latlongs, view_coords = _make_latlong_info(df_temp)

    # Initialize map
    m = folium.Map(location=view_coords, zoom_start=zoom, tiles='Cartodb Positron')

    # Add pins
    for ind in df_latlongs.index:
        if links:
            html = '<a href= "' + df_latlongs.loc[ind, 'url'] + '"> ' + df_latlongs.loc[ind, 'title'] + '</a>'
            iframe = folium.element.IFrame(html=html, width=400, height=50)
            popup = folium.Popup(iframe, max_width=400)
        else:
            try:
                popup = unidecode(df_latlongs.loc[ind, 'title'])+':\n\n\t'+unidecode(df_latlongs.loc[ind, 'post'])
            except UnicodeDecodeError:
                print 'UnicodeDecodeError: ', df_latlongs.loc[ind, 'url']
                continue
        folium.Marker(df_latlongs.loc[ind, ['latitude', 'longitude']].values, popup=popup, icon=folium.Icon(icon='heart-empty', color='red')).add_to(m)

    return m

def make_heat_map(df, zoom=9):
    '''
    Creates and returns a Folium Map object representing a heat map of posts.

    INPUT:
        - df (DataFrame): DataFrame from a MissedConn object (e.g. mc.df) or the
        'missedconn' table
        - zoom (int): initial zoom factor for viewing the map (large int means
        higher magnification). Folium Map object supports mouse zoom & pan during
        viewing as well.
    '''
    df_latlongs, view_coords = _make_latlong_info(df)

    # Initialize map
    m = folium.Map(location=view_coords, zoom_start=zoom, tiles='Cartodb Positron')

    # Heat
    coordinates = df_latlongs[['latitude', 'longitude']].values
    m.add_children(HeatMap(coordinates))

    return m

def _make_latlong_info(df, calc_view=False):
    df = _fix_cities(df)
    df_latlongs = df[~df['latitude'].isnull()]
    if calc_view:
        view_coords = tuple(map(np.median, zip(*df_latlongs[['latitude', 'longitude']].values)))
    else:
        geolocator = Nominatim()
        coords = geolocator.geocode(str(df['city'].unique()[0]))
        view_coords = coords.latitude, coords.longitude
    return df_latlongs, view_coords

def _fix_cities(df):
    city_dict = {
        'fortcollins': 'fort collins',
        'colosprings': 'colorado springs',
        'tampabay': 'tampa bay',
        'iowacity': 'iowa city',
        'kansascity': 'kansas city',
        'neworleans': 'new orleans',
        'washingtondc': 'dc',
        'annarbor': 'ann arbor',
        'grandrapids': 'grand rapids',
        'detroitmetro': 'detroit',
        'newyork': 'new york',
        'northjersey': 'north jersey',
        'sfbay': 'sf',
        'oklahomacity': 'oklahoma city',
        'rhodeisland': 'rhode island',
        'sandiego': 'san diego',
        'losangeles': 'los angeles',
        'orangeco': 'orange co',
        'orangecounty': 'orange co',
        'santabarbara': 'santa barbara',
        'sanantonio': 'san antonio',
        'saltlake': 'salt lake city',
        'washington': 'dc',
        'eauclaire': 'eau claire',
        'greenbay': 'green bay'}

    for i, city in enumerate(df['city']):
        if city in city_dict.keys():
            df.loc[i, 'city'] = city_dict[city]
    return df
