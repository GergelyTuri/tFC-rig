"""
Python script to launch GUI for experiments. Takes in user arguments and runs py_arduino_serial_camera.py

This script reads data from inputs in PyQt GUI, then calls a subprocess to call camera script.
User also has the option to edit trial parameters. These trial parameter fields are pre-filled with default values.
It then feeds the output in a output dialog window. User may choose to end experiment early and collect data.

Usage:
    python -m Software.Serial_read.py_arduino_serial_GUI
    
"""

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QFormLayout, QGroupBox, QMessageBox, QScrollArea, QComboBox, QGridLayout
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
from .constants import PARAMS_PATH, TRIAL_CLASSES
from ..camera_control import camera_class as cc
from .serial_comm import SerialComm as sc
from .update_sketch import UpdateSketch
from .utils import ComboBox, OutputDialogPlot, ProcessThread, SpinBox, CheckBox, LineEdit
import sys, serial, re


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

        self.number_of_trials = SpinBox(trialSettingsLayout, "Number of trials", 6, step=1, min=1, max=30)
        self.cs_plus_ratio = LineEdit(formLayout, "CS+ Ratio")
        self.is_training = CheckBox(
            layout=trialSettingsLayout,
            text="Is training session?",
            checked=False,
        )
        self.training_trials_are_rewarded = CheckBox(
            layout=trialSettingsLayout,
            text="Providing water reward (checked) or punishment (unchecked)?",
            checked=True,
        )
        # Trial Types
        self.trial_type_1 = ComboBox(trialSettingsLayout, 'Trial Type 1', TRIAL_CLASSES, TRIAL_CLASSES[0])
        self.trial_type_2 = ComboBox(trialSettingsLayout, 'Trial Type 2', TRIAL_CLASSES, TRIAL_CLASSES[1])
        self.min_iti = SpinBox(trialSettingsLayout, "Minimum iti duration", 60000, step=1000)
        self.max_iti = SpinBox(trialSettingsLayout, "Maximum iti duration", 300000, step=1000)
        self.trial_duration = SpinBox(trialSettingsLayout, "Trial duration", 50000, step=1000, max=2000000)
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
        found_an_error = False

        if self.primary_mouse_id.text() == '' or self.primary_port.text() == '':
            found_an_error = True
            QMessageBox.warning(self, "Warning", "Mouse ID and Primary Port fields must be set!")
        
        if not re.match(pattern, self.primary_mouse_id.text()) or (self.secondary_mouse_id.text() and not re.match(pattern, self.secondary_mouse_id.text())):
            found_an_error = True
            QMessageBox.warning(self, "Warning", "Mouse IDs must follow the pattern: {character(s)}_{digit(s)}")

        if (self.secondary_mouse_id.text() and not self.secondary_port.text()) or (self.secondary_port.text() and not self.secondary_mouse_id.text()):
            found_an_error = True
            QMessageBox.warning(self, "Warning", "Number of Mouse IDs must match number of Ports")

        if self.cs_plus_ratio.text() != "":
            found_an_error = True
            try:
                cs_plus_ratio = float(self.cs_plus_ratio.text())
                float(self.cs_plus_ratio.text())
            except (TypeError, ValueError):
                QMessageBox.warning(self, "Warning", f"Could not convert CS Plus Ratio to float. Given {cs_plus_ratio}")
            if cs_plus_ratio < 0.0 or cs_plus_ratio > 1.0:
                QMessageBox.warning(self, "Warning", f"CS Plus Ratio must be b/w 0, 1, not {cs_plus_ratio}")

        if self.min_iti.value()>self.max_iti.value():
            found_an_error = True
            QMessageBox.warning(self, "Warning", "Minimum iti duration cannot exceed Maximum iti duration")
        
        if self.water_disp_time.value()>=self.water_timeout.value():
            found_an_error = True
            QMessageBox.warning(self, "Warning", "Water timeout should be greater than water dispense time")

        if self.lick_timeout.value()>=self.lick_count_timeout.value():
            found_an_error = True
            QMessageBox.warning(self, "Warning", "Lick count timeout should be greater than lick timeout")

        if self.auditory_start.value()>=self.auditory_stop.value():
            found_an_error = True
            QMessageBox.warning(self, "Warning", "Auditory stop should be greater than auditory start")
        
        if self.auditory_stop.value()>=self.air_puff_start_time.value():
            found_an_error = True
            QMessageBox.warning(self, "Warning", "Airpuff Start Time should be greater than auditory stop")

        if self.trial_duration.value()<self.air_puff_start_time.value()+self.air_puff_duration.value():
            found_an_error = True
            QMessageBox.warning(self, "Warning", "Trial duration needs to be greater than or equal to Airpuff Start Time plus Airpuff Duration")

        # Check that ports and cameras are able to connect
        if not found_an_error:
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
                QMessageBox.critical(self, "Error", str(e))


    def submit(self):    
        """
        Starts the experiment by calling subprocess of experiment script.
        """    
        p_mouse_id = self.primary_mouse_id.text()
        s_mouse_id = f',{self.secondary_mouse_id.text()}' if self.secondary_mouse_id.text() else ''
        p = f' -p {self.primary_port.text()}'
        s1 = f' -s1 {self.secondary_port.text()}' if self.secondary_port.text() else ''
        c1 = f' -c1 {self.cam_1.text()}' if self.cam_1.text() else ''
        c2 = f' -c2 {self.cam_2.text()}' if self.cam_2.text() else ''

        command = f"python -m Software.Serial_read.py_arduino_serial_camera -ids {p_mouse_id}{s_mouse_id}{p}{s1}{c1}{c2}"
        process_thread = ProcessThread(command)
        dialog = OutputDialogPlot(process_thread, p_mouse_id, s_mouse_id, self)

        self.update_sketch(dialog)

        process_thread.output_updated.connect(dialog.update_output)
        process_thread.start()
        print(command)
        try:
            dialog.exec()
        except KeyboardInterrupt:
            print("KeyboardInterrupt detected.")

        
    def update_sketch(self, dialog: OutputDialogPlot):
        """
        Updates sketch if there are new trial parameters.
        """
        if self.params_has_changed():
            params = self.get_ino_params()
            ports = [self.primary_port.text()]
            if self.secondary_port.text(): ports.append(self.secondary_port.text())
            updater = UpdateSketch()
            updater_out = updater.write_and_compile_ino(params, self.primary_port.text(), ports)

            for out in updater_out: dialog.update_output(out)
            

    def params_has_changed(self):
        """
        Reads the header file and compares to GUI values to check if there are any param changes.

        Returns:
            Boolean indicating if there are any new changes.
        """

        with open(PARAMS_PATH, 'r') as file:
            content = file.read()

        pattern = r'const\s+(\w+\*?)\s+(\w+)(\[\])?\s*=\s*([^;]+);'
        header_fields = re.findall(pattern, content)
        header_params = {var_name: value for _, var_name, _, value in header_fields}

        gui_params = self.get_ino_params()

        for gui_field, gui_value in gui_params.items():
            if gui_field in header_params:
                header_value = header_params[gui_field]

                if isinstance(gui_value, bool):
                    header_value = header_value.lower() == 'true'
                elif isinstance(gui_value, str):
                    header_value = header_value[1:-1]
                else:
                    gui_type = type(gui_value)
                    header_value = gui_type(header_value)

                if gui_value != header_value:
                    return True
        return False

    def get_ino_params(self):
        """
        Get parameters for the .ino file. Check trial.h for more info on these parameters.

        Returns:
            dict: Dictionary containing parameters.
        """
        params = {
            "NUMBER_OF_TRIALS": self.number_of_trials.value(),
            "CS_PLUS_RATIO": self.cs_plus_ratio.currentText(),
            "IS_TRAINING": self.is_training.checkState() == Qt.CheckState.Checked,
            "TRAINING_TRIALS_ARE_REWARDED": self.training_trials_are_rewarded.checkState() == Qt.CheckState.Checked,
            "TRIAL_TYPE_1": self.trial_type_1.currentText(),
            "TRIAL_TYPE_2": self.trial_type_2.currentText(),
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