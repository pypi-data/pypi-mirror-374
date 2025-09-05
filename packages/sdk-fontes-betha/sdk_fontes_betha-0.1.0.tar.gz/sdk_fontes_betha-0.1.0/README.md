# SDK Requisições Betha

Um SDK Python para facilitar requisições e autorização em fontes de dados do Betha Cloud.

## 📋 Descrição

Este SDK fornece uma interface simplificada para realizar consumos autenticados para os serviços de fontes de dados do Betha Cloud

## 🚀 Instalação

```bash
pip install sdk-fontes-betha
```

## 📦 Funcionalidades

- **Autenticação Aplicação de tela**: Para correto consumo de fontes
- **Filtros e ordenação**: Suporte completo para uso de critério e ordenação
- **Validação de Token**: Verificação automática da validade do token
- **Refresh Automático**: Renovação automática do token quando necessário

## 🛠️ Uso

### Importação

```python
from sdk_fontes_betha import Autorizacao_fontes, Fonte_dados
```

### Exemplo Completo

```python
from sdk_fontes_betha import Autorizacao, Fonte_dados

autorizacaoFolha = Autorizacao(
    client_id="seu_client_id",
    redirect_uri="sua_redirect_uri",
    token="seu_token",
    user_access="https://folha.betha.cloud/"
)

#######
dados = Fonte_dados(
    url="https://folha-dados-v2.betha.cloud/folha/dados/api/funcionarios-cargos",
    autorizacao=autorizacaoFolha
).buscar(criterio="id in (123, 321)")
###Retorno será uma lista com o dado que possui o id contido em (123, 321)

######
dados = Fonte_dados(
    url="https://folha-dados-v2.betha.cloud/folha/dados/api/funcionarios-cargos",
    autorizacao=autorizacaoFolha
).buscar(criterio="id = 123", primeiro=True)
###Retorno será um objeto com o dado que possui o id 123

######
dados = Fonte_dados(
    url="https://folha-dados-v2.betha.cloud/folha/dados/api/funcionarios-cargos",
    autorizacao=autorizacaoFolha
).buscarPaginado(criterio="vinculo.id = 123", limit=200, offset=0)
###Retorno será 200 objetos, a partir do objeto 0, que possuem vinculo.id = 123

print (dados)
```

## 🔧 Parâmetros das Classes

### Autorizacao
- `token`: Token de acesso (Obtido através do F12)
- `user_access`: Token de acesso do usuário (Obtido através do F12)
- `client_id`: ID do cliente da aplicação (Pode ser obtido através da API de token info)
- `redirect_uri`: URI de redirecionamento

### Fonte_dados
- `authorization`: Instância de `Autorizacao`
- `url`: URL da fonte obtida através do "copiar path" ![imagemPath](image.png)
- `criterio`: String para realização de filter
- `ordenacao`: String para realização de sort

## 📋 Requisitos

- Python >= 3.7
- requests >= 2.0.0

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 👨‍💻 Autor

**Fernando Favaro Bonetti**
- Email: FernandoEuBonetti@gmail.com