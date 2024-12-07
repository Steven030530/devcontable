from etl.extract import read_excel
from etl.load import load_data
from etl.transform import Contable
from utils.utils import setup_logging
import logging
import os
import warnings

def run() -> None:
    
    # Configuration
    setup_logging()
    warnings.simplefilter('ignore')
    
    # Path Files
    company = input('Ingresa movimiento de archivos (IEO-JCZ): ')
    ruta_base = os.path.abspath(os.path.join(os.getcwd(),'../data'))
    mvto_conta = os.path.abspath(os.path.join(ruta_base,'input',f'{company}.xlsx'))
    formato = os.path.abspath(os.path.join(ruta_base,'input','Formato Migracion.xlsx'))
    formato_terceros = os.path.abspath(os.path.join(ruta_base,'input','TercerosWO.xls'))
    fact_final = os.path.abspath(os.path.join(ruta_base,'output',f'FactFinal_{company}.xlsx'))
    comp_final = os.path.abspath(os.path.join(ruta_base,'output',f'CompFinal_{company}.xlsx'))
    terc_comp_final = os.path.abspath(os.path.join(ruta_base,'output',f'Terceros_Compras_{company}.xlsx'))
    terc_vend_final = os.path.abspath(os.path.join(ruta_base,'output',f'Terceros_Ventas_{company}.xlsx'))
    
    # Read Data
    data_dian = read_excel(mvto_conta)
    data_format = read_excel(formato)
    data_tercero = read_excel(formato_terceros)
    data_dian2 = read_excel(mvto_conta)
    data_tercero2 = read_excel(formato_terceros)

    # Transform Data
    object_tr = Contable()
    facturas_process = object_tr.file_factura(data_dian, data_format)
    compras_process = object_tr.file_compra(data_dian, data_format)
    terceros_comp_process = object_tr.file_terceros_comp(data_dian, data_tercero)
    terceros_vent_process = object_tr.file_terceros_vent(data_dian2, data_tercero2)
        
    # Load Data
    load_data(facturas_process,fact_final)
    load_data(compras_process, comp_final)
    load_data(terceros_comp_process, terc_comp_final)
    load_data(terceros_vent_process, terc_vend_final)

if __name__ == '__main__':
    run()