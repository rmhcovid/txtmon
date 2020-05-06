Duplicating Alert Templates (ob_template) out to 14 days.

A design constraint has led to us having not one patient Observation instrument in REDCap, but many for each day/morning/afternoon. Each of these requires a number of alerts to be sent for SMSing staff during emergencies, etc.

Manually editing these is error prone. We have tools to synchronise the alerts.

The tools communicate directly with the REDCap administrative website as if you were clicking buttons. At time of writing we did not have API or Database access to do this in a more traditional fashion.

**NOTE** You will need to update the server URL to match your own servers.

**NOTE** Using these tools requires a valid web session ID (ie what your web browser gets in a cookie) and CSRF token. You can get these using the authenticate.py tool, or grab them from a real session using your browser's developer tools.

**NOTE**: The notes.txt file was Dan's notes while throwing this tool together. I haven't deleted it yet as I expect the tool to change before we hand over the project.


These tools are written in Python and have software dependancies. They are built with the Python Virtal Env and PIP which is/was common tooling when they were written. You should google for the usage but it usually boils down to
source env/bin/activate
pip install -r requirements.txt
./run_the_tool.py


list_alerts.py

This tool dumps the list of all the alerts currently defined in the REDCap project. It's useful for seeing what's defined, and grabbing the ID numbers of specific alerts.

  ./list_alerts.py PROJECTID PHPSESSIONID

There is more documentation inside the source of this tool.


update_alert.py

This tool updates the content of a single alert. ie you will run it a number of times to update all the instances of a particular alert. You need to tell it which project to update (by ID) which alert to update (enum) and the index (object id) that you wish to update.

This is a useful tool, but a sharp one. It knows about the struture of each tyep of alert that it can generate, but it requires you to snapshot. This will change to be simpler if we get time.

  ./update_alert.py PROJECTID PHPSESSIONID CSRF_TOKEN ALERT_TYPE ALERTINDEX OB_COD
There is more documentation inside the source of this tool.

TODO: There's a worked example of using this tool in developer_information.md. Move it here.
