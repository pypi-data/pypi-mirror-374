from datetime import datetime
import json
from os import getcwd, makedirs, path
from ..constants import *

class BaseHelper:

    def __init__(self):
        pass

class JsonHelper(BaseHelper):

    def save_json(self, filename, json_data):
        if json_data is None: return
        path_dir = path.join(getcwd(), 'output', 'json')
        if not path.exists(path_dir):
            makedirs(path_dir)

        with open(f"./output/json/{filename}.json", "w", encoding="utf-8") as json_file:
            json.dump( json_data, json_file, ensure_ascii=False, indent=4)

class JiraFieldsHelper(BaseHelper):

    def remove_null_fields(self, fields):
        fields_data_without_nulls = {}

        for key, value in fields.items():
            if value is not None:
                fields_data_without_nulls[key] = value

        return fields_data_without_nulls
    
    def _rename_fields(self, fields):
        fields = self._fields
        new_fields_data = {}

        for key, value in self._jira_fields.items():
            if value in fields:
                if "text" in fields[value]:
                    new_value = fields[value].get("text")
                elif "date" in fields[value]:
                    new_value = fields[value].get("date")
                elif "value" in fields[value]:
                    new_value = fields[value].get("value")
                else:
                    new_value = fields[value]

                new_fields_data[key] = new_value

        return new_fields_data
    
