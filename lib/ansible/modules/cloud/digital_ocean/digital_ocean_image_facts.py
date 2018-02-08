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
module: digital_ocean_image_facts
short_description: Gather facts about DigitalOcean images
description:
    - This module can be used to gather facts about DigitalOcean provided images.
    - These images can be either of type C(distribution), C(application) and C(private).
author: "Abhijeet Kasurde (@akasurde)"
version_added: "2.5"
options:
  image_type:
    description:
     - Specifies the type of image facts to be retrived.
     - If set to C(application), then facts are gathered related to all application images.
     - If set to C(distribution), then facts are gathered related to all distribution images.
     - If set to C(private), then facts are gathered related to all private images.
     - If not set to any of above, then facts are gathered related to all images.
    default: 'all'
    choices: [ 'all', 'application', 'distribution', 'private' ]
    required: false
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
- name: Gather facts about all images
  digital_ocean_image_facts:
    image_type: all
    oauth_token: "{{ oauth_token }}"

- name: Gather facts about application images
  digital_ocean_image_facts:
    image_type: application
    oauth_token: "{{ oauth_token }}"

- name: Gather facts about distribution images
  digital_ocean_image_facts:
    image_type: distribution
    oauth_token: "{{ oauth_token }}"

'''


RETURN = '''
data:
    description: DigitalOcean image facts
    returned: success
    type: list
    sample: [
        {
            "created_at": "2018-02-02T07:11:43Z",
            "distribution": "CoreOS",
            "id": 31434061,
            "min_disk_size": 20,
            "name": "1662.1.0 (beta)",
            "public": true,
            "regions": [
                "nyc1",
                "sfo1",
                "nyc2",
                "ams2",
                "sgp1",
                "lon1",
                "nyc3",
                "ams3",
                "fra1",
                "tor1",
                "sfo2",
                "blr1"
            ],
            "size_gigabytes": 0.42,
            "slug": "coreos-beta",
            "type": "snapshot"
        },
    ]
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils._text import to_native


def core(module):
    image_type = module.params['image_type']

    rest = DigitalOceanHelper(module)

    # Check if api_token is valid or not
    response = rest.get('account')
    if response.status_code == 401:
        module.fail_json(msg='Failed to login using api_token, please verify '
                             'validity of api_token')
    base_url = 'images?'
    if image_type == 'distribution':
        base_url += "type=distribution&"
    elif image_type == 'application':
        base_url += "type=application&"
    elif image_type == 'private':
        base_url += "private=true&"

    page = 1
    has_next = True
    images = []
    status_code = 400
    while has_next or status_code != 200:
        required_url = "{0}page={1}&per_page=20".format(base_url, page)
        response = rest.get(required_url)
        status_code = response.status_code
        # stop if any error during pagination
        if 200 != status_code:
            break
        page += 1
        images.extend(response.json["images"])
        has_next = "pages" in response.json["links"] and "next" in response.json["links"]["pages"]

    if status_code != 200:
        module.fail_json(msg="Failed to fetch images facts due to error : %s" % response.json['message'])

    module.exit_json(changed=False, data=images)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            image_type=dict(type='str',
                            required=False,
                            choices=['all', 'application', 'distribution', 'private'],
                            default='all'),
            oauth_token=dict(aliases=['DO_API_TOKEN', 'DO_API_KEY', 'DO_OAUTH_TOKEN'],
                             no_log=True),
        )
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()
