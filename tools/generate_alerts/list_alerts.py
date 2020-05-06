#! /usr/bin/env python
"""
List all the Alerts defined in a REDCap

This tool should output something like this:
  152 1 SMS Patient Registration - BIDAILY
  165 2 SMS Patient Registration - ESCALATION checkin
  175 3 SMS Late observation patient emergency contact - SMS
  176 4 EMAIL Late observation staff warning - EMAIL
  177 5 SMS Monitoring Discharge patient - SMS
  178 6 EMAIL Monitoring Discharge patient - EMAIL
  179 7 EMAIL Monitoring Discharge Required staff
  180 8 SMS Escalation checkin warning patient
  181 9 SMS Periodic info note - Public Health Messaging SMS
  182 10 SMS Periodic info note - Quarantine SMS
  183 11 SMS Periodic info note - Lifeline SMS
  184 12 SMS Periodic info note - Meals on Wheels
  200 13 SMS Obs Combined Staff alert - Ob_template
  201 14 SMS Obs Combined Patient alert - Ob_template
  202 15 SMS Obs Combined Patient alert - Ob_0
  203 16 SMS Obs Combined Patient alert - Ob_1a
  ...


Usage
  ./list_alerts.py PROJECTID PHPSESSIONID
  ./list_alerts.py 984 6437fdsjadfskh2fdl23k4j323


It works by issuing a GET request for the Alerts & Notifications page in
REDCap, and parsing the html for the alerts and metadata.
"""

from urllib.parse import parse_qs
import json
import re
import sys

import requests

URL = "https://redcap.yourcompay.com/redcap_v9.8.0/index.php"


def list_alerts(url, phpsessionid, projectid):
    """Load the REDCap Alerts & Notifications tab, parse out the list of alerts
    and their metadata and print it to stdout"""

    qwargs_template = "pid=nnn&route=AlertsController:setup"

    qwargs_data = parse_qs(qwargs_template)
    qwargs_data['pid'] = projectid

    headers = {
        'cookie': 'PHPSESSID=%s' % phpessionid,
    }

    res = requests.get(url, headers=headers, params=qwargs_data)
    # print(res)

    # Easiest place to find the title/id/index is in the javascript that
    # triggers the edit box for each alert
    # look for  function __rcfunc_editEmailAlert_emailRow....
    reg = r'__rcfunc_editEmailAlert_emailRow.*editEmailAlert\(({.*}),'

    matches = re.findall(reg, res.text)

    for match in matches:
        alert_data = json.loads(match)
        print(
            alert_data['alert-id'],
            alert_data['alert-number'],
            alert_data['alert-type'],
            alert_data['alert-title'],
        )


if __name__ == '__main__':

    if len(sys.argv) != 3:
        sys.exit("Usage:\n%s PROJECTID PHPSESSIONID" % sys.argv[0])

    projectid = sys.argv[1]
    phpessionid = sys.argv[2]

    list_alerts(url=URL, phpsessionid=phpessionid, projectid=projectid)
