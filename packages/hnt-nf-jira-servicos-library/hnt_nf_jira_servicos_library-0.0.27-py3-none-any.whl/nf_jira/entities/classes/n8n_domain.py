import requests
from ..constants import *

class N8NDomain:

    def get_nf_domain(self, type, cnpj):

        n8n_data = self._get_nf_domain_data(cnpj, type)
        return n8n_data

    def get_nf_sap_domain(self, cod_sap_service):

        n8n_data = self._get_nf_sap_domain_data(cod_sap_service)
        return n8n_data

    def _get_nf_domain_data(self, cnpj, type):

        try:
            domain_request = requests.get(
                f"{API_DOMAIN_N8N_URL}/{'fornecedores' if type == 'fornecedor' else 'centros'}?cnpj={cnpj}",
                auth=N8N_AUTH,
            )
            domain_request.raise_for_status()
            domain_data = domain_request.json()

            if not domain_data:
                raise Exception(f"Could not find domain, cnpj: {cnpj}")

        except Exception as e:
            raise Exception(f"Erro ao receber {type}:\n{e}")

        return domain_data

    def _get_nf_sap_domain_data(self, cod_nf_sap_service):

        try:
            domain_request = requests.get(
                f"{API_DOMAIN_N8N_URL}/codigo_servico_sap?codigo_servico_sap={cod_nf_sap_service}",
                auth=N8N_AUTH,
            )
            domain_request.raise_for_status()
            domain_data = domain_request.json()

            if not domain_data:
                raise Exception(f"Could not find domain, codigo_servico_sap: {cod_nf_sap_service}")

        except Exception as e:
            raise Exception(f"Erro ao receber dados de serviço:\n{e}")

        return domain_data
