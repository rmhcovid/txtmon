# REDCap Design

This document explains the structure and features of the home monitoring system.

Building the monitoring project in REDCap has at times been difficult. REDCap is a very powerful and rich survey tool with excellent end-user features for managing data. However some of the business logic we needed for monitoring did not fit well into the REDCap model and has required somewhat hacky workarounds.


# Core Elements

## Patients, Observations and Alerts and Clinical Notes

Our *Patients* are all real people who have had some contact with the Covid-19 virus and the Royal Melbourne Hospital. We use Patient UR numbers like the other hospital systems.

Each Record in REDCap is a Patient. But not all Patients are monitored!

We have different types of patients (different *Monitoring Group(s)*). Some we communicated with each day, some intermittently just to check in. We also store *ineligible patients* who did not meet our conditions for home monitoring but their details are useful to our research.

For the patients who are monitored, we do it for a period time, their *Monitoring Window*. A technical limitation means that monitoring cannot be indefinite. Currently we limit it to 14 days. Every patient has a *Patient Status* that encompasses all the situations.

An *Observation* is when a patient submits their Heart-Rate, Oxygen-Saturation and Temperature to us. Most patients will have many Observation during their time with us. We prompt patients each day via SMS to complete their Observation.

Observations may trigger a *Fever Warning*, *Clinical Review* or *METCall* if the patients numbers exceed certain *Thresholds* set for the patient.

We send many types of *Alerts*. These are the outgoing SMS and Emails that notify staff of patients with concerning readings, remind people they're late for their observations, provide useful tips to patients and more.

ClinicalNotes are plain text notes clinicians record about patients.


# Implementation

## Patient Registration and Ineligible Patients

TODO changing this week

## Patient Details

TODO changing this week

The Registration instrument holds the core patient contact information. Name, address, emergency contacts etc. 

TODO we intend to change where patient details are stored. Update me.
TODO change after split


### Phone numbers

Patients are primarily contacted through SMS. At registration we ask for their *Mobile Phone* number [mobile]. Our SMS Gateway Twilio needs numbers to be sent in international 614xxx format.

We enter and store the numbers in this international format. This is a design trade-off. Previously we had patients enter the number in local 04xxxxxxx format, and then used a REDCap trick to convert it to international. But this required staff to update multiple fields if a patient phone number had to change (eg if it was entered wrong).

## Patients Monitoring Groups

Patients have different levels of risk and we group them by their level of care. 

Some patients we must watch closely, others we just want to check in with useful information. This is their *Monitoring Group* [mon_group] (BIDAILY|WEEKLY).

Our *BIDAILY* patients we SMS twice each day and expect to get a morning and afternoon Observation.

Our *WEEKLY* patients we contact a number of days into their monitoring with some helpful information. At time of writing we had never had a real one of these and so this feature is fairly thin.

## Patient Status

The virus takes around a fortnight to run its course. Patients may come to us at any point in that time and so will be with us for different lengths of time. They may become very sick and return to hospital, so we must consider a patients location and if their monitoring should be paused.

