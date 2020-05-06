#!/usr/bin/env python
"""
Covid Home Monitoring Project REDcap project file Auditor

See README.txt in for full details


Instructions:
1. Open recap project 'Covid Home Monitoring'
2. Click 'Project Home'
3. Click 'Other Functionality' tab
4. Find the 'Copy or Back Up the Project' section
5. Tick 'Leave ASIs enabled (unless disabled)' box
6. Click 'Download metadata only (XML)' button
7. Place downloaded xml file in this directory
8. ./audit_project.py downloadefile.xml
9. look at the output
   TODO

"""

from os import access, R_OK
from os.path import isfile
import sys

import pytest
from lxml import etree

EXPECTED_OBSERVATIONS = [
    'ob_template', 'ob_0',
    'ob_1a', 'ob_2b', 'ob_2a', 'ob_2b', 'ob_3a', 'ob_3b', 'ob_4a', 'ob_4b',
    'ob_5a', 'ob_5b', 'ob_6a', 'ob_6b', 'ob_7a', 'ob_7b', 'ob_8a', 'ob_8b',
    'ob_9a', 'ob_9b', 'ob_10a', 'ob_10b', 'ob_11a', 'ob_11b',
    'ob_12a', 'ob_12b', 'ob_13a', 'ob_13b', 'ob_14a', 'ob_14b']

EXPECTED_OBSERVATION_AUTOMATIC_INVITES = [
    # 'ob_template', 'ob_0',   # these two are not automatically sent
    'ob_1a', 'ob_2b', 'ob_2a', 'ob_2b', 'ob_3a', 'ob_3b', 'ob_4a', 'ob_4b',
    'ob_5a', 'ob_5b', 'ob_6a', 'ob_6b', 'ob_7a', 'ob_7b', 'ob_8a', 'ob_8b',
    'ob_9a', 'ob_9b', 'ob_10a', 'ob_10b', 'ob_11a', 'ob_11b',
    'ob_12a', 'ob_12b', 'ob_13a', 'ob_13b', 'ob_14a', 'ob_14b']


# This is the phone number we expect to send our messages 'from'
# It is attached to our Twilio SMS account
AUSTRALIAN_TWILIO_NUMBER = '61480029178'

# This is the real mobile phone staff carry and should receive alerts on
STAFF_ALERT_PHONENUM = '61482525929'


# These are the pretend contact details we often use for testing
DEVELOPER_PHONENUMBERS = ['0419153623', '61419153623']
DEVELOPER_EMAILS = ['danielt@314.net.au', ]

# We're using pytest for most of the heavy lifting, but we need a way to
# pass in the project XML file from the cmdline. Pytest makes that difficult
# we have to define a cmldine arg '--projxmlfile' in the conftest.py file
#
# Then we don't want to parse the XML in every single test. So we parse it
# once and cache it in a module global variable
GLOBAL_REDCAP_XML_ROOT = None


@pytest.fixture
def projxmlpath(request):
    """Get the filepath to the XML file under test"""
    return request.config.getoption("--projxmlfile")


@pytest.fixture
def proj(request):
    """Get a lxml root element for the redcap project xml file
    Cache it in GLOBAL_REDCAP_XML_ROOT so we don't parse it every time"""
    global GLOBAL_REDCAP_XML_ROOT

    if GLOBAL_REDCAP_XML_ROOT is None:
        try:
            xmlfilepath = request.config.getoption("--projxmlfile")
            GLOBAL_REDCAP_XML_ROOT = etree.parse(xmlfilepath).getroot()
        except Exception:
            pytest.exit("Couldn't parse XML file %s" % pytest.GLOBAL_REDCAP_XML_FILEPATH)

    if GLOBAL_REDCAP_XML_ROOT is None:
        pytest.exit("Error accessing project xml root")

    return GLOBAL_REDCAP_XML_ROOT


def test_twilio_sending_from_australian_mobilenum(proj):
    """Project should be configured to send from our twilo australian number"""
    pytest.skip("Cannot test project settings from XML yet")
    # assert == AUSTRALIAN_TWILIO_NUMBER


