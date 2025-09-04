# pylint:disable=line-too-long,broad-exception-caught
"""
API Helper for LOCI
"""
import os
import sys
import json
import time

import requests

from enum import Enum

if 'LOCI_BACKEND_URL' not in os.environ:
    print("ERROR: LOCI_BACKEND_URL not set.")
    sys.exit(-1)

if 'LOCI_API_KEY' not in os.environ:
    print("ERROR: LOCI_API_KEY not set.")
    sys.exit(-1)

DEBUG = os.environ.get('LOCI_API_DEBUG', 'false').lower() == 'true'
BACKEND_HOST_URL = os.environ['LOCI_BACKEND_URL']
X_API_KEY = os.environ['LOCI_API_KEY']
REQUEST_TIMEOUT = 10

class FilterType(str, Enum):
    NEW = "New"
    MODIFIED = "Modified"
    NEW_N_MODIFIED = "New||Modified"


def upload_binary(file_path, version_name, compare_version_id, project_id, platform, event_id):
    """
    Uploads a file via POST request

    Args:
        file_path (str): Path to the file to upload
        version_name (str): the version name of the new version to be created
        compare_version_id (str): the version id against which we compare the new binary, if empty no comparison will be made
        project_id (str): the project id of the project for which we are creating the version
        platform (str): the platform of the new version (ARM|TRICORE)

    Returns:
        report_id: report id of the new report comparing the new version vs the compare_version
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' does not exist")
        return None

    try:
        url = BACKEND_HOST_URL + '/api/v1/reports/xapi-upload'
        if DEBUG:
            print(f"Uploading file: {file_path}")
            print(f"To URL: {url}")

        # Open the file in binary mode and send the request

        files = {'binaryFile': (file_path, open(file_path, 'rb'), 'application/octet-stream')}
        values = {'versionName': version_name,
                  'compareVersionId': compare_version_id,
                  'projectId': project_id,
                  'platform': platform,
                  'githubEventId': event_id}
        headers = {"X-Api-Key": X_API_KEY}

        response = requests.post(url, files=files, headers=headers, data=values, timeout=REQUEST_TIMEOUT)


        # Check if request was successful
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        # Try to parse JSON response
        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            return json_response['eventDetails']['reportId']
        except ValueError:
            print(response.text)
            return response.text

    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def get_last_version_id(project_id):
    """
    Gets the version id of the latest valid version uploaded for the project

    Args:
        project_id (str): the project id for which we are getting the latest version

    Returns:
        version_id (str): the version id of the latest valid version uploaded for the project or '' if not found
        version_name (str): the version name of the latest valid version uploaded for the project

    """
    try:
        url = BACKEND_HOST_URL + '/api/v1/graph/xapi-project-versions'
        if DEBUG:
            print(f"To URL: {url}")

        headers = {"X-Api-Key": X_API_KEY}
        values = {'projectId': project_id,
                  'app': 'diag_poc'}

        response = requests.post(url, headers=headers, data=values, timeout=REQUEST_TIMEOUT)


        # Check if request was successful
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        # Try to parse JSON response
        version_id = ''
        version_name = ''
        version_date = '0000-00-00'
        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            for version in json_response['message']:
                if version[0]['properties']['status'] == 0:
                    if version[0]['properties']['end_dt'] > version_date:
                        version_id = version[0]['properties']['version_id']
                        version_name = version[0]['properties']['version_name']
                        version_date = version[0]['properties']['end_dt']
            return version_id, version_name
        except ValueError:
            print(response.text)
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error error getting latest version id: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

def get_versions(project_id):
    """
    Returns list of all version objects for the project

    Args:
        project_id (str): the projects id for which we are getting the version objects

    Returns:
        versions ([Object]): list of version objects for the project, sorted in descending order with the most recent version first or [] if none found

    """
    try:
        url = BACKEND_HOST_URL + '/api/v1/graph/xapi-project-versions'
        if DEBUG:
            print(f"To URL: {url}")

        headers = {"X-Api-Key": X_API_KEY}
        values = {'projectId': project_id,
                  'app': 'diag_poc'}

        response = requests.post(url, headers=headers, data=values, timeout=REQUEST_TIMEOUT)


        # Check if request was successful
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        # Try to parse JSON response
        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            versions = []
            for version in json_response['message']:
                versions.append(version[0])
            versions.sort(key=lambda x: x['properties']['start_dt'], reverse=True)
            return versions
        except ValueError:
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error error getting latest version id: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def get_version_data(project_id, version_name):
    """
    Returns the version id for the given version name in the specified project

    Args:
        project_id (str): the id of the project
        version_name (str): the name of the version

    Returns:
        (version_id (str), report_id (str)): the id of the version and report or None if not found
    """
    versions = get_versions(project_id)
    if not versions:
        return None

    for version in versions:
        if version_name == version['properties']['version_name']:
            return (version['properties']['version_id'], version['properties']['report_id'])

    return None

def get_reports(project_id, version_name, version_name_base):
    try:
        url = BACKEND_HOST_URL + '/api/v1/graph/xapi-get-reports'
        if DEBUG:
            print(f"To URL: {url}")

        headers = {"X-Api-Key": X_API_KEY}
        
        values = {
            'project_id': project_id,
            'version_name': version_name,
            'version_name_base': version_name_base
        }

        response = requests.post(url, headers=headers, data=values, timeout=REQUEST_TIMEOUT)

        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            
            reports = []
            for report in json_response['message']:
                reports.append(report[0])
            reports.sort(key=lambda x: x['properties']['start_dt'], reverse=True)

            return reports
        except ValueError:
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error error getting reports: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def get_versions_data(project_id, version_name, version_name_base):
    """
    Returns the version IDs for the given target and base within the specified project.
    If a diff report exists, the IDs are taken from the same report; otherwise, 
    the IDs of the latest respective versions are returned.

    Args:
        project_id (str): the id of the project
        version_name (str): the name of the target version
        version_name_base (str): the name of the base version

    Returns:
        (version_id, base_version_id, report_id) (str|None, str|None, str|None): obtained version ids or None if not found 
        and additionally the respective report_id if report exists or None if not.
    """
    if not project_id and version_name and version_name_base:
        return (None, None, None)
    
    if not version_name_base:
        version_id, report_id = get_version_data(project_id, version_name)
        return (version_id, None, report_id)
    
    reports = get_reports(project_id, version_name, version_name_base)
    if reports:
        last_report = reports[0]
        return (last_report['properties']['target_version'], last_report['properties']['base_version'], last_report['properties']['report_id'])

    version_id, _ = get_version_data(project_id, version_name)
    version_id_base, _ = get_version_data(project_id, version_name_base)
    return (version_id, version_id_base, None)

def get_project_id(project_name):
    """
    Returns the project id for the project with the given project name

    Args:
        project_name (str): the name of the project we are searching

    Returns:
        project_id (str): project id for the matched project or '' if not found

    """
    try:
        url = BACKEND_HOST_URL + '/api/v1/projects/xapi-list-all'
        if DEBUG:
            print(f"To URL: {url}")

        headers = {"X-Api-Key": X_API_KEY}

        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

        # Check if request was successful
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        # Try to parse JSON response
        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            for project in json_response:
                if project['name'] == project_name:
                    return project['id'], project['architecture']
            return None, None
        except ValueError:
            print(response.text)
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"Error getting project id: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None

def get_projects():
    """
    Returns list of all project objects for the company

    Args:

    Returns:
        projects ([Object]): list of project objects for the company

    """
    try:
        url = BACKEND_HOST_URL + '/api/v1/projects/xapi-list-all'
        if DEBUG:
            print(f"To URL: {url}")

        headers = {"X-Api-Key": X_API_KEY}

        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)

        # Check if request was successful
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")
        projects = []
        # Try to parse JSON response
        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            for project in json_response:
                projects.append(project)
            return projects
        except ValueError:
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error getting project id: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def upload_finished(project_id, report_id):
    """
    Checks the status of the report with given report id

    Args:
        project_id (str): the projects id for which the report was created
        report_id (str): the report id of the report we are uploading

    Returns:
        (finished, status) (boolean, int): returns the status of the upload

    """
    try:
        url = BACKEND_HOST_URL + '/api/v1/reports/xapi-progress'
        if DEBUG:
            print(f"To URL: {url}")

        values = {'projectId': project_id,
                  'reportId': report_id}

        response = requests.post(url, data=values, timeout=REQUEST_TIMEOUT)

        # Check if request was successful
        response.raise_for_status()

        if DEBUG:
            print("Server Response:")

        # Try to parse JSON respons
        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            status = json_response['progress']['status']

            if status != -1:
                return (True, status)
            else:
                return (False, None)

        except ValueError:
            print(response.text)
            return (True, 0)

    except requests.exceptions.RequestException as e:
        print(f"Error error getting latest version id: {e}")
        return (True, 0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        return (True, 0)


def full_upload(file_path, version_name, project_name, use_latest=True, compare_version_id='', wait='True', event_id='') -> int:

    project_id, platform = get_project_id(project_name)
    if project_id is None:
        print("Uploading failed, Project does not exist.")
        return -1

    if use_latest:
        compare_version_id, _ = get_last_version_id(project_id)

    report_id = upload_binary(file_path, version_name, compare_version_id, project_id, platform, event_id)
    if not report_id:
        print("Uploading failed, See previous message for more details.")
        return -1

    print(f"Uploaded binary Report ID: {report_id}, Compare Version ID: {compare_version_id}, Project ID: {project_id}")


    status = 0
    tries = 0

    if wait.lower() == 'true':
        print("Waiting for processing to finish")
        while True:
            finished, status = upload_finished(project_id, report_id)
            if finished:
                break
            tries += 1
            if tries > 360:
                print("Processing not finished after 60 minutes. Please manually check status on the Loci Platform.")
                return -1
            time.sleep(10)

    return status


def get_function_insights(version_id,
                          version_id_base: str | None = None,
                          report_id: str | None = None,
                          perc_resp_limit: float | None = None,
                          perc_thro_limit: float | None = None,
                          perc_bott_limit: float | None = None,
                          pairs: list = None,
                          filter: FilterType | None = None):
    try:
        url = BACKEND_HOST_URL + '/api/v1/data/xapi-function-insights'

        if DEBUG:
            print(f"version_id      : {version_id}")
            print(f"version_id_base : {version_id_base}")
            print(f"report_id       : {report_id}")
            print(f"perc_resp_limit : {perc_resp_limit}")
            print(f"perc_thro_limit : {perc_thro_limit}")
            print(f"perc_bott_limit : {perc_bott_limit}")
            print(f"pairs           : {pairs}")
            print(f"filter          : {filter.value if filter else None}")

        values = {
            'version_id': version_id,
            'version_id_base': version_id_base,
            'report_id': report_id,
            'perc_resp_limit': perc_resp_limit,
            'perc_thro_limit': perc_thro_limit,
            'perc_bott_limit': perc_bott_limit,
            'pairs': pairs,
            'filter': filter.value if filter else None,
        }

        headers = {"X-Api-Key": X_API_KEY}
        response = requests.post(url, headers=headers, json=values, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            return json_response
        except ValueError:
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error getting function insights: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
    

def get_flame_graph(
    project_id: str,
    version_id: str,
    source_container: str,
    source_long_name: str,
) -> tuple[int, dict]:
    try:
        url = BACKEND_HOST_URL + "/api/v1/data/xapi-flame-graph"

        if DEBUG:
            print(f"project_id        : {project_id}")
            print(f"version_id        : {version_id}")
            print(f"source_container  : {source_container}")
            print(f"source_long_name  : {source_long_name}")

        values = {
            "project_id": project_id,
            "version_id": version_id,
            "source_container": source_container,
            "source_long_name": source_long_name,
        }

        headers = {"X-Api-Key": X_API_KEY}
        response = requests.post(
            url, headers=headers, json=values, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            return json_response
        except ValueError:
            print(response.text)
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error getting flame graph: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def get_version_status(
        project_id: str,
        version_id: str):
    try:
        url = BACKEND_HOST_URL + "/api/v1/reports/xapi-version-progress"
        
        if DEBUG:
            print(f"project_id        : {project_id}")
            print(f"version_id        : {version_id}")

        values = {
            "projectId": project_id,
            "versionId": version_id,
        }

        headers = {"X-Api-Key": X_API_KEY}
        response = requests.post(
            url, headers=headers, json=values, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            return json_response
        except ValueError:
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f'Error getting version status: {e}')
        return None
    except Exception as e:
        print(f'Unexpected error: {e}')
        return None

def get_function_insights_summary(
    project_id: str,
    version_id: str,
    version_id_base: str,
    repository: str,
    pr_number: str
) -> dict | None:
    try:
        url = BACKEND_HOST_URL + "/api/v1/data/xapi-insights-summary"

        owner, repo = repository.split('/', 1)

        if DEBUG:
            print(f"project_id        : {project_id}")
            print(f"version_id        : {version_id}")
            print(f"version_id_base   : {version_id_base}")
            print(f"owner             : {owner}")
            print(f"repo              : {repo}")
            print(f"pr_number         : {pr_number}")

        values = {
            "project_id": project_id,
            "version_id": version_id,
            "version_id_base": version_id_base,
            "owner": owner,
            "repo": repo,
            "pr_number": pr_number
        }

        headers = {"X-Api-Key": X_API_KEY}
        response = requests.post(
            url, headers=headers, json=values
        )
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            return json_response
        except ValueError:
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f'Error getting function insights summary: {e}')
        return None
    except Exception as e:
        print(f'Unexpected error: {e}')



def get_report_data(report_id: str):
    try:
        url = BACKEND_HOST_URL + '/api/v1/graph/xapi-get-report-symbols'

        if DEBUG:
            print(f"report_id      : {report_id}")

        values = {
            'report_id': report_id
        }

        headers = {"X-Api-Key": X_API_KEY}
        response = requests.post(url, headers=headers, json=values, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        if DEBUG:
            print("\nServer Response:")

        try:
            json_response = response.json()
            if DEBUG:
                print(json.dumps(json_response, indent=2))
            return json_response
        except ValueError:
            print(response.text)
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error getting report data: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
