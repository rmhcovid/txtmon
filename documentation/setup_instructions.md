# Setting up the Home Monitoring Project

Setting up the technical system is just one small part of running a Home Monitoring Project in your organisation. Organising staff, procedures, 

You *must* familiarise yourself with the overall project to have any hope of absorbing these technical systems. There is a copy of our overall project procedures document in /latest_version/RMH Covid-19 Home Monitoring Program.pdf. Stop now and read that document. You will need to understand our concept of Observations, Monitoring Period, Observation Days etc.

## Preparation

1. Download our latest REDCap project template file at:
   https://github.com/rmhcovid/txtmon/blob/master/latest_version/
   <br/>eg *CovidHomeMonitoring_2020-xx-xx_xxxx.REDCap.xml*
2. The system needs to send email to your medical staff
   <br/>Ask your IT staff to setup an email account (or email redirect) for the staff who will be managing patients and receiving alerts
   - eg 'staff@yourhospital.org.au'
3. The system communicates with staff and patients via SMS and SMS Gateway
   <br/>We use Twilio which closely integrates with REDCap
   <br/>You may be able to adapt a 3rd party service. We will assume Twilio.
   <br/>Ask your IT staff to setup a paid Twilio account
   <br/>Ask your REDCaps administrator to enable Twilio on your system
   <br/>Ask your IT staff to provide you the twilio account details and phone number
4. xxxxxx TODO anything else?


## Create the REDCap project onto your server

### (optional, but recommended)

Bulk update the email addresses and phone numbers in the xml file. This saves manually changing these in over 100 places.

1. Edit the XML file in a text editor
2. Find/Replace 'staff@yourhospital.org.au' to your staff email address
3. Find/Replace '61491570156' to your mobile phone number


### Import the project file

1. Click 'New Project' in title bar
2. Give your project a title eg 'Covid Home Monitoring System'
   <br/>give your project a purpose note
   <br/>(recommended) in the notes field put the version number of the template file. This will be useful when upgrading
3. Where it says "Start project from scratch or begin with a template?"
   <br/>Choose 'Upload a REDCap project XML file (CDISC ODM format)?'
   <br/>Select our template file eg *CovidHomeMonitoring_2020-xx-xx_xxxx.REDCap.xml*
4. Click 'Create Project'

## Configure Twilio in REDCap Project settings

These settings are not exported/imported in the xml file. You must set them manually.

*If you do not configure Twilio correctly inside the REDCap project settings you will get PHP server errors as you try to use the system*.

This guide assumes your REDCap server administrator has already configured it to be used with Twilio, and has supplied you with account numbers, auth tokens and a sending phone number. If you do not see various settings mentioned below, speak to your REDCap IT people.

1. Open your REDCap Project
2. Open 'Project Setup'
3. Click 'Enable' next to 'Twilio SMS and Voice Call services for surveys and alerts'
4. Click 'Modify' ntext to 'Twilio SMS and Voice Call services for surveys and alerts'
   - set 'Twilio SMS and Voice Call services' to 'Enabled'
   - fill in your Twilio Account SID, Auth Token, and phone number (in international format)
   - save
5. Find the 'Twilio SMS and Voice Call services' section of settings
6. Click 'Configure Twilio settings'
   - set 'Select the project modules in which the Twilio service will be enabled' to 'ALL: Surveys and survey invitations + Alerts & Notifications'
   - set 'Choose the default invitation preference for new survey participants' to 'SMS invitation (contains survey link)'
   - tick 'Send survey invitation with survey link via SMS'
   - set 'Designate a phone number field for survey invitations' to 'mobile ("Mobile Phone Number") 
   - save
7. Click the 'I'm Done' button next to 'Twilio SMS and Voice Call services'


## Configure the branding for your organisation

There are a large number of places in the project that refer to The Royal Melbourne Hospital, The RMH, RMH Covid-19 Home Monitoring, RMH Covid etc. You will want to change these.

You will likely find it easier to find/replace these directly in the project XML file before importing it, similar to what we recommended with phone numbers and email addresses. Search for 'RMH'.

Branding must be updated in:

- Alerts & Notifications
- Registration Instrument field text
- Consent Instrument field text
- Instrument Surveys (titles and intro text)
- Automatic Survey Invites

On a running system you will not want to make these changes manually to all the different alerts and observations. See the Developer Tools section below for how to do bulk updates.

# What to do next

## Process a sample patient

Once you think you have the system running, set yourself a pretend patient and go through the process yourself.

Find the registration link. In REDCap 

1. Click 'Survey Distribution Tools'
2. Click 'Open Public Survey'
3. Follow the registration procedure
4. Back in REDCap admin, open 'Record Status Dashboard'
   Is your new patient listed?