def test_patient_mobile_is_entered_in_international_format(proj):
    # TODO field helper function
    xpath = r"./Study/MetaDataVersion/ItemDef/[@OID='mobile']"
    itemdef = proj.find(xpath, proj.nsmap)
    assert itemdef is not None
    assert itemdef.attrib['{https://projectredcap.org}FieldType'] == "text"
    assert itemdef.attrib['DataType'] == "integer"

    # TODO make validation lookup helper
    # There should be min/max integer validation enforcing the number format
    # We have to use .xpath() here not .find()
    # And .xpath() takes a different namespace argument to .find()
    xpathns = {'xmlns': proj.nsmap[None]}
    xpathmin = r'./xmlns:RangeCheck/xmlns:CheckValue[text()="61400000000"]'
    xpathmax = r'./xmlns:RangeCheck/xmlns:CheckValue[text()="61499999999"]'
    range_check_min = itemdef.xpath(xpathmin, namespaces=xpathns)
    range_check_max = itemdef.xpath(xpathmax, namespaces=xpathns)
    assert range_check_min is not None
    assert range_check_max is not None


def test_observation_template_exists(proj):
    assert get_instrument(proj, 'ob_template') is not None


def test_registration_instrument_exists(proj):
    assert get_instrument(proj, 'registration') is not None


def test_clinicalnotes_instrument_exists(proj):
    assert get_instrument(proj, 'clinicalnote') is not None


def test_clinicalnotes_is_repeating_instrument(proj):
    """Clinical Notes must be set as repeatable so clinician's can add many notes"""
    instr = "clinicalnote"
    xpath = r"./Study/GlobalVariables/redcap:RepeatingInstrumentsAndEvents/redcap:RepeatingInstruments/redcap:RepeatingInstrument[@redcap:RepeatInstrument='%s']" % instr
    assert proj.find(xpath, proj.nsmap) is not None


def test_clinicalnotes_instrument_has_survey(proj):
    """Clinical Notes survey must be available as a survey"""
    assert get_instrument_survey(proj, 'clinicalnote') is not None


def test_clinicalnotes_survey_repeat_settings(proj):
    """Clinical Notes survey has to be able to repeat and should prompt the
    user to """
    surv = get_instrument_survey(proj, 'clinicalnote')
    assert surv.attrib['repeat_survey_enabled'] == "1"

    # The repeat button should show after they've submitted their note
    # And should have sensible text to explain it
    assert surv.attrib['repeat_survey_btn_location'] == "AFTER_SUBMIT"
    assert surv.attrib['repeat_survey_btn_text'] == "Add another clinical note"


def test_all_surveys_are_set_to_enhanced_ui(proj):
    """All surveys should have the 'Use enhanced radio buttons and checkboxes?'
    setting ticked"""
    xpath = r"./Study/GlobalVariables/redcap:SurveysGroup/redcap:Surveys"
    return proj.find(xpath, proj.nsmap)
    for surv in proj.find(xpath, proj.nsmap):
        assert surv.attrib['enhanced_choices'] == "1"


@pytest.mark.parametrize("obs", EXPECTED_OBSERVATIONS)
def test_observation_exists(proj, obs):
    assert get_instrument(proj, obs) is not None


@pytest.mark.parametrize("obs", EXPECTED_OBSERVATIONS)
def test_observation_structure_matches_template(proj, obs):
    tpl = get_instrument(proj, 'ob_template')
    obs = get_instrument(proj, obs)

    pytest.skip("Not Implemented")


@pytest.mark.parametrize("obs", EXPECTED_OBSERVATIONS)
def test_observation_has_survey(proj, obs):
    """Is a survey instrument defined for this observation"""
    assert get_instrument_survey(proj, obs) is not None


