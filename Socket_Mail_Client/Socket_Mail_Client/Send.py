import socket
import uuid
import os
import base64
from email.utils import formatdate
import time
import threading
import random
import string


import email
from email import policy
from email.parser import BytesParser


import email
from email import policy
from email.parser import BytesParser

from Config import Config


imageTypeList = ["png", "jpg", "jpeg", "gif"]
textTypeList = ["txt"]
applicationTypeList = ["pdf", "zip", "rar", "docx"]
fileTypeAll = [imageTypeList, textTypeList, applicationTypeList]
folder_path = "C:/Users/XANH/Source/Repos/Socket-Mail-Client/Socket Mail Client/Folder/"
letters = [string.digits, string.ascii_letters]
order_number = {
    1: "st",
    2: "nd",
    3: "rd",
}

C = Config()


class MailSender:
    SERVER_PORT = 2225

    def randomBoundary():
        boundary = "------------"
        for i in range(24):
            index = int(random.choice([0, 1]))
            boundary += random.choice(letters[index])

        return boundary

    def getFileType(filename):
        dot_index = filename.rfind(".")
        return filename[dot_index + 1 :]

    def connectToServer(TO_list, CC_list, BCC_list):
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((C.HOST, MailSender.SERVER_PORT))
        response = c.recv(1024).decode()

        c.sendall(f"EHLO [{C.HOST}]\r\n".encode())
        response = c.recv(1024).decode()

        c.sendall(f"MAIL FROM:<{C.mail_server}>\r\n".encode())
        response = c.recv(1024).decode()

        if TO_list != [""]:
            for i in range(len(TO_list)):
                c.sendall(f"RCPT TO:<{TO_list[i]}>\r\n".encode())
                response = c.recv(1024).decode()

        if CC_list != [""]:
            for i in range(len(CC_list)):
                c.sendall(f"RCPT TO:<{CC_list[i]}>\r\n".encode())
                response = c.recv(1024).decode()

        if BCC_list != [""]:
            for i in range(len(BCC_list)):
                c.sendall(f"RCPT TO:<{BCC_list[i]}>\r\n".encode())
                response = c.recv(1024).decode()

        c.sendall(f"DATA\r\n".encode())
        response = c.recv(1024).decode()

        return c

    def noFile_MailSender(TO_list, CC_list, BCC_list, subject, content):
        c = MailSender.connectToServer(TO_list, CC_list, BCC_list)

        email_data = f"Message-ID: <{str(uuid.uuid4())}@gmail.com>\r\n"
        email_data += f"Date: {formatdate(localtime=True)}\r\n"
        email_data += f"MIME-Version: 1.0\r\n"
        email_data += f"User-Agent: Mozilla Thunderbird\r\n"
        email_data += f"Content-Language: en-US\r\n"

        if TO_list == [""] and CC_list == [""] and BCC_list != [""]:
            email_data += f"To: undisclosed-recipients: ;\r"
        elif TO_list != [""] or CC_list != [""]:
            if TO_list != [""]:
                email_data += f"To: "
                for i in range(len(TO_list)):
                    if i > 0:
                        email_data += f", {TO_list[i]}"
                    else:
                        email_data += f"{TO_list[i]}"
            if CC_list != [""]:
                email_data += f"Cc: "
                for i in range(len(CC_list)):
                    if i > 0:
                        email_data += f", {CC_list[i]}"
                    else:
                        email_data += f"{CC_list[i]}"

        email_data += f"\nFrom: {C.username}\r\n"
        email_data += f"Subject: {subject}\r\n"
        email_data += f"Content-Type: text/plain; charset=UTF-8; format=flowed\r\n"
        email_data += f"Content-Transfer-Encoding: 7bit\r\n\n"

        for i in range(len(content)):
            content_lines = "\r\n".join(
                content[i][k : k + 72] for k in range(0, len(content[i]), 72)
            )
            email_data += f"{content_lines}\r\n\n"

        email_data += f".\r\n"

        c.sendall(email_data.encode())

    def file_MailSender(TO_list, CC_list, BCC_list, subject, content, attached_files):
        c = MailSender.connectToServer(TO_list, CC_list, BCC_list)

        boundary = MailSender.randomBoundary()

        email_data = f'Content-Type: multipart/mixed; boundary="{boundary}"\r\n'
        email_data += f"Message-ID: <{str(uuid.uuid4())}@gmail.com>\r\n"
        email_data += f"Date: {formatdate(localtime=True)}\r\n"
        email_data += f"MIME-Version: 1.0\r\n"
        email_data += f"User-Agent: Mozilla Thunderbird\r\n"
        email_data += f"Content-Language: en-US\r\n"

        if TO_list == [""] and CC_list == [""] and BCC_list != [""]:
            email_data += f"To: undisclosed-recipients: ;\r"
        elif TO_list != [""] or CC_list != [""]:
            if TO_list != [""]:
                email_data += f"To: "
                for i in range(len(TO_list)):
                    if i > 0:
                        email_data += f", {TO_list[i]}"
                    else:
                        email_data += f"{TO_list[i]}"
            if CC_list != [""]:
                email_data += f"Cc: "
                for i in range(len(CC_list)):
                    if i > 0:
                        email_data += f", {CC_list[i]}"
                    else:
                        email_data += f"{CC_list[i]}"

        email_data += f"\nFrom: {C.username}\r\n"
        email_data += f"Subject: {subject}\r\n\n"
        email_data += f"This is a multi-part message in MIME format.\r\n"
        email_data += f"--{boundary}\r\n"
        email_data += f"Content-Type: text/plain; charset=UTF-8; format=flowed\r\n"
        email_data += f"Content-Transfer-Encoding: 7bit\r\n\n"

        for i in range(len(content)):
            email_data += f"{content[i]}\r\n\n"

        for i in range(len(attached_files)):
            email_data += f"--{boundary}\r\n"
            fileType = MailSender.getFileType(attached_files[i])
            fileName = os.path.basename(attached_files[i])

            if fileType in fileTypeAll[0]:
                email_data += f'Content-Type: image/{fileType}; name="{fileName}"\r\n'
            elif fileType in fileTypeAll[1]:
                email_data += f"Content-Type: text/plain; charset=UTF-8;\r\n"
                email_data += f'name="{fileName}"\r\n'
            elif fileType in fileTypeAll[2]:
                email_data += f"Content-Type: application/"
                if fileType == "zip":
                    email_data += f'x-zip-compressed; name="{fileName}"\r\n'
                elif fileType == "rar":
                    email_data += f'x-compressed; name="{fileName}"\r\n'
                elif fileType == "pdf":
                    email_data += f'pdf; name="{fileName}"\r\n'
                elif fileType == "docx":
                    email_data += f"vnd.openxmlformats-officedocument.wordprocessingml.document; name={fileName}\r\n"

            email_data += f'Content-Disposition: attachment; filename="{fileName}"\r\n'
            email_data += f"Content-Transfer-Encoding: base64\r\n\n"

            if os.path.exists(attached_files[i]):
                with open(attached_files[i], "rb") as file:
                    file_content = file.read()
                    file_content_lines = "\r\n".join(
                        base64.b64encode(file_content).decode()[k : k + 72]
                        for k in range(
                            0, len(base64.b64encode(file_content).decode()), 72
                        )
                    )
                    email_data += f"{file_content_lines}\r\n"

        email_data += "\n"
        email_data += f"--{boundary}--\r\n.\r\n"

        c.sendall(email_data.encode())

    def enterAttachedFiles():
        attached_files = []
        out = False

        while not out:
            attached_file_size = 0
            attached_file_num = int(input("The number of attached file(s): "))

            for i in range(attached_file_num):
                if i <= 3:
                    attached_file_path = input(
                        f"The {i + 1}{order_number[i + 1]} attached file path: "
                    )
                else:
                    attached_file_path = input(f"The {i + 1}th attached file path: ")
                attached_file_size += os.path.getsize(attached_file_path)

                if attached_file_size <= 3000000:
                    attached_files.append(attached_file_path)
                else:
                    print(f"The size of {attached_file_num} file(s) is over 3 MB !")
                    print("Please enter again !")
                    break

                if i == attached_file_num - 1:
                    out = True

        return attached_files

    @staticmethod
    def mailSender():
        content = []

        print("Enter information (Press enter to skip):")
        TO_list = [str(x) for x in input("To: ").split(", ")]
        CC_list = [str(x) for x in input("CC: ").split(", ")]
        BCC_list = [str(x) for x in input("BCC: ").split(", ")]

        subject = input("Subject: ")
        line = input("Content: ")
        while line != ".":
            content.append(line)
            line = input()
        attached_file_check = int(input("Attaching file(s) ? (1. Yes, 2. No): "))

        if attached_file_check == 1:
            # Receive attached file(s) from sender
            attached_files = MailSender.enterAttachedFiles()

            # Send mail with attached file(s)
            MailSender.file_MailSender(
                TO_list, CC_list, BCC_list, subject, content, attached_files
            )

        elif attached_file_check == 2:
            # Send mail withou attached file(s)
            MailSender.noFile_MailSender(TO_list, CC_list, BCC_list, subject, content)

        print("\nMail successfully sent !\n")