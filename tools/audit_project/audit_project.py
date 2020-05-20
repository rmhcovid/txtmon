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

from copy import deepcopy
from os import access, R_OK
from os.path import isfile
import sys

import pytest
from lxml import etree

EXPECTED_OBSERVATIONS = [
    'ob_template', 'ob_0',
    'ob_1a', 'ob_1b', 'ob_2a', 'ob_2b', 'ob_3a', 'ob_3b', 'ob_4a', 'ob_4b',
    'ob_5a', 'ob_5b', 'ob_6a', 'ob_6b', 'ob_7a', 'ob_7b', 'ob_8a', 'ob_8b',
    'ob_9a', 'ob_9b', 'ob_10a', 'ob_10b', 'ob_11a', 'ob_11b', 'ob_12a', 'ob_12b',
    'ob_13a', 'ob_13b', 'ob_14a', 'ob_14b']

EXPECTED_OBSERVATION_AUTOMATIC_INVITES = [
    # 'ob_template', 'ob_0',   # these two are not automatically sent
    'ob_1a', 'ob_1b', 'ob_2a', 'ob_2b', 'ob_3a', 'ob_3b', 'ob_4a', 'ob_4b',
    'ob_5a', 'ob_5b', 'ob_6a', 'ob_6b', 'ob_7a', 'ob_7b', 'ob_8a', 'ob_8b',
    'ob_9a', 'ob_9b', 'ob_10a', 'ob_10b', 'ob_11a', 'ob_11b', 'ob_12a', 'ob_12b',
    'ob_13a', 'ob_13b', 'ob_14a', 'ob_14b']


# This is the phone number we expect to send our messages 'from'
# It is attached to our Twilio SMS account
AUSTRALIAN_TWILIO_NUMBER = '61480029178'

# This is the real mobile phone staff carry and should receive alerts on
STAFF_ALERT_PHONENUM = '61482525929'


# These are the pretend contact details we often use for testing
DEVELOPER_PHONENUMBERS = ['', '']
DEVELOPER_EMAILS = ['', ]

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
    pytest.skip("Project settings aren't present in XML file. Need to find alternate test method.")
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


# TODO rename and test this
def form_tree_definition(proj, formname):
    """Turn the form (instrument) definition in the project xml file into
    a python dictionary tree.

    In the XML structure items are defined in different places and the are
    various places where 'ref' items have to be looked up to find 'def'.

    Turn it into a nice neat:
    FormDef
        ItemGroup(s)
            Item(s)
    """

    """
    Form Def
    <FormDef OID="Form.ob_template" Name="Ob Template" Repeating="No" redcap:FormName="ob_template">
        <ItemGroupRef ItemGroupOID="ob_template.timestamp_template" Mandatory="No"/>
        ...
    </FormDef>


    <ItemGroupDef OID="ob_template.timestamp_template" Name="Ob Template" Repeating="No">
        <ItemRef ItemOID="timestamp_template" Mandatory="No" redcap:Variable="timestamp_template"/>
        <ItemRef ItemOID="title_measurements_template" Mandatory="No" redcap:Variable="title_measurements_template"/>
        ...
    </ItemGroupDef>
    <ItemGroupDef OID="ob_template.supqn_tired_template" Name="Confirm and Submit" Repeating="No">
        ...
    </ItemGroupDef>
    ...
    """

    tree = {}
    xpath = r"./Study/MetaDataVersion/FormDef/[@OID='%s']" % formname
    root = proj.find(xpath, proj.nsmap)

    tree = {**tree, **root.attrib}
    # tree['ItemGroupRef'] = []
    # tree['ItemGroupDef'] = []
    tree['ItemGroup'] = []

    for igr in root.getchildren():
        igr_oid = igr.attrib['ItemGroupOID']

        igd_xpath = r"./Study/MetaDataVersion/ItemGroupDef/[@OID='%s']" % igr_oid
        igd = proj.find(igd_xpath, proj.nsmap)

        itemgroup = {**igr.attrib, **igd.attrib}

        itemgroup['Item'] = []
        for itemref in igd.getchildren():
            item_oid = itemref.attrib['ItemOID']

            itmd_xpath = r"./Study/MetaDataVersion/ItemDef/[@OID='%s']" % item_oid
            itm = proj.find(itmd_xpath, proj.nsmap)

            item = {
                **itm.attrib
            }
            itemgroup['Item'].append(item)

        tree['ItemGroup'].append(itemgroup)

    return tree


