"""
Arguments for script
Required args:
-ids: mouse_ids
-p: primary port

Optional args:
-s1: secondary port 1
-c1: camera1
-c2: camera2

Trial parameters (can be found in Software/Rig/trial.h):

NUMBER_OF_TRIALS                   
MIN_ITI:                            minimum time for each inter-trial interval (ms)
MAX_ITI:                            maximum time for each inter-trial interval (ms)
TRIAL_DURATION:                     duration of each trial (ms)
POST_LAST_TRIAL_INTERVAL:           time after the last trial (ms)

Water reward parameters:

WATER_REWARD_AVAILABLE:             enables if water reward is available
USING_AUDITORY_CUES:                enables auditory signal and air puffs
USING_AIR_PUFFS:                    enables air puffs
AIR_PUFF_DURATION:                  duration of each air puff (ms)
REWARD_TYPE:                        type of reward (ex: water, sugary water, etc)

WATER_DISPENSE_ON_NUMBER_LICKS:     number of licks required to get reward
WATER_DISPENSE_TIME:                amount of time water is dispensed for each reward (ms)
WATER_TIMEOUT:                      time between water rewards (ms)

LICK_TIMEOUT:                       time that must elapse after an initial lick for a new lick to be counted (ms)
LICK_COUNT_TIMEOUT:                 time where lick count resets to 0, if there are no new licks (ms)


"""

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QSpinBox, QAbstractSpinBox, QFormLayout, QGroupBox, QMessageBox, QTextEdit, QDialog, QCheckBox, QScrollArea, QComboBox
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from ..camera_control import camera_class as cc
from .serial_comm import SerialComm as sc
import serial, subprocess
import sys, os, signal
import re, json
import serial.tools.list_ports

REWARD1 = "Water"
REWARD2 = "5% Sugar Water"
DEBUG = False

class OutputDialog(QDialog):
    def __init__(self, process_thread, parent=None):
        super().__init__(parent)
        
        self.process_thread = process_thread
        self.setWindowTitle("Output")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.resize(750, 300)

        self.outputTextEdit = QTextEdit()
        self.outputTextEdit.setReadOnly(True)
        layout.addWidget(self.outputTextEdit)

        stopButton = QPushButton("Stop and collect data")
        stopButton.clicked.connect(self.process_thread.stop_process)
        layout.addWidget(stopButton)

    def update_output(self, output):
        try:
            self.outputTextEdit.append(output)
        except KeyboardInterrupt:
            print("KeyboardInterrupt detected.")

