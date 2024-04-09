import subprocess, json, re

class UpdateSketch:
    def __init__(self, params: dict, primary_port: str):
        """Set file paths"""
        self.sketch_path = "Software/Rig/Rig.ino"
        self.default_params_path = "Software/Rig/trial_default.h"
        self.params_path = "Software/Rig/trial.h"

        self.params = params
        self.primary = primary_port
        self.out = []
        self.has_error = False
        
    def write_and_compile_ino(self):
        output = subprocess.run(["arduino-cli", "board", "list", "--format", "json"], capture_output=True, text=True)
        boards_info = json.loads(output.stdout)

        # Loop through list of boards
        for board in boards_info:
            try:
                com = board['port']['label']
                fqbn = board['matching_boards'][0]['fqbn']

                # update parameters in .ino file
                self.params["IS_PRIMARY_RIG"] = com == self.primary
                self.update_params()
                
                # Check if platform is installed. If not, install it
                platform = ":".join(fqbn.split(":")[:-1])
                output = subprocess.run(["arduino-cli", "core", "list", "--format", "json"], capture_output=True, text=True)
                cores_info = json.loads(output.stdout)
                platforms_list = [core["id"] for core in cores_info]
                if platform not in platforms_list:
                    install_command = ["arduino-cli", "core", "install", platform]
                    install_result = subprocess.run(install_command)
                
                # Compile and upload .ino file to rig
                compile_command = ["arduino-cli", "compile", "-b", fqbn, self.sketch_path]
                upload_command = ["arduino-cli", "upload", self.sketch_path, "-p", com, "-b", fqbn]
        
                
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
                self.out.append('Error: ', e)
                self.has_error = True
            
            if self.has_error:
                self.out.append("Running without updated parameters...\n")

        print(self.out)
        return self.out


    # Write to Rig.ino to update params
    def update_params(self):        
        try:
            with open(self.default_params_path, "r") as file:
                param_content = file.read()

            for param, value in self.params.items():

                pattern = re.compile(rf"({re.escape(param)}\s*=\s*)(\".*?\"|\d+|true|false);")
                param_content = re.sub(pattern, rf"\g<1>{value};", param_content)
                param_content = param_content.replace("True", "true")
                param_content = param_content.replace("False", "false")

            with open(self.params_path, "w") as file:
                file.write(param_content)
                
        except Exception as e:
            self.out.append('Error: ', e)
            self.has_error = True
