from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
import logging

# Configuração de logs
logging.basicConfig(
    level=logging.DEBUG,  # Define o nível de log
    format='%(asctime)s - %(levelname)s - %(message)s'  # Formato da mensagem
)

# Informações de conexão com o LDAP
AD_ADMIN_USER = "administrator"
AD_ADMIN_PASSWORD = "&ajhsRlm88s!@SF"
AD_DOMAIN = "digitalup.intranet"
AD_SERVER = f"ldap://{AD_DOMAIN}"  # Use ldaps:// para conexões seguras

# Dados do usuário a ser pesquisado
user_to_search = "rafael.zelak"

# Mapeamento de palavras-chave para empresas
GROUP_TO_COMPANY = {
    "sittax": "Sittax",
    "acessorias": "Acessórias",
    "best": "BestDoctors",
    "adv": "AdvEasy",
}

def get_user_company(ad_server, admin_user, admin_password, domain, username):
    conn = None  # Garante que a variável está inicializada
    try:
        # Configuração do servidor LDAP
        server = Server(ad_server, get_info=ALL)
        logging.info(f"Conectando ao servidor LDAP: {ad_server}")

        # Autenticação no LDAP (formato user@domain)
        user = f"{admin_user}@{domain}"
        conn = Connection(server, user=user, password=admin_password, auto_bind=True)
        logging.info("Conexão LDAP estabelecida com sucesso.")

        # Base de pesquisa no Active Directory
        search_base = f"DC={domain.replace('.', ',DC=')}"
        logging.info(f"Base de pesquisa configurada: {search_base}")

        # Filtro para localizar o usuário pelo atributo sAMAccountName
        search_filter = f"(sAMAccountName={username})"
        logging.info(f"Filtro de pesquisa configurado: {search_filter}")

        # Realiza a pesquisa no AD
        conn.search(
            search_base,
            search_filter,
            search_scope=SUBTREE,
            attributes=["memberOf"]  # Solicita o atributo que contém os grupos do usuário
        )

        # Verifica se o usuário foi encontrado
        if conn.entries:
            user_entry = conn.entries[0]
            logging.info(f"Usuário encontrado: {user_entry}")

            # Extrai os grupos do atributo 'memberOf'
            groups = user_entry.memberOf.values if "memberOf" in user_entry else []

            # Processa apenas os nomes comuns (CN) dos grupos
            cn_groups = [group.split(",")[0].replace("CN=", "").lower() for group in groups]

            # Procura pelos grupos de interesse
            for key, company in GROUP_TO_COMPANY.items():
                if any(key in group for group in cn_groups):
                    return {"user": username, "empresa": company}
            return None
        else:
            return None

    except Exception as e:
        logging.error(f"Erro ao buscar grupos: {str(e)}")
        return None

    finally:
        # Finaliza a conexão caso esteja aberta
        if conn and conn.bound:
            conn.unbind()
            logging.info("Conexão LDAP encerrada.")

# Executa a função para buscar a empresa do usuário
result = get_user_company(AD_SERVER, AD_ADMIN_USER, AD_ADMIN_PASSWORD, AD_DOMAIN, user_to_search)

# Exibe o resultado
if result:
    print(f"Usuário: {result['user']}, Empresa: {result['empresa']}")
else:
    print("Nenhuma empresa encontrada para o usuário.")
