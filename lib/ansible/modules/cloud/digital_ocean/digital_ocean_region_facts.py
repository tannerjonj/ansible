#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Ansible Project
# Copyright: (c) 2018, Abhijeet Kasurde <akasurde@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}


DOCUMENTATION = '''
---
module: digital_ocean_region_facts
short_description: Gather facts about DigitalOcean regions
description:
    - This module can be used to gather facts about regions.
author: "Abhijeet Kasurde (@akasurde)"
version_added: "2.5"
options:
  oauth_token:
    description:
     - DigitalOcean OAuth token.
    required: true
    aliases: ['DO_API_TOKEN', 'DO_API_KEY', 'DO_OAUTH_TOKEN']

notes:
  - Two environment variables can be used, DO_API_KEY, DO_OAUTH_TOKEN and DO_API_TOKEN.
    They both refer to the v2 token.

requirements:
  - "python >= 2.6"
'''


EXAMPLES = '''
- name: Gather facts about all regions
  digital_ocean_region_facts:
    oauth_token: "{{ oauth_token }}"
'''


RETURN = '''
data:
    description: DigitalOcean regions facts
    returned: success
    type: list
    sample: [
        {
            "available": true,
            "features": [
                "private_networking",
                "backups",
                "ipv6",
                "metadata",
                "install_agent",
                "storage"
            ],
            "name": "New York 1",
            "sizes": [
                "512mb",
                "s-1vcpu-1gb",
                "1gb",
                "s-3vcpu-1gb",
                "s-1vcpu-2gb",
                "s-2vcpu-2gb",
                "2gb",
                "s-1vcpu-3gb",
                "s-2vcpu-4gb",
                "4gb",
                "c-2",
                "m-1vcpu-8gb",
                "8gb",
                "s-4vcpu-8gb",
                "s-6vcpu-16gb",
                "16gb"
            ],
            "slug": "nyc1"
        },
    ]
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils._text import to_native


def core(module):
    rest = DigitalOceanHelper(module)

    # Check if api_token is valid or not
    response = rest.get('account')
    if response.status_code == 401:
        module.fail_json(msg='Failed to login using API token, please verify validity of API token.')

    page = 1
    has_next = True
    regions = []
    status_code = 400
    while has_next or status_code != 200:
        response = rest.get("regions?page={0}&per_page=20".format(page))
        status_code = response.status_code
        # stop if any error during pagination
        if 200 != status_code:
            break
        page += 1
        regions.extend(response.json["regions"])
        has_next = "pages" in response.json["links"] and "next" in response.json["links"]["pages"]

    if status_code != 200:
        module.fail_json(msg="Failed to fetch 'regions' facts due to error : %s" % response.json['message'])

    module.exit_json(changed=False, data=regions)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            oauth_token=dict(aliases=['DO_API_TOKEN', 'DO_API_KEY', 'DO_OAUTH_TOKEN'],
                             no_log=True),
        ),
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()
