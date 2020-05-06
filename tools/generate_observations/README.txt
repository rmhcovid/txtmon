Duplicating the Observation Template (ob_template) out to 14 days.

A design constraint has led to us having not one patient Observation instrument in REDCap, but 16 (a template, one at the patients time of registration, and then two each day for up to 14 days).

Manually editing these is error prone. We have tools to synchronise the observations and to check they are correct.


These are the latest exports from inside the REDCap management UI.
  HomeMonitoringEg_DataDictionary.csv
  HomeMonitoringEg_asi_import.csv

We copy out the ob_template fields from the data dictionary into this file
  observation_template.csv

We use this tool to generate the 14 days of observations from the template
  generate_obs_definitions.py


TODO there is a worked example of using this tool in 'developer_information.md'. Move it here.
