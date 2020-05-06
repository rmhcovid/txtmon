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
  ./update_alert.py PROJID PHPSESSIONID CSRF_TOKEN ALERT_TYPE ALERTINDEX OB_COD

ie update alert ALERTINDEX to match the template ALERT_TYPE, but substitute
the appropriate values for OB_COD.

eg

  ./update_alert.py 984 fdosjafjl2lf ffdsljaf LATE_OBS_STAFF_SMS 300 ob_2b
"""

import sys
import re
from pprint import pprint
from urllib.parse import parse_qs

import requests

"""
These curl update commands were captured using the chrome dev tools

ie Opened up REDCap in chrome, manually opened up the alert, clicked save
then in the 'network' tab I found the POST request, then right-clicked
'save as curl request'
"""

CURL_TEMPLATE_STAFF_COMBINED_EMAIL = r"curl 'https://redcap.yourcompay.com/redcap_v9.8.0/index.php?pid=984&route=AlertsController:saveAlert' \
  -H 'authority: redcap.yourcompay.com' \
  -H 'accept: */*' \
  -H 'x-requested-with: XMLHttpRequest' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36' \
  -H 'content-type: application/x-www-form-urlencoded; charset=UTF-8' \
  -H 'origin: https://redcap.yourcompay.com' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-dest: empty' \
  -H 'referer: https://redcap.yourcompay.com/redcap_v9.8.0/index.php?pid=984&route=AlertsController:setup' \
  -H 'accept-language: en-GB,en;q=0.9,en-US;q=0.8,la;q=0.7' \
  -H 'cookie: survey=vs2k9er1m0pdlfqqprlttih314; PHPSESSID=xxxxxxxxxxxxxxxxxxxxxxxxxx' \
  -H 'dnt: 1' \
  --data 'alert-title=Obs+Combined+Staff+alert+email+-+ob_template&alert-trigger=submit-logic&form-name=ob_template-2780&email-incomplete=0&alert-condition=%5Bcalc_trigger_alert_staff_template%5D+%3D+1&ensure-logic-still-true=on&alert-stop-type=RECORD&cron-send-email-on=now&cron-send-email-on-next-day-type=DAY&cron-send-email-on-next-time=&cron-send-email-on-time-lag-days=&cron-send-email-on-time-lag-hours=&cron-send-email-on-time-lag-minutes=&cron-send-email-on-date=&alert-send-how-many=once&email-repetitive=0&email-repetitive-change=0&email-repetitive-change-calcs=0&email-deleted=0&cron-repeat-for=0&cron-repeat-for-units=DAYS&cron-repeat-for-max=&alert-expiration=&alert-type=EMAIL&phone-number-to-freeform=61482525929&email-from-display=RMH+Covid&email-from=covidhmp%40mh.org.au&email-to=covidhmp%40mh.org.au&email-to-freeform=&email-cc-freeform=&email-bcc-freeform=&email-failed=&email-subject=%5Bcondtxt_alert_title_staff_template%5D%3A+%5Bcalc_name_display%5D+(UR+%5Bur%5D)&alert-message=%3Cp%3E%5Bcondtxt_alert_title_staff_template%5D%3A+%5Bcalc_name_display%5D+(UR+%5Bur%5D)%2C+has+just+recorded+a%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3EHR+%5Bhr_template%5D%3C%2Fp%3E%0D%0A%3Cp%3ESAT+%5Bsat_template%5D%3C%2Fp%3E%0D%0A%3Cp%3ETEMP+%5Btemp_template%5D%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3EThese+numbers+trigged+a+%5Bcondtxt_alert_title_staff_template%5D+for+this+patient+because+their+thresholds+are%3C%2Fp%3E%0D%0A%3Cp%3EClinical+Review%3A+temp+%5Bcr_high_temp%5D+sat+%5Bcr_low_sat%5D+hr+%5Bcr_high_hr%5D%3C%2Fp%3E%0D%0A%3Cp%3EMET+Call%3A+temp+%5Bmc_high_temp%5D+sat+%5Bmc_low_sat%5D+hr+%5Bmc_high_hr%5D%2F%5Bmc_high_hr%5D%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3EUR%3A+%5Bur%5D%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3EName%3A+%5Bcalc_name_display%5D%3C%2Fp%3E%0D%0A%3Cp%3EPhone%3A+%5Bmobile%5D%3C%2Fp%3E%0D%0A%3Cp%3EAge%3A+%5Bcalc_age%5D%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3EAddress%3A%3C%2Fp%3E%0D%0A%3Cp%3E%5Baddr_street_1%5D%3C%2Fp%3E%0D%0A%3Cp%3E%5Baddr_street_2%5D%3C%2Fp%3E%0D%0A%3Cp%3E%5Baddr_suburb%5D%3C%2Fp%3E%0D%0A%3Cp%3E%5Baddr_postcode%5D%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3ETheir+emergency+contact+is+%5Bemcontact_name%5D+%5Bemcontact_phone%5D.%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3EOpen+this+record%2C+and+record+your+response%3C%2Fp%3E%0D%0A%3Cp%3E%5Bform-url%3Aob_template%5D%3Cbr+%2F%3E%3Cbr+%2F%3EAnd%2FOr+add+a+clinical+note%3A%3Cbr+%2F%3E%5Bsurvey-queue-link%5D%3C%2Fp%3E&index_modal_update=216&redcap_csrf_token=fb2c2daccca979c308046dc65007ccbc&alert-message-editor=%3Cp%3E%5Bcondtxt_alert_title_staff_template%5D%3A+%5Bcalc_name_display%5D+(UR+%5Bur%5D)%2C+has+just+recorded+a%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3EHR+%5Bhr_template%5D%3C%2Fp%3E%0A%3Cp%3ESAT+%5Bsat_template%5D%3C%2Fp%3E%0A%3Cp%3ETEMP+%5Btemp_template%5D%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3EThese+numbers+trigged+a+%5Bcondtxt_alert_title_staff_template%5D+for+this+patient+because+their+thresholds+are%3C%2Fp%3E%0A%3Cp%3EClinical+Review%3A+temp+%5Bcr_high_temp%5D+sat+%5Bcr_low_sat%5D+hr+%5Bcr_high_hr%5D%3C%2Fp%3E%0A%3Cp%3EMET+Call%3A+temp+%5Bmc_high_temp%5D+sat+%5Bmc_low_sat%5D+hr+%5Bmc_high_hr%5D%2F%5Bmc_high_hr%5D%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3EUR%3A+%5Bur%5D%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3EName%3A+%5Bcalc_name_display%5D%3C%2Fp%3E%0A%3Cp%3EPhone%3A+%5Bmobile%5D%3C%2Fp%3E%0A%3Cp%3EAge%3A+%5Bcalc_age%5D%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3EAddress%3A%3C%2Fp%3E%0A%3Cp%3E%5Baddr_street_1%5D%3C%2Fp%3E%0A%3Cp%3E%5Baddr_street_2%5D%3C%2Fp%3E%0A%3Cp%3E%5Baddr_suburb%5D%3C%2Fp%3E%0A%3Cp%3E%5Baddr_postcode%5D%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3ETheir+emergency+contact+is+%5Bemcontact_name%5D+%5Bemcontact_phone%5D.%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3EOpen+this+record%2C+and+record+your+response%3C%2Fp%3E%0A%3Cp%3E%5Bform-url%3Aob_template%5D%3Cbr+%2F%3E%3Cbr+%2F%3EAnd%2FOr+add+a+clinical+note%3A%3Cbr+%2F%3E%5Bsurvey-queue-link%5D%3C%2Fp%3E&email-to=covidhmp%40mh.org.au&email-cc=&email-bcc=&phone-number-to=&email-attachment-variable=&redcap_csrf_token=fb2c2daccca979c308046dc65007ccbc' \
  --compressed"

CURL_TEMPLATE_STAFF_COMBINED_SMS = r"curl 'https://redcap.yourcompay.com/redcap_v9.8.0/index.php?pid=984&route=AlertsController:saveAlert' -H 'authority: redcap.yourcompay.com' -H 'accept: */*' -H 'sec-fetch-dest: empty' -H 'x-requested-with: XMLHttpRequest' -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36' -H 'content-type: application/x-www-form-urlencoded; charset=UTF-8' -H 'origin: https://redcap.yourcompay.com' -H 'sec-fetch-site: same-origin' -H 'sec-fetch-mode: cors' -H 'referer: https://redcap.yourcompay.com/redcap_v9.8.0/index.php?pid=984&route=AlertsController:setup' -H 'accept-language: en-GB,en;q=0.9,en-US;q=0.8,la;q=0.7' -H 'cookie: survey=bhdrgi5evnbo8lr1fel0t6u676; PHPSESSID=xxxxxxxxxxxxxxxxxxxxxxxxxx' -H 'dnt: 1' --data 'alert-title=Obs+Combined+Staff+alert+-+ob_template&alert-trigger=submit-logic&form-name=ob_template-2780&email-incomplete=0&alert-condition=%5Bcalc_trigger_alert_staff_template%5D+%3D+1&ensure-logic-still-true=on&alert-stop-type=RECORD&cron-send-email-on=now&cron-send-email-on-next-day-type=DAY&cron-send-email-on-next-time=&cron-send-email-on-time-lag-days=&cron-send-email-on-time-lag-hours=&cron-send-email-on-time-lag-minutes=&cron-send-email-on-date=&alert-send-how-many=once&email-repetitive=0&email-repetitive-change=0&email-repetitive-change-calcs=0&email-deleted=0&cron-repeat-for=0&cron-repeat-for-units=DAYS&cron-repeat-for-max=&alert-expiration=&alert-type=SMS&phone-number-to-freeform=61482525929&email-from-display=&email-from=&email-to-freeform=&email-cc-freeform=&email-bcc-freeform=&email-failed=&email-subject=&alert-message=%3Cp%3E%5Bcondtxt_alert_title_staff_template%5D%3A+%5Bcalc_name_display%5D+(UR+%5Bur%5D)%2C+has+just+recorded+a%3C%2Fp%3E%0D%0A%3Cp%3EHR+%5Bhr_template%5D%2C+%26nbsp%3BSAT+%5Bsat_template%5D%2C+%26nbsp%3BTEMP+%5Btemp_template%5D%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3E%3Cbr+%2F%3EPatient+phone+is+%5Bmobile%5D.%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3E%3Cbr+%2F%3EOpen+this+record%2C+and+record+your+response%3A%3Cbr+%2F%3E%5Bform-url%3Aob_template%5D%3C%2Fp%3E%0D%0A%3Cp%3EAnd%2FOr+add+a+clinical+note%3A%3Cbr+%2F%3E%5Bsurvey-queue-url%5D%3C%2Fp%3E&index_modal_update=200&redcap_csrf_token=539b6e4d00acd50f06d0a8ec66bd9e79&alert-message-editor=%3Cp%3E%5Bcondtxt_alert_title_staff_template%5D%3A+%5Bcalc_name_display%5D+(UR+%5Bur%5D)%2C+has+just+recorded+a%3C%2Fp%3E%0A%3Cp%3EHR+%5Bhr_template%5D%2C+%26nbsp%3BSAT+%5Bsat_template%5D%2C+%26nbsp%3BTEMP+%5Btemp_template%5D%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3E%3Cbr+%2F%3EPatient+phone+is+%5Bmobile%5D.%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3E%3Cbr+%2F%3EOpen+this+record%2C+and+record+your+response%3A%3Cbr+%2F%3E%5Bform-url%3Aob_template%5D%3C%2Fp%3E%0A%3Cp%3EAnd%2FOr+add+a+clinical+note%3A%3Cbr+%2F%3E%5Bsurvey-queue-url%5D%3C%2Fp%3E&email-to=&email-cc=&email-bcc=&phone-number-to=&redcap_csrf_token=539b6e4d00acd50f06d0a8ec66bd9e79' --compressed"

CURL_TEMPLATE_PATIENT_COMBINED_SMS = r"curl 'https://redcap.yourcompay.com/redcap_v9.8.0/index.php?pid=984&route=AlertsController:saveAlert' -H 'authority: redcap.yourcompay.com' -H 'accept: */*' -H 'sec-fetch-dest: empty' -H 'x-requested-with: XMLHttpRequest' -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36' -H 'content-type: application/x-www-form-urlencoded; charset=UTF-8' -H 'origin: https://redcap.yourcompay.com' -H 'sec-fetch-site: same-origin' -H 'sec-fetch-mode: cors' -H 'referer: https://redcap.yourcompay.com/redcap_v9.8.0/index.php?pid=984&route=AlertsController:setup' -H 'accept-language: en-GB,en;q=0.9,en-US;q=0.8,la;q=0.7' -H 'cookie: survey=bhdrgi5evnbo8lr1fel0t6u676; PHPSESSID=xxxxxxxxxxxxxxxxxxxxxxxxxx' -H 'dnt: 1' --data 'alert-title=Obs+Combined+Patient+alert+-+ob_template&alert-trigger=submit-logic&form-name=ob_template-2780&email-incomplete=0&alert-condition=%5Bcalc_trigger_alert_patient_template%5D+%3D+1&ensure-logic-still-true=on&alert-stop-type=RECORD&cron-send-email-on=now&cron-send-email-on-next-day-type=DAY&cron-send-email-on-next-time=&cron-send-email-on-time-lag-days=&cron-send-email-on-time-lag-hours=&cron-send-email-on-time-lag-minutes=&cron-send-email-on-date=&alert-send-how-many=once&email-repetitive=0&email-repetitive-change=0&email-repetitive-change-calcs=0&email-deleted=0&cron-repeat-for=0&cron-repeat-for-units=DAYS&cron-repeat-for-max=&alert-expiration=&alert-type=SMS&phone-number-to=%5Bsurvey-participant-phone%5D&phone-number-to-freeform=&email-from-display=&email-from=&email-to-freeform=&email-cc-freeform=&email-bcc-freeform=&email-failed=&email-subject=&alert-message=%3Cp%3EHi+%5Bname_first%5D%2C%3C%2Fp%3E%0D%0A%3Cp%3E%5Bcondtxt_instr_patient_template%5D%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3E-+Covid+Home+Monitoring+Team+0482525929%3C%2Fp%3E&index_modal_update=201&redcap_csrf_token=af60aa3e9fa27e5901ae7f024251bbdf&alert-message-editor=%3Cp%3EHi+%5Bname_first%5D%2C%3C%2Fp%3E%0A%3Cp%3E%5Bcondtxt_instr_patient_template%5D%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3E-+Covid+Home+Monitoring+Team+0482525929%3C%2Fp%3E&email-to=&email-cc=&email-bcc=&phone-number-to=%5Bsurvey-participant-phone%5D&redcap_csrf_token=af60aa3e9fa27e5901ae7f024251bbdf' --compressed"

CURL_TEMPLATE_LATE_OBS_STAFF_SMS = r"curl 'https://redcap.yourcompay.com/redcap_v9.8.0/index.php?pid=984&route=AlertsController:saveAlert' -H 'authority: redcap.yourcompay.com' -H 'accept: */*' -H 'sec-fetch-dest: empty' -H 'x-requested-with: XMLHttpRequest' -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36' -H 'content-type: application/x-www-form-urlencoded; charset=UTF-8' -H 'origin: https://redcap.yourcompay.com' -H 'sec-fetch-site: same-origin' -H 'sec-fetch-mode: cors' -H 'referer: https://redcap.yourcompay.com/redcap_v9.8.0/index.php?pid=984&route=AlertsController:setup' -H 'accept-language: en-GB,en;q=0.9,en-US;q=0.8,la;q=0.7' -H 'cookie: survey=7pqj6rcmq5fa5nvcikov0dbpf1; PHPSESSID=xxxxxxxxxxxxxxxxxxxxxxxxxx' -H 'dnt: 1' --data 'alert-title=Late+obs+staff+-+ob_template&alert-trigger=submit-logic&form-name=ob_template-2780&email-incomplete=0&alert-condition=%5Bcalc_allow_patient_comms%5D+%3D+1+and+%5Btimestamp_template%5D+%3D+%22%22&ensure-logic-still-true=on&alert-stop-type=RECORD&cron-send-email-on=next_occurrence&cron-send-email-on-next-day-type=DAY&cron-send-email-on-next-time=13%3A00&cron-send-email-on-time-lag-days=&cron-send-email-on-time-lag-hours=&cron-send-email-on-time-lag-minutes=&cron-send-email-on-date=&alert-send-how-many=once&email-repetitive=0&email-repetitive-change=0&email-repetitive-change-calcs=0&email-deleted=0&cron-repeat-for=0&cron-repeat-for-units=DAYS&cron-repeat-for-max=&alert-expiration=&alert-type=SMS&phone-number-to-freeform=61482525929&email-from-display=&email-from=&email-to-freeform=&email-cc-freeform=&email-bcc-freeform=&email-failed=&email-subject=&alert-message=%3Cp%3E%5Bcalc_name_display%5D+(UR+%5Bur%5D)+is+5+hours+late+submitting+an+observation.%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3EPatient+phone+is+%5Bmobile%5D.%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3ETheir+emergency+contact+is+%5Bemcontact_name%5D+%5Bemcontact_phone%5D.%3C%2Fp%3E%0D%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0D%0A%3Cp%3EAdd+a+clinical+note%3A%3Cbr+%2F%3E%5Bsurvey-queue-url%5D%3C%2Fp%3E&index_modal_update=307&redcap_csrf_token=51c31b9265334f210fb4dade58817bcc&alert-message-editor=%3Cp%3E%5Bcalc_name_display%5D+(UR+%5Bur%5D)+is+5+hours+late+submitting+an+observation.%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3EPatient+phone+is+%5Bmobile%5D.%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3ETheir+emergency+contact+is+%5Bemcontact_name%5D+%5Bemcontact_phone%5D.%3C%2Fp%3E%0A%3Cp%3E%26nbsp%3B%3C%2Fp%3E%0A%3Cp%3EAdd+a+clinical+note%3A%3Cbr+%2F%3E%5Bsurvey-queue-url%5D%3C%2Fp%3E&email-to=&email-cc=&email-bcc=&phone-number-to=&redcap_csrf_token=51c31b9265334f210fb4dade58817bcc' --compressed"

ALERT_TEMPLATES = {
    'STAFF_COMBINED_EMAIL': CURL_TEMPLATE_STAFF_COMBINED_EMAIL,
    'STAFF_COMBINED_SMS': CURL_TEMPLATE_STAFF_COMBINED_SMS,
    'PATIENT_COMBINED_SMS': CURL_TEMPLATE_PATIENT_COMBINED_SMS,
    'LATE_OBS_STAFF_SMS': CURL_TEMPLATE_LATE_OBS_STAFF_SMS
}

ALERT_TEMPLATE_ID = {
    'STAFF_COMBINED_EMAIL': '216',
    'STAFF_COMBINED_SMS': '200',
    'PATIENT_COMBINED_SMS': '201',
    'LATE_OBS_STAFF_SMS': '307'
}


def get_postdata_str_from_curl(curlcmd):
    postdata = re.findall(r"--data '([^']+)'", curlcmd)[0]
    assert postdata
    return postdata


def update_alert(alert_template_post_data, alert_type, phpsessionid, csrftoken, projectid, alert_index, obcode):

    template_postdata = parse_qs(keep_blank_values=True,
                                 strict_parsing=True,
                                 qs=alert_template_post_data)
    print(template_postdata)

    for key, val in template_postdata.items():

        # we only expect to get one value for each key
        # *except* 'redcap_csrf_token' because for dumb reasons REDCap sends
        # that twice
        EXPECT_DUPLICATES = ['redcap_csrf_token', 'email-to', 'phone-number-to']
        if len(val) != 1 and key not in EXPECT_DUPLICATES:
            print("Error Parsing curl template. Got multiple values for a POST var")
            breakpoint()

    # Deduplicate the key/vals
    # cleaned_template_data = {k: v[0] for k, v in template_postdata.items()}

    # Hack - remove duplicate email definitions
    # REDCap posts the email-to addresses thusly
    # email-to=covidhmp@mh.org.au
    # email-to=developer@company.com
    # email-to=covidhmp@mh.org.au,developer@company.com
    # ie it sends them again as a comma separated string, we don't want that one
    # But the only one it uses is the comma one, so remove the rest
    template_postdata['email-to'] = [em for em in template_postdata['email-to']
                                     if "," in em]

    # Different alerts need us to transform the template in different ways
    # Some are a simple string.replace('_template', '_4a'), some just be set
    # explicitly
    if alert_type in ['STAFF_COMBINED_EMAIL', 'STAFF_COMBINED_SMS',
                      'PATIENT_COMBINED_SMS']:
        transformed_data = prepare_postvars_obs_simplealert(template_postdata, obcode)
    elif alert_type == 'LATE_OBS_STAFF_SMS':
        transformed_data = prepare_postvars_late_obs_staff(template_postdata, obcode)
    else:
        sys.exit(f"Unknown alert_type: {alert_type}")


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
        'accept': '*/*',
        'sec-fetch-dest': 'empty',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://redcap.yourcompay.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,la;q=0.7',
        'cookie': 'PHPSESSID=%s' % phpessionid,
        'dnt': '1',
    }

    payload = transformed_data

    print(payload)
    # breakpoint()

    r = requests.post(URL, headers=headers, params=transformed_qvars_data, data=payload)
    print(r)
    print(r.text)


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
        tranformed_vals = [v.replace('_template', f'_{obcode_trailer}') for v in vals]

        # remove dupes in the val list
        tranformed_vals = list(set(tranformed_vals))

        # TODO what if that text exists as a literal in the text?
        # TODO do we test for undefined? [variables]?

        transformed_data[tranformed_key] = tranformed_vals

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
    transformed_data['form-name'] = [transformed_data['form-name'][0].replace('_template', f'_{preceding_obnum}')]

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


if __name__ == '__main__':

    if len(sys.argv) != 7:
        sys.exit(
            "Usage:\n%s PROJECTID PHPSESSIONID CSRF_TOKEN ALERT_TYPE ALERTINDEX OB_COD" %
            sys.argv[0])

    projectid = sys.argv[1]
    phpessionid = sys.argv[2]
    csrf_token = sys.argv[3]
    alert_type = sys.argv[4]
    alert_index = sys.argv[5]
    obcode = sys.argv[6]

    # TODO validate phpessionid

    # TODO validate projectid

    # TODO validate csrf_token

    # Is this an alert type we know?
    if alert_type not in ALERT_TEMPLATES.keys():
        sys.exit("Unknown alert type: %s\nKnown types: %s" % (alert_type, ALERT_TEMPLATES.keys()))

    # TODO validate alert_index
    if not alert_index.isdigit():
        sys.exit("Invalid alert index: %s" % alert_index)

    # TODO validate obcode
    if not valid_obcode(obcode):
        sys.exit("Invalid ob_code: %s" % obcode)


    template_postdata_str = get_postdata_str_from_curl(ALERT_TEMPLATES[alert_type])
    template_postdata = parse_qs(keep_blank_values=True,
                                 strict_parsing=True,
                                 qs=template_postdata_str)
    alert_title = template_postdata['alert-title'][0]

    # Did we get the right template? Check the expected redcap object id
    # is the same one that's in the curl cmd template
    assert template_postdata['index_modal_update'][0] == ALERT_TEMPLATE_ID[alert_type]

    print("Does this look right?...")
    pprint({
        'phpsessionid': phpessionid,
        'csrftoken': csrf_token,
        'template': alert_type,
        'template title': alert_title,
        'projectid': projectid,
        'alert_index': alert_index,
        'obcode': obcode
    })

    # Make user confirm before actually sending the update
    if False:
        print("y/n...")
        confirm = input().lower()

        if confirm != 'y':
            sys.exit("Aborting")

    update_alert(
        alert_template_post_data=template_postdata_str,
        alert_type=alert_type,
        phpsessionid=phpessionid,
        csrftoken=csrf_token,
        projectid=projectid,
        alert_index=alert_index,
        obcode=obcode)
