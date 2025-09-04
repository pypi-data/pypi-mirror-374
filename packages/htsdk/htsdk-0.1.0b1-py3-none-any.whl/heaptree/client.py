import os

import requests
from heaptree.enums import Language, NodeSize, NodeType, OperatingSystem
from heaptree.exceptions import HeaptreeAPIException
from heaptree.response_wrappers import (
    CreateNodeResponseWrapper,
    ExecutionResponseWrapper,
    NodesResponseWrapper,
    UsagesResponseWrapper,
)


class Heaptree:
    def __init__(self, api_key: str | None = None, *, base_url: str | None = None):
        """Create a new Heaptree SDK client.

        Args:
            api_key: Your platform **X-Api-Key**. Optional if you will be using a
                previously-delegated JWT instead (see :py:meth:`delegate_token`).
            base_url: Override the base URL of the Heaptree API (useful for local
                testing). Defaults to the hosted production endpoint.
        """

        self.api_key: str | None = api_key
        self.token: str | None = None
        self.base_url: str = base_url or "https://api.heaptree.com"

    # ------------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------------

    def call_api(self, endpoint: str, data: dict):
        url = f"{self.base_url}{endpoint}"

        # ----- Auth headers -----
        headers: dict[str, str] = {"Content-Type": "application/json"}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        elif self.api_key:
            headers["X-Api-Key"] = self.api_key
        else:
            raise HeaptreeAPIException(
                "No authentication credentials supplied – set api_key or call "
                "delegate_token() first."
            )

        response = requests.post(url, json=data, headers=headers)
        try:
            return response.json()
        except ValueError as e:
            # Response is not JSON (should not happen in normal operation)
            raise HeaptreeAPIException(
                f"Invalid JSON response for {endpoint}: {response.text}"
            ) from e

    # ------------------------------------------------------------------
    # OS management
    # ------------------------------------------------------------------

    def run_command(self, node_id: str, command: str) -> ExecutionResponseWrapper:
        """Execute a command on the remote node.
        
        Args:
            node_id: Target node.
            command: Command to execute.
            
        Returns:
            ExecutionResponseWrapper with convenient access to output, error, exit_code, etc.
        """
        data = {"node_id": node_id, "command": command}
        raw_response = self.call_api("/run-command", data)
        return ExecutionResponseWrapper(raw_response)

    def inject_packages(self, node_id: str):
        data = {"node_id": node_id}
        return self.call_api("/inject-packages", data)

    def run_code(self, node_id: str, lang: "Language", code: str) -> ExecutionResponseWrapper:
        """Execute **code** on the remote *node*.

        Args:
            node_id: Target node.
            lang: :pyclass:`~heaptree.enums.Language` specifying the language
                runtime to use.
            code: Source code to execute.
            
        Returns:
            ExecutionResponseWrapper with convenient access to output, error, exit_code, etc.
        """
        data = {"node_id": node_id, "lang": lang.value, "code": code}
        raw_response = self.call_api("/run-code", data)
        return ExecutionResponseWrapper(raw_response)

    # ------------------------------------------------------------------
    # File management
    # ------------------------------------------------------------------

    def upload(self, node_id: str, file_path: str, destination_path: str = None):
        """
        Upload a file to a node and transfer it to the node's filesystem.

        Args:
            node_id: The ID of the node to upload to
            file_path: Local path to the file to upload
            destination_path: Optional path on the node where file should be placed
                            (defaults to /home/ubuntu/Desktop/YOUR_FILES/)

        Returns:
            dict: Response containing upload status and transfer details
        """

        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract filename from path
        filename = os.path.basename(file_path)

        # Step 1: Get presigned upload URL
        upload_url_data = {"node_id": node_id, "filename": filename}

        upload_response = self.call_api("/get-upload-url", upload_url_data)
        if not upload_response:
            raise Exception(f"Failed to get upload URL: {upload_response}")
        print(upload_response)

        # Step 2: Upload file to S3 using presigned URL
        upload_url = upload_response["upload_url"]
        fields = upload_response["fields"]

        try:
            with open(file_path, "rb") as file:
                # Prepare multipart form data
                files = {"file": (filename, file, "application/octet-stream")}

                # Upload to S3
                s3_response = requests.post(upload_url, data=fields, files=files)
                s3_response.raise_for_status()

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")

        # Step 3: Transfer file from S3 to node filesystem
        transfer_data = {"node_id": node_id}

        transfer_response = self.call_api("/transfer-files", transfer_data)

        return {
            "upload_status": "success",
            "filename": filename,
            "s3_upload": "completed",
            "transfer_response": transfer_response,
        }

    def download(self, node_id: str, remote_path: str, local_path: str):
        data = {
            "node_id": node_id,
            "file_path": remote_path,  # API still expects 'file_path'
        }
        response_json = self.call_api("/download-files", data)
        s3_url = response_json.get("download_url")

        if not s3_url:
            return {"error": "No download URL found."}

        try:
            download_response = requests.get(s3_url)
            download_response.raise_for_status()

            with open(local_path, "wb") as f:
                f.write(download_response.content)
            return {"status": "success", "file_path": local_path}
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to download file: {e}"}

    def write_files(self, node_id: str, file_path: str, content: str):
        data = {"node_id": node_id, "file_path": file_path, "content": content}
        return self.call_api("/write-files", data)

    def read_files(self, node_id: str, file_path: str):
        data = {"node_id": node_id, "file_path": file_path}
        return self.call_api("/read-files", data)

    def transfer_files(self, node_id: str):
        data = {"node_id": node_id}
        return self.call_api("/transfer-files", data)

    def get_upload_url(self, node_id: str, filename: str):
        data = {"node_id": node_id, "filename": filename}
        return self.call_api("/get-upload-url", data)

    # ------------------------------------------------------------------
    # Usage management
    # ------------------------------------------------------------------

    def get_usages(self) -> UsagesResponseWrapper:
        """Retrieve usage records for the authenticated user.
        
        Returns:
            UsagesResponseWrapper with convenient access to usage data, costs, etc.
        """
        raw_response = self.call_api("/get-usages", {})
        return UsagesResponseWrapper(raw_response)

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def create_node(
        self,
        os: OperatingSystem = OperatingSystem.LINUX,
        num_nodes: int = 1,
        node_type: NodeType = NodeType.UBUNTU,
        node_size: NodeSize = NodeSize.SMALL,
        lifetime_seconds: int = 330,  # 5 minutes
        applications: list[str] = [],
    ) -> CreateNodeResponseWrapper:
        """
        Create one or more nodes.

        Returns CreateNodeResponseWrapper with convenient access:
        - result.node_id (for single node)
        - result.node_ids (for multiple nodes)
        - result.web_access_url (for single node)
        - result.web_access_urls (for multiple nodes)
        """
        data = {
            "os": os.value,
            "num_nodes": num_nodes,
            "node_size": node_size.value,
            "node_type": node_type.value,
            "lifetime_seconds": lifetime_seconds,
            "applications": applications,
        }
        raw_response = self.call_api("/create-node", data)
        return CreateNodeResponseWrapper(raw_response)

    def cleanup_node(self, node_id: str):
        data = {
            "node_id": node_id,
        }
        return self.call_api("/cleanup-node", data)

    def terminate_nodes(self, node_ids: list[str]):
        data = {"node_ids": node_ids}
        return self.call_api("/terminate-nodes", data)

    def get_nodes(self) -> NodesResponseWrapper:
        """Retrieve nodes owned by the authenticated user.
        
        Returns:
            NodesResponseWrapper with convenient access to node data, count, etc.
        """
        raw_response = self.call_api("/get-nodes", {})
        return NodesResponseWrapper(raw_response)

    def ping_node(self, node_id: str):
        """Check whether a node's no-VNC endpoint is responsive."""
        return self.call_api("/ping", {"node_id": node_id})

    # ------------------------------------------------------------------
    # API key management
    # ------------------------------------------------------------------

    def create_api_key(self, name: str, description: str = ""):
        data = {"name": name, "description": description}
        return self.call_api("/create-api-key", data)

    def get_api_keys(self):
        return self.call_api("/get-api-keys", {})

    def delete_api_keys(self, key_ids: list[str]):
        data = {"key_ids": key_ids}
        return self.call_api("/delete-api-keys", data)

    # ------------------------------------------------------------------
    # User management
    # ------------------------------------------------------------------

    def get_user_data(self):
        return self.call_api("/get-user-data", {})

    def update_user_profile(self, *, name: str | None = None):
        data = {}
        if name is not None:
            data["name"] = name
        return self.call_api("/update-user-profile", data)