# TODO rename and test this
def rename_tree(form_tree, obcode):
    """Given a tree template from form_tree_definition('Form.ob_template')
    recurse downwards renaming keys/vals from ob_template to ob_{code}

    Why? This results in a nice python dictionary object that we can ==
    compare with pytest and get pretty printed diff.
    """
    ob_suffix = obcode.split('_')[1]
    new_suffix = f'_{ob_suffix}'
    new = deepcopy(form_tree)
    new['Name'] = new['Name'].replace('Template', ob_suffix)
    new['OID'] = new['OID'].replace('_template', new_suffix)
    new['{https://projectredcap.org}FormName'] = new['{https://projectredcap.org}FormName'].replace('_template', new_suffix)

    for ig in new['ItemGroup']:
        ig['Name'] = ig['Name'].replace('Template', ob_suffix)
        ig['OID'] = ig['OID'].replace('_template', new_suffix)
        ig['ItemGroupOID'] = ig['ItemGroupOID'].replace('_template', new_suffix)

        # ig['{https://projectredcap.org}FormName'] = new['{https://projectredcap.org}FormName'].replace('_template', new_suffix)

        for item in ig['Item']:

            for k, v in item.items():
                item[k] = v.replace('_template', new_suffix)

            # item['Name'] = new['Name'].replace('_template', new_suffix)
            # item['{https://projectredcap.org}FormName'] = new['{https://projectredcap.org}FormName'].replace('_template', new_suffix)

    return new


@pytest.mark.parametrize("obs", EXPECTED_OBSERVATIONS)
def test_observation_structure_matches_template(proj, obs):
    # No need to compare template to itself
    if obs == 'ob_template':
        return True

    # Are the fields the same?
    # Are the
    # TODO break out all this code



    # Should have the same field structure
    tpl_formdef = form_tree_definition(proj, "Form.ob_template")
    obs_formdef = form_tree_definition(proj, f"Form.{obs}")

    assert obs_formdef == rename_tree(tpl_formdef, obs)


@pytest.mark.parametrize("obs", EXPECTED_OBSERVATIONS)
def test_observation_has_survey(proj, obs):
    """Is a survey instrument defined for this observation"""
    assert get_instrument_survey(proj, obs) is not None


@pytest.mark.parametrize("obs", EXPECTED_OBSERVATION_AUTOMATIC_INVITES)
def test_observation_has_automated_invite(proj, obs):
    """Does this observation (eg ob_3a) have an automatic invite defined"""
    assert get_instrument_survey_automated_invite(proj, obs) is not None


def test_registration_does_not_have_automated_invite(proj):
    """Registration is triggered by a staff member opening a link to register
    a new patient. It should not be automatically sent to anyone"""
    # Either not defined, or disabled (can't work out how to del the old one)
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

    # Invites should be triggered on save of ob_0
    assert invite.attrib['condition_surveycomplete_survey_id'] == 'ob_0'

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

    # Logic shoudl be enabled (instrument save, 'AND' ....)
    # Logic should be checked again before send
    assert invite.attrib['condition_andor'] == "AND"
    assert invite.attrib['reeval_before_send'] == "1"

    # Only sends if they're still under observation
    active_monitoring_check = '[calc_mon_status_observation] = 1'
    assert active_monitoring_check in invite.attrib['condition_logic']

    # Confirm the trigger scheduling. This is trick and ugly because of
    # redcap limitations. Read the design reason for this in
    # documentation/redcap_design_overview.md  'Observation Invites'
    # Fragile tests :(
    send_day = get_obs_day(obs)
    trigger_day = send_day - 1
    trigger_logic = f"[calc_mon_status_observation] = 1 and (datediff([mon_admission_date], 'today', 'd') = {trigger_day} or datediff([mon_admission_date], 'today', 'd') = {send_day})"

    assert invite.attrib['condition_logic'] == trigger_logic


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


