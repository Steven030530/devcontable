import logging
import pandas as pd


def read_excel(path_data:str)-> pd.DataFrame:
    '''
    Con esta funcion leemos los archivos
    necesarios para ejecutar el programa

    '''
    try:
        data = pd.read_excel(path_data)
        logging.info(f'El archivo se cargo exitosamente')
        return data
            
    except FileExistsError:
        logging.error(f'Fallo la lectura del archivo excel')
    except FileNotFoundError:
        logging.error(f'El archivo ingresado no existe')

