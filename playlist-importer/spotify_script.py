import os
import tekore as tk
import csv

from httpx import ConnectError
from tekore import RefreshingToken, Spotify
from tekore.model import FullPlaylist, PrivateUser, SimplePlaylistPaging


CLIENT_ID = '6390fd98ea7e4ad791d81538a49f9aab'
CLIENT_SECRET = 'cb1fe6104d164f5ca67ed4eeb98e647b'
REDIRECT_URI = 'https://example.com/callback'  
ARCHIVO_TEKORE = 'resources//tekore.cfg'


def cargar_token():

    token: RefreshingToken = None

    if os.path.exists(ARCHIVO_TEKORE):
        
        configuracion: tuple = tk.config_from_file(ARCHIVO_TEKORE, return_refresh=True)
        token = tk.refresh_user_token(*configuracion[:2], configuracion[3])        

    return token


def guardar_token(configuracion: tuple, token: RefreshingToken) -> None:

    tk.config_to_file(ARCHIVO_TEKORE, configuracion + (token.refresh_token,))


def es_token_invalido(token: RefreshingToken) -> bool:

    return not token


def autorizar_credenciales(configuracion: tuple) -> RefreshingToken:

    token = tk.prompt_for_user_token(*configuracion, scope=tk.scope.every)

    return token


def generar_token() -> RefreshingToken:

    token: RefreshingToken = cargar_token()
    configuracion = (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

    if es_token_invalido(token):

        token = autorizar_credenciales(configuracion)

        guardar_token(configuracion, token)

    return token


def obtener_servicio() -> Spotify:
    """
    Creador de la conexion a la API Spotify
    """
    return tk.Spotify(generar_token())


def obtener_usuario_actual(servicio: Spotify) -> dict:

    usuario: PrivateUser = None
    usuario_formateado: dict = dict()

    try:
        usuario = servicio.current_user()
    except tk.HTTPError as err:
        print(f'Un error ocurrió con la petición: {err}')
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')

    if usuario:
        usuario_formateado = {
            'id': usuario.id,
            'usuario': usuario.display_name,
            'email': usuario.email,
            'href': usuario.external_urls.get('spotify', str()),
            'uri': usuario.uri
        }

    return usuario_formateado


def obtener_playlists(servicio: Spotify, id_usuario: str) -> list:

    playlists: SimplePlaylistPaging = None
    playlists_formateadas: list = list()

    try:
        playlists = servicio.playlists(id_usuario)
    except tk.HTTPError as err:
        print(f'Un error ocurrió con la petición: {err}')
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')

    if playlists:
        for playlist in playlists.items:
            playlists_formateadas.append({
                'id': playlist.id,
                'nombre': playlist.name,
                'descripcion': playlist.description,
                'href': playlist.external_urls.get('spotify', str()),
                'uri': playlist.uri,
                'cantidad_de_canciones': playlist.tracks.total
            })

    return playlists_formateadas


def obtener_playlist(servicio: Spotify, id_playlist: str) -> list:

    playlist: FullPlaylist = None
    playlist_formateada: list = list()

    try:
        playlist = servicio.playlist(id_playlist)
    except tk.HTTPError as err:
        print(f'Un error ocurrió con la petición: {err}')
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')

    if playlist: 
        for item in playlist.tracks.items:
            playlist_formateada.append({
                'id': item.track.id,
                'nombre_de_cancion': item.track.name,
                'duracion_en_ms': item.track.duration_ms,
                'album': item.track.album.name,
                'artista': item.track.artists[0].name,
                'href': item.track.external_urls.get('spotify', str()),
                'uri': item.track.uri
            })

    return playlist_formateada


def crear_playlist(servicio: Spotify, id_usuario: str, 
                   nombre_de_playlist: str, descripcion: str, publico: bool = True) -> dict:

    playlist: FullPlaylist = None
    playlist_creada: dict = dict()

    try:
        playlist = servicio.playlist_create(
            user_id=id_usuario,
            name=nombre_de_playlist,
            public=publico,
            description=descripcion
        )
    except tk.HTTPError as err:
        print(f'Un error ocurrió con la petición: {err}')
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')

    if playlist:
        playlist_creada = {
            'id': playlist.id,
            'nombre': playlist.name,
            'descripcion': playlist.description,
            'href': playlist.external_urls.get('spotify', str()),
            'uri': playlist.uri,
            'cantidad_de_canciones': playlist.tracks.total
        }

    return playlist_creada


def agregar_canciones_a_playlist(servicio: Spotify, 
                                 id_playlist: str, uris: list) -> bool:

    id_snapshot_de_playlist: str = str()
    se_actualizo_playlist: bool = False

    try:
        id_snapshot_de_playlist = servicio.playlist_add(
            playlist_id=id_playlist,
            uris=uris,
        )
    except tk.HTTPError as err:
        print(f'Un error ocurrió con la petición: {err}')
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')

    if id_snapshot_de_playlist:
        se_actualizo_playlist = True

    return se_actualizo_playlist


spotify = obtener_servicio()

usuario = obtener_usuario_actual(spotify)

playlists = obtener_playlists(spotify, usuario.get('id', ''))

playlist = obtener_playlist(spotify, playlists[2].get('id', ''))

# playlist_creada = crear_playlist(spotify, usuario.get('id', ''), 'Prueba3', 'Una descripción')

id_playlist = agregar_canciones_a_playlist(spotify, playlists[2].get('id', ''), [
    playlist[0].get('uri', ''),
    playlist[1].get('uri', '')
])

print(id_playlist)

# playlists = spotify.playlists(current_user.id)

# playlist = spotify.playlist(playlists.items[0].id)

# tracks = list()
# songs = list()

# for item in playlist.tracks.items:

#     songs.append(
#         {
#             'nombre_de_cancion': item.track.name,
#             'artista': item.track.artists[0].name
#         }
#     )

# songs_list = [list(x.values()) for x in songs]
# header = [list(x.keys()) for x in songs]
# header = header[0]
# header = [x.upper() for x in header]

# write_csv(header, songs_list)

# playlists = spotify.playlist_create(
#     user_id=current_user.id,
#     name='News',
#     public=True,
#     description='Playlist creada desde Python'
# )
