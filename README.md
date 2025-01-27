# Sistema de Gerenciamento de Leads

Sistema web desenvolvido em Flask para gerenciamento de leads e empresas.

## 🚀 Funcionalidades

- Autenticação de usuários com Active Directory
- Gerenciamento de empresas/leads
- Integração com Casa dos Dados
- Integração com Bitrix24 CRM (múltiplos SPAs)
- Interface moderna e responsiva

## 💻 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone [url-do-repositorio]
cd leadsSetup
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente:
- Crie um arquivo `.env` na raiz do projeto
- Adicione as variáveis necessárias (veja o exemplo em `.env.example`)
  - `BITRIX_WEBHOOK_URL`: URL do webhook do Bitrix24
  - `AD_ADMIN_USER`: Usuário administrador do Active Directory
  - `AD_ADMIN_PASSWORD`: Senha do administrador do Active Directory
  - `AD_DOMAIN`: Domínio do Active Directory

## 🚀 Executando o projeto

1. Ative o ambiente virtual (se ainda não estiver ativo)
2. Execute o servidor:
```bash
python run.py
```
3. Acesse `http://localhost:5000` no seu navegador

## 🛠️ Tecnologias Utilizadas

- Flask - Framework web
- SQLAlchemy - ORM
- Bootstrap - Framework CSS
- JavaScript - Interatividade no frontend
- Casa dos Dados API - Integração para dados de empresas
- Bitrix24 API - Integração para CRM
- LDAP3 - Integração com Active Directory

## 📁 Estrutura do Projeto

```
leadsSetup/
├── app/
│   ├── models/         # Modelos do banco de dados
│   ├── routes/         # Rotas da aplicação
│   ├── services/       # Serviços e lógica de negócio
│   │   ├── bitrix/     # Serviços de integração com Bitrix24
│   │   └── auth/       # Serviços de autenticação
│   ├── static/         # Arquivos estáticos (CSS, JS)
│   └── templates/      # Templates HTML
├── venv/              # Ambiente virtual (não versionado)
├── .env              # Variáveis de ambiente (não versionado)
├── requirements.txt   # Dependências do projeto
└── run.py            # Arquivo principal para execução
```

## 🔄 Integração com Bitrix24

O sistema integra automaticamente com múltiplos SPAs do Bitrix24 CRM baseado no grupo do usuário:

### Grupos e SPAs

- **Acessórias**
  - EntityTypeId: 187
  - CategoryId: 171
  - StageId: DT187_171:NEW

- **BestDoctors**
  - EntityTypeId: 180
  - CategoryId: 167
  - StageId: DT180_167:NEW

- **Sittax**
  - EntityTypeId: 180
  - CategoryId: 167
  - StageId: DT180_167:NEW

### Campos Personalizados

Cada SPA possui seus próprios campos personalizados, incluindo:
- Nome Fantasia
- Razão Social
- CNPJ
- Telefones
- Email
- Endereço
- Sócios
- Valor
- Origem (Automação Lead)

### Roteamento Automático

O sistema automaticamente:
1. Identifica o grupo do usuário através do Active Directory
2. Roteia a requisição para o SPA correto baseado no grupo
3. Formata os dados de acordo com os campos personalizados específicos do SPA
4. Envia os dados com a configuração correta para o Bitrix24

## 👥 Autores

- Seu Nome

## 📄 Licença

Este projeto está sob a licença [sua licença] - veja o arquivo LICENSE.md para detalhes.