@pytest.mark.parametrize("obs", EXPECTED_OBSERVATION_AUTOMATIC_INVITES)
def test_all_observations_have_automated_invite(proj, obs):
    """Does this observation (eg ob_3a) have an automatic invite defined"""
    assert get_instrument_survey_automated_invite(proj, obs) is not None


def test_registration_does_not_have_automated_invite(proj):
    # Either note defined, or disabled
    invite = get_instrument_survey_automated_invite(proj, 'registration')
    assert invite is None or invite.attrib['active'] == '0'


def test_clinicalnote_does_not_have_automated_invite(proj):
    invite = get_instrument_survey_automated_invite(proj, 'clinicalnote')
    assert invite is None or invite.attrib['active'] == '0'


def test_observation_template_does_not_have_automated_invite(proj):
    invite = get_instrument_survey_automated_invite(proj, 'ob_template')
    assert invite is None or invite.attrib['active'] == '0'


def test_first_observation_does_not_have_automated_invite(proj):
    """The patient gets a link to their first observation during their
    registration, not via automatic invites"""
    invite = get_instrument_survey_automated_invite(proj, 'ob_0')
    assert invite is None or invite.attrib['active'] == '0'


def test_observation_survey_template_settings(proj):
    surv = get_instrument_survey(proj, 'ob_template')

    # Enabled
    assert surv.attrib['survey_enabled'] == "1"

    # Each instrument 'section' should be a different page of the survey
    # We need to do this so that fields defaults are calcuated before they
    # are displayed to patient
    assert surv.attrib['question_by_section'] == "1"

    # 'Previous' button should be disabled
    # We can't allow them to go back and change text boxes because we depend
    # on default value fields that won't get updated :(
    assert surv.attrib['hide_back_button'] == "1"

    # Fancy buttons
    assert surv.attrib['enhanced_choices'] == "1"


def test_observation_surveys_settings_all_match_template_settings(proj):
    """Every observation survey should match the settings on ob_template"""
    template = get_instrument_survey(proj, 'ob_template')

    # We expect these to be different on each survey
    IGNORE_SETTINGS = ['title', 'form_name', 'check_diversity_view_results', 'logo']


    template_vars = {
        k: v for k, v in template.attrib.items() if k not in IGNORE_SETTINGS}

    for obs in EXPECTED_OBSERVATIONS:
        # if obs in ['ob_4a', 'ob_6b', 'ob_8b', 'ob_9b', 'ob_14a']:
        #     continue

        surv = get_instrument_survey(proj, obs)
        surv_vars = {
            k: v for k, v in surv.attrib.items() if k not in IGNORE_SETTINGS}

        # if surv_vars != template_vars:
        #     breakpoint()

        assert surv_vars == template_vars


@pytest.mark.parametrize("obs", EXPECTED_OBSERVATION_AUTOMATIC_INVITES)
def test_observation_auto_invite_settings(proj, obs):
    """Check a number of specific logic / settings on observation auto invite"""
    invite = get_instrument_survey_automated_invite(proj, obs)

    # Triggers on the correct observation
    # ob_1a / ob_1b trigger on ob_0
    # ob_2a triggers on ob_1a
    # ob_2b triggers on ob_1b
    # ...and so on
    expected_trigger_obs = get_obs_preceding_obs(obs)
    assert invite.attrib['condition_surveycomplete_survey_id'] == expected_trigger_obs

    # The auto invite must be enabled
    assert invite.attrib['active'] == '1'

    # Sends a SMS invite
    assert invite.attrib['delivery_type'] == "SMS_INVITE_WEB"

    # Triggers at 8am or 3pm depending on type
    assert invite.attrib['condition_send_next_day_type'] == "DAY"
    if obs_is_morning(obs):
        expected_time = "08:00:00"
    elif obs_is_afternoon(obs):
        expected_time = "15:00:00"
    else:
        assert False  # Unknown obs type?

    assert invite.attrib['condition_send_next_time'] == expected_time

    # Only sends if they're still under observation
    # And checks this logic as it's about to be sent
    assert invite.attrib['condition_andor'] == "AND"
    assert invite.attrib['condition_logic'] == "[calc_mon_status_observation] = 1"
    assert invite.attrib['reeval_before_send'] == "1"

    # Is set to remind the patient
    # Twice, every two hours
    assert invite.attrib['reminder_type'] == "TIME_LAG"
    assert invite.attrib['reminder_num'] == "2"  # remind them twice
    assert invite.attrib['reminder_timelag_days'] == "0"
    assert invite.attrib['reminder_timelag_hours'] == "2"
    assert invite.attrib['reminder_timelag_minutes'] == "0"


