"""
Config for PyTest module

Our audit_project.py tool uses the pytesting framework. Pytest expects to be
run as a command and pointed at a directory of test. But we want a cmdline tool
that accepts a XML file to validate as a cmdline argument. To do that we must
jump through pytest global config hoops (below) and these have to live in a
separate conftest.py file.
"""


def pytest_addoption(parser):
    parser.addoption(
        "--projxmlfile", action="store", default="xxxxxx",
        help='specify project xmlfile: "CovidHomeMonitoring_2020-04-16_1204.REDCap.xml'
    )