Patients have a *Monitoring Status* [calc_mon_status] (OBSERVATION|ESCALATION|PAUSED|ENDED) that at any point tell us if we should be conducting the twice-daily Observations, just sending them Escalation warnings, Pause their monitoring (don't communicate with them) or that their monitoring has Ended. REDCaps limited calculation system means monitoring status is a nasty nested if logic. See notes below about getting around this.

A patients status depends on their *Monitoring Group* [mon_group] (chosen by staff at registration), their *Location* [patient_loc] (set by staff), and whether they are in their *Monitoring Window*.

Their Monitoring Window is worked out from their date of *Monitoring Admission* [mon_admission_date] and how long the clinician wants them monitored for *Monitoring days* [mon_period_days]. We work out how many days have passed since their admission in [calc_admission_days] and whether this is more than [mon_period_days]. The calculation variable [calc_in_mon_window] wraps this all up in a neat IN/NOT-IN boolean.

Previously we worked out patients monitoring window from the *Symptom Start Date* [symptom_startdate], which explains the seemingly unused *Days since Symptoms began* [calc_symptom_days].


There are some shorthand helper variables for checking a patients status. These are set to 1/0, (true/false). This is just because REDCap doesn't contain enums, or have a way to return strings from a calculation. This makes some of our other calculations less cumbersome.

- [calc_mon_status_observation]
- [calc_mon_status_escalation]
- [calc_mon_status_paused]
- [calc_mon_status_ended]. 

The patients status also impacts whether we should contact them. We don't want to send an embarrassing or upsetting message if the patient is back in hospital or has died. We capture this logic in the [calc_allow_patient_comms] variable (1 ALLOW, 0 MUTE). There are further details on this in the Alerts documentation.

## Observations

Observations are the patient sending us their medical readings. We expect this to happen twice each day (Morning and Afternoon).

Each Observation has its own timestamps, health values, and calculations to decide if it warrants health alerts.

Observations also have some inline help information for the user. Currently we only have one model of Pulse Oximeter and so only a single help video is shown to all users. In the future we expect to use branching logic to show appropriate help for the users device.

Observations include a number of *Supplementary Questions* for research purposes. These questions are all asked on the second page of the observation and are prefixed with supqn_. They DO NOT impact whether the observation triggers an alert (and nor should they). We expect these questions to change over time. We **do not delete** supplementary questions. Instead we hide the old ones so the data is still available.

## Why are there all these observation instruments!??

There is a separate instrument for each morning/afternoon for each day of their observation period. A subtle REDCap limitation forced us into this (see below). They are named like this:

- ob_0 - the demo observation we do when onboarding the patient
- ob_1a - morning of their first day
- ob_1b - afternoon of their first day
- ob_2a - morning of their second day... and so on

The a/b naming scheme is in case we decide to change the number of observations per day.

The only one you edit in REDCap is **ob_template**. The others are copied from this one using supporting tools we've built (see below).

This design unfortunately also means there is a copy of each REDCap *Alert* for each observation. One for patient SMS alerts, one for Staff SMS alerts, one for Late observations, etc. This adds up quickly. **You Do Not Manage This Manually**. The cmdline tools also automatically generate and sync these alerts/observations. You only edit the ...ob_template versions.

Ideally we would use a REDCap *Repeating Instrument* for this. Twice each day (via a scheduled alert) we would send patients a SMS with a link. That link would create a fresh Observatio repeating instance. Then we'd only need one Observation Instrument and one type of each patient/staff medical alerts. *BUT* REDCap has no way to generate a link to a *new* repeating instrument. If you use the [survey-url] [survey-link] tags in emails/sms they always link to the first instance. So it works great for the first observation, but the next one gives the user 'Sorry, you've already completed this survey' error.

We considered using the *Survey Queue* for this. That does give the user a button for 'Add another xxxx'. But we decided this was confusing, and it also let patients records multiple observations in a row.

We also considered Longitudinal Observations. They almost gave us what we needed. It was still limited to a fixed number of events/observations, but at least meant there would only be one Observation instrument. I couldn't find a way to get the correct daily scheduling of invites (8am/3pm). You can manually set these times when you generate an *Event Schedule* in Redcap, but it was out of the question that we'd have clinicians manually typing in 28 of these values.

**You might be able to remove this complexity**. If REDCap has since added a feature to send [survey-url]s to new instances of Repeating Instruments then you have everything you need to remove all this complexity.

## Observation Medical Alert Thresholds

Observations might meet three mutually-exclusive alert thresholds based on how bad the patients vitals are.

*Fever Warning* just send the patient some useful information.
*Clinical Review* alert the patient and staff for followup.
*MET Call* alert the patient and staff to the emergency.

Each patient has defined a number of thresholds (high/low) for their Temperature, Heart Rate and Oxygen Saturation. These have default values, but they are copied to each patient so they can be changed.

The Observation instrument contains a number of calculated fields to work out if we have met these thresholds and if alerts should fire. The large number of calculated fields to to keep the logic neat because REDCap calculations are limited to returning integers, and we want to keep the consumers of these calculations (eg the Alert SMS) simple.

- calc_in_fw_temp               (Temp in Fever warning range)
- calc_in_cr_temp               (Temp in Clinical Review range)
- calc_in_cr_sat                (Sats in Clinical Review range)
- calc_in_cr_hr                 (Heartrate in Clinical Review range)
- calc_in_mc_temp               (Temp in MET Call range)
- calc_in_mc_sat                (Sats int MET Call range)
- calc_in_mc_hr                 (Heartrate in MET Call range)
- calc_trigger_fw               (Trigger a Fever Warning)
- calc_trigger_cr               (Trigger a Clinical Review)
- calc_trigger_mc               (Trigger a MET Call)
- calc_trigger_alert_patient    (Should REDCap send a patient alert?)
- calc_trigger_alert_staff      (Should REDCap send a staff alert?)
- calc_trigger_alert_level      (Alert Level, 0 NONE, 1 FEVER_WARNING, 2 CLINICALREVIEW 3 METCALL)

If you're adding new conditions, keep the naming scheme consistent.

The mutually-exclusive alerting is implemented in the logic for calc_trigger_[fw|cr|mc]. **IMPORTANT** redcap calculates the fields in order, and it does NOT do a query planning step. That means that if a calculation depends on another field, that field must occur before it on the form. **If you change the order of these fields** then you can break the calculations. We need calc_trigger_fw to be calculated before calc_trigger_cr and so on. This is subtle and dangerous REDCap issue.


### Medical Alert Text

In the SMS/Emails we send to patients we need to add words like 'MET Call' and 'Clinical Review'. But REDCap has no way to do if/then logic in the text templates. Instead we use a hacky REDCap workaround.

Each Observation has *Conditional Text* fields that are populated with the appropriate text . Then we can just include those fields in the SMS/EMail.


- condtxt_alert_title_staff     (Conditional Text - Alert level name for staff alerts)
                                0, ""
                                1, ""
                                2, "Clinical Review"
                                3, "MET Call"
- condtxt_instr_patient         (Conditional Text - Patient instructions for alerts) 

This is a crappy way to manage stock text and alerts but the best we have available at this time.

## Observation Invites

We need to prompt the patients each day to fill out their observations. We do this using the built in REDCap *Automatic (Survey) Invite* functionality.

Each observation instrument has an *Automatic Invitation* defined that sends the user a SMS invite at a particular time (eg 8am or 3pm).

Invitations have a logic check ([calc_mon_status_observation] = 1) to ensure the patient is still under observation. The patient might have finished their monitoring, or they might have been admitted back to hospital, or they may never have been under observation.

Automatic Invites are also how the *Late Observation Reminder* to the patient is sent. The *Enable Reminder* section is configured to send them a reminder every N hours. This is NOT how the alert to staff about late observations is built. That works off Alerts. See below.

These invites are NOT defined for ob_0 (the one at registration). That's because we want that invite included in the *Registration SMS* we send the user. So that's built with a REDCap Alert rather than Automatic Invite.


**You do not need to edit these manually**. Use the built in feature 'Upload or Download Auto Invites' in REDCap to just dump them as a csv and edit them that way.

Our project audit cmdline tool checks to make sure all the invites are consistent. See the tooling section.

I think a good alternative to this would be an out of REDCap process via the API or something else that just sends them the messages. This would let us construct a URL that created a new Repeating Instrument and remove a lot of this complexity. The trade-off is that it's another system to manage outside of REDCap and that's not viable at the moment.


## Clinical Notes

The ClinicalNotes instrument is for clinicians to record plain text notes against patients. This is implemented as a REDCap Repeating Instrument.

We want to add a link to staff alert SMS that lets them directly add a new Clinical Note. Unfortunately we cannot create a survey-url to a repeating instrument (same problem we have with Observations). Instead we use the Survey Queue functionality. The user follows a link to the queue and they get a nice '+ Add another Clinical Note' button.

The downside of this method is that patients can add their own notes. RMH is aware of this and are ok with it for now.


## Alerts

We heavily use the REDCap *Alerts and Notifications* system for communicating with Patients and Staff. The Twilio integration handles our SMS sending.

The design tradeoff that resulted in having many Observation instruments (see the documentation above) also means duplicating many of the alerts.

**You do not have to edit these manually.** As with Observations, you only edit the ob_template version use the cmdline tools to copy the changes to the rest. See the section on tooling.

### Suppressing (Unneeded, Upsetting and Embarrassing) Alerts

Patients finish their monitoring period, and some return to hospital sick, or die. We do not want to send upsetting or embarrassing alerts in these situations.

Many of our alerts in REDCap first do a check on '[calc_allow_patient_comms] = 1' (documented above). Some alerts heck the patients status manually for instance where we send an alert after they have been discharged (which mutes most communication).

### Patient Registration Welcome Message

We have different sign-up messages depending on the *Monitoring Group* of the patient. They are triggered on the Registration Instrument being saved, but conditional logic on the alert sends the appropriate one.

- 'Patient Registration - BIDAILY'
- 'Patient Registration - ESCALATION checkin'

### Observation triggered Medical Alerts

When a patient submits concerning health readings we message them and sometimes staff. Read the sections above on how Observations and thresholds work.

We have three alerts that communicate with the patient, and staff (email & sms):

- 'Obs Combined Staff alert - ob_template'
- 'Obs Combined Staff alert email - ob_template'
- 'Obs Combined Patient alert - ob_template'

**Only edit the template versions manually** and use the cmdline tools to sync the remaining ones.


### Late Observation Alerts Reminder Patient

If a patient is late submitting their observations we prompt them (currently at 2 hours and 4 hours late). This is implemented using the 'Automatic Invitation Reminders' system in REDCap, NOT Alerts and Notifications. Read the section on Observation Invites above.

### Late Observation Alert for Staff

If a patient is hours late submitting an observation (currently set to 5) we alert staff. This is built by having an alert for *every* observation, and then suppressing the alert at send time if the patient has in fact submitted an observation. Bit hacky, but it works.

These alerts are triggered for N hours past when we prompt them for their observation. ie 12pm to check on the 8am observation. But they are **triggered off the previous days observation** being submitted. This is a subtle and annoying limitation of REDCap alerts. They have the ability to schedule at a time of day, but only 'the next day'. You cannot schedule an alert to go out at a particular time of day today (I believe this is because alerts are scheduled/triggered by a cron job that only runs every 12 hours). So we must create our alert the previous day. ie ob_2b is triggered by ob_1b. The conditional logic still runs before the alert is sent which lets us check the submitted status of the observation we care about.

**Only edit the template versions manually** and use the cmdline tools to sync the remaining ones.


### ESCALATION patients day N escalation warning

Our patients that are in the WEEKLY monitoring group we do not talk to each day. After a few days we SMS them and remind them that should their symptoms get worse, they should contact us or a doctor.

'Escalation checkin warning patient'

This alert is triggered at the time of their registration, but is delayed for N days by the 'Send after lapse of time' feature. Conditional logic on the alert checks that it's still relevant before it's actually sent.

At time of writing we have none of these patients and this feature is enabled, but unused.

### Patient Discharge Reminder for Staff

When a patient has come to the end of their home monitoring period we prompt staff by email telling them to discharge the patient.

'Monitoring Discharge Required staff'

This alert is fired as soon as a patient finishes their monitoring window, if they are still in their home. We don't want to send this if the patient returned to hospital or died during their monitoring period.

A patients monitoring period might change (clinician might alter their [mon_period_days] days of monitoring. That is why this alert checks on their status, not on Registration + Days.

### Discharge Information for Patient

Two alerts are sent to a patient when their status changes to DISCHARGED.

- Monitoring Discharge patient - SMS
- Monitoring Discharge patient - EMAIL

The check [patient_loc] = '3' and [mon_discharge_reason] = '1' fires when they are DISCHARGED, and only if they are healthy (discharge reason 1).
TODO change this to trigger on completion of the new Discharge instrument.

### Post Discharge Feedback Survey

Two days after a patient is DISCHARGED and was HEALTHY we send them a link to a feedback survey and remind them about sending back their electronic monitoring kit.

'Post Discharge Patient Follow-up - SMS'

The check [patient_loc] = '3' and [mon_discharge_reason] = '1' fires when they are DISCHARGED, and only if they are healthy (discharge reason 1). But the message is delayed by two days using the 'Send after lapse of time' scheduling feature.
TODO change this to trigger on completion of the new Discharge instrument.


### Staff Call Reminder for BIDAILY patients

If a patient has been under home observation for 7 days we want a clinician to give them a call and check on their well-being. 

'Staff Reminder Patient Call BIDAILY Day 7'

This alert is triggered at the time of their registration, but is delayed for 7 days by the 'Send after lapse of time' feature. Conditional logic on the alert checks that it's still relevant before it's actually sent.

### Ongoing helpful health information SMS (Quarantine, Meals on Wheels, ...)

We intend to send regular helpful SMS to monitoring patients every few days telling them about services like Lifeline, Meals on Wheels and maintaining their Quarantine.

These are just simple repeating alerts that also check the status of the patient so that they stop when their monitoring stops.

At time of writing we have disabled this feature.

## Custom Dashboards

We have a single custom data dashboard in REDCap that shows a list of the currently monitored ('Current Observation Patients') patients.

It would be useful to create different dashboards for different classes of patient.

## Reports

At time of writing there are only a few simple reports. The intention is that over time the information we gather about patients will be useful in managing the greater Covid-19 viral program.

*Are you a developer new to the system?* Check to see if the reports have been fleshed out and update this documentation.


## Patient Export Report

There is a reporting tool inside the RMH Business Intelligent Unit that is responsible for creating a PDF archive of the patients information after they are dicharged from monitoring. That was built by Tim Fazio's team and is outside the scope of this documentation.


## Patient backup Report

We asked that a twice daily export of the data in the system be made as a backup safety-net in case something happened to REDCap while the project was running. ie maybe the staff could continue monitoring staff via excel in the interim. That has not eventuated but patient numbers have been low so far.