def test_observation_auto_invite_all_have_same_text(proj):
    # Grab the invite message text from each observation invite
    invite_texts = [
        # Be sure to store the message string. Not a node reference
        "" + get_instrument_survey_automated_invite(proj, obs).attrib['email_content']
        for obs in EXPECTED_OBSERVATION_AUTOMATIC_INVITES
    ]

    # We should have got one for each obs
    assert len(invite_texts) == len(EXPECTED_OBSERVATION_AUTOMATIC_INVITES)

    # Remove dupes. They should all be the same
    assert len(set(invite_texts)) == 1



def test_alert_template_exists_combined_staff_alert_sms_exists(proj):
    assert get_alert_template_combined_staff_alert_sms(proj) is not None


def test_alert_template_exists_combined_staff_alert_email_exists(proj):
    assert get_alert_template_combined_staff_alert_email(proj) is not None


def test_alert_template_exists_combined_patient_alert_sms_exists(proj):
    assert get_alert_template_combined_patient_alert_sms(proj) is not None


@pytest.mark.parametrize(", obs", EXPECTED_OBSERVATIONS)
def test_observation_has_staff_alerts(proj, obs):

    # SMS combined alert
    alert_title = "Obs Combined Staff alert - %s" % obs
    node = get_alert(proj, alert_title, form_name=obs, alert_type='SMS')
    assert node is not None

    # EMAIL combined alert
    alert_title = "Obs Combined Staff alert email - %s" % obs
    node = get_alert(proj, alert_title, form_name=obs, alert_type='EMAIL')
    assert node is not None


@pytest.mark.parametrize(", obs", EXPECTED_OBSERVATIONS)
def test_observation_has_patient_alert(proj, obs):
    # SMS combined alert
    alert_title = "Obs Combined Patient alert - %s" % obs
    node = get_alert(proj, alert_title, form_name=obs, alert_type='SMS')
    assert node is not None


@pytest.mark.parametrize(", obs", EXPECTED_OBSERVATIONS)
def test_observation_staff_alerts_match_template(proj, obs):
    """Each ob_nn observation staff alert should have the same structure and
    content as the ob_template version of the alert. Tests SMS and EMAIL version"""
    if obs == "ob_template":
        return True

    template = get_alert_template_combined_staff_alert_sms(proj)
    alert_title = "Obs Combined Staff alert - %s" % obs
    sms = get_alert(proj, alert_title, form_name=obs, alert_type='SMS')
    assert obs_alert_matches_template(sms, obs, template)

    template = get_alert_template_combined_staff_alert_email(proj)
    alert_title = "Obs Combined Staff alert email - %s" % obs
    email = get_alert(proj, alert_title, form_name=obs, alert_type='EMAIL')
    assert obs_alert_matches_template(email, obs, template)


@pytest.mark.parametrize(", obs", EXPECTED_OBSERVATIONS)
def test_observation_patient_alerts_match_template(proj, obs):
    """Each ob_nn observation alert for the patient should have the same
    content and settings as the ob_template version."""
    if obs == "ob_template":
        return True

    template = get_alert_template_combined_patient_alert_sms(proj)
    alert_title = "Obs Combined Patient alert - %s" % obs
    sms = get_alert(proj, alert_title, form_name=obs, alert_type='SMS')
    assert obs_alert_matches_template(sms, obs, template)


