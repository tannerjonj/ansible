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
module: digital_ocean_snapshot_facts
short_description: Gather facts about DigitalOcean Snapshot
description:
    - This module can be used to gather facts about snapshot facts based upon provided values such as droplet, volume and snapshot id.
author: "Abhijeet Kasurde (@akasurde)"
version_added: "2.5"
options:
  snapshot_type:
    description:
     - Specifies the type of snapshot facts to be retrived.
     - If set to C(droplet), then facts are gathered related to snapshots based on Droplets only.
     - If set to C(volume), then facts are gathered related to snapshots based on volumes only.
     - If set to C(by_id), then facts are gathered related to snapshots based on snapshot id only.
     - If not set to any of the above, then facts are gathered related to all snapshots.
    default: 'all'
    choices: [ 'all', 'droplet', 'volume', 'by_id']
    required: false
  snapshot_id:
    description:
     - To retrieve information about a snapshot, please specify this as a snapshot id.
     - If set to actual snapshot id, then facts are gathered related to that particular snapshot only.
     - This is required parameter, if C(snapshot_type) is set to C(by_id).
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
- name: Gather facts about all snapshots
  digital_ocean_snapshot_facts:
    snapshot_type: all
    oauth_token: "{{ oauth_token }}"

- name: Gather facts about droplet snapshots
  digital_ocean_snapshot_facts:
    snapshot_type: droplet
    oauth_token: "{{ oauth_token }}"

- name: Gather facts about volume snapshots
  digital_ocean_snapshot_facts:
    snapshot_type: volume
    oauth_token: "{{ oauth_token }}"

- name: Gather facts about snapshot by snapshot id
  digital_ocean_snapshot_facts:
    snapshot_type: by_id
    snapshot_id: 123123123
    oauth_token: "{{ oauth_token }}"
'''


RETURN = '''
data:
    description: DigitalOcean snapshot facts
    returned: success
    type: list
    sample: [
        {
            "id": "4f60fc64-85d1-11e6-a004-000f53315871",
            "name": "big-data-snapshot1",
            "regions": [
                "nyc1"
            ],
            "created_at": "2016-09-28T23:14:30Z",
            "resource_id": "89bcc42f-85cf-11e6-a004-000f53315871",
            "resource_type": "volume",
            "min_disk_size": 10,
            "size_gigabytes": 0
        },
    ]
'''

from traceback import format_exc
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digital_ocean import DigitalOceanHelper
from ansible.module_utils._text import to_native


def core(module):
    snapshot_type = module.params['snapshot_type']

    rest = DigitalOceanHelper(module)

    # Check if api_token is valid or not
    response = rest.get('account')
    if response.status_code == 401:
        module.fail_json(msg='Failed to login using api_token, please verify '
                             'validity of api_token')
    base_url = 'snapshots'
    snapshot = []
    status_code = 400

    if snapshot_type == 'by_id':
        base_url += "/{0}".format(module.params.get('snapshot_id'))
        response = rest.get(base_url)
        status_code = response.status_code
        snapshot.extend(response.json["snapshot"])
    else:
        if snapshot_type == 'droplet':
            base_url += "?resource_type=droplet&"
        elif snapshot_type == 'volume':
            base_url += "?resource_type=volume&"

        page = 1
        has_next = True
        while has_next or status_code != 200:
            required_url = "{0}page={1}&per_page=20".format(base_url, page)
            response = rest.get(required_url)
            status_code = response.status_code
            # stop if any error during pagination
            if 200 != status_code:
                break
            page += 1
            snapshot.extend(response.json["snapshots"])
            has_next = "pages" in response.json["links"] and "next" in response.json["links"]["pages"]

    if status_code != 200:
        module.fail_json(msg="Failed to fetch snapshot facts due to error : %s" % response.json['message'])

    module.exit_json(changed=False, data=snapshot)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            snapshot_type=dict(type='str',
                               required=False,
                               choices=['all', 'droplet', 'volume', 'by_id'],
                               default='all'),
            oauth_token=dict(aliases=['DO_API_TOKEN', 'DO_API_KEY', 'DO_OAUTH_TOKEN'],
                             no_log=True),
            snapshot_id=dict(type='str', required=False),
        ),
        required_if=[
            ['snapshot_type', 'by_id', ['snapshot_id']],
        ],
    )

    try:
        core(module)
    except Exception as e:
        module.fail_json(msg=to_native(e), exception=format_exc())


if __name__ == '__main__':
    main()
