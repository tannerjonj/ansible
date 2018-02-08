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
module: digital_ocean_size_facts
short_description: Gather facts about DigitalOcean Sizes
description:
    - This module can be used to gather facts about sizes.
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
- name: Gather facts about all sizes
  digital_ocean_size_facts:
    oauth_token: "{{ oauth_token }}"
'''


RETURN = '''
data:
    description: DigitalOcean size facts
    returned: success
    type: list
    sample: [
        {
            "available": true,
            "disk": 20,
            "memory": 512,
            "price_hourly": 0.00744,
            "price_monthly": 5.0,
            "regions": [
                "ams2",
                "ams3",
                "blr1",
                "fra1",
                "lon1",
                "nyc1",
                "nyc2",
                "nyc3",
                "sfo1",
                "sfo2",
                "sgp1",
                "tor1"
            ],
            "slug": "512mb",
            "transfer": 1.0,
            "vcpus": 1
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

    response = rest.get('sizes')
    if response.status_code != 200:
        module.fail_json(msg="Failed to fetch 'sizes' facts due to error : %s" % response.json['message'])

    module.exit_json(changed=False, data=response.json['sizes'])


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
