#! /usr/bin/env python
"""
Connect to the REDCap admin site and update a specific existing alerts settings

Use this tool to update an alert based on another template alert. We use it
to copy out all the various ob_0, ob_1a, ob_1b, ... alerts.

THIS IS NOT A GENERIC TOOL. It relies on lots of developer input and update.
But it's better than clicking 400 buttons in the admin UI.

This injects http POST requests into the server. Authenticates by using an
existing PHP session cookie and a CSRF token. See the documentation for how
to get these.


Usage
  ./update_alert.py phpsession csrftoken project type template target obcode

ie update alert ALERTINDEX to match the template ALERT_TYPE, but substitute
the appropriate values for OB_COD.

eg

  ./update_alert.py d7kbb39c... 31ee8469.... 984 STAFF_ALERT_COMBINED_SMS 200 290 ob_14b
"""

import json
import sys
import re
from pprint import pprint
from urllib.parse import parse_qs

import requests


# These are the html post vars required to update an alert
# they map *almost* 1-to-1 with a structure set by javascript inside the
# alert page editEmailAlert({...}, ...)
POST_TEMPLATE = {
    # REDCap seems to pull these from the database
    # They are all present in the script call
    'alert-type',
    'email-to',
    'ensure-logic-still-true',
    'cron-send-email-on-date',
    'alert-expiration',
    'cron-send-email-on-next-time',
    'email-failed',
    'email-bcc',
    'email-repetitive-change-calcs',
    'cron-repeat-for',
    'email-deleted',
    'redcap_csrf_token',
    'phone-number-to',
    'alert-stop-type',
    'alert-title',
    'email-subject',
    'cron-send-email-on-time-lag-days',
    'email-from',
    'cron-send-email-on',
    'alert-message',
    'cron-repeat-for-units',
    'email-cc',
    'alert-condition',
    'cron-repeat-for-max',
    'cron-send-email-on-time-lag-minutes',
    'email-attachment-variable',
    'email-incomplete',
    'cron-send-email-on-next-day-type',
    'form-name',
    'email-repetitive',
    'email-repetitive-change',
    'cron-send-email-on-time-lag-hours',
    'email-from-display',

    # REDCap set by JS during the save
    'alert-send-how-many',
    'index_modal_update',
    'phone-number-to-freeform',
    'email-to-freeform',
    'email-cc-freeform',
    'alert-trigger',
    'email-bcc-freeform',

    # REDCap UI housekeeping
    'redcap_csrf_token',
    'alert-message-editor',
}


ALERT_TEMPLATE_ID = {
    'STAFF_ALERT_COMBINED_EMAIL': '216',
    'STAFF_ALERT_COMBINED_SMS': '200',
    'PATIENT_ALERT_COMBINED_SMS': '201',
    'LATE_OBS_STAFF_SMS': '307'
}


def update_alert(sess, template_postdata, alert_type, csrftoken, projectid, alert_index, obcode):

    # Different alerts need us to transform the template in different ways
    # Some are a simple string.replace('_template', '_4a'), some just be set
    # explicitly
    if alert_type in ['STAFF_ALERT_COMBINED_EMAIL', 'STAFF_ALERT_COMBINED_SMS',
                      'PATIENT_ALERT_COMBINED_SMS']:
        transformed_data = prepare_postvars_obs_simplealert(template_postdata, obcode)
    elif alert_type == 'LATE_OBS_STAFF_SMS':
        transformed_data = prepare_postvars_late_obs_staff(template_postdata, obcode)
    else:
        sys.exit(f"Unknown alert_type: {alert_type}")


    # Form update stuff
    transformed_data['index_modal_update'] = alert_index
    transformed_data['redcap_csrf_token'] = csrftoken

    for key, val in transformed_data.items():
        print(f"{key}: {val}")

    URL = "https://redcap.yourcompay.com/redcap_v9.8.0/index.php"
    QVAR_TEMPLATE = "pid=984&route=AlertsController:saveAlert"

    template_qvar_data = {k: v[0] for k, v in parse_qs(QVAR_TEMPLATE).items()}
    # TODO assert contains the values we expect?
    transformed_qvars_data = {k: v for k, v in template_qvar_data.items()}
    transformed_qvars_data['pid'] = projectid

    headers = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    }

    payload = transformed_data
    pprint(payload)


    req = requests.Request(
        'POST', url=URL, headers=headers, params=transformed_qvars_data, data=payload)
    prep = req.prepare()
    prep.headers = {**sess.headers, **prep.headers}

    #breakpoint()
    res = sess.send(prep)

    checkexit_redcap_loggout(res)
    print(res)
    print(res.text)


