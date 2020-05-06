#!/usr/bin/env python
"""
Authenticate with your REDCap website to get a PHPSESSID and redcap_csrf_token
"""

import re
import sys

import requests


def attempt_login(url, username, password):
    """
    Attempt to login to the given REDCap server admin site and retrieve
    a valid PHP session id and CSRF token.
    """

    # Login requires a token included in the html form
    # Kind of like a csrf token (but different to the real csrf used elsewhere)
    res = requests.get(url)
    login_token = re.search(r"id='(redcap_login_[^']+)'", res.text).group(1)

    # Data required for authentication
    data = {
        'username': username,
        'password': password,
        'submitted': 1,
        login_token: '',
    }

    # Use a Requests session object so we can capture the cookies
    sess = requests.Session()
    res = sess.post(url, data=data)

    # REDcap doesn't give any http header indication of a failed login
    # only the page text changes.
    if 'redcap_csrf_token' in res.text:
        session_cookie = sess.cookies['PHPSESSID']
        csrf_token = re.findall(r"var redcap_csrf_token = '([^']+)'", res.text)[0]
    else:
        session_cookie = None
        csrf_token = None

    return (session_cookie, csrf_token)


if __name__ == '__main__':

    if len(sys.argv) != 4:
        sys.exit("Usage:\n%s URL USERNAME PASSWORD" % sys.argv[0])

    url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    (session, csrf) = attempt_login(url=sys.argv[1],
                                    username=sys.argv[2],
                                    password=sys.argv[3])

    if not (session and csrf):
        sys.exit("Could not authenticate")

    sys.stdout.write(f"PHPSESSID: '{session}'\n")
    sys.stdout.write(f"csrf: '{csrf}'\n")
