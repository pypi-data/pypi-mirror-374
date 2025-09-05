import requests
import json

class Autorizacao:
    def __init__(self:str, client_id:str, redirect_uri:str, token:str, user_access:str):
        self.client_id = client_id
        self.scopes = [
            "campos-adicionais.suite",
            "contas-usuarios.suite",
            "dados.suite",
            "gerenciador-configuracoes.suite",
            "gerenciador-relatorios.suite",
            "gerenciador-scripts.suite",
            "licenses.suite",
            "modelo-dados.suite",
            "naturezas.suite",
            "notifications.suite",
            "quartz.suite",
            "sistema_interno",
            "user-accounts.suite"
        ]
        self.redirect_uri = redirect_uri
        self.token = token
        self.user_access = user_access

    def getToken(self):
        return 'Bearer ' + str(self.token)

    def getUserAccess(self):
        return str(self.user_access)

    @property
    def dict_header(self):
        return {"authorization": self.getToken(), "user-access": self.getUserAccess()}

    def refresh(self):
        novo_token = requests.get(url="https://plataforma-oauth.betha.cloud/auth/oauth2/authorize",
                                   params={'client_id': self.client_id,
                                           'response_type': 'token',
                                           'redirect_uri': self.redirect_uri,
                                           'silent': 'true',
                                           'callback': '',
                                           'bth_ignore_origin': 'true',
                                           'previous_access_token': self.token
                                           })
        novo_token = json.loads(novo_token.text.replace("(", "").replace(")", "")).get("accessToken")
        
        print("""--------------Token expirado--------------""")
        print("""------------Atualizando token-------------""")
        print(novo_token)
        print("""------------------------------------------""")

        self.token = novo_token
        return novo_token

    @property
    def infos(self):
        request = requests.get(url='https://plataforma-oauth.betha.cloud/auth/oauth2/tokeninfo',
                         params={"access_token": self.token})
        return request.json()

    def valid(self):
        return not self.infos.get("expired")