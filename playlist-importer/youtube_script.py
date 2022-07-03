import os

from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from httpx import ConnectError
from io import TextIOWrapper

SCOPES = [
    'https://www.googleapis.com/auth/youtube'
]

# Archivo generado para la API
ARCHIVO_CLIENT_SECRET = 'resources\\credentials.json'
ARCHIVO_TOKEN = 'resources\\token.json'


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

    flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(ARCHIVO_CLIENT_SECRET, SCOPES)

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


def obtener_artista_del_video(item_de_playlist: dict) -> str:

    artista_del_video: str = str()
    partes_del_titulo: list = item_de_playlist.get('snippet', dict()).get('title', str()).split('-')

    if len(partes_del_titulo) == 1:
        partes_del_titulo = item_de_playlist.get('snippet', dict()).get('videoOwnerChannelTitle', str()).split('-')
        artista_del_video = partes_del_titulo[0].strip()

    else:
        artista_del_video = partes_del_titulo[0].strip()

    return artista_del_video


def obtener_nombre_del_video(item_de_playlist: dict) -> str:

    nombre_del_video: str = str()
    partes_del_titulo: list = item_de_playlist.get('snippet', dict()).get('title', str()).split('-')

    if len(partes_del_titulo) == 1:
        nombre_del_video = item_de_playlist.get('snippet', dict()).get('title', str())

    else:
        nombre_del_video = partes_del_titulo[1].strip()

    return nombre_del_video


def buscar_video(servicio: Resource, cancion_a_buscar: str) -> list:

    resultado_de_busqueda: dict = dict()
    videos: list = list()

    try:
        resultado_de_busqueda = servicio.search().list(
            part='id, snippet',
            maxResults=10,
            q=cancion_a_buscar
        ).execute()
    except HttpError as err:
        print(f'Un error ocurrió con la petición: {err}')
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')

    for item in resultado_de_busqueda.get('items', list()):
        if item.get('id', dict()).get('kind', str()) == 'youtube#video':
            videos.append({
                'id': item.get('id', dict()).get('videoId', str()),
                'nombre_de_video': item['snippet']['title']
            })

    return videos


def obtener_playlists(servicio: Resource) -> list:

    playlists: dict = dict()
    playlists_formateadas: list = list()

    try:
        playlists = servicio.playlists().list(
            part='snippet',
            mine=True,
            maxResults=10
        ).execute()
    except HttpError as err:
        print(f'Un error ocurrió con la petición: {err}')
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')

    if playlists:
        for item in playlists.get('items', list()):
            playlists_formateadas.append({
                'id': item.get('id', str()),
                'nombre': item.get('snippet', dict()).get('title', ''),
                'descripcion': item.get('snippet', dict()).get('description', ''),
                'href': str(),
                'uri': str(),
                'cantidad_de_canciones': int()
            })        

    return playlists_formateadas


def obtener_playlist(servicio: Resource, id_playlist: str) -> list:

    playlist: dict = dict()
    playlist_formateada = list()

    try:
        playlist = servicio.playlistItems().list(
            part='snippet',
            playlistId=id_playlist,
            maxResults=50      
        ).execute()
    except HttpError as err:
        print(f'Un error ocurrió con la petición: {err}')
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')

    if playlist:
        for item in playlist.get('items', list()):
            playlist_formateada.append({
                'id': item.get('id', ''),
                'nombre_de_cancion': obtener_nombre_del_video(item),
                'artista': obtener_artista_del_video(item),
                'duracion_en_ms': int(),
                'album': str(),
                'href': str(),
                'uri': str()            
            })

    return playlist_formateada


def crear_playlist(servicio: Resource, titulo: str, 
                   descripcion: str, privacidad: str = 'public') -> dict:

    playlist: dict = dict()
    playlist_creada: dict = dict()

    try:
        playlist = servicio.playlists().insert(
            part='snippet, status',
            body={
                'snippet': {
                    'title': titulo,
                    'description': descripcion
                },
                'status': {
                    'privacyStatus': privacidad
                }
            }
        ).execute()
    except HttpError as err:
        print(f'Un error ocurrió con la petición: {err}')
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}') 

    if playlist:
        playlist_creada = {
            'id': playlist.get('id', str()),
            'nombre': playlist.get('snippet', dict()).get('title', ''),
            'descripcion': playlist.get('snippet', dict()).get('description', ''),
            'href': str(),
            'uri': str(),
            'cantidad_de_canciones': int()
        }     

    return playlist_creada


def agregar_elementos_a_playlist(servicio: Resource, id_playlist: str, videos: list) -> bool:

    elemento_de_playlist: dict = dict()
    se_agregaron_todos_los_elementos: bool = True

    for video in videos:
        try:
            elemento_de_playlist = servicio.playlistItems().insert(
                part='snippet',
                body={
                    'kind': 'youtube#playlistItem',
                    'snippet': {
                        'playlistId': id_playlist,
                        'resourceId': {
                            'kind': 'youtube#video',
                            'videoId': video.get('id', str())
                        }                
                    }
                }
            ).execute()

        except HttpError as err:
            print(f'Un error ocurrió con la petición: {err}')
        except ConnectError as err:
            print(f'Un error ocurrió con la conexión a internet: {err}')
        except Exception as err:
            print(f'Un error ocurrió: {err}')

        if not elemento_de_playlist:
            se_agregaron_todos_los_elementos = False

    return se_agregaron_todos_los_elementos