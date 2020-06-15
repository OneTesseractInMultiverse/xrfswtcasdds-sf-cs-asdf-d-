from palo_alto.device import Firewall, LDAPServer
import pprint
import os
import io
import sys

username = str(sys.argv[1])
password_hash = str(sys.argv[2])


with open('inventory') as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

for line in content:
    line.replace(" ", "")



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

for device in content:
    print("Creating Breakglass Account on: {}".format(device))
    # Authenticate with Firewall and abstract device through Firewall object
    fw = Firewall(hostname=device, user='Sec-PaloUtil', password=os.environ.get('PALO_PASS'))
    # response = fw.create_ldap_server_profile(
    #     'Automation Test Profile',
    #     dc_servers,
    #     'paloaltoADquery@softlayer.local',
    #     'DKpYcuFEZGXPR2d'
    # )
    response = fw.create_local_administrator(
        username=username,
        password_hash=password_hash
    )
    pprint.pprint(response.text)
    print('===============================================================================')