def prepare_postvars_obs_simplealert(template_postdata, obcode):
    """In these alerts we just change anything _template to _n
    eg   [hr_template] -> [hr_4a]
    eg   "combined email ob_template" -> "combined email ob_4a"
    """

    obprefix, obcode_trailer = obcode.split('_')

    transformed_data = {}
    for key, vals in template_postdata.items():
        print(f"{key}: {vals}")

        tranformed_key = key.replace('_template', f'_{obcode_trailer}')

        # TODO what if that text exists as a literal in the text?
        # TODO do we test for undefined? [variables]?


        tranformed_vals = vals
        if tranformed_vals:
            tranformed_vals = vals.replace('_template', f'_{obcode_trailer}')

        transformed_data[tranformed_key] = tranformed_vals

    if transformed_data['phone-number-to-freeform'] is None:
        if transformed_data['phone-number-to'] > '':
            transformed_data['phone-number-to-freeform'] = transformed_data['phone-number-to']

            transformed_data['phone-number-to'] = None
    return transformed_data


def prepare_postvars_late_obs_staff(template_postdata, obcode):
    """Creat postdata for updating a late_obs_staff alert.
    This is trickier than the 'combined staff' alerts. They just need all
    the _template text changed to _OBSNUMBER

    But late obs alerts have references to multiple observations. They are
    triggered by one observation, and have the details of another.
    ie ob_3a triggers the alert to check ob_4a
    """
    preceding_obprefix, preceding_obnum = get_obs_preceding_obs(obcode).split("_")

    # Explicitly set the triggering form to be the PRECEEDING observation
    transformed_data = template_postdata
    transformed_data['form-name'] = transformed_data['form-name'].replace('_template', f'_{preceding_obnum}')

    # Now just replace the rest as usual
    transformed_data = prepare_postvars_obs_simplealert(transformed_data, obcode)

    # And set the alert time to be 5 hours after due time
    # 1pm for the morning, 8pm for the evening
    if obs_is_morning(obcode):
        transformed_data['cron-send-email-on-next-time'] = '13:00'
    elif obs_is_afternoon(obcode):
        transformed_data['cron-send-email-on-next-time'] = '20:00'
    else:
        assert False  # unknown obcode

    return transformed_data


# TODO code is doubled up with audit_project.py
def valid_obcode(code):
    # Special cases
    if code in ['ob_template', 'ob_0']:
        return True

    if '_' not in code:
        return False

    if not code[0:3] == 'ob_':
        return False

    # They shoudl all end in 'a' or 'b' excep ob_0 and ob_template
    if code[-1] not in ['a', 'b']:
        return False

    # Digits
    if not code[3:-1].isdigit():
        return False

    return True


# TODO code is doubled up with audit_project.py
def obs_is_morning(obcode):
    """Given an observation code (eg 'ob_1a', 'ob12_b') is this a morning obs?"""
    return obcode[-1] == 'a'


# TODO code is doubled up with audit_project.py
def obs_is_afternoon(obcode):
    """Given an observation code (eg 'ob_1a', 'ob12_b') is this an afternoon obs?"""
    return obcode[-1] == 'b'


# TODO code is doubled up with audit_project.py
def get_obs_preceding_obs(obcode):
    """Given an observation eg ob_4a, which observation precedes it?
    We have two streams, the 'a' (morning) and 'b' (afternoon) obs.

    But the first day follows on from the demo observation ob_0 -> ob_1a
                                                           ob_0 -> ob_1b
    The rest follow the previous. ob_1a -> ob_2a -> ob_3a
                                  ob_1b -> ob_2b -> ob_3b
    """
    assert valid_obcode(obcode)

    # First day follows the demo observation
    if obcode in ['ob_1a', 'ob_1b']:
        return 'ob_0'

    # The rest follow the previous day (number -1)
    ob_day = obcode[3:-1]
    prev_day = int(ob_day) - 1

    if obs_is_morning(obcode):
        return 'ob_%sa' % prev_day
    elif obs_is_afternoon(obcode):
        return 'ob_%sb' % prev_day
    else:
        assert False  # unknown obcode


