import subprocess, json, re
from .constants import SKETCH_PATH, PARAMS_PATH

class UpdateSketch:
    def __init__(self):
        """
        Initialize UpdateSketch object with parameters and primary port.

        """
        self.out = []
        self.has_error = False
        

    def write_and_compile_ino(self, params: dict, primary_port: str, ports):
        """
        Write parameters to .ino file, compile, and upload it to the rig.

        Args:
            params (dict): Dictionary containing parameters.
            primary_port (str): Primary port for uploading sketches.

        """
        
        # Loop through list of boards
        try:
            output = subprocess.run(["arduino-cli", "board", "list", "--format", "json"], capture_output=True, text=True)
            boards_info = json.loads(output.stdout)
            # After updating arduino-cli use: boards_info['detected_ports']:
            for board in boards_info:
                com = board['port']['label']
                com = com.replace('/cu.', '/tty.')      # Needed for macOS
                if com not in ports:
                    continue
                fqbn = board['matching_boards'][0]['fqbn']

                # update parameters in .ino file
                params["IS_PRIMARY_RIG"] = com == primary_port
                self.update_params(params)
                
                # Check if platform is installed. If not, install it
                platform = ":".join(fqbn.split(":")[:-1])
                output = subprocess.run(["arduino-cli", "core", "list", "--format", "json"], capture_output=True, text=True)
                cores_info = json.loads(output.stdout)
                # TODO: After updating arduino-cli uses cores_info['platforms']
                if cores_info is None or platform not in [core["id"] for core in cores_info]:
                    install_command = ["arduino-cli", "core", "install", platform]
                    install_result = subprocess.run(install_command)
                
                # Compile and upload .ino file to rig
                compile_command = ["arduino-cli", "compile", "-b", fqbn, SKETCH_PATH]
                upload_command = ["arduino-cli", "upload", SKETCH_PATH, "-p", com, "-b", fqbn]
        
                compile_result = subprocess.run(compile_command, capture_output=True, text=True)
                upload_result = subprocess.run(upload_command, capture_output=True, text=True)

                if compile_result.returncode != 0:
                    self.out.append(f"Sketch compilation failed for {com}. Errors:")
                    self.out.append(compile_result.stderr)
                    self.has_error = True
                if upload_result.returncode != 0:
                    self.out.append(f"Sketch upload failed for {com}. Errors:")
                    self.out.append(upload_result.stderr)
                    self.has_error = True
                elif compile_result.returncode == 0 and upload_result.returncode == 0:
                    self.out.append(f"Sketch compiled and uploaded successfully for {com}!\n")
                    self.has_error = False

        except Exception as e:
            err_str = f'Error: {e}'
            self.out.append(err_str)
            self.has_error = True
            
        if self.has_error:
            self.out.append("Running without updated parameters...\n")

        print(self.out)
        return self.out


    def update_params(self, params: dict): 
        """
        Update parameters in the .ino file.
        """       
        try:
            with open(PARAMS_PATH, "r") as file:
                param_content = file.read()

            for param, value in params.items():
                if isinstance(value, str):
                    value = f"\"{value}\""  # Ensure the value is surrounded by double quotes
                elif isinstance(value, bool):
                    value = str(value).lower()  

                pattern = re.compile(rf"({re.escape(param)}(\[\])?\s*=\s*)(\".*?\"|\d+|true|false);")
                param_content = re.sub(pattern, rf"\g<1>{value};", param_content)

            with open(PARAMS_PATH, "w") as file:
                file.write(param_content)
                
        except Exception as e:
            self.out.append(f'Error: {e}')
            self.has_error = True
