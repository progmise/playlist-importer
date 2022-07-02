import csv
import os

from io import TextIOWrapper
from re import sub
from tekore import Spotify

from spotify_script import ARCHIVO_TEKORE
from spotify_script import agregar_canciones_a_playlist, buscar_cancion
from spotify_script import crear_playlist, obtener_playlist, obtener_playlists
from spotify_script import obtener_servicio, obtener_usuario_actual


def validar_numero(numero: str) -> bool:

    numero_formateado: str = str()
    es_numero_valido: bool = bool()

    numero_formateado = sub('[a-zA-Z]+', '', numero)

    try:
        int(numero_formateado)
        es_numero_valido = True

    except ValueError:
        print('\n¡Sólo se pueden ingresar numeros!')
        es_numero_valido = False

    return es_numero_valido


def validar_opcion(opcion: str, opciones: list) -> bool:

    numero_de_opcion: int = int()
    flag_opcion_valida: bool = False

    if opcion.isnumeric():
        numero_de_opcion = int(opcion)

        if numero_de_opcion > 0 and numero_de_opcion <= len(opciones):
            flag_opcion_valida = True

        else:
            print(f'\n¡Sólo puedes ingresar una opción entre el 1 y el {len(opciones)}!')

    else:
        print(f'\n¡Las opciones son numeros enteros, sin decimales!')

    return flag_opcion_valida


def validar_opcion_ingresada(opciones: list) -> str:

    opcion_ingresada: str = str()
    flag_numero_valido: bool = False
    flag_opcion_valida: bool = False

    while not (flag_numero_valido and flag_opcion_valida):

        opcion_ingresada = input('\nIngrese una opción: ')

        flag_numero_valido = validar_numero(opcion_ingresada)

        flag_opcion_valida = validar_opcion(opcion_ingresada, opciones)

    return opcion_ingresada


def obtener_entrada_usuario(opciones: list) -> str:

    opcion: str = str()

    print('\nOpciones válidas: \n')

    for x in range(len(opciones)):
        print(x + 1, '-', opciones[x])

    opcion = validar_opcion_ingresada(opciones)

    return opcion


def eliminar_archivo(ruta_de_archivo: str) -> None:

    if os.path.exists(ruta_de_archivo):
        os.remove(ruta_de_archivo)
        print('El archivo fue eliminado satisfactoriamente')

    else:
        print('¡El archivo no existe!')


def leer_archivo_csv(ruta_de_archivo: str) -> 'list[str]':

    datos: list = list()
    archivo: TextIOWrapper = open(ruta_de_archivo, 'r', encoding='utf-8')

    try:
        with archivo:
            csv_lector = csv.reader(archivo, delimiter=',')
        
            for dato in csv_lector:
                datos.append(dato)

    except IOError:
        print('\nNo se pudo leer el archivo: ', ruta_de_archivo)
    
    finally:
        archivo.close()

    return datos


def escribir_archivo_csv(ruta_de_archivo: str, encabezados: list, contenido: list) -> None:

    archivo: TextIOWrapper = open(ruta_de_archivo, 'w', encoding='utf-8')

    try:
        with archivo:
            csv_escritor = csv.writer(archivo, quoting=csv.QUOTE_NONNUMERIC, lineterminator='\n')

            csv_escritor.writerow(encabezados)
            csv_escritor.writerows(contenido)

    except IOError:
        print('\nNo se pudo escribir el archivo: ', ruta_de_archivo)

    finally:
        archivo.close()     


def mostrar_playlists(playlists: dict) -> None:

    print('\nListas de reproducción: \n')

    for x in range(len(playlists)):
        print(' '*2, f'{x + 1}° playlist: ')

        for key, value in playlists[x].items():
            print(' '*5, f'{key} - {value}')    


def mostrar_playlists_de_spotify(servicio: Spotify, usuario: dict) -> None:

    playlists: list = obtener_playlists(servicio, usuario.get('id', ''))

    mostrar_playlists(playlists)


def iniciar_menu_de_spotify() -> None:

    opciones: list = [
        'Crear nueva playlist',
        'Listar playlists',
        'Listar canciones de playlist',
        'Agregar canción a una playlist',
        'Exportar playlist a Youtube',
        'Cerrar sesión',
        'Salir'
    ]

    se_cerro_sesion: bool = False
    servicio: Spotify = obtener_servicio()
    usuario: dict = obtener_usuario_actual(servicio)

    opcion: int = int(obtener_entrada_usuario(opciones))

    while opcion != 7:

        if se_cerro_sesion:
            servicio: Spotify = obtener_servicio()
            usuario: dict = obtener_usuario_actual(servicio)
            se_cerro_sesion = False

        if opcion == 1:
            pass

        elif opcion == 2:
            mostrar_playlists_de_spotify(servicio, usuario)

        elif opcion == 3:
            pass

        elif opcion == 4:
            pass

        elif opcion == 5:
            pass        

        elif opcion == 6:
            eliminar_archivo(ARCHIVO_TEKORE)
            se_cerro_sesion = True

        opcion = int(obtener_entrada_usuario(opciones))    


def main() -> None:

    opciones: list = [
        'Spotify',
        'Youtube',
        'Cerrar sesiones',
        'Salir'
    ]

    opcion: int = int(obtener_entrada_usuario(opciones))

    while opcion != 4:

        if opcion == 1:
            iniciar_menu_de_spotify()

        elif opcion == 2:
            pass

        elif opcion == 3:
            pass         

        opcion = int(obtener_entrada_usuario(opciones))

    print('\nPrograma finalizado')


if __name__ == '__main__':
    main()