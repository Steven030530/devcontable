import logging
import pandas as pd

def load_data(data: pd.DataFrame,path:str) -> None:
    '''
    Esta funcion nos ayuda para cargar los datos
    finales en una ruta especifica
    '''
    try:
        data.to_excel(path,index=False)
        logging.info("Se cargo el archivo en %r", path)
    
    except FileNotFoundError:
        logging.error(f'La ruta {path} no existe')
    except PermissionError:
        logging.error(f'No tienes permisos para guardar este archivo en esta ruta {path}')
    except AttributeError:
        logging.error('No existe un archivo que se pueda cargar en la ruta')
            