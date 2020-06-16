import requests
from typing import List
from urllib.parse import urlencode
import urllib3
import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# -----------------------------------------------------------------------------
# CLASS LDAP SERVER
# -----------------------------------------------------------------------------
class LDAPServer(object):

    # -------------------------------------------------------------------------
    # CONSTRUCTOR
    # -------------------------------------------------------------------------
    def __init__(self, name: str, ip_address: str, port: int):
        self.name: str = name
        self.ip_address: str = ip_address
        self.port: int = port

    # -------------------------------------------------------------------------
    # METHOD AS XML STRING NODE
    # -------------------------------------------------------------------------
    def as_xml_string_node(self) -> str:
        return """
        <entry name="{name}">
          <address>{ip}</address>
          <port>{port}</port>
        </entry>
        """.format(
            name=self.name,
            ip=self.ip_address,
            port=self.port
        ).replace("\n", '')


# -----------------------------------------------------------------------------
# CLASS LDAP SERVER PROFILE
# -----------------------------------------------------------------------------
class LDAPServerProfile(object):

    def __init__(
            self,
            profile_name: str = 'LDAP_auth_profile_automation',
            ldap_servers=None,
            dn: str = 'paloaltoADquery@softlayer.local',
            ldap_account_password: str = None
    ):
        if ldap_servers is None:
            ldap_servers = []
        self.profile_name: str = profile_name
        self.ldap_servers: List[LDAPServer] = ldap_servers
        self.xml_path = "/config/shared/server-profile/ldap/entry[@name=\'{}\']".format(profile_name)
        self.dn = dn
        self.ldap_account_password = ldap_account_password

    # -------------------------------------------------------------------------
    # METHOD CONVERT SERVERS TO XML STRING
    # -------------------------------------------------------------------------
    def _convert_servers_to_xml_string(self) -> str:
        servers = ""
        for server in self.ldap_servers:
            servers += server.as_xml_string_node()
        return servers

    # -------------------------------------------------------------------------
    # METHOD BUILD REQUEST PARAMETERS
    # -------------------------------------------------------------------------
    def get_creation_request(self) -> dict:
        return {
            'type': 'config',
            'action': 'set',
            'xpath': self.xml_path,
            'element': """
            <server>
            {servers}
            </server>
            <ldap-type>active-directory</ldap-type>
            <bind-dn>{dn}</bind-dn>
            <bind-password>{password}</bind-password>
            """.format(
                servers=self._convert_servers_to_xml_string(),
                dn=self.dn,
                password=self.ldap_account_password
            ).replace("\n", "")
        }


# -----------------------------------------------------------------------------
# CLASS FIREWALL ENDS
# -----------------------------------------------------------------------------
class Firewall(object):

    # -------------------------------------------------------------------------
    # CONSTRUCTOR
    # -------------------------------------------------------------------------
    def __init__(self, hostname: str, user: str, password: str):
        self.is_authenticated = False
        self.base_url = "https://{hostname}/api/?".format(hostname=hostname)
        self.__authenticate(user, password)

    # -------------------------------------------------------------------------
    # AUTHENTICATE
    # -------------------------------------------------------------------------
    def __authenticate(self, user: str, password: str):
        print('Authenticating with Firewall')
        parameters = {
            'type': ' keygen',
            'user': user,
            'password': password,
        }
        response = requests.get(self.base_url, params=parameters, verify=False)
        self.access_token = response.text[42:-26]
        print('Access Token: {}'.format(self.access_token))

    # -------------------------------------------------------------------------
    # CREATE LOCAL ADMINISTRATOR
    # -------------------------------------------------------------------------
    def create_local_administrator(self, username: str = "padmin", password_hash: str =""):
        parameters = {
            'type': 'config',
            'action': 'set',
            'xpath': "/config/mgt-config/users/entry[@name=\'{}\']".format(username),
            'element': """
            <permissions>
                <role-based>
                    <superuser>yes</superuser>
                </role-based>
            </permissions>
            <phash>{password_hash}</phash>
            """.format(
                          password_hash=password_hash
                      ).replace("\n", ""),
            'key': self.access_token
        }
        req_url = self.base_url + urlencode(parameters)
        return requests.get(req_url, verify=False)

    def create_local_administrator_password(self, username: str = "padmin", password_hash: str =""):
        parameters = {
            'type': 'config',
            'action': 'set',
            'xpath': "/config/mgt-config/users/entry[@name=\'{}\']".format(username),
            'element': """
            <phash>{password_hash}</phash>""".format(password_hash=password_hash),
            'key': self.access_token
        }
        pprint.pprint(parameters)
        req_url = self.base_url + urlencode(parameters)
        return requests.get(req_url, verify=False)

    # -------------------------------------------------------------------------
    # METHOD BUILD REQUEST PARAMETERS
    # -------------------------------------------------------------------------
    def update_ldap_account_for_template(self, template: str, auth_profile: str, dn: str, password: str):
        parameters = {
            'type': 'config',
            'action': 'edit',
            'xpath': "/config/devices/entry[@name='localhost.localdomain']/template/entry[@name='{template}']/config/shared/server-profile/ldap/entry[@name='{auth_profile}']".format(
                template=template,
                auth_profile=auth_profile
            ),
            'element': """
                <ldap-type>active-directory</ldap-type>
                <bind-dn>{dn}</bind-dn>
                <bind-password>{password}</bind-password>
            """.format(
                dn=dn,
                password=password
            ).replace("\n", ""),
            'key': self.access_token
        }
        pprint.pprint(parameters)
        req_url = self.base_url + urlencode(parameters)
        return requests.get(req_url, verify=False)

    # -------------------------------------------------------------------------
    # COMMIT
    # -------------------------------------------------------------------------
    def commit(self):
        parameters = {
            'type': 'commit',
            'cmd': '<commit></commit>',
            'key': self.access_token
        }
        req_url = self.base_url + urlencode(parameters)
        return requests.get(req_url, verify=False)

    # -------------------------------------------------------------------------
    # CREATE LDAP SERVER PROFILE
    # -------------------------------------------------------------------------
    def create_ldap_server_profile(self,
                                   profile_name: str = 'LDAP_auth_profile_automation',
                                   ldap_servers=None,
                                   dn: str = 'paloaltoADquery@softlayer.local',
                                   ldap_account_password: str = None
                                   ):
        ldap_profile = LDAPServerProfile(
            profile_name,
            ldap_servers,
            dn,
            ldap_account_password
        )

        parameters = ldap_profile.get_creation_request()
        parameters['key'] = self.access_token
        req_url = self.base_url + urlencode(parameters)
        return requests.get(req_url, verify=False)