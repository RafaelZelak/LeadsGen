from ldap3 import Server, Connection, ALL, ALL_ATTRIBUTES, SUBTREE, LEVEL
from flask import session
from decouple import config

class AuthService:
    @staticmethod
    def get_admin_connection():
        try:
            domain = config('AD_DOMAIN')
            admin_user = config('AD_ADMIN_USER')
            admin_password = config('AD_ADMIN_PASSWORD')

            server = Server(domain, get_info=ALL_ATTRIBUTES)
            admin_conn = Connection(
                server,
                user=f'{admin_user}@{domain}',
                password=admin_password,
                authentication='SIMPLE'
            )

            if admin_conn.bind():
                return admin_conn
            else:
                return None
        except Exception as e:
            return None

    @staticmethod
    def get_user_groups(username, admin_conn):
        try:
            domain = config('AD_DOMAIN')
            ad_server = f"ldap://{domain}"

            # Configuração do servidor LDAP
            server = Server(ad_server, get_info=ALL_ATTRIBUTES)

            # Base de pesquisa no Active Directory
            search_base = f"DC={domain.replace('.', ',DC=')}"

            # Filtro para localizar o usuário pelo atributo sAMAccountName
            search_filter = f"(sAMAccountName={username})"

            # Realiza a pesquisa no AD
            success = admin_conn.search(
                search_base,
                search_filter,
                search_scope=SUBTREE,
                attributes=["memberOf"]  # Solicita o atributo que contém os grupos do usuário
            )

            # Verifica se o usuário foi encontrado
            if success and admin_conn.entries:
                user_entry = admin_conn.entries[0]

                # Extrai os grupos do atributo 'memberOf'
                groups = user_entry.memberOf.values if hasattr(user_entry, 'memberOf') else []

                # Processa apenas os nomes comuns (CN) dos grupos
                cn_groups = [group.split(",")[0].replace("CN=", "") for group in groups]

                return cn_groups
            else:
                return []

        except Exception as e:
            import traceback
            return []

    @staticmethod
    def get_user_group():
        groups = session.get('user_groups', [])

        # Mapeamento de palavras-chave para empresas (igual ao teste.py)
        GROUP_TO_COMPANY = {
            "sittax": "Sittax",
            "acessorias": "Acessórias",
            "best": "BestDoctors",
            "adv": "AdvEasy",
        }

        # Processa apenas os nomes dos grupos
        cn_groups = [group.lower() for group in groups]

        # Procura pelos grupos de interesse
        for key, company in GROUP_TO_COMPANY.items():
            if any(key in group for group in cn_groups):
                return company

        return None

    @staticmethod
    def authenticate(username, password):
        try:
            domain = config("AD_DOMAIN")
            server = Server(domain, get_info=ALL_ATTRIBUTES)
            user = f'{username}@{domain}'

            # Primeiro valida as credenciais do usuário
            conn = Connection(server, user=user, password=password)

            if not conn.bind():
                return False

            conn.unbind()

            # Credenciais de admin vindas do .env
            admin_user = config("AD_ADMIN_USER")
            admin_password = config("AD_ADMIN_PASSWORD")
            ad_server = f"ldap://{domain}"

            # Configuração do servidor LDAP com admin
            server = Server(ad_server, get_info=ALL)
            admin_user_full = f"{admin_user}@{domain}"
            admin_conn = Connection(server, user=admin_user_full, password=admin_password, auto_bind=True)

            # Base de pesquisa no Active Directory
            search_base = f"DC={domain.replace('.', ',DC=')}"
            search_filter = f"(sAMAccountName={username})"

            # Realiza a pesquisa no AD
            success = admin_conn.search(
                search_base,
                search_filter,
                search_scope=SUBTREE,
                attributes=["memberOf", "displayName"]
            )

            if success and admin_conn.entries:
                user_entry = admin_conn.entries[0]
                display_name = user_entry.displayName.value if hasattr(user_entry, 'displayName') else username
                groups = user_entry.memberOf.values if hasattr(user_entry, 'memberOf') else []
                cn_groups = [group.split(",")[0].replace("CN=", "") for group in groups]

                # Atualiza a sessão
                session['user'] = username
                session['display_name'] = display_name
                session['user_groups'] = cn_groups

                admin_conn.unbind()
                return True

            return False

        except Exception as e:
            import traceback
            return False

    @staticmethod
    def is_authenticated():
        return 'user' in session

    @staticmethod
    def get_user_display_name():
        return session.get('display_name', 'Usuário')

    @staticmethod
    def logout():
        session.clear()