@pytest.mark.parametrize(", obs", EXPECTED_OBSERVATIONS)
def test_late_observation_staff_alert_match_template(proj, obs):
    """Each 'Late obs staff - ob_xx' alert should have the same structure and
    content as the 'Late obs staff - ob_template' version of the alert."""

    # Skip the template itself, and ob_0 which should't get this alert
    # We don't worry about late observations for the demo _0 obs
    if obs in ["ob_template", "ob_0"]:
        return True

    # These trigger on the previous days alert
    preceding_obs = get_obs_preceding_obs(obs)
    alert_title = "Late obs staff - %s" % obs
    sms = get_alert(proj, alert_title, form_name=preceding_obs, alert_type='SMS')

    template = get_alert_template_late_obs_staff_alert_sms(proj)
    assert obs_alert_matches_template(sms, obs, template)


@pytest.mark.parametrize(", obs", EXPECTED_OBSERVATIONS)
def test_late_observation_staff_alert_triggers_at_5_hours(proj, obs):
    # We don't worry about late observations for the demo _0 obs
    if obs in ["ob_template", "ob_0"]:
        return True

    # These trigger on the previous days alert, so we load them that way
    # These trigger on the previous days alert
    preceding_obs = get_obs_preceding_obs(obs)
    alert_title = "Late obs staff - %s" % obs
    sms = get_alert(proj, alert_title, form_name=preceding_obs, alert_type='SMS')

    # Check the time that it triggers at:
    if obs_is_morning(obs):
        assert sms.attrib['cron_send_email_on_next_time'] == "13:00:00"
    elif obs_is_afternoon(obs):
        assert sms.attrib['cron_send_email_on_next_time'] == "20:00:00"
    else:
        assert False  # unknown obcode


def test_staff_are_reminded_to_call_bidaily_patients_after_n_days(proj):
    """We should prompt staff after N days to call our daily monitoring patients"""

    TITLE = 'Staff Reminder Patient Call BIDAILY Day 7'
    sms = get_alert(proj, alert_title=TITLE, form_name=None, alert_type='SMS')
    assert sms is not None

    AFTER_DAYS = 7
    assert sms.attrib['cron_send_email_on'] == "time_lag"
    assert sms.attrib['cron_send_email_on_time_lag_days'] == str(AFTER_DAYS)
    assert sms.attrib['cron_send_email_on_time_lag_hours'] == "0"
    assert sms.attrib['cron_send_email_on_time_lag_minutes'] == "0"


def test_post_discharge_patient_followup_alert_is_scheduled(proj):
    """After a patient has been discharged, and if they are healthy, we should
    contact them after N days and ask them to participtate in our feedback
    survey"""
    TITLE = 'Post Discharge Patient Follow-up - SMS'

    sms = get_alert(proj, alert_title=TITLE, form_name=None, alert_type='SMS')
    assert sms is not None

    AFTER_DAYS = 2
    assert sms.attrib['cron_send_email_on'] == "time_lag"
    assert sms.attrib['cron_send_email_on_time_lag_days'] == str(AFTER_DAYS)
    assert sms.attrib['cron_send_email_on_time_lag_hours'] == "0"
    assert sms.attrib['cron_send_email_on_time_lag_minutes'] == "0"


