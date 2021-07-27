import os
from posixpath import split
import zipfile
import re
import csv

directory = "KIBO_RPC_Log_File"
log_file = "adb.log"
json_file = "result.json"
csv_file = "kibo_log.csv"

with open(csv_file, mode='w') as write_file:
    fieldnames = ['FileName', 'Memo', 'Pattern', 'Qr_Position', 'Qr_Content', 'Ar_Corner', 'Laser_move', 'Start_Time', 'Qr_Time', 'Ar_Time', 'Total_Time']
    writer = csv.DictWriter(write_file, fieldnames=fieldnames)
    writer.writeheader()

    # get info from dir
    for dir_name in os.listdir(directory):
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

        # Process log file

        print(f"Processing log file in {dir_name}")

        file_name_dir = os.path.join(directory, dir_name)

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

        writer.writerow({
                        'FileName' : dir_name, 
                        'Memo' : memo,
                        'Pattern' : get_pattern, 
                        'Qr_Position' : PosQR, 
                        'Qr_Content' : QrContent, 
                        'Ar_Corner' : ArContent, 
                        'Laser_move' : Laser_move
                        })