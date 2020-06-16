from palo_alto.device import Firewall, LDAPServer
import pprint
import os
import io
import sys

password = str(sys.argv[1])

with open('templates') as f:
    content = f.readlines()
# you may also want to remove whitespace characters like `\n` at the end of each line
content = [x.strip() for x in content]

templates = []
for line in content:
    line.replace(" ", "")
    sp = line.split(',')
    templates.append({
        'hostname': sp[0].replace(" ", ""),
        'template': sp[2].replace(" ", ""),
        'auth_profile': sp[3].replace(" ", "")
    })

print('Templates Loaded: ')
pprint.pp(templates)

# fw = Firewall(hostname='172.29.253', user='Sec-PaloUtil', password=os.environ.get('PALO_PASS'))

for template in templates:
    print("Updating LDAP Account for Template: {}".format(template['template']))

    pprint.pprint(fw.update_ldap_account_for_template(
        template=template['template'],
        auth_profile=template['auth_profile'],
        dn='paloaltoADquery1@softlayer.local',
        password=password
    ).text)

    print('---------------------------')
    pprint.pprint(template)

    # No Commit
    # pprint.pprint(fw.commit().text)
    print('===============================================================================')

