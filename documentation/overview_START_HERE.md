# What is it? How does it work?

We have provided you with a REDCap project template for you to adapt into your own Covid-19 patient home-monitoring system and various tools to manage it.

This REDCap project stores the patient information, schedules and send SMS/EMAIL to your patient sand staff, triggers alerts on patient health readings, and performs a number of reporting and administrative functions.

Running home monitoring is much more than just the technical systems. **Before continuing, have you read** [Home Monitoring Program Guide](https://github.com/rmhcovid/txtmon/blob/master/latest_version/RMH%20Covid-19%20Home%20Monitoring%20Program.pdf)? We will assume you're at least basically familiar with our monitoring project and our terminology around Observation, Monitoring Periods etc. Please do take the time to read and prepare. It will make setting up your own system much easier.


# Major components of the system

- The REDCap project is responsible for all the data keeping. It is the only website patients and staff interact with. It handles all the health threshold trigger logic and initiating all outbound communications.

- We use the 3rd party Twilio service for our outbound SMS, and also to redirecting any inbound SMS/Calls. There is more information about how this works in the setup_instructions.md documentation.

- A real mobile phone is the primary point of contact for staff. You may choose to redirect this to multiple staff, or pass the phone around.

- We use a second REDCap project to record Patient feedback. It is disconnected from the primary REDCap project and we do not link the two for privacy/confidentiality reasons. A SMS alert from the primary project gives Patients their link to the feedback system. That is the only interaction between the two. You can safely remove references to this.

- A number of command line tools exists to aid the developer in making bulk changes. This is necessary due to some design tradeoffs we encountered building the system inside of REDCap.

- An audit tool is able to check the structure of the REDCap project. It checks for a large number of mistakes that might have been inadvertently been made via the administrative UI and automated tools.


# What to do now

1. Read the program guide 'RMH Covid-19 Home Monitoring Program.pdf' (you can find it in /latest_version/). It explains how we run the project at The Royal Melbourne, how to operate the software, what our staff processes are etc.

2. Identify the person in your organisation best able to understand the monitoring program as a whole (staff, patients, processes, resourcing and technology).

3. Work out the person in your organisation best able to configure and setup this system. You might have a dedicated REDCap administrator, a helpful IT department, or a technically skilled clinician.

4. To setup a test copy of the monitoring system using the documentation/setup_instructions.md.

5. Read and understand the design in documentation/redcap_design_overview.md. Consider how you will need to adapt this to your organisations needs. 

6. Let us know that you're using the project. RMH is not in a position to offer technical support, but we are excited to hear if you've been able to adapt our work. We'd love to hear about improvements, simplifications or other features you've added.
