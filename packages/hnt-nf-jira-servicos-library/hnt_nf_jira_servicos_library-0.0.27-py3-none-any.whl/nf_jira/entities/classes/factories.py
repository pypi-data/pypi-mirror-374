from datetime import datetime
from ..constants import *
from .helper import GuiandoHelper

class Factories:

    def __init__(self) -> None:
        self.GuiandoHelper = GuiandoHelper()
        pass
    def nota_pedido_item_factory(self, json_data: dict):
        if len(json_data['item']) == 0:
            return [{
                "nro_servico": json_data[CODIGO_SAP_SERVICO][0],
                "centro_custo": f"{json_data[CENTRO_DE_CUSTO][0]}" if CENTRO_DE_CUSTO in json_data and json_data[CENTRO_DE_CUSTO] != None else None,
                "ord_interna": f"{json_data[ORDEM_INTERNA][0]}" if ORDEM_INTERNA in json_data and json_data[ORDEM_INTERNA] != None else None,
                "valor_bruto": float(json_data[VALOR_TOTAL_DA_FATURA].replace('.','').replace(',','.'))
            }]
        item = []
        for rateio in json_data['item']:
            item.append({
                "nro_servico": json_data[CODIGO_SAP_SERVICO][0],
                "centro_custo": rateio['centro_custo'],
                "ord_interna": f"{json_data[ORDEM_INTERNA][0]}" if ORDEM_INTERNA in json_data and json_data[ORDEM_INTERNA] != None else None,
                "valor_bruto": rateio['valor_bruto']               
            })
        return item

    def nota_pedido_servico_factory(self, issue: dict):

        sintese_itens = []

        item = {
            "nro_servico": issue["json_data"][CODIGO_SAP_SERVICO][0],
            "centro_custo": f"{issue['json_data'][CENTRO_DE_CUSTO][0]}" if CENTRO_DE_CUSTO in issue["json_data"] and issue["json_data"][CENTRO_DE_CUSTO] != None else None,
            "ord_interna": f"{issue['json_data'][ORDEM_INTERNA][0]}" if ORDEM_INTERNA in issue["json_data"] and issue["json_data"][ORDEM_INTERNA] != None else None,
            "valor_bruto": float(issue["json_data"][VALOR_TOTAL_DA_FATURA].replace('.','').replace(',','.'))
        }

        fatura = {
            "cod_imposto": issue['json_data'][CODIGO_IMPOSTO]
        }

        sintese_item = {
            "categoria_cc": "F" if item['ord_interna'] is not None else "K",
            "centro": issue['domain_data']['centro']['centro'],
            "texto_breve": issue['json_data']["texto_breve"],
            "fatura": fatura,
            "grp_mercadorias": issue["domain_data"]["sap_service"]["grpmercads"],
            "item": self.nota_pedido_item_factory(issue["json_data"])
        }

        sintese_itens.append(sintese_item)



        nota_pedido_servico = {
            "org_compras": issue['domain_data']["centro"]["org_compras"],
            "grp_compradores": issue['json_data'][GRUPO_COMPRADORES][0],
            "cod_fornecedor": issue["json_data"][CODIGO_FORNECEDOR] if CODIGO_FORNECEDOR in issue["json_data"] and issue["json_data"][CODIGO_FORNECEDOR] else None,
            "sintese_itens": sintese_itens,
            "anexo": issue['pdf_data'],
        }

        return nota_pedido_servico

    def miro_factory(self, issue: dict, pedido=None):

        dados_basicos = {
            "data_da_fatura": datetime.strptime(
                issue['json_data'][DATA_DE_EMISSAO], "%Y-%m-%d"
            ).strftime("%d.%m.%Y"),
            "referencia": f"{issue['json_data'].get(NUMERO_FISCAL)[-MAX_LEN_NRO_NF:].rjust(MAX_LEN_NRO_NF, '0')}-{SERIE_NF}",
            "montante": float(issue['json_data'][VALOR_TOTAL_DA_FATURA].replace('.','').replace(',','.')),
            "texto": issue['domain_data']['sap_service']['lista_concatenada'][issue['domain_data']['sap_service']['lista_concatenada'].find(' - ') + 3:]
        }
        referencia_pedido = { "numero_pedido": pedido }
        detalhe = {
            "ctg_nf": "Y6"
            }

        miro_model = {
            "dados_basicos": dados_basicos,
            "referencia_pedido": None if pedido is None else { "numero_pedido": pedido },
            "detalhe": detalhe,
            "imposto": { "sem_retencao": True } if issue['json_data'][IMPOSTO_SEM_RETENCAO] else None
        }
        return miro_model
    
    def fatura_factory(self, issue): 

        texto = datetime.strptime(issue['json_data'][DATA_DE_EMISSAO], "%Y-%m-%d").strftime("%b/%y").upper()
        itens = {
                    "cta_razao": issue['json_data'][CONTA_RAZAO][0], #Conta Contabil SAP
                    "montante":  float(issue['json_data'][VALOR_TOTAL_DA_FATURA].replace('.','').replace(',','.')),
                    "percentage" : CEM_PORCENTO_DO_VALOR_BRUTO,
                    "loc_negocios": issue['domain_data']['centro']['centro'],
                    "atribuicao": datetime.strptime(issue['json_data'][DATA_DE_EMISSAO], "%Y-%m-%d").strftime("%Y%m%d"),
                    "texto": texto,
                    "centro_custo":  f"{issue['domain_data']['centro']['centro_custo']}"
                }

        dados_basicos = {
            "cod_fornecedor": issue['json_data'][CODIGO_FORNECEDOR], #ID_EXTERNO_SAP
            "data_fatura": datetime.strptime(issue['json_data'][DATA_DE_EMISSAO], "%Y-%m-%d").strftime("%d.%m.%Y"),
            "referencia": issue['json_data'][NUMERO_FISCAL],
            "montante": float(issue['json_data'][VALOR_TOTAL_DA_FATURA].replace('.','').replace(',','.')),
            "bus_pl_sec_cd": itens["loc_negocios"],
            "texto": texto,
            "itens": [itens]
        }

        pagamento = {
            "data_basica": datetime.now().strftime("%d.%m.%Y"),
            "cond_pgto": "0000" #CONSTANTE 
        }

        fatura_model = {
            "dados_basicos": dados_basicos,
            "pagamento":pagamento,
        }

        return fatura_model