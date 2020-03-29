# RMH Covid-19 Home Monitor
RMH Home Monitor lets hospitals manage a large number of Covid-19 cases in the patient's own homes using their smartphone and two simple medical devices (pulse oximeter + thermometer).

The goal is to oversee a large number of realatively health patients with Covid-19 in their own homes, saving bed space and staff resources.

The system prompts patients twice per day to submit their own heart rate, body temperature and oxygen saturation via a website. Clinicians are alerted to patients with concerning or critical vitals. Automation keep staff interaction and administrative work minimal.

RMH Txtmon is a [REDCap](https://projectredcap.org/software/) (Research Electronic Data Capture tool) project template that you can copy and adapted for your facility. Users intereact with the system via a public website (a REDCap *Survey*).

## Features

- Patient registration
- Contact patients for their heart rate, temperature and oxygen saturation
- Store and analyse these 'Observations'
- Alert staff when should be reviewed by a clinician because of high/low vitals
- Alert staff if a patient should return to the hospital immediately (a MET call)
- Alert patient and staff of patients who have missed submitting their observation.
- Keep clinical notes for each patient
- Discharge the patient and produce medical records
- Ask various other tracking questions for medical analysis


**As of April 2020** txtmon is in use at the Royal Melbourne Hospital in Victoria, Australia.

This project has been developed by Martin Dutch and Tim Fazio and is shared with compliments of [The Royal Melbourne Hospital, Victoria, Australia](https://www.thermh.org.au/).

## Requirements for using the system

*You must have your own running REDCap system to use this tool. Unfortunately we are not in a position to host your institution's health data.*

- a [REDCap](https://projectredcap.org/software/) installation and license
- a recent enough version of REDCap to support the *Alerts and Notifications Function*
- an outgoing email server and SMS gateway
- TODO

TODO - info about the medical pack.

## Download, setup the tool, and prepare your team

Take a copy of our REDCap project file. **You must modified it** before you use it.

TODO

1. Read the brief [overview guide](https://github.com/rmhcovid/txtmon/blob/master/documentation/overview_START_HERE.md)
2. Follow the [setup instructions](https://github.com/rmhcovid/txtmon/blob/master/documentation/setup_instructions.md) to get a copy up and running
3. Read the [technical_overview](https://github.com/rmhcovid/txtmon/blob/master/documentation/technical_overview.md) to understand how the tool works and adapt it to your needs


## Documentation

TODO see /documentation/ directory

## Reporting Issues

TODO

## Help and Known Issues

The best place to obtain help is ... TODO 

If you REDCap instance doesn't have *Alerts and notifications* under the applications heading, then your version is too old. 
It may be possible to maintain an old version using the [Autonotify plugin](https://github.com/123andy/redcap-plugin-autonotify) from 123Andy. We are unable to provide support for this.

## How to Contribute

TODO

## Legal

Please see the attached LICENSE document.

## Version History

- See  [CHANGELOG.md](https://github.com/rmhcovid/txtmon/blob/master/CHANGELOG.md)
- TODO

## Author and Acknowledgements

This project was designed and managed using the [REDCap](https://projectredcap.org/software/) electronic data capture tool
hosted by the [Royal Melbourne Hospital Business Intelligence Unit](https://www.thermh.org.au/).
