from argparse import ArgumentParser, Namespace
import os
import csv

from io import TextIOWrapper
from typing import Any
from googleapiclient.discovery import Resource, build
from googleapiclient.errors import HttpError, Error
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from oauth2client.tools import argparser, _CreateArgumentParser

SCOPES = [
    'https://www.googleapis.com/auth/youtube'
]

# Archivo generado para la API
ARCHIVO_SECRET_CLIENT = 'credentials.json'
ARCHIVO_TOKEN = 'token.json'

FILENAME = "songs.csv"


def cargar_credenciales() -> Credentials:

    credencial: Credentials = None

    if os.path.exists(ARCHIVO_TOKEN):
        
        archivo: TextIOWrapper = open(ARCHIVO_TOKEN, 'r', encoding='utf-8')

        try:
            with archivo:
                credencial = Credentials.from_authorized_user_file(ARCHIVO_TOKEN, SCOPES)

        except IOError:
            print('\nNo se pudo leer el archivo: ', ARCHIVO_TOKEN)
        
        finally:
            archivo.close()            

    return credencial


def guardar_credenciales(credencial: Credentials) -> None:

    archivo: TextIOWrapper = open(ARCHIVO_TOKEN, 'w', encoding='utf-8')

    try:
        with archivo:
            archivo.write(credencial.to_json())

    except IOError:
        print('\nNo se pudo escribir el archivo: ', ARCHIVO_TOKEN)

    finally:
        archivo.close()             


def son_credenciales_invalidas(credencial: Credentials) -> bool:

    return not credencial or not credencial.valid


def son_credenciales_expiradas(credencial: Credentials) -> bool:

    return credencial and credencial.expired and credencial.refresh_token


def autorizar_credenciales() -> Credentials:

    flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(ARCHIVO_SECRET_CLIENT, SCOPES)

    return flow.run_local_server(open_browser=False, port=0)


def generar_credenciales() -> Credentials:

    credencial: Credentials = cargar_credenciales()

    if son_credenciales_invalidas(credencial):

        if son_credenciales_expiradas(credencial):
            credencial.refresh(Request())

        else:
            credencial = autorizar_credenciales()

        guardar_credenciales(credencial)

    return credencial


def obtener_servicio() -> Resource:
    """
    Creador de la conexion a la API Youtube
    """
    return build('youtube', 'v3', credentials=generar_credenciales())


def crear_criterio_de_busqueda(elemento_a_buscar: str, cantidad_de_resultados: int) -> Namespace:

    argparser: ArgumentParser = _CreateArgumentParser()

    argparser.add_argument('--q', help='Search term', default=elemento_a_buscar)
    argparser.add_argument('--max-results', help='Max results', default=cantidad_de_resultados)

    return argparser.parse_args()    


def buscar_en_youtube(servicio: Resource, opciones: Namespace) -> tuple:

    respuesta_de_busqueda: dict = dict()
    videos: list = list()
    canales: list = list()
    playlists: list = list()

    try:
        respuesta_de_busqueda = servicio.search().list(
            q=opciones.q,
            part='id, snippet',
            maxResults=opciones.max_results
        ).execute()

    except (HttpError, Error):
        print(f'Un error ocurrió: {Error}') 

    for resultado_de_busqueda in respuesta_de_busqueda.get('items', list()):

        if resultado_de_busqueda['id']['kind'] == 'youtube#video':
            videos.append({
                'title': resultado_de_busqueda['snippet']['title'],
                'video_id': resultado_de_busqueda['id']['videoId'],
                'kind': resultado_de_busqueda['id']['kind']
            })

        elif resultado_de_busqueda['id']['kind'] == 'youtube#channel':
            videos.append({
                'title': resultado_de_busqueda['snippet']['title'],
                'video_id': resultado_de_busqueda['id']['channelId'],
                'kind': resultado_de_busqueda['id']['kind']
            })

        elif resultado_de_busqueda['id']['kind'] == 'youtube#playlist':
            videos.append({
                'title': resultado_de_busqueda['snippet']['title'],
                'video_id': resultado_de_busqueda['id']['playlistId'],
                'kind': resultado_de_busqueda['id']['kind']
            })

    return videos, canales, playlists


