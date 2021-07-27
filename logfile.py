import os
from posixpath import split
import zipfile
import re
import csv
import json
from datetime import datetime

directory = "KIBO_RPC_Log_File"
Extract_to = "Unzip"
log_file = "adb.log"
json_file = "result.json"
csv_file = "kibo_log.csv"

def fn_str_time(time):
    time_str = time.split()
    return_time = int(time_str[0] + time_str[1])
    return int(time_str[1])

# create Unzip folder
unzip_exits = os.path.isdir(Extract_to) 
if (unzip_exits == False):
    os.mkdir(Extract_to)
    
# extracting all the files
print('Extracting all the files now...')
for filename in os.listdir(directory):
    file_name = os.path.join(directory, filename)

    with zipfile.ZipFile(file_name, 'r') as zip:
        extract_dir = os.path.join(Extract_to, filename)

        # printing all the contents of the zip file 
        print("Extracting " + filename)
        # zip.printdir()

        unzipped = os.path.isdir(extract_dir)
        if (unzipped == False):
            os.mkdir(extract_dir)
            zip.extractall(extract_dir)
print('Unzipping Done!')

with open(csv_file, mode='w') as write_file:
    fieldnames = ['FileName', 'Memo', 'Pattern', 'Qr_Position', 'Qr_Content', 
                    'Ar_Corner', 'Laser_move', 'Start_Time', 'Qr_Time', 'Ar_Time', 
                    'Total_Time', 'Laser_off_X', 'Laser_off_Y','Class']
    writer = csv.DictWriter(write_file, fieldnames=fieldnames)
    writer.writeheader()

    # get info from dir
    for dir_name in os.listdir(Extract_to):
        # for file_name in os.listdir(os.path.join(Extract_to, dir_name)):
        memo = None
        PosQR = None
        QrContent = None
        get_pattern = None
        ArContent = []
        Laser_move = None
        Js_Report = None
        Js_Illegal = None
        Js_Qr = None
        Js_Ar = None
        Js_Time = None
        
        print(file_name)
        # Process log file

        print(f"Processing log file in {dir_name}")

        file_name_dir = os.path.join(Extract_to, dir_name, log_file)

        with open(file_name_dir, 'rb') as file_object:
            for line in file_object:
                words = line.split()

                if (words[2] == b'D/Start[MEMO]:'):
                    memo = words[4].decode()
                
                elif (words[2] == b'D/QR[status]:('):
                    line_qr = line.decode()
                    words_qr = line_qr.split()
                    check_content = re.findall("\A{\"p\"", words_qr[4])

                    if (words[4] == b'Position:'):
                        PosQR = f"{words[5]} {words[5]} {words[5]}" 

                    elif (check_content):
                        QrContent = words_qr[4]
                        get_pattern = re.findall("[0-9]", words_qr[4])[0]

                elif(words[2] == 'D/QR[content]:'):
                    QrContent = words[4].encode()

                elif (words[2] == b'D/AR[status]:'):
                    line_ar = line.decode()
                    words_ar = line_ar.split()
                    check_ar_corner = re.findall("[\[][0-9]", words_ar[5])
                    
                    if (check_ar_corner):
                        ArContent.append(words_ar[5] + words_ar[6] + words_ar[7] + words_ar[8] + words_ar[9] + words_ar[10] + words_ar[11] + words_ar[12])
                
                elif (words[2] == b'D/Laser[Status]:('):
                    if (words[4] == b'MoveTo:'):
                        line_laser = line.decode()
                        words_laser = line_laser.split()

                        Laser_move = words_laser[5:]


        print(f"Processing result file in {dir_name}")

        file_name_dir = os.path.join(Extract_to, dir_name, json_file)

        with open(file_name_dir, 'rb') as file_object:
            pop_data = json.load(file_object)

        Js_Report = pop_data['Report']
        Js_Illegal = pop_data['Illegal']

        if (pop_data['QR'] == {}):
            writer.writerow({
                            'FileName' : dir_name, 
                            'Memo' : memo,
                            'Class' : 'D'
                            })

        elif (pop_data['Approach'][0] == {}):
            Js_Qr = pop_data['QR']['0']
            Js_Time = pop_data['Mission Time']

            writer.writerow({
                            'FileName' : dir_name, 
                            'Memo' : memo,
                            'Pattern' : get_pattern, 
                            'Qr_Position' : PosQR, 
                            'Qr_Content' : QrContent, 
                            'Ar_Corner' : ArContent, 
                            'Laser_move' : Laser_move, 
                            'Qr_Time' : ((fn_str_time(Js_Qr['timestamp']) - fn_str_time(Js_Time['start'])) / 1e5), 
                            'Class' : 'C'
                            })

        else:
            Js_Qr = pop_data['QR']['0']
            Js_Ar = pop_data['Approach'][0]['0']
            Js_Time = pop_data['Mission Time']

            if (len(Js_Time) == 1):
                writer.writerow({
                            'FileName' : dir_name, 
                            'Memo' : memo,
                            'Pattern' : get_pattern, 
                            'Qr_Position' : PosQR, 
                            'Qr_Content' : QrContent, 
                            'Ar_Corner' : ArContent, 
                            'Laser_move' : Laser_move, 
                            'Qr_Time' : ((fn_str_time(Js_Qr['timestamp']) - fn_str_time(Js_Time['start'])) / 1e5), 
                            'Ar_Time' : ((fn_str_time(Js_Ar['timestamp']) - fn_str_time(Js_Time['start'])) / 1e5), 
                            'Laser_off_X' : Js_Ar['x'],
                            'Laser_off_Y' : Js_Ar['y'],
                            'Class' : 'B'
                            })

            elif (not Js_Ar['direction']):
                writer.writerow({
                            'FileName' : dir_name, 
                            'Memo' : memo,
                            'Pattern' : get_pattern, 
                            'Qr_Position' : PosQR, 
                            'Qr_Content' : QrContent, 
                            'Ar_Corner' : ArContent, 
                            'Laser_move' : Laser_move, 
                            'Qr_Time' : ((fn_str_time(Js_Qr['timestamp']) - fn_str_time(Js_Time['start'])) / 1e5), 
                            'Ar_Time' : ((fn_str_time(Js_Ar['timestamp']) - fn_str_time(Js_Time['start'])) / 1e5), 
                            'Total_Time': ((fn_str_time(Js_Time['finish']) - fn_str_time(Js_Time['start'])) / 1e5),
                            'Laser_off_X' : Js_Ar['x'],
                            'Laser_off_Y' : Js_Ar['y'],
                            'Class' : 'B'
                            })

            else:
                writer.writerow({
                                'FileName' : dir_name, 
                                'Memo' : memo,
                                'Pattern' : get_pattern, 
                                'Qr_Position' : PosQR, 
                                'Qr_Content' : QrContent, 
                                'Ar_Corner' : ArContent, 
                                'Laser_move' : Laser_move, 
                                'Qr_Time' : ((fn_str_time(Js_Qr['timestamp']) - fn_str_time(Js_Time['start'])) / 1e5), 
                                'Ar_Time' : ((fn_str_time(Js_Ar['timestamp']) - fn_str_time(Js_Time['start'])) / 1e5), 
                                'Total_Time': ((fn_str_time(Js_Time['finish']) - fn_str_time(Js_Time['start'])) / 1e5),
                                'Laser_off_X' : Js_Ar['x'],
                                'Laser_off_Y' : Js_Ar['y'],
                                'Class' : 'A'
                                })

print(f"All DONE! Everything save at {csv_file}")
