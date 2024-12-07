'''
Este modulo contiene dos funciones para la transformacion en facturas
de venta y facturas de compra para la importacion en el sistema contable
WO
'''

# Importacion librerias
import logging
import pandas as pd
from random import randint, choice

class Contable:
    
    def __init__(self) -> None:
        
        try:
            self.date = input('Ingresa la fecha para procesar datos (dia/mes/año): ')            
            self.company = input('Elige una empresa para iniciar variables (IEO - JCZ): ')
            if self.company not in ['IEO', 'JCZ']:
                raise ValueError                

            if self.company == 'IEO':
                self.cuenta_ingreso = "413554"
                self.name_company = "IEO SAS JULIAN"
                self.tercero_interno = "98771330"
                self.cuenta_iva_generado = "24080101"
                self.cuenta_costo = "613554"
                self.cuenta_iva_descontable = "24080201"
                self.nit_company = 901211276
            elif self.company == 'JCZ':
                self.cuenta_ingreso = "413010"
                self.name_company = "JCZ CONSTRUCCIONES"
                self.tercero_interno = "1040741062"
                self.cuenta_iva_generado = "24080110"
                self.cuenta_costo = "613501"
                self.cuenta_iva_descontable = "24080201"
                self.nit_company = 901365790
        except ValueError:
            logging.error('No selecciono una empresa adecuada')

    def file_factura(self,data1:pd.DataFrame,data2:pd.DataFrame)-> pd.DataFrame:

        '''Agregar data1 el Movimiento del mes y en la variable
        data2 agregar el formato de migración WO'''
        # Crear columna Subtotal

        data1["SUBTOTAL"] = data1["Total"] - data1["IVA"]
        facturas = pd.DataFrame(columns=data2.columns)
        # Filtramos dataset por las facturas electronicas emitidas
        data_emi = data1[(data1["Grupo"]=="Emitido")]
        data_emi = data_emi[(data_emi["Tipo de documento"]=="Factura electrónica")]
        data_emi.reset_index(inplace=True)
        # Solicitamos fecha para el archivo plano
        fecha = self.date
        # Intentamos crear un archivo plano para importar al sistema
        try:
            facturas["Encab: Tercero Externo"] = data_emi["NIT Receptor"]
            facturas["Encab: Tipo Documento"] = "NC"
            facturas["Detalle Con: IdCuentaContable"] = self.cuenta_ingreso
            facturas["Detalle Con: Nota"]= "Factura de Venta"
            facturas["Detalle Con: Tercero_Externo"] = data_emi["NIT Receptor"]
            facturas["Detalle Con: Débito"] = 0
            facturas["Detalle Con: Crédito"] = data_emi["SUBTOTAL"]
            facturas["Encab: Empresa"] = self.name_company
            facturas["Encab: Fecha"] = fecha
            facturas["Encab: Tercero Interno"] = self.tercero_interno
            facturas["Encab: Documento Número"] = data_emi["Folio"]
            facturas["Encab: Nota"] = data_emi["Folio"]
            facturas["Encab: Verificado"] = 0
            facturas["Encab: Anulado"] = 0
            # Agregamos el IVA a cada uno de los registros
            for i in range(len(facturas["Encab: Documento Número"])):
                iva = [self.name_company,"NC","",data_emi["Folio"][i],fecha,
                    self.tercero_interno,data_emi["NIT Receptor"][i],
                    "Factura de Venta " + str(data_emi["Folio"][i]),0,0,"","","","","",
                    "","","","","","","","","","","","",self.cuenta_iva_generado,"Factura de Venta",
                    data_emi["NIT Receptor"][i],"",0,(data_emi["SUBTOTAL"][i]) * 0.19,
                    "","","","","","","","","","","","","","",""]

                facturas.loc[len(facturas.index)] = iva

            document = list(facturas["Encab: Documento Número"])
            document = set(document)
            # Agregamos la cuenta por cobrar a los clientes
            for i in document:
                cc_cod = facturas.loc[facturas["Encab: Documento Número"] == i].reset_index()
                cxc = [self.name_company,"NC","",i,fecha,
                    self.tercero_interno,cc_cod["Encab: Tercero Externo"][0],
                    "Factura de Venta " + str(i),0,0,"","","","","",
                    "","","","","","","","","","","","","13050501","Factura de Venta",
                    cc_cod["Detalle Con: Tercero_Externo"][0],"",sum(cc_cod["Detalle Con: Crédito"]),0,
                    "","","","","","","","","","","","","","",""]
                facturas.loc[len(facturas.index)]  = cxc
            facturas = facturas.sort_values("Encab: Documento Número",ignore_index=True)
            # Creamos un consecutivo en el prefijo para que la importacion no arroje inconsistencias
            facturas["Encab: Prefijo"] = [i+1 for i in range(len(facturas["Encab: Tipo Documento"]))]
            logging.info("Los datos fueron transformados exitosamente")

            return facturas

        except Exception as e:
            logging.error(f'Fallo la creacion del archivo plano de facturas de venta: {e}')

    def file_compra(self,data1:pd.DataFrame,data2:pd.DataFrame)-> pd.DataFrame:
        '''Agregar data1 el Movimiento del mes y en la variable data2 
        agregar el formato de migración WO'''

        data1["SUBTOTAL"] = data1["Total"] - data1["IVA"]
        compras = pd.DataFrame(columns=data2.columns)
        data_rec = data1[(data1["Grupo"]=="Recibido") & (data1["Total"]!=0)] 
        data_rec = data_rec.reset_index()
        data_rec["%IVA"] = data_rec["IVA"] / data_rec["SUBTOTAL"]
        # Solicitamos fecha para el archivo plano
        fecha = self.date
        # Intentamos crear un archivo plano para importar al sistema
        try:
            compras["Encab: Tercero Externo"] = data_rec["NIT Emisor"]
            compras["Encab: Tipo Documento"] = "NC"
            compras["Detalle Con: IdCuentaContable"] = self.cuenta_costo
            compras["Detalle Con: Nota"]= "Factura de Compra"
            compras["Detalle Con: Tercero_Externo"] = data_rec["NIT Emisor"]
            compras["Detalle Con: Débito"] = data_rec["SUBTOTAL"]
            compras["Detalle Con: Crédito"] = 0
            compras["Encab: Empresa"] = self.name_company
            compras["Encab: Fecha"] = fecha
            compras["Encab: Tercero Interno"] = self.tercero_interno
            compras["Encab: Documento Número"] = 1000 + data_rec["Folio"]
            compras["Encab: Nota"] = data_rec["Folio"]
            compras["Encab: Verificado"] = 0
            compras["Encab: Anulado"] = 0
            # Agregamos el IVA a cada uno de los registros
            for i in range(len(compras["Encab: Documento Número"])):
                if data_rec["%IVA"][i] > 0 :
                    iva = [self.name_company,"NC","", data_rec["Folio"][i],fecha,
                        self.tercero_interno,data_rec["NIT Emisor"][i],
                        "Factura de Compra " + str(data_rec["Folio"][i]),0,0,"","","","","",
                        "","","","","","","","","","","","",self.cuenta_iva_descontable,"Factura de Compra",
                        data_rec["NIT Emisor"][i],"",(data_rec["SUBTOTAL"][i]) * 0.19,0,
                        "","","","","","","","","","","","","","",""]
                    compras.loc[len(compras.index)] = iva

            document = list(compras["Encab: Documento Número"])
            document = set(document)
            # Agregamos el banco a cada uno de los registros de compra
            for i in document:
                bc_cod = compras.loc[compras["Encab: Documento Número"] == i].reset_index()
                banco = [self.name_company,"NC","",i,fecha,
                    self.tercero_interno,bc_cod["Encab: Tercero Externo"][0],
                    "Factura de Compra " + str(i),0,0,"","","","","",
                    "","","","","","","","","","","","","11100501","Facturas de Compra",
                    bc_cod["Detalle Con: Tercero_Externo"][0],"",0,sum(bc_cod["Detalle Con: Débito"]),
                    "","","","","","","","","","","","","","",""]
                compras.loc[len(compras.index)]  = banco
            compras = compras.sort_values("Encab: Documento Número",ignore_index=True)
            # Creamos un consecutivo en el prefijo para que la importacion no arroje inconsistencias
            compras["Encab: Prefijo"] = [i+1 for i in range(len(compras["Encab: Tipo Documento"]))]
            logging.info("Los datos fueron transformados exitosamente")

            return compras

        except Exception as e:
            logging.error(f'Fallo la creacion del archivo de compras: {e}')

    def file_terceros_comp(self, data_dian:pd.DataFrame, data_format:pd.DataFrame)-> pd.DataFrame:

        '''Agregar data1 el Movimiento del mes y en la variable data2 
        agregar el formato de terceros WO'''

        try:                      

            type_adress = ['CL','CR', 'TV']
            type_letter = ['', 'A', 'B']
            type_cardinal = ['','SUR']
        
            data_emi = data_dian[data_dian['NIT Emisor'] != self.nit_company].reset_index()
       
            list_nits = list(data_emi['NIT Emisor'].unique())

            list_names = []

            for id in list_nits:
                name_id = data_emi.loc[data_emi["NIT Emisor"] == id, "Nombre Emisor"]
                list_names.append(name_id.iloc[0])

            data_format['No. Identificación'] = list_nits
            data_format['Tipo Identificación'] = 'NIT'
            data_format['1er. Nombre o Razón Social '] = list_names
            data_format['Ciudad Identificación'] = 'Medellín'
            data_format['Propiedad Activa'] = 'Proveedor; Cliente;'
            data_format['Activo'] = '-1'
            data_format['Propiedad Retención'] = 'Persona Juridica'
            data_format['Fecha Creación'] = self.date
            data_format['Plazo'] = 0
            data_format['Clasificación Dian'] = 'Normal'
            data_format['Tipo Dirección'] = 'Empresa/Oficina'
            data_format['Ciudad Dirección'] = 'Medellín'
            data_format['Dirección Principal'] = '-1'
            data_format['Teléfonos'] = '1234567'

            for x in range(len(data_format)):
                temp_nom = choice(type_adress)
                temp_n1 = randint(1,120)
                temp_n2 = randint(1,120)
                temp_card = choice(type_cardinal)
                temp_lett = choice(type_letter)
                data_format['Dirección'][x] = temp_nom + ' ' + str(temp_n1) + ' ' + temp_lett + temp_card + ' ' + str(temp_n2)

            logging.info('Creación exitosa de los terceros de compras')

            return data_format

        except AttributeError as e:
            logging.error(f'Los terceros no se puedieron procesar no hay información: {e}')

    def file_terceros_vent(self, data_dian:pd.DataFrame, data_format:pd.DataFrame)-> pd.DataFrame:

        '''Agregar data1 el Movimiento del mes y en la variable data2 
        agregar el formato de terceros WO'''

        try:        

            type_adress = ['CL','CR', 'TV']
            type_letter = ['', 'A', 'B']
            type_cardinal = ['','SUR']
         
            data_emi = data_dian[data_dian['NIT Receptor'] != self.nit_company].reset_index()  
            list_nits = list(data_emi['NIT Receptor'].unique())
            list_names = []

            for id in list_nits:
                name_id = data_emi.loc[data_emi["NIT Receptor"] == id, "Nombre Receptor"]
                list_names.append(name_id.iloc[0])

            data_format['No. Identificación'] = list_nits
            data_format['Tipo Identificación'] = 'NIT'
            data_format['1er. Nombre o Razón Social '] = list_names
            data_format['Ciudad Identificación'] = 'Medellín'
            data_format['Propiedad Activa'] = 'Proveedor; Cliente;'
            data_format['Activo'] = '-1'
            data_format['Propiedad Retención'] = 'Persona Juridica'
            data_format['Fecha Creación'] = self.date
            data_format['Plazo'] = 0
            data_format['Clasificación Dian'] = 'Normal'
            data_format['Tipo Dirección'] = 'Empresa/Oficina'
            data_format['Ciudad Dirección'] = 'Medellín'
            data_format['Dirección Principal'] = '-1'
            data_format['Teléfonos'] = '1234567'

            for x in range(len(data_format)):
                temp_nom = choice(type_adress)
                temp_n1 = randint(1,120)
                temp_n2 = randint(1,120)
                temp_card = choice(type_cardinal)
                temp_lett = choice(type_letter)
                data_format['Dirección'][x] = temp_nom + ' ' + str(temp_n1) + ' ' + temp_lett + temp_card + ' ' + str(temp_n2)

            logging.info('Creación exitosa de los terceros en ventas')
            
            return data_format
            
        except AttributeError as e:
            logging.error(f'Los terceros no se puedieron procesar no hay información: {e}')
  