def obtener_playlists(servicio: Resource) -> list:

    respuesta: dict = dict()
    playlists: list = list()

    respuesta = servicio.playlists().list(
        part="snippet",
        mine=True
    ).execute()

    for item in respuesta.get('items', list()):
        playlists.append({
            'id': item.get('id', str())
        })

    return playlists


def obtener_playlist(servicio: Resource, id_playlist: str) -> list:

    respuesta: dict = dict()
    items_de_playlist = list()

    respuesta = servicio.playlistItems().list(
        part="snippet",
        playlistId=id_playlist         
    ).execute()

    for item in respuesta.get('items', list()):
        items_de_playlist.append({
            'nombre_de_cancion': item.get('snippet', dict()).get('title', str()),
            'artista': item.get('snippet', dict()).get('videoOwnerChannelTitle', str()).split('-')[0].strip()
        })

    return items_de_playlist


def crear_playlist(servicio: Resource, titulo: str, descripcion: str, privacidad: str) -> list:

    respuesta: dict = dict()

    try:
        respuesta = servicio.playlists().insert(
            part='snippet, status',
            body=dict(
                snippet=dict(
                    title=titulo,
                    description=descripcion
                ),
                status=dict(
                    privacyStatus=privacidad
                )
            )
        ).execute()

    except (HttpError, Error):
        print(f'Un error ocurrió: {Error}')     

    return respuesta.get('id', str())


def agregar_elemento_a_playlist(servicio: Resource, id_playlist: str, video: dict) -> Any:

    respuesta: dict = dict()

    try:
        respuesta = servicio.playlistItems().insert(
            part="snippet",
            body={
                'kind': "youtube#playlistItem",
                'snippet': {
                    'playlistId': id_playlist,
                    'position': 0,
                    'resourceId': {
                        'kind': video.get('kind', str()),
                        'videoId': video.get('video_id', str())
                    }                
                }
            }
        ).execute()    

    except (HttpError, Error):
        print(f'Un error ocurrió: {Error}')

    return respuesta


# youtube = obtener_servicio()


# This code creates a new, private playlist in the authorized user's channel.
# playlists_insert_response = youtube.playlists().insert(
#     part="snippet, status",
#     body=dict(
#         snippet=dict(
#         title="Varios",
#         description="A private playlist created with the YouTube API v3"
#         ),
#         status=dict(
#         privacyStatus="public"
#         )
#     )
# ).execute()

# print("New playlist id: %s" % playlists_insert_response["id"])


# canciones = read_csv(FILENAME)

# canciones = canciones[1::]

# for cancion in canciones:

#     argparser = _CreateArgumentParser()

#     argparser.add_argument("--q", help="Search term", default=' - '.join(cancion))
#     argparser.add_argument("--max-results", help="Max results", default=25)
#     args = argparser.parse_args()

#     videos, channels, playlists = youtube_search(youtube, args)

#     response = youtube.playlistItems().insert(
#         part="snippet",
#         body={
#             'kind': "youtube#playlistItem",
#             'snippet': {
#                 'playlistId': playlists_insert_response['id'],
#                 'position': 0,
#                 'resourceId': {
#                     'kind': videos[0]['kind'],
#                     'videoId': videos[0]['video_id']
#                 }                
#             }
#         }
#     ).execute()

#     print(response)


# response = youtube.playlists().list(
#     part="snippet",
#     mine=True   

# ).execute()

# print(response)

# channel_id = response.get('items')[0].get('snippet').get('channelId')
# playlist_id = response.get('items')[0].get('id')

# response = youtube.playlistItems().list(
#     part="snippet",
#     playlistId=playlist_id            
# ).execute()

# playlist_items = list()

# for item in response.get('items'):
#     playlist_items.append({
#         'nombre_de_cancion': item.get('snippet').get('title'),
#         'artista': item.get('snippet').get('videoOwnerChannelTitle').split('-')[0].strip()
#     })


# songs_list = [list(x.values()) for x in playlist_items]
# header = [list(x.keys()) for x in playlist_items]
# header = header[0]
# header = [x.upper() for x in header]

# write_csv(header, songs_list)