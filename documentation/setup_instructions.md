# Setting up the Home Monitoring Project

## Preparation

1. Download our latest REDCap project template file at:
   https://github.com/rmhcovid/txtmon/blob/master/latest_version/
   <br/>eg *CovidHomeMonitoring_2020-xx-xx_xxxx.REDCap.xml*
2. The system needs to send email to your medical staff
   <br/>Ask your IT staff to setup an email account (or email redirect) for the staff who will be managing patients and receiving alerts
   - eg 'staff@yourhospital.org.au'
3. The system communicates with staff and patients via SMS and SMS Gateway
   <br/>The project uses Twilio which closely integrates with REDCap
   <br/>Ask your IT staff to setup a paid Twilio account
   <br/>Ask your REDCaps administrator to enable Twilio on your system
   <br/>You may be able to adapt a 3rd party service
4. xxxxxx TODO


## Create the REDCap project on your server

1. Click 'New Project' in title bar
2. Give your project a title eg 'Covid Home Monitoring System'
   <br/>give your project a purpose
   <br/>(recommended) in the notes field put the version number of the template file. This will be useful when upgrading
3. Where it says "Start project from scratch or begin with a template?"
   <br/>Choose 'Upload a REDCap project XML file (CDISC ODM format)?'
   <br/>Select our template file eg *CovidHomeMonitoring_2020-xx-xx_xxxx.REDCap.xml*
4. Click 'Create Project'

## Configure your Twilio Account

TODO



## Configure the outgoing emails / letters for your hospital

You must update the notification emails or they will appear to come from the Royal Melbourne Hospital (or not send at all).

1. Open REDCap 'Alerts & Notifications'
2. For each alert - change the **From email address**
3. For [TODO list of ward clerk emails] change the Ward Clerk email addresses
   <br/>wardclerks@yourhospital.org.au -> YOUR WARD CLERK EMAIL
   TODO staff@yourhospital.org.au
4. For each [TODO list of clinician emails] change the Clinician email address
   <br/>clinicians@yourhospital.org.au -> YOUR CLINICIAN EMAIL
5. For **every** alert - change the text of the email to reflect your hospital
6. TODO - change the 'Email 10 Tips' email as desired

## Configure SMS numbers for your Staff
TODO

## TODO what other project setup?

TODO

# Using this system in your emergency department

TODO information from Louis

# Process a sample patient

TODO
- register a patient via the survey link
- todo, consent pages?
- have them complete ob_0
- confirm ob_1a has been scheduled
- perform observations...
- discharge patient
- TODO

# Known Issues
- php 500 error if twilio not correctly configured
- interrupted observations if missed
- survey queue
