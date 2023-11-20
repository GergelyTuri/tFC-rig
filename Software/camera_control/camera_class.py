"""This is a class for handling e3Vision cameras."""

import logging

import requests
import urllib3


class e3VisionCamera:
    """A class for handling e3Vision cameras."""

    def __init__(self, camera_serial, watchtowerurl="https://127.0.0.1:4343"):
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

        try:
            response = requests.post(
                f"{self.watchtowerurl}/api/cameras/action",
                data=data,
                verify=False,
                timeout=5,
            )
            response.raise_for_status()
            logging.info(f"Action {action} for Camera {self.camera_serial} successful")
            return response
        except requests.RequestException as e:
            logging.error(f"Error with Camera {self.camera_serial}: {e}")
            return None
