#!/usr/bin/env python3

# Spotify playlist cover generator

from PIL import Image, ImageDraw, ImageFont
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64
from termcolor import colored
import unidecode
import json


scope = "playlist-read-private, playlist-modify-private, playlist-modify-public, ugc-image-upload"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))


def main():
    spotify_user_id = get_user_id()
    playlists = load_user_owned_playlists(spotify_user_id)

    print(colored('SPOTIFY PLAYLIST MANAGEMENT: ', attrs=['bold']))
    print('1: Create all playlist covers')
    print('2: Create individual playlist cover')
    print('3: Upload all playlist covers')
    print('4: Upload individual playlist cover')
    print('5: Uppercase all playlist names')
    option = input('Select option: ')

    if (option == '1'):
        for playlist in playlists:
            create_album_art(playlist)
    elif (option == '2'):
        selected_playlist = playlists[int(option) - 1]
        create_album_art(selected_playlist)
    elif (option == '3'):
        for playlist in playlists:
            upload_album_art(playlist)
    elif (option == '4'):
        selected_playlist = playlists[int(option) - 1]
        upload_album_art(selected_playlist)
    elif (option == '5'):
        for playlist in playlists:
            uppercase_playlist_name(playlist)


def get_user_id():
    user_id = sp.current_user()['id']
    return user_id


def load_user_owned_playlists(user_id):
    playlists = sp.user_playlists(user_id)
    user_owned_playlists = []
    for playlist in playlists['items']:
        if playlist['owner']['id'] == user_id:
            user_owned_playlists.append(playlist)
    json.dump(user_owned_playlists, open('playlists.json', 'w'))
    return user_owned_playlists


def print_all_user_playlists(user_id, playlists):
    print(colored('USER PLAYLISTS: ', attrs=['bold']))
    print('00: All playlists')
    index = 1
    for playlist in playlists:
        print(str(index).zfill(2) + ': ' + playlist['name'])
        index += 1


def create_album_art(playlist):
    x_dimension = 500
    y_dimension = 500

    bg_color = '#131313'
    fg_color = '#FFFFFF'

    font = ImageFont.truetype('Humane-VF.ttf', 140)
    font.set_variation_by_name('Bold')

    img = Image.new('RGB', (x_dimension, y_dimension), color=bg_color)
    draw = ImageDraw.Draw(img)

    filename = str(unidecode.unidecode(playlist['name'])).lower()
    try:
        background = Image.open('src/' + filename + '.jpg')

        # background.size[0] = x axis
        # background.size[1] = y axis

        # background image horizontal
        if (background.size[0] > background.size[1]):
            background = background.resize((round(y_dimension / background.size[1] *
                                                  background.size[0]), y_dimension),
                                           Image.Resampling.LANCZOS)
            img.paste(background, (-(round((background.size[0] - x_dimension) / 2)), 0))
        # background image vertical
        else:
            background = background.resize((x_dimension, round(x_dimension / background.size[0] *
                                                               background.size[1])),
                                           Image.Resampling.LANCZOS)
            img.paste(background, (0, -(round((background.size[1] - y_dimension) / 2))))
    except FileNotFoundError:
        # no background image found
        pass

    overlay = Image.open('overlay.png')
    img.paste(overlay, (0, 0), mask=overlay)

    cover_text = str(playlist['name']).upper()
    draw.text((x_dimension / 2, y_dimension / 2),
              cover_text,
              font=font,
              fill=fg_color,
              anchor='mm',
              align='center',
              )
    img.save('out/' + playlist['id'] + '.jpg')
    print('Saved ' + playlist['name'] + ' as out/' + playlist['id'] + '.jpg')


def upload_album_art(playlist):
    try:
        with open('out/' + playlist['id'] + '.jpg', 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read())
            sp.playlist_upload_cover_image(playlist['id'], encoded_image)
            print('Uploaded ' + playlist['name'] + ' as out/' + playlist['id'] + '.jpg')
    except FileNotFoundError:
        pass


def uppercase_playlist_name(playlist):
    sp.playlist_change_details(playlist['id'], name=str(playlist['name']).upper())
    print('Uppercased ' + playlist['name'] + ' as ' + str(playlist['name']).upper())


if __name__ == "__main__":
    main()