You should receive a SMS at this point welcoming you to monitoring. It should include a link to your first observation (we call this ob_0, it's a demonstration observation that a clinician guides the patient through).

Once you complete that Observation check that the next observation invites for the patient is scheduled to go out the next day.

1. Click 'Survey Distribution Tools'
2. Click 'Survey Invitation Log'
3. Click 'View future invitations'
   Are their observations for tomorrow morning and afternoon listed?

On your next observation, try triggering some alerts.

- Try submitting a temperature of 38.1 and see that the patient receives a fever warning SMS
- Try submitting a heart rate of 121 and see that the patient/staff receive a Clinical Review alert
- Try submitting an O2 saturation of 89 and see that the patient/staff receive a METCall alert

When your pretend patient reaches the end of their monitoring period, your staff should get an email prompting them to discharge the patient. Discharge the patient and see that they are sent a thank you SMS/EMAIL with follow up details

Some other things to try:

- Try registering patients for different periods of observation (mon_period_days)
- Try adding Clinical Notes against a patient
- Try registering patients with different alert criteria (eg higher heart rates)
- Pretend that a patient has been re-admitted to hospital (patient_loc). Confirm that monitoring is muted.
- Ignore an Observation SMS and check that you are reminded by SMS 2 hours later
- TODO

# Using this system in your emergency department

How we operate this in our hospital is set out in '/latest_version/RMH Covid-19 Home Monitoring Program.pdf'

TODO supporting flyers, paperwork etc?

# Development Support Tools

There are some development tools in the /tools/ directory to aid in altering the project.

Some design constraints in REDCap meant that we were unable to build the monitoring system using Longitudinal or Repeating instruments. Instead we had to create an Observation instrument for each morning/afternoon of the patients monitoring period (ob_1a, ob_1b, ob_2a, ...). In turn that required alerts for each obs. This is undesirable and *we hope to change this in the future*.

It's not practical to update every instance of these duplicate. Instead we change template versions and use cmdline tools to update the rest.

You should be aware and learn to use these tools that were build to make the project more manageable. They're not the friendliest but they're better than clicking the same boxes in REDCap 400 times.


Some of the tools talk to the REDCap server by injecting HTTP GET/POST requests as if you were pointing and clicking in the web UI. They are authenticated by grabbing a PHPSession cookie / CSRF token out of a real REDCap session. There is an included tool to grab these identifiers.

This web injection was the simplest way around automating as we did not have API access when the system was built. *This may have since changed making these tools redundant*.

**These tools will not work out of the box**. You will need to edit them to point at your own deployment, and likely make changes. They're a starting point only.

These tools are built in Python and use a Python venv / requirements.txt to manage their dependencies. 

## authenticate

This tool logs into your REDCap server using your username/password and returns a PHPSESSIONID and csrf token as are required by the other cmdline tools.

 eg ./authenticate.py 'https://biredcap.mh.org.au/' username password

**Warning** be careful that you do not expose your password via the history feature in shell. You might wish to use ENV variables instead.

## generate_alerts

Tools to list all the Alerts defined in the system, and another to bulk update alerts.

You give it a TEMPLATE alert and a TARGET alert and it will make the target like the template, but subbing in appropriate variables (obs_1a, obs_2a, ...).

See tool README.txt for details.

## generate_observations

For reasons we have a different Observation instrument for each time a person submits us their hr/temp/o2. Keeping the structure/content/text of those observations is difficult. REDCap already has a feature to dump/import observation definitions as a csv file. This tool generates that csv data.

See tool README.txt for details and a worked example later in this document.

## audit_project

This is an attempt to bring unit testing into REDCap to keep this project manageable.

This tool interrogates the project export metadata xml files generated by REDCap to check a large number of structural items that could easily be changed by mistake. eg

- checks that each observation instance has the same text
- checks that each staff alert has the same text
- checks that all surveys are set to use mobile friendly buttons
- and many more

See tool README.txt for details.


# Known Issues

## Incorrectly configured Twilio settings cause PHP 500 errors

If Twilio isn't setup correctly (valid auth details, valid sending phone number) you will get a PHP 500 error any time the system tries to send a SMS. The error message shown will not explain this.

## You do not need to be authenticated to add a patient Clinical Note

We want clinicians to be able to follow a link from an alert SMS and easily add Clinical Notes to patients. To allow this we have enabled the REDCap Survey queue functionality for Clinical Notes. This means that if a patient (or someone else) finds their REDCap survey queue URL they too can add a clinical note. This is a design trade off we are looking for an alternative to.

Please see 'documentation/redcap_design_overview.md' for more details.
 