def test_email_alerts_have_to_address(proj):
    """All email alerts in the system must have an email-to address.
    Regression test. One of our tools broke and removed the to address in some
    existing email alerts
    """
    alerts_path = r"./Study/GlobalVariables/redcap:AlertsGroup"
    alerts = proj.find(alerts_path, proj.nsmap)
    xpath = f"redcap:Alerts/[@alert_type='EMAIL']"
    for alert in alerts.findall(xpath, proj.nsmap):
        assert alert.attrib['email_to'] > ''


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

    ignore_fields = ['cron_send_email_on_next_time']

    template = get_alert_template_combined_staff_alert_sms(proj)
    alert_title = "Obs Combined Staff alert - %s" % obs
    sms = get_alert(proj, alert_title, form_name=obs, alert_type='SMS')
    assert obs_alert_matches_template(sms, obs, template, ignore_fields)

    template = get_alert_template_combined_staff_alert_email(proj)
    alert_title = "Obs Combined Staff alert email - %s" % obs
    email = get_alert(proj, alert_title, form_name=obs, alert_type='EMAIL')
    assert obs_alert_matches_template(email, obs, template, ignore_fields)


@pytest.mark.parametrize(", obs", EXPECTED_OBSERVATIONS)
def test_observation_patient_alerts_match_template(proj, obs):
    """Each ob_nn observation alert for the patient should have the same
    content and settings as the ob_template version."""
    if obs == "ob_template":
        return True

    template = get_alert_template_combined_patient_alert_sms(proj)
    alert_title = "Obs Combined Patient alert - %s" % obs
    sms = get_alert(proj, alert_title, form_name=obs, alert_type='SMS')
    assert obs_alert_matches_template(sms, obs, template, [])


@pytest.mark.parametrize(", obs", EXPECTED_OBSERVATIONS)
def test_late_observation_staff_alert_match_template(proj, obs):
    """Each 'Late obs staff - ob_xx' alert should have the same structure and
    content as the 'Late obs staff - ob_template' version of the alert."""

    # Skip the template itself, and ob_0 which should't get this alert
    # We don't worry about late observations for the demo _0 obs
    if obs in ["ob_template", "ob_0"]:
        return True

    # These trigger on the previous days alert
    # Dumb redcap reason. 
    # See documentation/redcap_design_overview.md  'Late Observation Alert for Staff'
    preceding_obs = get_obs_preceding_obs(obs)
    alert_title = "Late obs staff - %s" % obs
    sms = get_alert(proj, alert_title, form_name=preceding_obs, alert_type='SMS')
    template = get_alert_template_late_obs_staff_alert_sms(proj)

    # Ignore the time of day, that will be different for morning/afternoons
    ignore_fields = ['cron_send_email_on_next_time']
    assert obs_alert_matches_template(sms, obs, template, ignore_fields)


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


def test_registered_patients_should_immediately_be_directed_to_consent_form(proj):
    """After a patient is registered we then ask them to fill out the Consent
    instrument"""
    # This is implemented as an alert that is sent on Registration save
    # that checks the monitoring group of the new patient
    # Remember ineligible patients have no need to go to the consent form
    # but they still get a Registration instrument.
    TITLE = 'Patient Registration - Consent'
    sms = get_alert(proj, title=TITLE, form_name='registration', alert_type='SMS')
    assert sms is not None

    # TODO change this to be an AST comparison so it's less flakey
    alert_logic = sms.attrib['alert_condition']
    assert alert_logic == "[mon_group] <> '0'"

    # Should be sent immediately
    assert sms.attrib['cron_send_email_on'] == 'now'


def test_after_completing_consent_patient_should_be_linked_to_first_observation(proj):
    """After patient completes consent form (and agrees) they should be
    get a link telling them what to do next (based on monitoring group)

    BIDAILY - should get first observation link
    WEEKLY - just a thank you and a note to speak to staff"""
    TITLE = 'Patient Registration - BIDAILY'

    # Should trigger off of consent
    trigger_instrument = 'consent'
    sms = get_alert(proj, title=TITLE, form_name=trigger_instrument, alert_type='SMS')
    assert sms is not None

    # TODO change this to be an AST comparison so it's less flakey
    # Check that they've agreed, and they're under observation
    alert_logic = sms.attrib['alert_condition']
    assert 'cons_agree' in alert_logic
    assert 'calc_mon_status_observation' in alert_logic


