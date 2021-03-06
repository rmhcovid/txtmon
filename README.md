# RMH Covid-19 Home Monitoring Project
RMH Home Monitoring lets a hospital manage a large number of Covid-19 patients using their smartphones and two simple medical devices (pulse oximeter + thermometer).

The goal is to oversee a large number of relatively healthy patients in their own homes, saving bed space and staff resources.

The system prompts patients twice per day to submit their own heart rate, body temperature and oxygen saturation via a website. Clinicians are alerted to patients with concerning or critical vitals. Automation keep staff interaction and administrative work minimal.

RMH Home Monitoring is a [REDCap](https://projectredcap.org/software/) (Research Electronic Data Capture tool) project template that you can copy and adapted for your facility. Patients interact with the system via public websites (REDCap *Surveys*).

## Features

- Patient registration
- Automatically prompt patients for their heart rate, temperature and oxygen saturation
- Store and analyse these 'Observations'
- Alert staff to patients that should be reviewed because of high/low vitals
- Alert staff if a patient should return to the hospital immediately (a MET call)
- Alert patient and staff of patients who are late submitting their data
- Alert thresholds are set per patient
- Keep clinical notes for each patient
- Discharge patients and produce medical records
- Ask various other tracking questions for medical analysis

![Screenshot](https://user-images.githubusercontent.com/1585749/81142763-d1cccf80-8fb3-11ea-9c00-5e8d08e0de3d.png)


**As of April 2020** the project is in use at the Royal Melbourne Hospital in Victoria, Australia.

This project has been developed by Dr Martin Dutch and Associate Professor Jonathan Knott and is shared with compliments of [The Royal Melbourne Hospital, Victoria, Australia](https://www.thermh.org.au/). [The Peter Doherty Institute for Infection and Immunity](https://www.doherty.edu.au/) has provided funding for the project through a research grant.

You may use and adapt this project free of charge, however we ask that you acknowledge this project and the Royal Melbourne Hospital in your copy, and any associated academic publications.

We would be delighted to received correspondence if your health service has found our contribution useful, and would be happy to work collaboratively to measure the impact of this service delivery. Contact details are below.

Though a non-traditional tool for building a monitoring system, REDCap allowed us to rapidly prototype the system in response to the pandemic in early 2020. We hope it will also make the system accessible to organisations facing Covid-19 pressure but without the resources to build software projects.

## Requirements for using the system

*You must have your own running REDCap system to use this tool. Unfortunately we are not in a position to host your institution's health data.*

- a [REDCap](https://projectredcap.org/software/) installation and license
- a recent enough version of REDCap to support the *Alerts and Notifications Function*
- a mobile phone that can receive SMS for staff alerts
- an outgoing SMS service (ideally Twilio)
- an outgoing email server and an email address for your staff
- ability to provide patients with a digital thermometer and pulse oximeter
- staff to respond to patient observations and alerts
- staff to manage patient registrations and discharge

## Download, setup the tool, and prepare your team

Take a copy of our REDCap project file. **You must modified it** before you use it.

1. Read the brief [Overview Guide](https://github.com/rmhcovid/txtmon/blob/master/documentation/overview_START_HERE.md).
2. Read the [Home Monitoring Program Guide](https://github.com/rmhcovid/txtmon/blob/master/latest_version/RMH%20Covid-19%20Home%20Monitoring%20Program.pdf) that explains how the project is run, the staff and patient processes.
3. Follow the [Setup Instructions](https://github.com/rmhcovid/txtmon/blob/master/documentation/setup_instructions.md) to get a copy up and running.

## Help and Known Issues

Please see a list of known issues in the [Setup Instructions](https://github.com/rmhcovid/txtmon/blob/master/documentation/setup_instructions.md).

## How to Contribute

We'd love to get your feedback and to hear about how you've been able to use this work in your own organisations. You can email us at rmhcovid@314.net.au.

## Reporting Issues

We are not in a position to offer technical support. We are offering our work so far in the hope that it might be useful for other organisations. You may run something similar to what we have, or adapt it for your needs.

You are welcome to add Issues using the normal GitHub process, however you *should not expect to get a reply*.

We will consider any formal pull requests made via the usual GitHub process.


## Legal

Please see the attached LICENSE document.

## Version History

- See  [CHANGELOG.md](https://github.com/rmhcovid/txtmon/blob/master/CHANGELOG.md)
- 1.1.0 - 2020-05-20 - COVIDHomeMonitoring_2020-05-20_1527.REDCap.xml
- 0.9.0 - 2020-05-05 - CovidHomeMonitoring_2020-05-05_1649.REDCap.xml

## Author and Acknowledgements

This project was designed and managed using the [REDCap](https://projectredcap.org/software/) electronic data capture tool hosted by the [Royal Melbourne Hospital Business Intelligence Unit](https://www.thermh.org.au/). [The Peter Doherty Institute for Infection and Immunity](https://www.doherty.edu.au/) has provided funding through a research grant to make this project possible.
