from httpx import ConnectError
from lyricsgenius import Genius
from lyricsgenius.song import Song
from re import sub


GENIUS_TOKEN = 'A25rNPH1iFssaSQuogqVeZSYosZO6O6gQvTE3pyAzkxklGul_JWfcMDUoQj0mD8B'


def buscar_cancion(servicio: Genius, 
                   nombre_de_cancion: str, artista: str) -> dict:
    
    resultado_de_busqueda: Song = None
    cancion: dict = dict()

    try:
        resultado_de_busqueda = servicio.search_song(
            title=nombre_de_cancion, 
            artist=artista,
            get_full_info=False
        )
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')

    if not resultado_de_busqueda is None:
        cancion = {
            'id': resultado_de_busqueda.id,
            'nombre_de_cancion': resultado_de_busqueda.title,
            'duracion_en_ms': int(),
            'album': str(),
            'artista': resultado_de_busqueda.artist,
            'href': resultado_de_busqueda.url,
            'uri': resultado_de_busqueda.path
        }

    return cancion

def obtener_letra(servicio: Genius, id_cancion: str) -> str:

    resultado_de_busqueda: str = str()
    letra_de_cancion: str = str()

    try:
        resultado_de_busqueda = servicio.lyrics(
            song_id=id_cancion,
            remove_section_headers=True
        )
    except ConnectError as err:
        print(f'Un error ocurrió con la conexión a internet: {err}')
    except Exception as err:
        print(f'Un error ocurrió: {err}')    
    
    if not resultado_de_busqueda is None:
        letra_de_cancion = resultado_de_busqueda.replace('\n', ' ')
        letra_de_cancion = sub(r'\s{2,}', ' ', letra_de_cancion)

    return letra_de_cancion