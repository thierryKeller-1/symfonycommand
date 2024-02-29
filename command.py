import os
import sys
import json
import subprocess
import shlex
import time
import platform
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

LOG_PATH = f"{os.environ.get('LOG_FOLDER_PATH')}"
LOG_FILE_PATH = f"{LOG_PATH}/log.json"
SYMFONY_PROJECT_FOLDER_PATH = os.environ.get('SYMFONY_PROJECT_FOLDER_PATH')
COMMAND_PROJECT_FOLDER_PATH = os.environ.get('COMMAND_PROJECT_FOLDER_PATH')
START_DATE = os.environ.get('START_DATE')
END_DATE = os.environ.get('END_DATE')

if not START_DATE or not END_DATE:
    print('   ===> dates not defined in environment variable')
    sys.exit()


start_date = datetime.strptime(START_DATE, "%Y-%m-%d")
end_date = datetime.strptime(END_DATE, '%Y-%m-%d')

DATES = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').to_list()

print(DATES)

if DATES:
    print('dates are invalid')



class SymfonyCommand(object):

    def __init__(self, number_of_page:int=1, number_of_data:int=50000) -> None:
        self.number_of_page = number_of_page
        self.number_of_data = number_of_data
        self.log = {}

    def set_number_of_page(self, value:int) -> None:
        self.number_of_page = value + 1

    def set_number_of_data(self, value:int) -> None:
        self.number_of_data = value

    def create_log(self) -> None:
        global LOG_FILE_PATH
        log = {
            'last_date': 0, 
            'last_page_decomposed': 1, 
            'last_page_recovered': 1, 
            'number_of_page':self.number_of_page,
            'command_finished':[]
            }
        if not Path(LOG_PATH).exists():
            os.makedirs(LOG_PATH)
        if not Path(LOG_FILE_PATH).exists():
            with open(LOG_FILE_PATH, 'w') as openfile:
                openfile.write(json.dumps(log, indent=4))

    def load_log(self) -> None:
        global LOG_FILE_PATH
        if Path(LOG_FILE_PATH).exists():
            with open(LOG_FILE_PATH, 'r') as openfile:
                self.log = json.loads(openfile.read())
        else:
            print("   log file path not found or file does not exist   ")

    def set_log(self, log_value:dict) -> None:
        if Path(LOG_FILE_PATH).exists():
            with open(LOG_FILE_PATH, 'w') as openfile:
                openfile.write(json.dumps(log_value))
        self.load_log()

    def clear_log(self) -> None:
        global LOG_FILE_PATH
        if Path(LOG_FILE_PATH).exists():
            os.remove(LOG_FILE_PATH)
            print('   ==> log file cleared')
        else:
            print('   ===> log file not found')

    def setup(self):
        print('   ===> setup project')
        global COMMAND_PROJECT_FOLDER_PATH
        match(platform.system):
            case 'windows':
                process = subprocess.Popen(shlex.split(f"pip install -r {COMMAND_PROJECT_FOLDER_PATH}/requirements.txt"), stdout=subprocess.PIPE, shell=True)
                output, error = process.communicate()
                print(output)
            case 'linux':
                process = subprocess.Popen(shlex.split(f"python3 -m pip install -r {COMMAND_PROJECT_FOLDER_PATH}/requirements.txt"), stdout=subprocess.PIPE, shell=True)
                output, error = process.communicate()
                print(output)


    def run(self):
        global DATES

        print('   ===> process start')

        try:
            os.chdir(SYMFONY_PROJECT_FOLDER_PATH)
        except Exception as e:
            print(e)
            print('   Symfony project path not incorrect or not found  ')


        for k in range(self.log['last_date'], len(DATES)):
            if 'decompose' not in self.log['command_finished']:
                for i in range(self.log['last_page_decomposed'], self.log['number_of_page']):
                    date = DATES[self.log['last_date']]
                    print(f"   ===> decomposing {date} page {self.log['last_page_decomposed']}")
                    if self.log['last_page_decomposed'] == self.number_of_page - 1:
                        self.log['command_finished'].append('decompose')
                        self.set_log(self.log)
                        print("   ===> decomposition done ...")
                        break
                    while True:
                        command1 = f"app:decompose:booking {DATES[self.log['last_date']]} {self.log['last_page_decomposed']} {self.number_of_data}"
                        print(f"  ==> launching command {command1}")
                        process1 = subprocess.Popen(shlex.split(command1), stdout=subprocess.PIPE, shell=True)
                        output, error = process1.communicate()
                        print(output)
                        if 'decomposed' in output.decode('utf-8'):
                            print(f"   ===> decomposing {DATES[self.log['last_date']]} page {self.log['last_page_decomposed']} finished ")
                            break
                        else:
                            print("   ===> attemped decomposing failed ...")
                            time.sleep(1)
                            print("   ===> retrying ...")
                    current_page = self.log['last_page_decomposed']
                    self.log['last_page_decomposed'] = current_page + 1
                    self.set_log(self.log)
            elif 'recovered' not in self.log['command_finished']:
                for _ in range(self.log['last_page_recovered'], self.log['number_of_page']):
                    print(f"   ===> recovering {DATES[self.log['last_date']]} page {self.log['last_page_recovered']}")
                    if self.log['last_page_recovered'] == self.number_of_page - 1:
                        self.log['command_finished'].append('recovered')
                        self.set_log(self.log)
                        print("   ===> recovering done ...")
                        break
                    while True:
                        command2 = f"app:recovery:data booking {self.date} {self.log['last_page']} {self.number_of_data}"
                        print(f"  ==> launching command {command2}")
                        process2 = subprocess.Popen(shlex.split(command2), stdout=subprocess.PIPE, shell=True)
                        output, error = process2.communicate()
                        if 'recovered' in output.decode('utf-8'):
                            print(f"   ===> recovering {DATES[self.log['last_date']]} page {self.log['last_page_recovered']} finished ")
                            break
                        else:
                            print("   ===> attemped recovering failed ...")
                            time.sleep(1)
                            print("   ===> retrying ...")
                    current_page = self.log['last_page_recovered']
                    self.log['last_page_recovered'] = current_page + 1
                    self.set_log(self.log)
            else:
                print(f"  ===> date {self.log['last_date']} decomposed and recovered ...  ")
                self.log['last_date'] = k + 1
                self.log['last_page_decomposed'] = 1
                self.log['last_page_recovered'] = 1
                self.log['command_finished'] = []
                self.set_log(self.log)


            

                    



