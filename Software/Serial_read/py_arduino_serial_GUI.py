"""
Python script to launch GUI for experiments. Takes in user arguments and runs py_arduino_serial_camera.py

This script reads data from inputs in PyQt GUI, then calls a subprocess to call camera script.
User also has the option to edit trial parameters. These trial parameter fields are pre-filled with default values.
It then feeds the output in a output dialog window. User may choose to end experiment early and collect data.

Usage:
    python -m Software.Serial_read.py_arduino_serial_GUI
    
"""

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QSpinBox, QAbstractSpinBox, QFormLayout, QGroupBox, QMessageBox, QTextEdit, QDialog, QCheckBox, QScrollArea, QComboBox
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from ..camera_control import camera_class as cc
from .serial_comm import SerialComm as sc
from .update_sketch import UpdateSketch
import serial, subprocess
import sys, os, signal
import re
import serial.tools.list_ports

REWARD1 = "Water"
REWARD2 = "5% Sugar Water"
DEBUG = False

class OutputDialog(QDialog):
    """
    QDialog window for displaying output of experiment process.

    Attributes:
        process_thread (QThread): Thread for the process.
    """
    def __init__(self, process_thread, parent=None):
        super().__init__(parent)
        
        self.process_thread = process_thread
        self.setWindowTitle("Output")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.resize(750, 300)

        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        layout.addWidget(self.output_text_edit)

        stop_button = QPushButton("Stop and collect data")
        stop_button.clicked.connect(self.process_thread.stop_process)
        layout.addWidget(stop_button)

    def update_output(self, output):
        """
        Update the output text edit by appending output.

        Args:
            output (str): Output to append to current output.
        """
        try:
            self.output_text_edit.append(output)
        except KeyboardInterrupt:
            print("KeyboardInterrupt detected.")

class ProcessThread(QThread):
    """
    Thread for running a subprocess.

    Attributes:
        output_updated (pyqtSignal): Signal emitted when output is updated.
        command (str): Command to run.
        process (subprocess.Popen): Process object.
    """

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
    """
    Subclass of QSpinBox with disabled scrolling.

    Attributes:
        layout (QFormLayout): Layout to add the spin box to.
        text (str): Text label for the spin box.
        default (int): Default value. Defaults to 1.
        step (int): Step size. Defaults to 10.
        min (int): Minimum value. Defaults to 1.
        max (int): Maximum value. Defaults to 1000000.
    """
    def __init__(self, layout: QFormLayout, text: str, default = 1, step = 10, min = 1, max=1000000):
        super().__init__()
        self.wheelEvent = lambda event: None  # Disables scrolling in boxes
        # spinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)  # Disables arrow buttons
        self.setRange(min, max)
        self.setSingleStep(step)
        self.setValue(default)
        layout.addRow(QLabel(text), self)

class CheckBox(QCheckBox):
    """
    Subclass of QCheckBox.

    Attributes:
        layout (QFormLayout): Layout to add the check box to.
        text (str): Text label for the check box.
    """
    def __init__(self, layout: QFormLayout, text: str, checked: bool):
        super().__init__(text)
        if checked:
            self.setCheckState(Qt.CheckState.Checked)
        else:
            self.setCheckState(Qt.CheckState.Unchecked)
        layout.addRow(self)

class LineEdit(QLineEdit):
    """
    Subclass of QLineEdit.

    Attributes:
        layout (QFormLayout): Layout to add the line edit to.
        text (str): Text label for the line edit.
    """
    def __init__(self, layout: QFormLayout, text: str):
        super().__init__()
        layout.addRow(QLabel(text), self)