def load_postdata_from_template(sess, projectid, template_id):
    alerts_page_url = get_alerts_page_url(projectid)
    res = sess.get(alerts_page_url, allow_redirects=False)
    checkexit_redcap_loggout(res)

    alerts_page_html = res.text
    data = extract_alert_data_structure(alerts_page_html, template_id)

    # Add the extra post fields

    # Update the triggering form to include event code
    # This is probably a bug. Not sure how this works with longitudinal
    data['form-name'] = "%s-%s" % (data['form-name'], data['form-name-event'])

    data = {
        'alert-send-how-many': None,
        'index_modal_update': template_id,
        'phone-number-to-freeform': None,
        'email-to-freeform': None,
        'email-cc-freeform': None,
        'alert-trigger': 'submit-logic',
        'email-bcc-freeform': None,
        'redcap_csrf_token': None,
        'alert-message-editor': None,
        **data
    }

    filtered = {k: data[k] for k in POST_TEMPLATE}

    assert set(POST_TEMPLATE) == set(filtered.keys())
    return filtered


def extract_alert_data_structure(alerts_page_html, alertid):
    """
    Find the javascript call to open the editor for alertid. Extract params.

    Looks something like this:
       <script type="text/javascript">function __rcfunc_editEmailAlert_emailRow10(){ editEmailAlert({"alert-id":"200","alert-title":"...},200,11) }</script>
    """
    for scriptcall in re.findall(r"editEmailAlert\({(.*)}.*\)", alerts_page_html):
        if f'"alert-id":"{alertid}"' in scriptcall:
            data = json.loads("{" + scriptcall + "}")
            return data

    raise Exception("Could not find template alert structure")


def get_alerts_page_url(projectid):
    # TODO break out to config
    return f"https://redcap.yourcompay.com/redcap_v9.8.0/index.php?pid={projectid}&route=AlertsController:setup"


def checkexit_redcap_loggout(response):
    """Given a requests response exit with error if we've been logged out.

    Redcap does not give a http response code on logout. You just get back
    Detect if we've been bumped to a login page and exit"""

    # Quick and dirty. Look for the forgot password link
    if response.status_code == 302 or 'Authentication/password_recovery.php' in response.text:
        sys.exit("Logged out of REDCap")


if __name__ == '__main__':

    if len(sys.argv) != 8:
        sys.exit(
            "Usage:\n%s phpsession csrftoken project type template target obcode" %
            sys.argv[0])

    phpsessionid = sys.argv[1]
    csrf_token = sys.argv[2]
    projectid = sys.argv[3]
    alert_type = sys.argv[4]
    template_id = sys.argv[5]
    target_id = sys.argv[6]
    obcode = sys.argv[7]

    # TODO validate phpessionid

    # TODO validate projectid

    # TODO validate csrf_token

    # Is this an alert type we know?
    if alert_type not in ALERT_TEMPLATE_ID.keys():
        sys.exit("Unknown alert type: %s\nKnown types: %s" % (alert_type, ALERT_TEMPLATE_ID.keys()))

    if not template_id.isdigit():
        sys.exit("Invalid template index: %s" % template_id)

    if not target_id.isdigit():
        sys.exit("Invalid target index: %s" % target_id)

    # TODO validate obcode
    if not valid_obcode(obcode):
        sys.exit("Invalid ob_code: %s" % obcode)


    # Authenticated requests session
    sess = requests.Session()
    sess.headers.update({'cookie': f'PHPSESSID={phpsessionid}'})



    template_postdata = load_postdata_from_template(sess, projectid, template_id)


    alert_title = template_postdata['alert-title']

    # Did we get the right template? Check the expected redcap object id
    # is the same one that's in the curl cmd template
    assert template_postdata['index_modal_update'] == ALERT_TEMPLATE_ID[alert_type]

    print("Does this look right?...")
    pprint({
        'phpsessionid': phpsessionid,
        'csrftoken': csrf_token,
        'projectid': projectid,
        'type': alert_type,
        'template_id': template_id,
        'template title': alert_title,
        'target_id': target_id,
        'obcode': obcode
    })

    # Make user confirm before actually sending the update
    if False:
        print("y/n...")
        confirm = input().lower()

        if confirm != 'y':
            sys.exit("Aborting")

    update_alert(
        sess,
        template_postdata=template_postdata,
        alert_type=alert_type,
        csrftoken=csrf_token,
        projectid=projectid,
        alert_index=target_id,
        obcode=obcode)
