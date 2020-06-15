#!/usr/bin/python
from pandevice import firewall
from pandevice.base import PanDevice
from pandevice.firewall import Firewall
from pandevice.base import PanConfig
import pprint
from collections import defaultdict
import json
import datetime


# -----------------------------------------------------------------------------
# CONVERT XML TO DICTIONARY
# -----------------------------------------------------------------------------
def etree_to_dict(t) -> object:
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


# -----------------------------------------------------------------------------
# FUNCTION LIST CERTIFICATES
# -----------------------------------------------------------------------------
def list_certificates(palo: PanDevice):
    certs = palo.op('request certificate show')
    certs_dict = etree_to_dict(certs)
    expired = []
    now = (datetime.datetime.now() + datetime.timedelta(days=2)).timestamp()
    for cert in certs_dict['response']['result']['entry']:
        if float(cert['expiry']) < now:
            expired.append(cert)
    return expired


# -----------------------------------------------------------------------------
# DELETE FROM DEVICE
# -----------------------------------------------------------------------------
def delete_from_device(palo: PanDevice, expired: list):
    results = []
    for cert in expired:
        results.append(palo.remove_by_name(cert['@name']))
    return expired


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

    certs = list_certificates(palo)
    deleted = delete_from_device(palo, certs)
    # palo.commit()

    # Exit the module and return some value
    module.exit_json(changed=True, info=str(deleted))


# This goes against Python PEP8 Style Guides, but it is required here since this is not the final code, this
# is used to import some generated code that wraps the module before executing it.
from ansible.module_utils.basic import *

main()