def obs_alert_matches_template(alert, obsid, templatealert):
    """Compare a redcap observation <redcap:Alerts nodes to see if its content
    is equivalent to the _template version of the alert. We don't expect them
    to be identical. The variables names (eg hr_template hr_1a) will differ
    and some meta data like alert IDs and timestamps."""

    # These fields we expect to be different
    IGNORE_FIELDS = ['alert_number', 'form_name', 'alert_condition',
                     'alert_message', 'alert_title', 'email_subject',
                     'email_timestamp_sent', 'email_sent']

    # Compare all the simple fields that should be identical
    alert_vars = {
        k: v for k, v in alert.attrib.items() if k not in IGNORE_FIELDS}

    template_vars = {
        k: v for k, v in templatealert.attrib.items() if k not in IGNORE_FIELDS}

    for field in [f for f in templatealert.attrib.keys() if f not in IGNORE_FIELDS]:
        # if not alert_vars[field] == template_vars[field]:
        #     breakpoint()

        #pytest.xfail("Not Implemented")
        assert alert_vars[field] == template_vars[field]

    if not alert_vars == template_vars:
        return False

    # Check the content (title, subject, bodytext) of the alert and conditional
    # logic. These we expect to change based on the obs eg hr_template, hr_3a
    # eg
    #    alert_title="Obs Combined Patient alert - ob_4a"
    #    alert_condition # "[calc_trigger_alert_patient_4a] = 1"
    fields = ['alert_condition', 'alert_title', 'alert_message']
    for field in fields:
        test = equiv_template_text(text=alert.attrib[field],
                                   tpltext=templatealert.attrib[field],
                                   expected_obs_id=obsid)
        # if not test:
        #    print(f"error with field {field}")
        #    breakpoint()
        assert test

    # The alert shouldn't be using any variables that end in _template
    # [xxx_template] vars either. We might have forgotten to change one when
    # copying from the template.
    for field in fields:
        assert "_template]" not in alert.attrib[field]

    return True


def test_staff_reminder_patient_day_7_alert_exists(proj):
    #  Staff Reminder Patient Call BIDAILY Day 7 - SMS
    pytest.skip("Not Implemented")


def get_instrument_variable_names(proj, id):
    instr = get_instrument(proj, id)

    item_group_oids = [x.attrib['ItemGroupOID'] for x in
                       instr.findall(r'./ItemGroupRef', proj.nsmap)]

    variables = []
    for oid in item_group_oids:
        for item_group_def in proj.findall(r".//ItemGroupDef[@OID='%s']" % oid, proj.nsmap):
            for item_ref in item_group_def:
                variables.append(item_ref.attrib['ItemOID'])

    return variables


def get_instrument(proj, id):
    return proj.find(
        r"./Study/MetaDataVersion/FormDef[@redcap:FormName='%s']" % id,
        proj.nsmap)


def get_instrument_survey(proj, id):
    xpath = r"./Study/GlobalVariables/redcap:SurveysGroup/redcap:Surveys[@form_name='%s']" % id
    return proj.find(xpath, proj.nsmap)


def get_instrument_survey_automated_invite(proj, id):
    """Given an instrument id return the automated invite definition if defined"""
    xpath = r"./Study/GlobalVariables/redcap:SurveysSchedulerGroup/redcap:SurveysScheduler[@survey_id='%s']" % id
    return proj.find(xpath, proj.nsmap)



def get_alert_template_combined_staff_alert_sms(proj):
    alert_title = "Obs Combined Staff alert - ob_template"
    form_name = "ob_template"
    alert_type = "SMS"

    node = get_alert(proj, alert_title, form_name, alert_type)

    assert node.attrib['alert_condition'] == "[calc_trigger_alert_staff_template] = 1"

    return node


def get_alert_template_combined_staff_alert_email(proj):
    alert_title = "Obs Combined Staff alert email - ob_template"
    form_name = "ob_template"
    alert_type = "EMAIL"

    node = get_alert(proj, alert_title, form_name, alert_type)

    assert node.attrib['alert_condition'] == "[calc_trigger_alert_staff_template] = 1"

    return node


def get_alert_template_combined_patient_alert_sms(proj):
    alert_title = "Obs Combined Patient alert - ob_template"
    form_name = "ob_template"
    alert_type = "SMS"

    node = get_alert(proj, alert_title, form_name, alert_type)
    assert node.attrib['alert_type'] == alert_type
    assert node.attrib['alert_condition'] == "[calc_trigger_alert_patient_template] = 1"

    return node


def get_alert_template_late_obs_staff_alert_sms(proj):
    alert_title = "Late obs staff - ob_template"
    form_name = "ob_template"
    alert_type = "SMS"

    node = get_alert(proj, alert_title, form_name, alert_type)
    assert node.attrib['alert_type'] == alert_type
    assert node.attrib['alert_condition'] == "[calc_allow_patient_comms] = 1 and [timestamp_template] = \"\""

    return node


