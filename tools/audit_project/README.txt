Home Monitoring REDCap project file Auditor

REDCap does not have any built in testing features. So we've built cmdline
tools that interrogate REDCap project xml files and talk to the admin website.

Example checks
- daily Observations all have the same logic
- surveys are set to use mobile-friendly buttons
- 

Some of the tools talk to the REDCap website. They depend on a session variable
and CSRF token. You use your web browsers developer tools to snatch these from
a real web session. Instructions are in the tools themselves.



download_project_xml.py

This tool connects to the REDCap admin and downloads and exports a project xml 
file for auditing.
  ./download_project_xml.py PROJECTID PHPSESSIONID
  ./download_project_xml.py 984 a15ab48ab4eu49jf69s2tm9797


audit_project.py

Checks a REDCap project export against a large number of validity tests
  ./audit_project.py Project.REDCAP.xml
  ./audit_project.py CovidHomeMonitoring_2020-04-21_1233.REDCap.xml
