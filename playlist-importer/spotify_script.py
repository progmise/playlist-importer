import os
import tekore as tk
import csv

from tekore import RefreshingToken, Spotify
from tekore.model import FullPlaylist, PrivateUser, SimplePlaylistPaging


CLIENT_ID = '6390fd98ea7e4ad791d81538a49f9aab'
CLIENT_SECRET = 'cb1fe6104d164f5ca67ed4eeb98e647b'
REDIRECT_URI = 'https://example.com/callback'  
ARCHIVO_TEKORE = 'tekore.cfg'


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


def obtener_usuario_actual(servicio: Spotify) -> PrivateUser:

    usuario: PrivateUser = None

    try:
        usuario = servicio.current_user()
    except tk.HTTPError:
        print(f'Un error ocurrió: {tk.HTTPError}') 

    return usuario


def obtener_playlists(servicio: Spotify, id_usuario: str) -> SimplePlaylistPaging:

    playlists: SimplePlaylistPaging = None

    try:
        playlists = servicio.playlists(id_usuario)
    except tk.BadRequest:
        print(f'Un error en la petición: {tk.BadRequest}')
    except tk.HTTPError:
        print(f'Un error ocurrió: {tk.HTTPError}')  

    return playlists


def obtener_playlist(servicio: Spotify, id_playlist: str) -> list:

    playlist: FullPlaylist = None
    items_de_playlist = list()

    try:
        playlist = servicio.playlist(id_playlist)
    except tk.BadRequest:
        print(f'Un error en la petición: {tk.BadRequest}')
    except tk.HTTPError:
        print(f'Un error ocurrió: {tk.HTTPError}')  

    for item in playlist.tracks.items:
        items_de_playlist.append(
            {
                'nombre_de_cancion': item.track.name,
                'artista': item.track.artists[0].name
            }
        )

    return items_de_playlist


def crear_playlist(servicio: Spotify, id_usuario: str, 
                   nombre_de_playlist: str, descripcion: str, publico: bool = True) -> str:

    playlist: FullPlaylist = None

    playlist = servicio.playlist_create(
        user_id=id_usuario,
        name=nombre_de_playlist,
        public=publico,
        description=descripcion
    )

    return playlist.id


# current_user = spotify.current_user()


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