def get_alert(proj, alert_title, form_name, alert_type):
    alerts_path = r"./Study/GlobalVariables/redcap:AlertsGroup"
    alerts = proj.find(alerts_path, proj.nsmap)
    xpath = f"redcap:Alerts/[@form_name='{form_name}'][@alert_title='{alert_title}'][@alert_type='{alert_type}']"
    return alerts.find(xpath, proj.nsmap)


def obs_is_morning(obcode):
    """Given an observation code (eg 'ob_1a', 'ob12_b') is this a morning obs?"""
    return obcode[-1] == 'a'


def obs_is_afternoon(obcode):
    """Given an observation code (eg 'ob_1a', 'ob12_b') is this an afternoon obs?"""
    return obcode[-1] == 'b'


def get_obs_preceding_obs(obcode):
    """Given an observation eg ob_4a, which observation precedes it?
    We have two streams, the 'a' (morning) and 'b' (afternoon) obs.

    But the first day follows on from the demo observation ob_0 -> ob_1a
                                                           ob_0 -> ob_1b
    The rest follow the previous. ob_1a -> ob_2a -> ob_3a
                                  ob_1b -> ob_2b -> ob_3b
    """
    assert valid_ob_code(obcode)

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


def valid_ob_code(obcode):
    """Is obcode a valid looking observation"""
    # return len(obcode) >= 3 and obcode[0:3] == 'ob_' and obcode[-1] in ['0', 'a', 'b']
    return obcode in EXPECTED_OBSERVATIONS


def equiv_template_text(text, tpltext, expected_obs_id):
    """True if text matches tpltext except for variable names.

    The text may be different inside [variable definitions] so long as the
    difference is only the suffix changing from _template to _expected_obs_id
    eg.
        'Your Hr was [hr_3a]' == 'Your Hr was [hr_template]' -> True
        'Your Hr was [hr_3a]' == 'Heart rate  [hr_template]' -> False"""
    expected_suffix = expected_obs_id[3:]  # 'ob_3a' ->  '3a'
    return tpltext == text.replace(f'_{expected_suffix}', '_template')


def test_equiv_template_text():
    """Internal test of audit logic"""
    assert equiv_template_text("hello", "hello", "ob_1a")
    assert not equiv_template_text("hello", "Hello", "ob_1a")
    assert equiv_template_text("", "", "")
    assert equiv_template_text("", "", "ob_1a")
    assert equiv_template_text("hello [name]", "hello [name]", "1a")
    assert equiv_template_text("hello [name_1a]", "hello [name_template]", "ob_1a")

    assert not equiv_template_text("hello [name]", "hello [name_template]", "ob_1a")

    # We are testing a _1a alert, but the template has _3a
    assert not equiv_template_text("hello [name_3a]", "hello [name_template]", "ob_1a")


def test_xml_doesnt_contain_dev_email(projxmlpath):
    """Daniel's email should not be present in the project
    TODO: Bad test"""
    for email in DEVELOPER_EMAILS:
        with open(projxmlpath) as file:
            assert email not in file.read()


def test_xml_doesnt_contain_dev_phone(projxmlpath):
    """Daniel's email should not be present in the project
    TODO: Bad test"""
    for phone in DEVELOPER_PHONENUMBERS:
        with open(projxmlpath) as file:
            assert phone not in file.read()


if __name__ == '__main__':

    # TODO cmd line checking
    if len(sys.argv) != 2:
        sys.exit("Usage:\n%s Project.REDCAP.xml" % sys.argv[0])

    proj_path = sys.argv[1]

    if not (isfile(proj_path) and access(proj_path, R_OK)):
        sys.exit("%s does not exist or is not readable" % proj_path)

    # Hand over to pytest
    # HACK. Stuff xml path into a pytest variable, defined in conftest.py
    pytest.main(["audit_project.py", "-v",
                 "--projxmlfile", proj_path])
