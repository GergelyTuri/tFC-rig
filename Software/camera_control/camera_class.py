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
        response = requests.post(url, data=data, verify=False, timeout=10)

        try:
            response.raise_for_status()
            logging.info(f"Action {action} for Camera {self.camera_serial} successful")
            return response
        except requests.RequestException as e:
            logging.error(f"Error with Camera {self.camera_serial}: {e}")
            return None


class CameraState:
    """
    * 12/29/2023 not tested, not used at the moment *
    Represents the state of a camera.

    Attributes:
        is_connected (bool): Indicates whether the camera is connected.
        is_bound (bool): Indicates whether the camera is bound.
        is_recording (bool): Indicates whether the camera is currently recording.
    """

    def __init__(self):
        self.is_connected = False
        self.is_bound = False
        self.is_recording = False

    def update_state(self, action, success):
        """
        Updates the camera state based on the given action and success status.

        Args:
            action (str): The action performed on the camera.
            success (bool): Indicates whether the action was successful.
        """
        if action == "CONNECT" and success:
            self.is_connected = True
        elif action == "DISCONNECT":
            self.is_connected = False
        elif action == "BIND" and success:
            self.is_bound = True
        # ... and so on for other states and actions ...
            
def checkCam(cam_input):
    INTERFACE = "172.29.96.1"
    if cam_input:
        try:
            cam = e3VisionCamera(cam_input)
            cam.camera_action("UPDATEMC")
            cam.camera_action(
                "CONNECT",
                Config="480p15",
                Codec="MJPEG",
                IFace=INTERFACE,
                Annotation="Time",
                Segtime="3m",
            )
            cam.camera_action("DISCONNECT")
        except Exception as e:
            raise Exception(f"Issue connecting to camera {cam_input}:\n\n{str(e)}")