class ProcessThread(QThread):
    output_updated = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            self.process = subprocess.Popen(self.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

            for line in iter(self.process.stdout.readline, ''):
                self.output_updated.emit(line.strip())
            self.process.wait()
        except Exception as e:
            self.output_updated.emit(str(e))
    
    def stop_process(self):
        if self.process:
            print("Interrupting experiment")
            if os.name == 'nt':  # Windows
                self.process.send_signal(signal.CTRL_C_EVENT)
            else:
                self.process.send_signal(signal.SIGINT)

class SpinBox(QSpinBox):
    def __init__(self, layout: QFormLayout, text: str, default = 1, step = 10, min = 1, max=1000000):
        super().__init__()
        self.wheelEvent = lambda event: None  # Disables scrolling in boxes
        # spinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)  # Disables arrow buttons
        self.setRange(min, max)
        self.setSingleStep(step)
        self.setValue(default)
        layout.addRow(QLabel(text), self)

class CheckBox(QCheckBox):
    def __init__(self, layout: QFormLayout, text: str):
        super().__init__(text)
        self.setCheckState(Qt.CheckState.Checked)
        layout.addRow(self)

class LineEdit(QLineEdit):
    def __init__(self, layout: QFormLayout, text: str):
        super().__init__()
        layout.addRow(QLabel(text), self)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        
        self.resize(500, 400)
        self.setWindowTitle("tFC experiment")
        # TODO: Add window icon?
        self.setWindowIcon(QIcon(QPixmap(50,50)))
 
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 20, 5, 20)
        self.setLayout(layout)


        # Script Input Arguments
        formGroupBox = QGroupBox()
        formLayout = QFormLayout()

        self.mouseIdsField = LineEdit(formLayout, "Mouse IDs")
        self.pField = LineEdit(formLayout, "Primary Port")
        self.s1Field = LineEdit(formLayout, "Secondary Port 1 (Optional)")
        self.c1Field = LineEdit(formLayout, "Camera 1 (Optional)")
        self.c2Field = LineEdit(formLayout, "Camera 2 (Optional)")

        formGroupBox.setLayout(formLayout)
        layout.addWidget(formGroupBox)


        # Trial Settings
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        
        trailSettingsGroupBox = QGroupBox("Trial Settings")
        trialSettingsLayout = QFormLayout()

        self.numTrials = SpinBox(trialSettingsLayout, "Number of trials", 6, step=1, min=1, max=6)
        self.minIti = SpinBox(trialSettingsLayout, "Minimum iti duration", 60000, step=1000)
        self.maxIti = SpinBox(trialSettingsLayout, "Maximum iti duration", 300000, step=1000)
        self.trialDuration = SpinBox(trialSettingsLayout, "Trial duration", 50000, step=1000)
        self.postTrialDuration = SpinBox(trialSettingsLayout, "Post-last trial duration", 60000, step=1000)

        trailSettingsGroupBox.setLayout(trialSettingsLayout)
        
        # Rewards Settings
        rewardsGroupBox = QGroupBox("Water Reward Settings")
        rewardsLayout = QFormLayout()
        
        self.waterEnabled = CheckBox(rewardsLayout, "Water Rewards enabled")
        self.audAirEnabled = CheckBox(rewardsLayout, "Auditory Cues and Air Puffs enabled")
        self.airEnabled = CheckBox(rewardsLayout, "Air Puffs enabled")
        self.rewardType = QComboBox()
        self.airPuffDuration = SpinBox(rewardsLayout, "Air Puff duration", 200)
        self.waterDispNumLicks = SpinBox(rewardsLayout, "Number of licks for water", 2, step=1)
        self.waterDispTime = SpinBox(rewardsLayout, "Water dispense time", 200)
        self.waterTimeout = SpinBox(rewardsLayout, "Water timeout", 700)
        self.lickTimeout = SpinBox(rewardsLayout, "Lick timeout", 100)
        self.lickCountTimeout = SpinBox(rewardsLayout, "Lick Count timeout", 1000)

        # TODO: Uncomment after adding Reward Type functionality in .ino
        # rewards = [REWARD1, REWARD2]
        # for reward in rewards:
        #     self.rewardType.addItem(reward)
        # rewardsLayout.addRow(QLabel("Reward type"), self.rewardType)  

        rewardsGroupBox.setLayout(rewardsLayout)
        trialSettingsLayout.addRow(rewardsGroupBox)

        scrollArea.setWidget(trailSettingsGroupBox)
        layout.addWidget(scrollArea)

        # Form Button(s)
        self.submitBtn = QPushButton(text="Start")
        self.submitBtn.clicked.connect(self.validateFields)
        layout.addWidget(self.submitBtn)
    

    def validateFields(self):
        pattern = r"[a-zA-Z0-9]*_\d+"

        if self.mouseIdsField.text() == '' or self.pField.text() == '':
            QMessageBox.warning(self, "Warning", "Mouse ID and Primary Port fields must be set!")
        
        elif not re.match(pattern, self.mouseIdsField.text()):
            QMessageBox.warning(self, "Warning", "Mouse ID must follow the pattern: {character(s)}_{digit(s)}")
        
        elif self.minIti.value()>self.maxIti.value():
            QMessageBox.warning(self, "Warning", "Minimum iti duration cannot exceed Maximum iti duration")
        
        else:
            # Check that ports and cameras are able to connect
            try:
                comm=sc(self.pField.text(), 9600)
                comm.close()

                if self.s1Field.text():
                    comm = sc(self.s1Field.text(), 9600)
                    comm.close()

                self.checkCam(self.c1Field.text())
                self.checkCam(self.c2Field.text())

                # If everything connects, run script
                try:
                    self.submit()
                
                except Exception as e:
                    QMessageBox.critical(self, "Error", "Error when attempting to compile ino and run script: \n\n" + str(e))

            except serial.SerialException as e:
                QMessageBox.critical(self, "Error", "Issue connecting to port: \n\n" + str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error", "Issue connecting to camera(s): \n\n" + str(e))


    def checkCam(self, camInput):
        INTERFACE = "172.29.96.1"
        if camInput:
            cam = cc.e3VisionCamera(camInput)
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

    def submit(self):        
        mouseIds = f' -ids {self.mouseIdsField.text()}'
        p = f' -p {self.pField.text()}'
        s1 = f' -s1 {self.s1Field.text()}' if self.s1Field.text() else ''
        c1 = f' -c1 {self.c1Field.text()}' if self.c1Field.text() else ''
        c2 = f' -c2 {self.c2Field.text()}' if self.c2Field.text() else ''

        self.writeAndCompileIno()

        command = f"python -m Software.Serial_read.py_arduino_serial_camera{mouseIds}{p}{s1}{c1}{c2}"

        process_thread = ProcessThread(command)
        dialog = OutputDialog(process_thread, self)
        process_thread.output_updated.connect(dialog.update_output)
        process_thread.start()
        try:
            dialog.exec()
        except KeyboardInterrupt:
            print("KeyboardInterrupt detected.")


    def writeAndCompileIno(self):
            
        sketch_path = "Software/Rig/Rig.ino"

        output = subprocess.run(["arduino-cli", "board", "list", "--format", "json"], capture_output=True, text=True)
        boards_info = json.loads(output.stdout)

        # Loop through list of boards
        for board in boards_info:
            com = board['port']['label']
            fqbn = board['matching_boards'][0]['fqbn']


            # update parameters in .ino file
            self.updateParams(com)
            

            # Check if platform is installed. If not, install it
            platform = ":".join(fqbn.split(":")[:-1])

            output = subprocess.run(["arduino-cli", "core", "list", "--format", "json"], capture_output=True, text=True)
            cores_info = json.loads(output.stdout)
            platforms_list = [core["id"] for core in cores_info]

            if platform not in platforms_list:
                install_command = ["arduino-cli", "core", "install", platform]
                install_result = subprocess.run(install_command)
            

            # Compile and upload .ino file to rig

            compile_command = ["arduino-cli", "compile", "-b", fqbn, sketch_path]
            upload_command = ["arduino-cli", "upload", sketch_path, "-p", com, "-b", fqbn]
            
            compile_result = subprocess.run(compile_command)
            upload_result = subprocess.run(upload_command)

            if compile_result.returncode == 0 and upload_result.returncode == 0:
                print(f"Sketch compiled and uploaded successfully for {com}!\n")
            else:
                if compile_result.returncode != 0:
                    print(f"Sketch compilation failed for {com}. Errors:")
                    print(compile_result.stderr)
                else:
                    print(f"Sketch upload failed for {com}. Errors:")
                    print(upload_result.stderr)
                print("Running without updated parameters...\n")


    # Write to Rig.ino to update params
    def updateParams(self, com: str):

        isPrimary = com == self.pField.text()
        
        default_params_path = "Software/Rig/trial_default.h"
        params_path = "Software/Rig/trial.h"

        with open(default_params_path, "r") as file:
            param_content = file.read()

        params = {
            "NUMBER_OF_TRIALS": self.numTrials.value(), 
            "MIN_ITI": self.minIti.value(), 
            "MAX_ITI": self.maxIti.value(), 
            "TRIAL_DURATION": self.trialDuration.value(),
            "POST_LAST_TRIAL_INTERVAL": self.postTrialDuration.value(),
            "WATER_REWARD_AVAILABLE": self.waterEnabled.checkState() == Qt.CheckState.Checked,
            "USING_AUDITORY_CUES": self.audAirEnabled.checkState() == Qt.CheckState.Checked,
            "USING_AIR_PUFFS": self.airEnabled.checkState() == Qt.CheckState.Checked,
            "AIR_PUFF_DURATION": self.airPuffDuration.value(),
            "WATER_DISPENSE_ON_NUMBER_LICKS": self.waterDispNumLicks.value(),
            "WATER_DISPENSE_TIME": self.waterDispTime.value(),
            "WATER_TIMEOUT": self.waterTimeout.value(),
            "LICK_TIMEOUT": self.lickTimeout.value(),
            "LICK_COUNT_TIMEOUT": self.lickCountTimeout.value(),
            "IS_PRIMARY_RIG": isPrimary
        }

        for param, value in params.items():
            
            pattern = re.compile(rf"({re.escape(param)}\s*=\s*)(\".*?\"|\d+|true|false);")
            param_content = re.sub(pattern, rf"\g<1>{value};", param_content)
            param_content = param_content.replace("True", "true")
            param_content = param_content.replace("False", "false")

        with open(params_path, "w") as file:
            file.write(param_content)

        
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())