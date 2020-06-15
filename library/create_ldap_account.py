#!/usr/bin/python
from palo_alto.device import Firewall, LDAPServer

# -----------------------------------------------------------------------------
# MAIN MODULE'S FUNCTION
# -----------------------------------------------------------------------------
def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_address=dict(required=True),
            username=dict(required=True, no_log=True),  # Sensitive Parameter so passwords or keys do not end up in logs
            password=dict(required=True, no_log=True),  # Sensitive Parameter so passwords or keys do not end up in logs
            profile_name=dict(required=True),
            dn=dict(required=True),
            # Sensitive Parameter so passwords or keys do not end up in logs
            ldap_account_password=dict(required=True, no_log=True)

        ),
        supports_check_mode=False
    )

    module.log('This is a messageß')

    username = module.params['username']
    password = module.params['password']
    ip_address = module.params['ip_address']

    profile_name = module.params['profile_name']
    ldap_servers = [
        {"name": "SLDCDA1101", "ip_address": "172.30.74.20", "port": 636},
        {"name": "SLDCWDC0401", "ip_address": "172.17.82.20", "port": 636}
    ]
    dn = module.params['dn']
    ldap_account_password = module.params['ldap_account_password']

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
    fw = Firewall(hostname=ip_address, user=username, password=password)
    response = fw.create_ldap_server_profile(
        profile_name,
        dc_servers,
        dn,
        ldap_account_password
    )

    # Exit the module and return some value
    module.exit_json(changed=True, info="HTTP STATUS CODE: {code} \n {text}".format(
        code=response.status_code,
        text=response.text
    ))


# This goes against Python PEP8 Style Guides, but it is required here since this is not the final code, this
# is used to import some generated code that wraps the module before executing it.
# from ansible.module_utils.basic import *
#
# main()











