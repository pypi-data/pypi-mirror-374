import requests
import logging
from time import sleep
from typing import List, Dict, Any


class TopomojoException(Exception):
    """Exception raised when the TopoMojo API returns an error."""

    def __init__(self, status_code, response_message):
        """Initialize the exception with a status code and API message."""

        self.status_code = status_code
        self.response_message = response_message
        super().__init__(f"Topomojo API Error - Status Code: {status_code}, Response: {response_message}")


class Topomojo:
    """Client for interacting with a TopoMojo instance."""

    def __init__(self, app_url, api_key, debug:bool=False):
        """Create a new :class:`Topomojo` client.

        Parameters
        ----------
        app_url: str
            Base URL to the TopoMojo application (e.g. ``https://example.com/topomojo``).
        api_key: str
            API key used for authentication.
        debug: bool, optional
            When ``True`` debug logging is enabled.
        """

        self.app_url = app_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({'accept': 'application/json', 'x-api-key': api_key})

        # Setup logger
        self.logger = logging.getLogger(__name__)

        if debug:
            self.logger.setLevel(logging.DEBUG)
            # Create console handler and set level to the provided log level
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

            # Add formatter to ch
            ch.setFormatter(formatter)

            # Add ch to logger
            self.logger.addHandler(ch)
            self.logger.debug("Topomojo class initialized with logging enabled")
        else:
            self.logger.disabled = True

    ################################## TEMPLATE FUNCTIONS#####################################################################################
    def get_templates(self, WantsAudience=None, WantsPublished=None, WantsParents=None,
                      aud=None, pid=None, sib=None, Term=None,
                      Skip=None, Take=None, Sort=None, Filter=None):
        """Get templates from TopoMojo.

        Parameters correspond to the query arguments documented by the
        TopoMojo API and are passed directly to the endpoint.

        Returns the list of templates via JSON from the TopoMojo API.
        """

        # Construct the full URL
        full_url = self.app_url + '/api/templates'  # Updated from api_url to app_url

        # Construct the parameters for the request
        params = {
            'WantsAudience': WantsAudience,
            'WantsPublished': WantsPublished,
            'WantsParents': WantsParents,
            'aud': aud,
            'pid': pid,
            'sib': sib,
            'Term': Term,
            'Skip': Skip,
            'Take': Take,
            'Sort': Sort,
            'Filter': Filter,
        }

        self.logger.debug(f"Getting templates with query params: {params}")
        # Make a GET request to the API endpoint with the provided parameters
        response = self.session.get(full_url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def update_template(self, changed_template: Dict[str, Any]):
        """Update an existing template with new data that is passed directly to the TopoMojo API.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        # Construct the full URL for the specific template
        full_url = f"{self.app_url}/api/template"

        # Make a PUT request to the API endpoint with the provided changed_template_json
        self.logger.debug(f"Updating template with content {changed_template}")
        response = self.session.put(full_url, json=changed_template)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def new_workspace_template(self, template_link_data: Dict[str, Any]):
        """Add a template to a workspace.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        # Construct the full URL
        full_url = self.app_url + '/api/template'

        self.logger.debug(f"Adding template with data {template_link_data}")

        # Make a POST request to the API endpoint with the provided template_link_data
        response = self.session.post(full_url, json=template_link_data)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def unlink_template(self, template_link_data: Dict[str, Any]):
        """Unlink a template from a parent.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        # Construct the full URL
        full_url = self.app_url + '/api/template/unlink'

        self.logger.debug(f"Unlinking Template {template_link_data}")
        # Make a POST request to the API endpoint with the provided template_link_data
        response = self.session.post(full_url, json=template_link_data)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def get_template(self, template_id):
        """Get a template by ID.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        # Construct the full URL
        full_url = f"{self.app_url}/api/vm-template/{template_id}"

        self.logger.debug(f"Getting template {template_id}")

        # Make a GET request to the API endpoint
        response = self.session.get(full_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def get_template_detail(self, template_id):
        """Get full template details by ID.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Loading template detail for template ID: {template_id}")
        # Construct the full URL
        full_url = f"{self.app_url}/api/template-detail/{template_id}"

        # Make a GET request to the API endpoint
        response = self.session.get(full_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def initialize_template(self, template_id, wait=True):
        """Initialize a template after it has been unlinked.
        Optionally wait for completion.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        # Construct the full URL
        full_url = f"{self.app_url}/api/vm-template/{template_id}"

        self.logger.debug(f"Initializing template {template_id}")

        # Make a PUT request to the API endpoint
        response = self.session.put(full_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # if wait is true, then wait for the disk to be done initializing before returning
            if wait:
                while True:
                    check = self.get_template(template_id)
                    task = check.get('task')
                    if task:
                        self.logger.debug(f"Initializing {task['progress']}%")
                        sleep(1)
                    else:
                        if task is None:
                            self.logger.debug("No initialization task found")
                        else:
                            self.logger.debug("Done Initializing")
                        break
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def deploy_vm_from_template(self, template_id):
        """Deploy a VM from an existing template.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        # Construct the full URL
        full_url = f"{self.app_url}/api/vm-template/{template_id}"

        self.logger.debug(f"Deploying VM template {template_id}")

        # Make a POST request to the API endpoint
        response = self.session.post(full_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    ################################## WORKSPACE FUNCTIONS#####################################################################################
    def get_workspaces(self, aud: str = None, scope: str = None, doc: int = None,
                    WantsAudience: bool = None, WantsManaged: bool = None,
                    WantsDoc: bool = None, WantsPartialDoc: bool = None,
                    Term: str = None, Skip: int = None, Take: int = None,
                    Sort: str = None, Filter: List[str] = None) -> List[Dict[str, Any]]:
        """List workspaces matching the provided criteria.

        Parameters correspond to the query arguments documented by the
        TopoMojo API and are passed directly to the endpoint.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        full_url = f"{self.app_url}/api/workspaces"
        params = {
            "aud": aud,
            "scope": scope,
            "doc": doc,
            "WantsAudience": WantsAudience,
            "WantsManaged": WantsManaged,
            "WantsDoc": WantsDoc,
            "WantsPartialDoc": WantsPartialDoc,
            "Term": Term,
            "Skip": Skip,
            "Take": Take,
            "Sort": Sort,
            "Filter": Filter
        }
        self.logger.debug(f"Calling get_workspaces API with params: {params}")

        response = self.session.get(full_url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise TopomojoException(response.status_code, response.text)


    def create_workspace(self, new_workspace_data: Dict[str, Any]):
        """Create a new workspace.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        # Construct the full URL
        full_url = self.app_url + '/api/workspace'

        self.logger.debug(f"Creating workspace {new_workspace_data}")

        # Make a POST request to the API endpoint with the provided new_workspace_data
        response = self.session.post(full_url, json=new_workspace_data)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def update_workspace(self, workspace_id: str, changed_workspace_data: Dict[str, Any]):
        """Modify an existing workspace.

        Server behavior: the `PUT /api/workspace` endpoint expects a full
        `RestrictedChangedWorkspace` payload and requires `name` to be present.
        To allow callers to pass only changed fields, this function:
        - Loads the current workspace via `GET /api/workspace/{id}`.
        - Merges unspecified fields from the current workspace into the payload.
        - Sends a `PUT` to `/api/workspace` with `id` plus merged fields.

        Allowed fields merged/sent: `name`, `description`, `tags`, `author`, `audience`.
        To clear a field, provide it explicitly (e.g., empty string) if allowed by the API.

        Returns an empty dict on success (200), otherwise raises TopomojoException.
        """

        full_url = f"{self.app_url}/api/workspace"

        changes = dict(changed_workspace_data) if changed_workspace_data is not None else {}

        # Prepare base payload with required id
        payload: Dict[str, Any] = {'id': workspace_id}

        # Fields allowed by RestrictedChangedWorkspace
        allowed_fields = ["name", "description", "tags", "author", "audience"]

        # Try to load existing workspace to preserve unspecified fields
        current: Dict[str, Any] = {}
        try:
            load_resp = self.session.get(f"{self.app_url}/api/workspace/{workspace_id}")
            if load_resp.status_code == 200:
                current = load_resp.json() or {}
            else:
                self.logger.debug(
                    f"Could not load current workspace {workspace_id} (status {load_resp.status_code}); "
                    f"will require 'name' in changes."
                )
        except Exception as e:
            self.logger.debug(f"Error loading current workspace {workspace_id}: {e}")

        # Merge: explicit changes take precedence; otherwise fall back to current values
        for field in allowed_fields:
            if field in changes:
                payload[field] = changes[field]
            elif current and field in current:
                payload[field] = current[field]

        # Ensure required 'name' is present when we couldn't load current
        if 'name' not in payload or payload['name'] is None or (isinstance(payload['name'], str) and payload['name'].strip() == ''):
            if 'name' not in changes and not current:
                raise ValueError("Workspace name is required for update and could not be loaded from server.")

        self.logger.debug(f"Updating workspace {workspace_id} with payload {payload}")

        response = self.session.put(full_url, json=payload)

        if response.status_code == 200:
            # Server returns empty 200 on success
            return {}
        else:
            raise TopomojoException(response.status_code, response.text)


    def get_workspace_invite(self, workspace_id):
        """Generate an invite code for a workspace.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Generating invitation code for workspace ID: {workspace_id}")
        # Construct the full URL
        full_url = f"{self.app_url}/api/workspace/{workspace_id}/invite"

        # Make a PUT request to the API endpoint
        response = self.session.put(full_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def delete_workspace(self, workspace_id):
        """Delete a workspace.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Deleting workspace with ID: {workspace_id}")
        # Construct the full URL
        full_url = f"{self.app_url}/api/workspace/{workspace_id}"

        # Make a DELETE request to the API endpoint
        response = self.session.delete(full_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            self.logger.debug("Workspace deleted successfully")
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def export_workspaces(self, ids: List[str]) -> None:
        """Export multiple workspaces by their IDs.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Exporting {len(ids)} workspaces with IDs: {ids}")
        # Construct the full URL
        full_url = f"{self.app_url}/api/admin/export"

        # Make a POST request to the API endpoint with the list of IDs in the body
        response = self.session.post(full_url, json=ids)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            self.logger.debug("Workspaces exported successfully")
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def export_workspace(self, workspace_id: str):
        """Export a single workspace by ID.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Exporting workspace with ID: {workspace_id}")
        return self.export_workspaces([workspace_id])


    def download_workspaces(self, workspace_ids: List[str], output_file: str) -> None:
        """Download an export package containing one or more workspaces.
        All workspaces listed will be included in the same export package.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Downloading an export package for workspaces: {workspace_ids}")

        url = f"{self.app_url}/api/admin/download"
        response = self.session.post(url, json=workspace_ids, stream=True)

        if response.status_code == 200:
            self.logger.debug(f"Saving export package to file: {output_file}")
            with open(output_file, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def download_workspace(self, workspace_id: str, output_file: str):
        """Download a single workspace export package.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Downloading an export package for workspace: {workspace_id}")
        return self.download_workspaces([workspace_id], output_file)


    def upload_workspace(self, archive_path: str) -> List[str]:
        """Upload a single workspace export package.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Uploading workspace archive: {archive_path}")

        url = f"{self.app_url}/api/admin/upload"

        with open(archive_path, "rb") as archive:
            response = self.session.post(url, files={"files": archive})

        if response.status_code == 200:
            return response.json()
        else:
            raise TopomojoException(response.status_code, response.text)


    def upload_workspaces(self, archive_paths: List[str]) -> List[str]:
        """Upload multiple workspace export packages.

        Returns a list of JSON from TopoMojo API.
        """

        uploaded_ids: List[str] = []
        for path in archive_paths:
            uploaded_ids.extend(self.upload_workspace(path))
        return uploaded_ids


    ################################## GAMESPACE FUNCTIONS#####################################################################################
    def get_gamespaces(self, WantsAll: bool = None, WantsActive: bool = None,
                       Term: str = None, Skip: int = None, Take: int = None,
                       Sort: str = None, Filter: List[str] = None):
        """List gamespaces available to the user.

        Parameters correspond to the query arguments documented by the
        TopoMojo API and are passed directly to the endpoint.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        # Construct the full URL
        full_url = f"{self.app_url}/api/gamespaces"

        # Construct the query parameters
        params = {
            "WantsAll": WantsAll,
            "WantsActive": WantsActive,
            "Term": Term,
            "Skip": Skip,
            "Take": Take,
            "Sort": Sort,
            "Filter": Filter
        }

        self.logger.debug(f"Listing gamespaces with params: {params}")

        # Make a GET request to the API endpoint with the provided query parameters
        response = self.session.get(full_url, params=params)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def stop_gamespace(self, gamespace_id:str):
        """Stop a running gamespace.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Stopping gamespace {gamespace_id}")
        # Construct the full URL
        full_url = f"{self.app_url}/api/gamespace/{gamespace_id}/stop"

        # Make a POST request to the API endpoint
        response = self.session.post(full_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)


    def complete_gamespace(self, gamespace_id:str):
        """Mark a gamespace as complete.

        Returns JSON from TopoMojo API if 200 OK was returned. Otherwise, raise a TopoMojo Exception.

        Raises: TopoMojoException
        """

        self.logger.debug(f"Completing gamespace {gamespace_id}")
        # Construct the full URL
        full_url = f"{self.app_url}/api/gamespace/{gamespace_id}/complete"

        # Make a POST request to the API endpoint
        response = self.session.post(full_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the JSON response
            return response.json()
        else:
            # If the request was not successful, raise a custom exception
            raise TopomojoException(response.status_code, response.text)
