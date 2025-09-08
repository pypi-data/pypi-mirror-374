import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
from datetime import datetime
from typing import Dict, Any, List, Optional


class SeiProcessSearchError(Exception):
    """Exceção personalizada para erros de busca no SEI."""
    pass


class SeiRegisterSearcher:
    """
    Classe responsável por realizar consultas de processos no SEI (ANP).
    Suporta paginação e múltiplas pesquisas com filtros dinâmicos.
    """

    BASE_URL = (
        "https://sei.anp.gov.br/sei/modulos/pesquisa/md_pesq_controlador_ajax_externo.php"
        "?acao_ajax_externo=protocolo_pesquisar&id_orgao_acesso_externo=0"
        "&isPaginacao=true"
    )

    DEFAULT_FORM_DATA = {
        "txtProtocoloPesquisa": "",
        "q": "",
        "chkSinProcessos": "P",
        "txtParticipante": "",
        "hdnIdParticipante": "",
        "txtUnidade": "",
        "hdnIdUnidade": "",
        "selTipoProcedimentoPesquisa": "",
        "selSeriePesquisa": "",
        "txtDataInicio": "",   # Obrigatório
        "txtDataFim": "",      # Obrigatório
        "txtInfraCaptcha": "2MI42G",
        "hdnInfraCaptcha": "1",
        "txtNumeroDocumentoPesquisa": "",
        "txtAssinante": "",
        "hdnIdAssinante": "",
        "txtDescricaoPesquisa": "",
        "txtAssunto": "",
        "hdnIdAssunto": "",
        "txtSiglaUsuario1": "",
        "txtSiglaUsuario2": "",
        "txtSiglaUsuario3": "",
        "txtSiglaUsuario4": "",
        "hdnSiglasUsuarios": "",
        "hdnCId": "PESQUISA_PUBLICA1757167558039",
        "partialfields": "",
        "requiredfields": "",
        "as_q": "",
        "hdnFlagPesquisa": "1",
    }

    def __init__(self, start_date: Optional[str] = None, end_date: Optional[str] = None, **optional_filters: Any):
        """
        Inicializa a consulta ao SEI.
        :param start_date: Data de início no formato DD/MM/YYYY.
                          Se não for informada, será usada a data atual.
        :param optional_filters: Demais parâmetros opcionais aceitos pelo formulário.
        """
        if not start_date:
            start_date = datetime.today().strftime("%d/%m/%Y")

        if not end_date:
            end_date = datetime.today().strftime("%d/%m/%Y")

        self.search_params = self.DEFAULT_FORM_DATA.copy()
        self.set_filters(start_date=start_date, end_date=end_date, **optional_filters)

    def set_filters(self, start_date: Optional[str] = None, end_date: Optional[str] = None, filters: Optional[Any] = {}):
        """
        Atualiza os filtros da pesquisa. Pode ser chamado várias vezes.
        :param start_date: Data de início (DD/MM/YYYY).
        :param end_date: Data de fim (DD/MM/YYYY).
        :param filters: Outros parâmetros opcionais.
        """

        if start_date:
            self.search_params["txtDataInicio"] = start_date
        if end_date:
            self.search_params["txtDataFim"] = end_date

        if not self.search_params["txtDataInicio"] or not self.search_params["txtDataFim"]:
            raise ValueError("Os campos 'start_date' e 'end_date' são obrigatórios.")

        for key, value in filters.items():
            if key in self.search_params:
                self.search_params[key] = value

        # Atualiza campo partialfields baseado nas datas
        
        iso_start = self._to_iso_format(self.search_params["txtDataInicio"])
        iso_end = self._to_iso_format(self.search_params["txtDataFim"])
        self.search_params["partialfields"] = (
            f"sta_prot:P AND (dta_ger:[{iso_start} TO {iso_end}] "
            f"OR dta_inc:[{iso_start} TO {iso_end}])"
        )

    def execute_search(self, page: int = 0, rows_per_page: int = 50) -> List[Dict[str, Any]]:
        """
        Executa a requisição de busca no SEI.
        :param page: Número da página (0 = primeira).
        :param rows_per_page: Quantidade de registros por página.
        :return: Lista de dicionários com os resultados da pesquisa.
        """
        inicio = page * rows_per_page
        url = f"{self.BASE_URL}&inicio={inicio}&rowsSolr={rows_per_page}"
        try:
            response = requests.post(url, data=self.search_params)
            response.raise_for_status()
        except requests.RequestException as e:
            raise SeiProcessSearchError(f"Erro na requisição ao SEI: {e}")

        return self._parse_response(response.text)

    @staticmethod
    def _to_iso_format(date_str: str) -> str:
        """Converte DD/MM/YYYY para formato ISO esperado pelo SEI."""
        try:
            date_obj = datetime.strptime(date_str, "%d/%m/%Y")
            return date_obj.strftime("%Y-%m-%dT00:00:00Z")
        except ValueError:
            raise ValueError(f"Data inválida: {date_str}. Use o formato DD/MM/YYYY.")

    @staticmethod
    def _parse_response(raw_response: str) -> List[Dict[str, Any]]:
        """Faz o parse da resposta XML/HTML do SEI."""
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
        soup = BeautifulSoup(raw_response, "lxml")

        resultados = []

        # cada resultado vem em pares de <tr class="pesquisaTituloRegistro"> e o <tr> seguinte
        registros = soup.find_all("tr", class_="pesquisaTituloRegistro")

        for reg in registros:
            # protocolo e descrição
            link = reg.find("a", class_="protocoloNormal")
            if not link:
                continue

            protocolo = link.text.strip()
            descricao = reg.get_text(" ", strip=True).replace(protocolo, "").replace("Registro:", "").strip()
            url_processo = link.get("href")

            # unidade e data (estão na próxima linha <tr>)
            tr_next = reg.find_next_sibling("tr")
            unidade = tr_next.find("a", class_="ancoraSigla")
            unidade = unidade.text.strip() if unidade else ""
            data = ""
            for td in tr_next.find_all("td"):
                if "Data:" in td.get_text():
                    data = td.get_text().replace("Data:", "").strip()

            resultados.append({
                "protocolo": protocolo,
                "descricao": descricao,
                "unidade": unidade,
                "data": data,
                "link": url_processo
            })

        return resultados