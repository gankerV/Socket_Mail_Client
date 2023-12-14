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
folder_path = "C:/Users/XANH/Downloads/Socket_Mail_Client/Socket_Mail_Client/Folder/"
letters = [string.digits, string.ascii_letters]
stop_thread = False

C = Config()


class ParserEmail:
    def __init__(self):
        self.From = None
        self.To = None
        self.Subject = None
        self.Content = None
        self.msg = None

    def parse(self, lines):
        self.msg = BytesParser(policy=policy.default).parsebytes(lines)

        self.From = self.msg.get("From")
        start_index = self.From.find("<") + 1
        end_index = self.From.find(">")
        self.From = self.From[start_index:end_index]

        self.To = self.msg.get("To")
        self.Subject = self.msg.get("Subject")
        self.Content = self.get_email_content()

    def get_email_content(self):
        if self.msg.is_multipart():
            content_parts = []

            for part in self.msg.iter_parts():
                content_type = part.get_content_type()

                if content_type == "text/plain" or content_type == "text/html":
                    content_parts.append(part.get_payload(decode=True).decode("utf-8"))

            return "\n".join(content_parts)
        else:
            return self.msg.get_payload(decode=True).decode("utf-8")


class MailReceiver:
    POP3_PORT = 3335

    @staticmethod
    def folderCreater():
        for folder in C.folders:
            if not os.path.exists(os.path.join(folder_path, folder[:-1])):
                os.makedirs(os.path.join(folder_path, folder[:-1]))

    def getSenderEmailId(response):
        lines = response.splitlines()[1:-1]
        num_ids = [line.split(" ")[0] for line in lines]
        second_part = [line.split(" ")[1] for line in lines]
        email_ids = [element.split(".")[0] for element in second_part]

        return num_ids, email_ids

    def checkImportantMail(email):
        for keyword in C.important_filter:
            if keyword in email.Subject:
                return True

        return False

    def checkWorkMail(email):
        for keyword in C.work_filter:
            if keyword.encode("utf-8") in email.Content:
                return True

        return False

    def checkSpamMail(email):
        for keyword in C.spam_filter:
            if keyword in email.Subject:
                return True

            if keyword.encode("utf-8") in email.Content:
                return True

        return False

    def mailFilter(email):
        if email.From in C.project_filter:
            return "Project/"
        elif MailReceiver.checkImportantMail(email):
            return "Important/"
        elif MailReceiver.checkWorkMail(email):
            return "Work/"
        elif MailReceiver.checkSpamMail(email):
            return "Spam/"
        else:
            return "Inbox/"

    def header_footerRemover(data):
        index = data.find("\n")
        return data[index + 1 : -7]

    def headerRemover(data):
        index = data.find("\n")
        return data[index + 1 :]

    def footerRemover(data):
        return data[:-7]

    def checkExistFile(folder_path, mail_id):
        file_names = []  # danh sách lưu các file đã tải, chỉ dùng trong hàm này
        for foldername, subfolders, filenames in os.walk(folder_path):
            for file_name in filenames:
                # lấy id của mỗi file đã được tải về
                start_index = file_name.find(")") + 2
                end_index = file_name.find("_")
                file_name_id = file_name[start_index:end_index]
                if file_name_id == str(mail_id):
                    return True

        return False

    def checkEndMail(data, boundary):
        if data.endswith(f"{boundary}--\r\n.\r\n"):
            return True
        elif data.endswith(".\r\n"):
            return True
        return False

    @staticmethod
    def mailLoader():
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.connect((C.HOST, MailReceiver.POP3_PORT))
        response = c.recv(1024).decode()

        c.sendall(f"CAPA\r\n".encode())
        response = c.recv(1024).decode()

        c.sendall(f"USER {C.mail_server}\r\n".encode())
        response = c.recv(1024).decode()

        c.sendall(f"PASS {C.password}\r\n".encode())
        response = c.recv(1024).decode()

        c.sendall(f"STAT\r\n".encode())
        response = c.recv(1024).decode()

        c.sendall(f"LIST\r\n".encode())
        response = c.recv(1024).decode()

        c.sendall(f"UIDL\r\n".encode())
        response = c.recv(1024).decode()

        num_ids, mail_ids = MailReceiver.getSenderEmailId(response)

        for num_id in num_ids:
            num_id = int(num_id)
            boundary = ""
            times = 1

            if MailReceiver.checkExistFile(folder_path, mail_ids[num_id - 1]):
                continue

            c.sendall(f"RETR {num_id}\r\n".encode())

            response_file_name = str(mail_ids[num_id - 1]) + ".msg"
            response_file_path = os.path.join(folder_path, "Inbox/", response_file_name)

            with open(response_file_path, "wb") as file:
                while True:
                    data = c.recv(1048576)

                    if times == 1:
                        index = data.decode().find("------------")
                        boundary = data.decode()[index : index + 36]
                        if MailReceiver.checkEndMail(data.decode(), boundary):
                            file.write(
                                MailReceiver.header_footerRemover(data.decode()).encode(
                                    "utf-8"
                                )
                            )
                            break
                        else:
                            file.write(
                                MailReceiver.headerRemover(data.decode()).encode(
                                    "utf-8"
                                )
                            )
                    else:
                        if MailReceiver.checkEndMail(data.decode(), boundary):
                            file.write(
                                MailReceiver.footerRemover(data.decode()).encode(
                                    "utf-8"
                                )
                            )
                            break
                        else:
                            file.write(data.decode().encode("utf-8"))

                    times = times + 1

            with open(response_file_path, "rb") as file:
                email_data = file.read()

            email = ParserEmail()
            email.parse(email_data)
            folder = MailReceiver.mailFilter(email)

            sender_name = email.From

            file_name = (
                "(chưa đọc)"
                + " "
                + str(mail_ids[num_id - 1])
                + "_"
                + str(sender_name)
                + ".msg"
            )

            des_file_path = folder_path + folder + file_name
            os.rename(response_file_path, des_file_path)

        c.sendall(f"QUIT\r\n".encode())

    @staticmethod
    def mailAutoLoader():
        while not stop_thread:
            MailReceiver.mailLoader()
            time.sleep(C.auto_load_time)

    @staticmethod
    def getMailsFromFolder(folder):
        index = 1

        for file_name in os.listdir(os.path.join(folder_path, folder)):
            if os.path.isfile(os.path.join(folder_path, folder, file_name)):
                print(index, ". ", file_name)

            index = index + 1

    @staticmethod
    def checkValidMailNum(folder_choose, file_choose):
        count = 0

        for file_name in os.listdir(
            os.path.join(folder_path, C.folders[folder_choose - 1])
        ):
            count = count + 1

        if file_choose > count:
            return False
        return True

    def updateReadFile(folder_choose, file_choose):
        file_index = 1

        for file_name in os.listdir(
            os.path.join(folder_path, C.folders[folder_choose - 1])
        ):
            if file_index == file_choose:
                index = file_name.find(") ")
                new_file_name = "(đã đọc)" + " " + file_name[index + 2 :]
                new_file_path = (
                    folder_path + C.folders[folder_choose - 1] + new_file_name
                )
                os.rename(
                    os.path.join(folder_path, C.folders[folder_choose - 1], file_name),
                    new_file_path,
                )

            file_index = file_index + 1

    @staticmethod
    def readEmail(folder_choose, file_choose):
        file_index = 1

        for file_name in os.listdir(
            os.path.join(folder_path, C.folders[folder_choose - 1])
        ):
            if file_index == file_choose:
                with open(
                    os.path.join(folder_path, C.folders[folder_choose - 1], file_name),
                    "rb",
                ) as file:
                    email_data = file.read()
                    email = ParserEmail()
                    email.parse(email_data)
                    print(email.Content)

                    break

            file_index = file_index + 1

    def is_base64(s):
        try:
            decoded_data = base64.b64decode(s)
            return True
        except base64.binascii.Error as e:
            return False

    def checkFileInMail(folder_choose, file_choose):
        file_index = 1

        for file_name in os.listdir(
            os.path.join(folder_path, C.folders[folder_choose - 1])
        ):
            if file_index == file_choose:
                with open(
                    os.path.join(folder_path, C.folders[folder_choose - 1], file_name),
                    "r",
                ) as file:
                    line = file.readline()
                    if line.split(":")[0] == "Content-Type":
                        return True
                    return False

            file_index = file_index + 1

    def downFile(folder_link, folder_choose, file_choose):
        file_index = 1
        for file_name in os.listdir(
            os.path.join(folder_path, C.folders[folder_choose - 1])
        ):
            if file_index == file_choose:
                with open(
                    os.path.join(folder_path, C.folders[folder_choose - 1], file_name),
                    "r",
                ) as read_file:
                    boundary = read_file.readline().split('"')[1]

                    stop = False
                    while True:
                        if stop:
                            break
                        line = ""
                        while line.split(":")[0] != "Content-Disposition":
                            line = read_file.readline()

                        attached_file_name = line.split('"')[1]

                        read_file.readline()
                        read_file.readline()

                        with open(
                            os.path.join(folder_link, attached_file_name), "wb"
                        ) as write_file:
                            line = read_file.readline()
                            while not line in [f"--{boundary}\n", f"--{boundary}"]:
                                if line != "\n":
                                    while not MailReceiver.is_base64(line[:-1]):
                                        if line.endswith("\n"):
                                            line = line[:-1] + "=\n"
                                        else:
                                            line = line + "=\n"

                                    write_file.write(base64.b64decode(line))

                                line = read_file.readline()

                                if line == f"--{boundary}":
                                    stop = True
                                    break

                break

            file_index = file_index + 1

    @staticmethod
    def mailReceiver():
        folder_choose = 0
        file_choose = -1

        while True:
            print("\nĐây là danh sách các folder trong mailbox của bạn:")
            print("1. Inbox")
            print("2. Project")
            print("3. Important")
            print("4. Work")
            print("5. Spam")
            folder_choose = input(
                "Bạn muốn xem email trong folder nào (Nhấn enter để thoát ra ngoài): "
            )

            if folder_choose == "":
                quit()

            if int(folder_choose) >= 1 and int(folder_choose) <= 5:
                break

        folder_choose = int(folder_choose)

        print("")

        while True:
            while True:
                print(
                    f"Đây là danh sách email trong {C.folders[folder_choose - 1][:-1]} folder"
                )
                MailReceiver.getMailsFromFolder(C.folders[folder_choose - 1])

                print("")

                file_choose = input(
                    "Bạn muốn đọc Email thứ mấy (Nhấn enter để thoát ra ngoài, nhấn 0 để xem lại danh sách mail): "
                )

                if file_choose == "":
                    quit()

                if file_choose == "0":
                    MailReceiver.mailReceiver()
                    quit()

                file_choose = int(file_choose)

                if not MailReceiver.checkValidMailNum(folder_choose, file_choose):
                    print(
                        f"{C.folders[folder_choose - 1]} folder không có file thứ ",
                        file_choose,
                    )
                    continue
                else:
                    break

            print(f"Nội dung của mail thứ {str(file_choose)}:")
            MailReceiver.readEmail(folder_choose, file_choose)

            if MailReceiver.checkFileInMail(folder_choose, file_choose):
                save = int(
                    input(
                        "Trong email này có file đính kèm, bạn có muốn lưu không? (1. có, 2. không): "
                    )
                )

                if save == 1:
                    folder_link = input("Cho biết đường dẫn đến thư mục bạn muốn lưu: ")
                    MailReceiver.downFile(folder_link, folder_choose, file_choose)

            MailReceiver.updateReadFile(folder_choose, file_choose)