def test_staff_are_reminded_to_call_bidaily_patients_after_n_days(proj):
    """We should prompt staff after N days to call our daily monitoring patients"""

    TITLE = 'Staff Reminder Patient Call BIDAILY Day 7'
    sms = get_alert(proj, title=TITLE, form_name='registration', alert_type='SMS')
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

    # TODO change this to be based on Discharge form
    sms = get_alert(proj, title=TITLE, form_name='discharge', alert_type='SMS')
    assert sms is not None

    AFTER_DAYS = 2
    assert sms.attrib['cron_send_email_on'] == "time_lag"
    assert sms.attrib['cron_send_email_on_time_lag_days'] == str(AFTER_DAYS)
    assert sms.attrib['cron_send_email_on_time_lag_hours'] == "0"
    assert sms.attrib['cron_send_email_on_time_lag_minutes'] == "0"


def test_discharge_reminder_to_staff_should_include_discharge_link(proj):
    """We email staff telling them to discharge a patient when the time comes.
    That email should include a link to jump straight to the discharge form
    in redcap"""
    TITLE = 'Monitoring Discharge Required staff'
    sms = get_alert(proj, title=TITLE, form_name="", alert_type='EMAIL')
    assert sms is not None

    assert '[form-url:discharge]' in sms.attrib['alert_message']


def test_patients_awaiting_discharge_should_show_in_awaiting_discharge_report(proj):
    """We have a report 'Patients awaiting discharge' that should show staff
    any patients that they need to discharge."""

    TITLE = 'Patients awaiting discharge'
    rpt = get_report(proj, title=TITLE)
    assert rpt is not None

    # It probably should match the same patients as the staff dischage reminder
    # TODO this is a bad test
    TITLE = 'Monitoring Discharge Required staff'
    alert = get_alert(proj, title=TITLE, form_name="", alert_type='EMAIL')
    assert alert is not None

    report_logic = rpt.attrib['advanced_logic']
    alert_logic = alert.attrib['alert_condition']

    # TODO change this to be an AST comparison so it's less flakey
    assert report_logic == alert_logic


def obs_alert_matches_template(alert, obsid, templatealert, allowed_field_differences):
    """Compare a redcap observation <redcap:Alerts nodes to see if its content
    is equivalent to the _template version of the alert. We don't expect them
    to be identical. The variables names (eg hr_template hr_1a) will differ
    and some meta data like alert IDs and timestamps."""

    # These fields we expect to be different
    ALWAYS_IGNORE_FIELDS = ['alert_number', 'form_name', 'alert_condition',
                            'alert_message', 'alert_title', 'email_subject',
                            'email_timestamp_sent', 'email_sent']

    ignore_fields = ALWAYS_IGNORE_FIELDS + allowed_field_differences

    # Compare all the simple fields that should be identical
    alert_vars = {
        k: v for k, v in alert.attrib.items() if k not in ignore_fields}

    template_vars = {
        k: v for k, v in templatealert.attrib.items() if k not in ignore_fields}

    for field in [f for f in templatealert.attrib.keys() if f not in ignore_fields]:
        # if not alert_vars[field] == template_vars[field]:
        #     breakpoint()

        #pytest.xfail("Not Implemented")
        if not alert_vars[field] == template_vars[field]:
        #    if template_vars[field] == 'covidhmp@mh.org.au':
        #    breakpoint()
            pass

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
    # Staff are reminded to call home observation patients 7 days after they
    # begin their observation.
    #  Staff Reminder Patient Call BIDAILY Day 7 - SMS

    TITLE = 'Staff Reminder Patient Call BIDAILY Day 7'

    # TODO change this to be based on Discharge form
    sms = get_alert(proj, title=TITLE, form_name='registration', alert_type='SMS')
    assert sms is not None

    AFTER_DAYS = 7
    assert sms.attrib['cron_send_email_on'] == "time_lag"
    assert sms.attrib['cron_send_email_on_time_lag_days'] == str(AFTER_DAYS)
    assert sms.attrib['cron_send_email_on_time_lag_hours'] == "0"
    assert sms.attrib['cron_send_email_on_time_lag_minutes'] == "0"


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


def get_alert(proj, title, form_name, alert_type):
    """Find REDCap Alert definition node in project xml file"""
    alerts_path = r"./Study/GlobalVariables/redcap:AlertsGroup"
    alerts = proj.find(alerts_path, proj.nsmap)
    xpath = f"redcap:Alerts/[@form_name='{form_name}'][@alert_title='{title}'][@alert_type='{alert_type}']"
    return alerts.find(xpath, proj.nsmap)


