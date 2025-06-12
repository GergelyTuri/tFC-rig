from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QLineEdit, QSpinBox, QFormLayout, QLabel, QCheckBox, QComboBox
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
from datetime import datetime
import os, signal, subprocess
from .constants import START_STRING

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
            if self.process.stdout:
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


class OutputDialogPlot(QDialog):
    """
    QDialog window for displaying output of experiment process.

    Attributes:
        process_thread (QThread): Thread for the process.
    """
    def __init__(self, process_thread: ProcessThread, primary_m_id: str, secondary_m_id: str, parent=None):
        super().__init__(parent)
        
        self.process_thread = process_thread
        self.primary_mouse_id = primary_m_id
        self.secondary_mouse_id = secondary_m_id[1:]
        self.setWindowTitle("Output")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.resize(750, 650)

        # Output text
        self.output_text_edit = QTextEdit()
        self.output_text_edit.setReadOnly(True)
        layout.addWidget(self.output_text_edit)

        stop_button = QPushButton("Stop and collect data")
        stop_button.clicked.connect(self.stop)
        layout.addWidget(stop_button)

        # Live plot
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedSize(750, 400)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Number of Licks")
        self.ax.set_title("Licks Over Time")
        layout.addWidget(self.canvas)
        
        self.licks_data = pd.DataFrame(columns=["Time", "Licks"])
        self.licks_data_s = pd.DataFrame(columns=["Time", "Licks"]) if self.secondary_mouse_id else None

        self.started = False
        self.started_secondary = not self.secondary_mouse_id
        self.start_time = datetime.now()

        # Timer for updating the plot
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        """
        Update the live plot with the latest data.
        """
        if self.started and self.started_secondary: 
            self.update_licks(primary=True, licks = 0)
            if self.secondary_mouse_id:
                self.update_licks(primary=False, licks = 0)
            
        self.ax.clear()
        self.ax.grid(True)
        time_values = self.licks_data["Time"].to_numpy()
        licks_values = self.licks_data["Licks"].to_numpy()
        self.ax.plot(time_values, licks_values, marker='.', linestyle='-', label=self.primary_mouse_id)

        if self.secondary_mouse_id:
            time_values_secondary = self.licks_data_s["Time"].to_numpy()
            licks_values_secondary = self.licks_data_s["Licks"].to_numpy()
            self.ax.plot(time_values_secondary, licks_values_secondary, marker='.', linestyle='--', label=self.secondary_mouse_id)
            self.ax.legend()

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Lick rate (licks/s)")
        self.ax.set_title("Licks Over Time")
        self.canvas.draw()

    def update_output(self, output):
        """
        Update the output text edit by appending output.

        Args:
            output (str): Output to append to current output.
        """
        try:
            self.output_text_edit.append(output)
            
            if START_STRING in output:
                if self.primary_mouse_id in output:
                    self.started = True
                else:
                    self.started_secondary = True

                if self.started and self.started_secondary:
                    self.start_time = datetime.now()

            if "Lick" in output: 
                if self.primary_mouse_id in output:
                    self.update_licks(primary=True)
                else:
                    self.update_licks(primary=False)

        except KeyboardInterrupt:
            print("KeyboardInterrupt detected.")

    def update_licks(self, primary: bool, licks=1):
        """
        Update the number of licks.

        Args:
            licks (int): Number of licks to add.
        """
        if self.started and self.started_secondary:
            current_time = int((datetime.now() - self.start_time).total_seconds())  # Calculate elapsed time
            
            if primary:
                if current_time in self.licks_data["Time"].values:
                    self.licks_data.loc[self.licks_data["Time"] == current_time, "Licks"] += licks
                else:
                    new_row = pd.DataFrame({"Time": [current_time], "Licks": [licks]})
                    self.licks_data = pd.concat([self.licks_data, new_row], ignore_index=True)
            else:
                if current_time in self.licks_data_s["Time"].values:
                    self.licks_data_s.loc[self.licks_data_s["Time"] == current_time, "Licks"] += licks
                else:
                    new_row = pd.DataFrame({"Time": [current_time], "Licks": [licks]})
                    self.licks_data_s = pd.concat([self.licks_data_s, new_row], ignore_index=True)
        
    def stop(self):
        self.timer.stop()
        self.process_thread.stop_process()


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
        self.changed = False
        # self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)  # Disables arrow buttons
        self.setRange(min, max)
        self.setSingleStep(step)
        self.setValue(default)
        self.set_initial()
        self.valueChanged.connect(self.check_changes)
        layout.addRow(QLabel(text), self)
    
    def wheelEvent(self, event):                                # Disable scrolling
        event.ignore()
    
    def check_changes(self):
        self.changed = (self.value() != self.initial_value)

    def set_initial(self):
        self.initial_value = self.value()

class CheckBox(QCheckBox):
    """
    Subclass of QCheckBox.

    Attributes:
        layout (QFormLayout): Layout to add the check box to.
        text (str): Text label for the check box.
        checked (bool): initial value for check box.
    """
    def __init__(self, layout: QFormLayout, text: str, checked: bool=True):
        super().__init__(text)
        self.changed = False
        if checked:
            self.setCheckState(Qt.CheckState.Checked)
        else:
            self.setCheckState(Qt.CheckState.Unchecked)
        self.set_initial()
        self.stateChanged.connect(self.check_changes)
        layout.addRow(self)

    def check_changes(self):
        self.changed = (self.checkState() != self.initial_value)

    def set_initial(self):
        self.initial_value = self.checkState()

class ComboBox(QComboBox):
    def __init__(self, layout: QFormLayout, text: str, items, default = None):
        super().__init__()
        for item in items:
            self.addItem(item)
        if default:
            self.setCurrentText(default)
        layout.addRow(QLabel(text), self)
        
    def wheelEvent(self, event):                                # Disable scrolling
        event.ignore()

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