class Window(QWidget):
    """
    Main window for the experiment GUI.
    """
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

        self.primary_mouse_id = LineEdit(formLayout, "Primary Mouse ID")
        self.primary_port = LineEdit(formLayout, "Primary Port")
        self.secondary_mouse_id = LineEdit(formLayout, "Secondary Mouse ID (Optional)")
        self.secondary_port = LineEdit(formLayout, "Secondary Port 1 (Optional)")
        self.cam_1 = LineEdit(formLayout, "Camera 1 (Optional)")
        self.cam_2 = LineEdit(formLayout, "Camera 2 (Optional)")

        formGroupBox.setLayout(formLayout)
        layout.addWidget(formGroupBox)


        # Trial Settings
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        
        trailSettingsGroupBox = QGroupBox("Trial Settings")
        trialSettingsLayout = QFormLayout()

        self.num_trials = SpinBox(trialSettingsLayout, "Number of trials", 6, step=1, min=1, max=6)
        self.is_training = CheckBox(
            layout=trialSettingsLayout,
            text="Is training session?",
            checked=False,
        )
        self.min_iti = SpinBox(trialSettingsLayout, "Minimum iti duration", 60000, step=1000)
        self.max_iti = SpinBox(trialSettingsLayout, "Maximum iti duration", 300000, step=1000)
        self.trial_duration = SpinBox(trialSettingsLayout, "Trial duration", 50000, step=1000)
        self.post_trial_duration = SpinBox(trialSettingsLayout, "Post-last trial duration", 60000, step=1000)

        trailSettingsGroupBox.setLayout(trialSettingsLayout)
        
        # Rewards Settings
        rewardsGroupBox = QGroupBox("Water Reward Settings")
        rewardsLayout = QFormLayout()
        
        self.water_enabled = CheckBox(rewardsLayout, "Water Rewards enabled")
        self.aud_air_enabled = CheckBox(rewardsLayout, "Auditory Cues and Air Puffs enabled")
        self.air_enabled = CheckBox(rewardsLayout, "Air Puffs enabled")
        self.reward_type = QComboBox()
        self.air_puff_duration = SpinBox(rewardsLayout, "Air Puff duration", 200)
        self.air_puff_start_time = SpinBox(rewardsLayout, "Air Puff start time", 45000, step=1000)
        self.auditory_start = SpinBox(rewardsLayout, "Auditory start", 15000, step=1000)
        self.auditory_stop = SpinBox(rewardsLayout, "Auditory stop", 35000, step=1000)
        self.water_disp_num_licks = SpinBox(rewardsLayout, "Number of licks for water", 2, step=1)
        self.water_disp_time = SpinBox(rewardsLayout, "Water dispense time", 200)
        self.water_timeout = SpinBox(rewardsLayout, "Water timeout", 700)
        self.lick_timeout = SpinBox(rewardsLayout, "Lick timeout", 100)
        self.lick_count_timeout = SpinBox(rewardsLayout, "Lick Count timeout", 1000)

        # TODO: Uncomment after adding Reward Type functionality in .ino
        # rewards = [REWARD1, REWARD2]
        # for reward in rewards:
        #     self.reward_type.addItem(reward)
        # rewardsLayout.addRow(QLabel("Reward type"), self.reward_type)  

        rewardsGroupBox.setLayout(rewardsLayout)
        trialSettingsLayout.addRow(rewardsGroupBox)

        scrollArea.setWidget(trailSettingsGroupBox)
        layout.addWidget(scrollArea)

        # Form Button(s)
        self.submitBtn = QPushButton(text="Start")
        self.submitBtn.clicked.connect(self.validateFields)
        layout.addWidget(self.submitBtn)
    

    def validateFields(self):
        """
        Validate input fields before starting the experiment.
        """
        pattern = r"^[a-zA-Z0-9]+_\d+$"

        if self.primary_mouse_id.text() == '' or self.primary_port.text() == '':
            QMessageBox.warning(self, "Warning", "Mouse ID and Primary Port fields must be set!")
        
        elif not re.match(pattern, self.primary_mouse_id.text()) or (self.secondary_mouse_id.text() and not re.match(pattern, self.secondary_mouse_id.text())):
            QMessageBox.warning(self, "Warning", "Mouse IDs must follow the pattern: {character(s)}_{digit(s)}")

        elif (self.secondary_mouse_id.text() and not self.secondary_port.text()) or (self.secondary_port.text() and not self.secondary_mouse_id.text()):
            QMessageBox.warning(self, "Warning", "Number of Mouse IDs must match number of Ports")

        elif self.min_iti.value()>self.max_iti.value():
            QMessageBox.warning(self, "Warning", "Minimum iti duration cannot exceed Maximum iti duration")
        
        elif self.water_disp_time.value()>=self.water_timeout.value():
            QMessageBox.warning(self, "Warning", "Water timeout should be greater than water dispense time")

        elif self.lick_timeout.value()>=self.lick_count_timeout.value():
            QMessageBox.warning(self, "Warning", "Lick count timeout should be greater than lick timeout")

        elif self.auditory_start.value()>=self.auditory_stop.value():
            QMessageBox.warning(self, "Warning", "Auditory stop should be greater than auditory start")
        
        elif self.auditory_stop.value()>=self.air_puff_start_time.value():
            QMessageBox.warning(self, "Warning", "Airpuff Start Time should be greater than auditory stop")

        elif self.trial_duration.value()<self.air_puff_start_time.value()+self.air_puff_duration.value():
            QMessageBox.warning(self, "Warning", "Trial duration needs to be greater than or equal to Airpuff Start Time plus Airpuff Duration")

        else:
            # Check that ports and cameras are able to connect
            try:
                comm=sc(self.primary_port.text(), 9600)
                comm.close()

                if self.secondary_port.text():
                    comm = sc(self.secondary_port.text(), 9600)
                    comm.close()

                cc.checkCam(self.cam_1.text())
                cc.checkCam(self.cam_2.text())

                # If everything connects, run script
                self.submit()

            except serial.SerialException as e:
                QMessageBox.critical(self, "Error", "Issue connecting to port: \n\n" + str(e))
            except Exception as e:
                QMessageBox.critical(self, "Error: ", str(e))


    def submit(self):    
        """
        Updates the sketch with new trial parameters
        Then starts the experiment by calling subprocess of experiment script.
        """    
        p_mouse_id = self.primary_mouse_id.text()
        s_mouse_id = f',{self.secondary_mouse_id.text()}' if self.secondary_mouse_id.text() else ''
        p = f' -p {self.primary_port.text()}'
        s1 = f' -s1 {self.secondary_port.text()}' if self.secondary_port.text() else ''
        c1 = f' -c1 {self.cam_1.text()}' if self.cam_1.text() else ''
        c2 = f' -c2 {self.cam_2.text()}' if self.cam_2.text() else ''

        params = self.get_ino_params()
        updater = UpdateSketch(params, self.primary_port.text())
        updater_out = updater.write_and_compile_ino()

        command = f"python -m Software.Serial_read.py_arduino_serial_camera -ids {p_mouse_id}{s_mouse_id}{p}{s1}{c1}{c2}"
        print(command)
        process_thread = ProcessThread(command)
        dialog = OutputDialog(process_thread, self)
        for out in updater_out: dialog.update_output(out)
        process_thread.output_updated.connect(dialog.update_output)
        process_thread.start()
        try:
            dialog.exec()
        except KeyboardInterrupt:
            print("KeyboardInterrupt detected.")


    def get_ino_params(self):
        """
        Get parameters for the .ino file. Check trial.h for more info on these parameters.

        Returns:
            dict: Dictionary containing parameters.
        """
        params = {
            "NUMBER_OF_TRIALS": self.num_trials.value(),
            "IS_TRAINING": self.is_training.checkState() == Qt.CheckState.Checked,
            "MIN_ITI": self.min_iti.value(), 
            "MAX_ITI": self.max_iti.value(), 
            "TRIAL_DURATION": self.trial_duration.value(),
            "POST_LAST_TRIAL_INTERVAL": self.post_trial_duration.value(),
            "WATER_REWARD_AVAILABLE": self.water_enabled.checkState() == Qt.CheckState.Checked,
            "USING_AUDITORY_CUES": self.aud_air_enabled.checkState() == Qt.CheckState.Checked,
            "USING_AIR_PUFFS": self.air_enabled.checkState() == Qt.CheckState.Checked,
            "AIR_PUFF_DURATION": self.air_puff_duration.value(),
            "WATER_DISPENSE_ON_NUMBER_LICKS": self.water_disp_num_licks.value(),
            "WATER_DISPENSE_TIME": self.water_disp_time.value(),
            "WATER_TIMEOUT": self.water_timeout.value(),
            "LICK_TIMEOUT": self.lick_timeout.value(),
            "LICK_COUNT_TIMEOUT": self.lick_count_timeout.value()
        }
        return params
        
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())