def get_report(proj, title):
    """Find REDCap definition node in project xml file"""
    reports_path = r"./Study/GlobalVariables/redcap:ReportsGroup"
    reports = proj.find(reports_path, proj.nsmap)
    xpath = f"redcap:Reports/[@title='{title}']"
    return reports.find(xpath, proj.nsmap)


def obs_is_morning(obcode):
    """Given an observation code (eg 'ob_1a', 'ob12_b') is this a morning obs?"""
    return obcode[-1] == 'a'


def obs_is_afternoon(obcode):
    """Given an observation code (eg 'ob_1a', 'ob12_b') is this an afternoon obs?"""
    return obcode[-1] == 'b'


def get_obs_day(obcode):
    """Given an observation code get the day number as integer
    ob_11b -> 11
    ob_4a  -> 4
    """
    assert valid_ob_code(obcode)

    # The rest follow the previous day (number -1)
    if obcode == 'ob_0':
        return 0

    ob_day = int(obcode[3:-1])
    return ob_day


def get_obs_preceding_obs(obcode):
    """Given an observation eg ob_4a, which observation precedes it?
    We have two streams, the 'a' (morning) and 'b' (afternoon) obs.

    But the first day follows on from the demo observation ob_0 -> ob_1a
                                                           ob_0 -> ob_1b
    The rest follow the previous. ob_1a -> ob_2a -> ob_3a
                                  ob_1b -> ob_2b -> ob_3b
    """
    assert valid_ob_code(obcode)

    # Nothing comes before ob_0
    if obcode == 'ob_0':
        assert False

    # First day follows the demo observation
    if obcode in ['ob_1a', 'ob_1b']:
        return 'ob_0'

    # The rest follow the previous day (number -1)
    prev_day = get_obs_day(obcode) - 1

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


def test_get_obs_day():
    assert get_obs_day('ob_0') == 0
    assert get_obs_day('ob_1a') == 1
    assert get_obs_day('ob_2b') == 2
    assert get_obs_day('ob_14a') == 14
    assert get_obs_day('ob_0') == 0

    with pytest.raises(AssertionError):
        get_obs_day('')

    with pytest.raises(AssertionError):
        get_obs_day('ob_5')

    with pytest.raises(AssertionError):
        get_obs_day('blaa')


def test_get_obs_preceding_obs():
    assert get_obs_preceding_obs('ob_2a') == 'ob_1a'
    assert get_obs_preceding_obs('ob_2b') == 'ob_1b'
    assert get_obs_preceding_obs('ob_10b') == 'ob_9b'

    with pytest.raises(AssertionError):
        assert get_obs_preceding_obs('ob_0')

    with pytest.raises(AssertionError):
        get_obs_preceding_obs('')

    with pytest.raises(AssertionError):
        get_obs_preceding_obs('ob_5')

    with pytest.raises(AssertionError):
        get_obs_preceding_obs('blaa')


def test_project_uses_capital_letters_for_covid(projxmlpath):
    """We should use COVID-19 not covid Covid covid-19"""
    with open(projxmlpath) as file:
        assert "covid" not in file.read()
    with open(projxmlpath) as file:
        assert "Covid" not in file.read()


def test_project_doesnt_contain_dev_email(projxmlpath):
    """Daniel's email should not be present in the project's xml file
    TODO: Bad test"""
    for email in DEVELOPER_EMAILS:
        with open(projxmlpath) as file:
            assert email not in file.read()


def test_project_doesnt_contain_dev_phone(projxmlpath):
    """Daniel's email should not be present in the project's xml file
    TODO: Bad test"""
    for phone in DEVELOPER_PHONENUMBERS:
        with open(projxmlpath) as file:
            assert phone not in file.read()


def test_project_doesnt_contain_old_staff_email(projxmlpath):
    """The pre may 2020 staff email address should not be used anywhere
    in the project xml file"""
    with open(projxmlpath) as file:
        assert "covidhmp@mh.org.au" not in file.read()



if __name__ == '__main__':

    # TODO cmd line checking
    if len(sys.argv) != 2:
        sys.exit("Usage:\n%s Project.REDCAP.xml" % sys.argv[0])

    proj_path = sys.argv[1]

    if not (isfile(proj_path) and access(proj_path, R_OK)):
        sys.exit("%s does not exist or is not readable" % proj_path)

    # Hand over to pytest
    # HACK. Stuff xml path into a pytest variable, defined in conftest.py
    pytest.main(["audit_project.py", "-vvvx",
                 "--projxmlfile", proj_path])
