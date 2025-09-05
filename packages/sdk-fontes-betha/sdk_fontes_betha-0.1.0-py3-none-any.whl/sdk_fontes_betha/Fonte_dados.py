import requests
from .Autorizacao_fontes import Autorizacao

class Fonte_dados:
    def __init__(self, url: str, autorizacao: Autorizacao = None):
        self.url = url
        self.autorizacao = autorizacao
        self.tentou_atualizar_token = False
    
    def buscarPaginado(self, offset:int, limit:int, criterio:str=None, ordenacao:str=None) -> requests.Request:
        params = {k: v for k, v in (("offset", offset), ("limit", limit), ("filter", criterio), ("sort", ordenacao)) if v is not None}
        req = requests.request(
            method="GET",
            url=self.url,
            headers={
                **self.autorizacao.dict_header
            },
            params=params
        )
        
        if (not req.ok) and (req.status_code == 401) and (not self.tentou_atualizar_token):
            self.tentou_atualizar_token = True
            self.autorizacao.refresh()
            return self.buscarPaginado(offset=offset, limit=limit, criterio=criterio, ordenacao=ordenacao)

        return req.json()
    
    def buscar(self, criterio:str=None, ordenacao:str=None, primeiro:bool=False) -> object:
        dados = []
        offset = 0
        limit = 200
        if primeiro:
            return self.buscarPaginado(offset=0, limit=1, criterio=criterio, ordenacao=ordenacao)['content'][0]

        while True:
            req = self.buscarPaginado(offset=offset, limit=limit, criterio=criterio, ordenacao=ordenacao)
            dados.append(req['content'])
            
            if not req['hasNext']:
                break
            
            offset += limit
        
        return dados
