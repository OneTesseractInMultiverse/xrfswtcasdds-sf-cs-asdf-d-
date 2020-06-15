from palo_alto.device import Firewall, LDAPServer
import pprint
import os

print('Starting ...')
ldap_servers = [
    {"name": "SLDCDA1101", "ip_address": "172.30.74.20", "port": 636},
    {"name": "SLDCWDC0401", "ip_address": "172.17.82.20", "port": 636}
]

dc_servers = []
for srv in ldap_servers:
    dc_servers.append(
        LDAPServer(
            srv['name'],
            srv['ip_address'],
            srv['port']
        )
    )

# Authenticate with Firewall and abstract device through Firewall object
fw = Firewall(hostname='172.30.71.70', user='Sec-PaloUtil', password=os.environ.get('PALO_PASS'))
# response = fw.create_ldap_server_profile(
#     'Automation Test Profile',
#     dc_servers,
#     'paloaltoADquery@softlayer.local',
#     'DKpYcuFEZGXPR2d'
# )
response = fw.create_local_administrator(
    username='padmin_automation',
    password_hash='$1$dyvrefvm$abTG.kIKX6qJUMJGOr6TD.'
)
pprint.pprint(response.text)

