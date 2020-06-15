#!/usr/bin/python
from pandevice import firewall
from pandevice.base import PanDevice
from pandevice.device import Administrator
import pprint
from collections import defaultdict


# -----------------------------------------------------------------------------
# MAIN MODULE'S FUNCTION
# -----------------------------------------------------------------------------
def main():
    module = AnsibleModule(
        argument_spec=dict(
            ip_address=dict(required=True),
            username=dict(required=True, no_log=True),  # Sensitive Parameter so passwords or keys do not end up in logs
            password=dict(required=True, no_log=True)   # Sensitive Parameter so passwords or keys do not end up in logs
        ),
        supports_check_mode=False
    )

    username = module.params['username']
    password = module.params['password']
    ip_address = module.params['ip_address']

    palo = PanDevice.create_from_device(
        hostname=ip_address,
        api_username=username,
        api_password=password
    )

    admin = Administrator.refreshall(palo, add=True)

    # Exit the module and return some value
    module.exit_json(changed=True, info=str(palo.children))


# This goes against Python PEP8 Style Guides, but it is required here since this is not the final code, this
# is used to import some generated code that wraps the module before executing it.
from ansible.module_utils.basic import *

main()