class GuiandoHelper(BaseHelper):
        
    def __init__(self):
        self._check_sefaz = lambda form_data: form_data[POSSUI_CHAVE_ACESSO][0] == "1"
        self._check_document_type = lambda document_type: 'ME21N' if document_type == "2" else 'FV60'

    def include_cod_sap_miro(self, cod_sap, miro):
        miro['referencia_pedido']['numero_pedido'] = cod_sap
        return miro
        
    ## Validar o Form com base no Sefaz
    def check_guiando_form(self, form_data, request_type):

        if request_type == ISSUE_TYPE_CONSUMO: 
            check_sefaz = self._check_sefaz(form_data)
            if check_sefaz: self._check_sefaz_form(form_data)
            self._check_consumo_form(form_data)
        pass

    def get_template_form(self, issue_data): 
        request_type = self._get_request_type(issue_data)
        template_form = self._get_template_form(request_type)
        return template_form

    def get_nf_type(self, form_data): self._get_nf_type(form_data)

    def get_request_type(self, form_data): return self._get_request_type(form_data)

    def match_form_fields(self, attachment, form_data):
        nf_type = self.get_nf_type(form_data)
        attachment_match = self._match_form_fields(attachment, form_data, nf_type)
        attachment_value_match = self._match_nf_value(attachment_match, form_data)
        return attachment_value_match

    def _check_sefaz_form(self, form_data):
        for sefaz_field in SEFAZ_FIELDS:
            if sefaz_field not in form_data: raise KeyError(f"ERRO - O campo {sefaz_field} não foi enviado.")
            if form_data[sefaz_field] is None or form_data[sefaz_field] == "" : raise KeyError(f"ERRO - O campo {sefaz_field} estA vazio.")
        pass

    def _check_fiscal_form(self, form_data):
        if 'nro_nota_fiscal' not in form_data: raise KeyError(f"ERRO - O Campo {'nro_nota_fiscal'} não foi enviado.")
        if form_data['nro_nota_fiscal'] is None or form_data['nro_nota_fiscal'] == "": raise KeyError(f"ERRO - O Campo {'nro_nota_fiscal'} estA vazio.")
        pass

    def _check_fatura_form(self, form_data):
        if 'nro_fatura' not in form_data: raise KeyError(f"ERRO - O Campo {'nro_fatura'} não foi enviado.")
        if form_data['nro_fatura'] is None or form_data['nro_fatura'] == "": raise KeyError(f"ERRO - O Campo {'nro_fatura'} estA vazio.")
        pass

    def _check_consumo_required_form(self, form_data):
        for field in form_data:
            if field not in OPTIONAL_FIELDS_CONSUMO and field not in SEFAZ_FIELDS:
                if form_data[field] is None or form_data[field] == "":raise KeyError(f"ERRO - O Campo {field} esta vazio")
        pass

    def _check_consumo_form(self, form_data):
        transition_type = self._get_transition_type(form_data)
        self._check_fiscal_form(form_data) if transition_type == SAP_NOTA_FISCAL else self._check_fatura_form(form_data)
        self._check_consumo_required_form(form_data)
        pass

    def _check_servico_required_form(self, form_data):
        for field in form_data:
            if field not in OPTIONAL_FIELDS_SERVICO and field not in SEFAZ_FIELDS:
                if form_data[field] is None or form_data[field] == "":raise KeyError(f"ERRO - O Campo {field} estA vazio")
        pass

    def _check_servico_form(self, form_data):
        transition_type = self._get_transition_type(form_data)
        self._check_fiscal_form(form_data) if transition_type == SAP_NOTA_FISCAL else self._check_fatura_form(form_data)
        self._check_servico_required_form(form_data)
        pass

    def _get_template_form(self, request_type):
        check_issue_type = request_type == ISSUE_TYPE_SERVICO
        request_type = FORM_TEMPLATE_SERVICO if check_issue_type else FORM_TEMPLATE_COMPLEMENTO
        return request_type
    
    def _get_request_type(self, issue_data): 
        return issue_data.get('fields')['customfield_10010']['requestType']['name']

    def _get_nf_type(self, form_data):
        nf_type_field = form_data["tipo_conta"]

        if nf_type_field == "AGUA":
            return COMPLEMENTO_DE_AGUA

        elif nf_type_field == "ENERGIA":
            return COMPLEMENTO_DE_ENERGIA

        elif nf_type_field == "GAS":
            return COMPLEMENTO_DE_GAS
        
    def _match_form_fields(self, attachment, form_data, nf_type):

        attachment[CNPJ_DO_FORNECEDOR] = form_data['cnpj_fornecedor']
        attachment[RAZAO_SOCIAL_DO_FORNECEDOR] = form_data['razao_social_fornecedor']
        attachment[CNPJ_DO_CLIENTE] = form_data['cnpj_destinatario']
        attachment[NUMERO_DA_FATURA] = form_data['nro_nota_fiscal']
        attachment[NUMERO_DA_FATURA_DO_FORNECEDOR] = form_data['nro_fatura']
        attachment[DATA_DE_EMISSAO] = form_data['data_emissao']
        attachment[DATA_DE_VENCIMENTO] = form_data['data_vencimento']
        attachment[CHAVE_DE_ACESSO_DA_FATURA] = form_data['chave_acesso']
        attachment[DATA_DE_REFERENCIA] = form_data['periodo_referencia']
        attachment["numero_log"] = form_data['protocolo_autorizacao']
        attachment["data_procmto"] = form_data['data_autorizacao']
        attachment["hora_procmto"] = form_data['hora_autorizacao']
        attachment[nf_type] = {
            "DataLeituraAnterior" : form_data['data_leitura_anterior'],
            "DataLeituraAtual"    : form_data['data_leitura_atual']
        }
        attachment["grupo_compradores"] = form_data['grupo_compradores']

        return attachment
    
    def _match_nf_value(self, attachment, form_data):

        if form_data['valor_liquido'] != "" and form_data['valor_liquido'] != None:
            attachment[VALOR_TOTAL_DA_FATURA] = form_data['valor_liquido']
        elif form_data['valor_nota'] != None and form_data['valor_nota'] != "":
            attachment[VALOR_TOTAL_DA_FATURA] = form_data['valor_nota']
        else:
            attachment[VALOR_TOTAL_DA_FATURA] = attachment.get(VALOR_TOTAL_DA_FATURA)

        return attachment
    

    
    def get_transition_type(self, complement_form):
        return self._get_transition_type(complement_form)

    def _get_transition_type(self, complement_form):
        
        try:

            if "transacao" in complement_form:
                transition_type = (
                    SAP_NOTA_FISCAL if complement_form["transacao"][0] == "1" else SAP_FATURA
                )

            elif "document_type" in complement_form:
                transition_type = (
                    SAP_NOTA_FISCAL if complement_form["document_type"][0] == "2" else SAP_FATURA
                )

            else:
                raise Exception(f"Nenhum tipo de processo encontrado.\nEx: Consumo, Serviço.")
        
        except Exception as e:
            raise Exception(f"Erro ao receber o tipo do processo,\nErro: {e}")

        return transition_type
    
    def prepare_attachment(self, attachment, complement_form, request_type, rateio_sintese_iten):

        model_value = {}

        if request_type != ISSUE_TYPE_SERVICO:
            nf_type_id = complement_form["tipo_conta"]
            nf_type = self._get_nf_type(nf_type_id, attachment)
            model_data = self._insert_complement_data_into_attachment_consumo(
                complement_form, attachment, nf_type
            )
            model_data[ALOCACOES_DE_CUSTO] = attachment[ALOCACOES_DE_CUSTO]
            model_value = self._calc_value(complement_form)

        else:
            model_data = self._insert_complement_data_into_attachment_servico(
                complement_form
            )

        return {**model_data, **model_value, **rateio_sintese_iten}
    
    def _get_nf_type(self, nf_type_id, attachment):

        if nf_type_id == "ÁGUA":
            nf_type = COMPLEMENTO_DE_AGUA

        elif nf_type_id == "ENERGIA":
            nf_type = COMPLEMENTO_DE_ENERGIA

        elif nf_type_id == "GÁS":
            nf_type = COMPLEMENTO_DE_GAS

        else:
            if attachment[COMPLEMENTO_DE_AGUA] is not None:
                nf_type = COMPLEMENTO_DE_AGUA
            elif attachment[COMPLEMENTO_DE_ENERGIA] is not None:
                nf_type = COMPLEMENTO_DE_ENERGIA
            elif attachment[COMPLEMENTO_DE_GAS] is not None:
                nf_type = COMPLEMENTO_DE_GAS

        return nf_type

    def _insert_complement_data_into_attachment_consumo(
        self, complement_form, attachment, nf_type
    ):

        model_data = {
            CNPJ_DO_FORNECEDOR: complement_form["cnpj_fornecedor"],
            RAZAO_SOCIAL_DO_FORNECEDOR: complement_form["razao_social_fornecedor"],
            CNPJ_DO_CLIENTE: complement_form["cnpj_destinatario"],
            NUMERO_DA_FATURA: complement_form["nro_nota_fiscal"],
            NUMERO_DA_FATURA_DO_FORNECEDOR: complement_form["nro_fatura"],
            DATA_DE_EMISSAO: complement_form["data_emissao"],
            DATA_DE_VENCIMENTO: complement_form["data_vencimento"],
            CHAVE_DE_ACESSO_DA_FATURA: complement_form["chave_acesso"],
            DATA_DE_REFERENCIA: complement_form["periodo_referencia"],
            PROTOCOLO_AUTORIZACAO: complement_form["protocolo_autorizacao"],
            DATA_AUTORIZACAO: complement_form["data_autorizacao"],
            HORA_AUTORIZACAO: complement_form["hora_autorizacao"],
            GRUPO_COMPRADORES: complement_form["grupo_compradores"],
            ALOCACOES_DE_CUSTO: attachment[ALOCACOES_DE_CUSTO],
            nf_type: {
                "DataLeituraAnterior": complement_form["data_leitura_anterior"],
                "DataLeituraAtual": complement_form["data_leitura_atual"],
            },
        }

        return model_data

    def _insert_complement_data_into_attachment_servico(self, complement_form):

        model_data = {
            CNPJ_DO_FORNECEDOR: complement_form["cnpj_fornecedor"],
            CNPJ_DO_CLIENTE: complement_form["cnpj_destinatario"],
            RAZAO_SOCIAL_DO_FORNECEDOR: complement_form["razao_fornecedor"],
            CODIGO_DE_SERVICO: complement_form["cod_servico"],
            CODIGO_SAP_SERVICO: complement_form["sap_cod_servico"],
            CODIGO_FORNECEDOR: complement_form["sap_cod_fornecedor"],
            NUMERO_FISCAL: complement_form["nro_nota_fiscal"],
            DATA_DE_EMISSAO: complement_form["data_emissao"],
            UNIDADE_LOJA: complement_form["unidade_loja"],
            CODIGO_IMPOSTO: complement_form["codigo_imposto"],
            GRUPO_COMPRADORES: complement_form["grupo_compradores"],
            VALOR_TOTAL_DA_FATURA: complement_form["valor_nota"],
            ORDEM_INTERNA: complement_form["ord_interna"],
            CODIGO_VERIFICACAO: complement_form["cod_verificacao"],
            TEXTO_BREVE: complement_form["texto_breve"],
            CENTRO_DE_CUSTO: complement_form["centro_custo"],
            CONTA_RAZAO: complement_form["conta_razao"],
            IMPOSTO_SEM_RETENCAO: IMPOSTO_SEM_RETENCAO in complement_form and complement_form[IMPOSTO_SEM_RETENCAO] is not None and len(complement_form[IMPOSTO_SEM_RETENCAO]) and complement_form[IMPOSTO_SEM_RETENCAO][0]['value'] == SEM_RETENCAO
        }

        return model_data

    def _calc_value(self, complement_form):

        model_value = {
            VALOR_TOTAL_DA_FATURA: float(
                complement_form["valor_nota"].replace(".", "").replace(",", ".")
            ),
            VALOR_LIQUIDO_DA_FATURA: 0,
            JUROS_DA_FATURA: 0,
        }
        if (
            complement_form["valor_liquido"] != ""
            and complement_form["valor_liquido"] != None
        ):
            model_value[VALOR_LIQUIDO_DA_FATURA] = float(
                complement_form["valor_liquido"].replace(".", "").replace(",", ".")
            )
        if complement_form["juros"] != "" and complement_form["juros"] != None:
            model_value[JUROS_DA_FATURA] = float(
                complement_form["juros"].replace(".", "").replace(",", ".")
            )

        return model_value