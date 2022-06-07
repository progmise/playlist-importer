import csv
from io import TextIOWrapper


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


