"""This is a class for handling e3Vision cameras."""

import logging

import requests


class e3VisionCamera:
    """A class for handling e3Vision cameras."""

    def __init__(self, camera_serial, watchtowerurl="https://localhost:4343"):
        """Initialize the camera."""
        self.camera_serial = camera_serial
        self.watchtowerurl = watchtowerurl
        # self.interface = "

    def camera_action(self, action, **kwargs):
        """Perform an action on the camera."""
        data = {"Action": action}

        # this is needed for grouped operations
        if "SerialGroup" in kwargs:
            data["SerialGroup[]"] = kwargs.pop("SerialGroup")
        else:
            data["Serial"] = self.camera_serial
        data.update(kwargs)

        url = f"{self.watchtowerurl}/api/cameras/action"
        logging.info(f"Sending POST request to url {url} with data: {data}")
        response = requests.post(url, data=data, verify=False, timeout=5)

        try:
            response.raise_for_status()
            logging.info(f"Action {action} for Camera {self.camera_serial} successful")
            return response
        except requests.RequestException as e:
            logging.error(f"Error with Camera {self.camera_serial}: {e}")
            return None


class CameraState:
    def __init__(self):
        self.is_connected = False
        self.is_bound = False
        self.is_recording = False

    def update_state(self, action, success):
        if action == "CONNECT" and success:
            self.is_connected = True
        elif action == "DISCONNECT":
            self.is_connected = False
        elif action == "BIND" and success:
            self.is_bound = True
        # ... and so on for other states and actions ...
