#!/usr/bin/python

from pandevice import firewall
from pandevice.base import PanDevice
import pprint
import xml.etree.ElementTree as ET


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

    device = PanDevice.create_from_device(
        hostname=ip_address,
        api_username=username,
        api_password=password
    )

    sys_info = device.op('show system info', xml=True)

    pprint.pprint(sys_info)

    # Exit the module and return some value
    module.exit_json(changed=True, info=sys_info)


# This goes against Python PEP8 Style Guides, but it is required here since this is not the final code, this
# is used to import some generated code that wraps the module before executing it.
from ansible.module_utils.basic import *

main()
