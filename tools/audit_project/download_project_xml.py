#! /usr/bin/env python
"""
Connect to redcap and download the project metadata xml file
eg CovidHomeMonitoring_2020-04-16_1120.REDCap.xml

Downloads a metadata export of your project.
Includes Automated Survey Invites and leaves them enabled.

Equivalent to this in the REDCap admin:
- open project
- Project Home
- Other Functionality
- Copy or Backup Project
- Include the following in the XML file: (tick all)
- Download metadata only (XML)


Equivalent to this curl statement, captured from chrome dev tools.

curl 'https://redcapserver.yourcompany.org/redcap_v9.8.0/ProjectSetup/export_project_odm.php?pid=984&xml_metadata_options=userroles,reports,alerts,surveys,sq,asi,asienable' -H 'authority: redcap.yourcompay.com' -H 'upgrade-insecure-requests: 1' -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36' -H 'sec-fetch-dest: document' -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' -H 'sec-fetch-site: same-origin' -H 'sec-fetch-mode: navigate' -H 'sec-fetch-user: ?1' -H 'referer: https://redcap.yourcompay.com/redcap_v9.8.0/ProjectSetup/other_functionality.php?pid=984' -H 'accept-language: en-GB,en;q=0.9,en-US;q=0.8,la;q=0.7' -H 'cookie: survey=fdsljsfdljsdfjldfljfdjjdk6; PHPSESSID=aabbcacaafdaaaaadfafaaaaaa' -H 'dnt: 1' --compressed

"""

from pathlib import Path
from urllib.parse import parse_qs
import os
import re
import sys

import requests
from pathvalidate import sanitize_filename


EXPORT_URL = r"https://redcap.yourcompay.com/redcap_v9.8.0/ProjectSetup/export_project_odm.php"


def download_project_metadata(projectid, phpsessionid):

    querystring = "pid=984&xml_metadata_options=userroles,reports,alerts,surveys,sq,asi,asienable"

    # Sub in the correct project ID
    qwargs_data = parse_qs(querystring)
    qwargs_data['pid'] = projectid

    # Sub in our session ID to let our script authenticate
    headers = {
        'cache-control': 'max-age=0',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'cookie': 'PHPSESSID=%s' % phpessionid,
    }

    res = requests.get(url=EXPORT_URL, headers=headers, params=qwargs_data)
    # print(res)

    # Work out the filename it generated for us from the headers
    # eg 'Content-Disposition': 'attachment; filename="CovidHomeMonitoring_2020-04-16_1127.REDCap.xml"'
    filename = re.findall('filename="(.+)"', res.headers['content-disposition'])[0]

    # Sanitise the filename. Basic securtiy
    clean_filename = sanitize_filename(filename, replacement_text="_")
    newfile_path = Path(".") / clean_filename

    # Don't overwrite an existing file with the same name
    if os.path.exists(newfile_path):
        sys.exist(f"Cannot write xml file. File already exists: {clean_filename}")

    with open(newfile_path, 'wb') as f:
        f.write(res.content)

    sys.stdout.write(f"Project saved to {newfile_path}\n")


if __name__ == '__main__':

    if len(sys.argv) != 3:
        sys.exit("Usage:\n%s PROJECTID PHPSESSIONID" % sys.argv[0])

    projectid = sys.argv[1]
    phpessionid = sys.argv[2]

    # TODO validate projectid?
    # TODO phpsessionid
    download_project_metadata(projectid=projectid, phpsessionid=phpessionid)
