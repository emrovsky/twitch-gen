import requests
import time


class salamoonder:
    """Salamoonder API wrapper for Python"""

    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.create_url = "https://salamoonder.com/api/createTask"
        self.get_url = "https://salamoonder.com/api/getTaskResult"

    def createTask(self, task_type, **kwargs):
        """Creates a task with the specified task type and additional parameters.
        Args:
            task_type (str): The type of task to create.
            **kwargs: Additional keyword arguments specific to the task type.

                Possible keyword arguments:
                - For "KasadaCaptchaSolver":
                    pjs_url (str): The URL of the page JavaScript file.
                    cd_only (bool): Whether to use cdOnly.
                - For "Twitch_CheckIntegrity":
                    token (str): The Twitch token for integrity checking.
                - For "Twitch_PublicIntegrity":
                    access_token (str): The Twitch access token.
                    proxy (str): The proxy IP address and port.
                    device_id (str, optional): The device ID (optional).
                    client_id (str, optional): The client ID (optional).
                - For "Twitch_LocalIntegrity":
                    proxy (str): The proxy IP address and port.
                    device_id (str, optional): The device ID (optional).
                    client_id (str, optional): The client ID (optional).
                - For "Twitch_RegisterAccount":
                    email (str): The email address for registering a Twitch account.

        Returns:
            str or None: The task ID if the task is successfully created, otherwise None.
        """
        try:
            task_payload = {"api_key": self.api_key, "task": {"type": task_type}}

            if task_type == "KasadaCaptchaSolver":
                task_payload["task"]["pjs"] = kwargs.get("pjs_url")
                task_payload["task"]["cdOnly"] = kwargs.get("cd_only")

            elif task_type == "Twitch_CheckIntegrity":
                task_payload["task"]["token"] = kwargs.get("token")

            elif task_type == "Twitch_PublicIntegrity":
                task_payload["task"]["access_token"] = kwargs.get("access_token")
                task_payload["task"]["proxy"] = kwargs.get("proxy")
                if "device_id" in kwargs: task_payload["task"]["deviceId"] = kwargs.get("device_id")
                if "client_id" in kwargs: task_payload["task"]["clientId"] = kwargs.get("client_id")

            elif task_type == "Twitch_LocalIntegrity":
                task_payload["task"]["proxy"] = kwargs.get("proxy")
                if "device_id" in kwargs: task_payload["task"]["deviceId"] = kwargs.get("device_id")
                if "client_id" in kwargs: task_payload["task"]["clientId"] = kwargs.get("client_id")

            elif task_type == "Twitch_RegisterAccount":
                task_payload["task"]["email"] = kwargs.get("email")

            createTask_response = self.session.post(self.create_url, json=task_payload);
            createTask_response.raise_for_status()

            taskId = createTask_response.json().get("taskId")

            return taskId
        except Exception as e:
            print("Failed to create task:", e, createTask_response.text)
            return None

    def getTaskResult(self, api_key, task_id):
        """Retrieves the result of a previously created task.

        Args:
            task_id (str): The ID of the task whose result is to be retrieved.
            api_key (str): Your Salamoonder API key.

        Returns:
            dict or None: A dictionary containing the task result if available, otherwise None.
        """
        try:
            while True:
                getTaskResult_response = self.session.post(self.get_url, json={"api_key": api_key, "taskId": task_id});
                getTaskResult_response.raise_for_status()

                result_json = getTaskResult_response.json()

                status = result_json.get("status")

                if status == "PENDING":
                    time.sleep(1)
                elif status == "ready":
                    solution = result_json.get("solution")
                    return solution
                else:
                    return None
        except Exception as e:
            # Print error message if getting task result fails
            print("Failed to get task result:", e)
            return None

