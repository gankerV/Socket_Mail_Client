from Recieve import MailReceiver
from Send import MailSender
import time
import threading
import random
import string

stop_thread = False


class MailManipulation:
    def mailManupilation():
        while True:
            print("Vui lòng chọn Menu:")
            print("1. Để gửi mail")
            print("2. Để xem danh sách các email đã nhận")
            print("3. Thoát")

            choose = int(input("Bạn chọn: "))

            if choose == 1:
                attached_files = []
                content = []

                print(
                    "Đây là thông tin soạn email: (nếu không điền vui lòng nhấn enter để bỏ qua)"
                )
                TO_list = [str(x) for x in input("To: ").split(", ")]
                CC_list = [str(x) for x in input("CC: ").split(", ")]
                BCC_list = [str(x) for x in input("BCC: ").split(", ")]

                subject = input("Subject: ")
                line = input("Content: ")
                while line != ".":
                    content.append(line)
                    line = input()
                attached_file_check = int(input("Có gửi kèm file (1. có, 2. không): "))

                if attached_file_check == 1:
                    attached_file_num = int(input("Số lượng file muốn gửi: "))
                    for i in range(attached_file_num):
                        attached_file = input(f"Cho biết đường dẫn file thứ {i + 1}: ")
                        attached_files.append(attached_file)

                    # Gửi mail có đính kèm file
                    MailSender.file_MailSender(
                        TO_list, CC_list, BCC_list, subject, content, attached_files
                    )
                elif attached_file_check == 2:
                    # Gửi mail không đính kèm file
                    MailSender.noFile_MailSender(
                        TO_list, CC_list, BCC_list, subject, content
                    )

                print("\nĐã gửi email thành công\n")

            elif choose == 2:
                MailReceiver.mailLoader()

                MailReceiver.mailReceiver()

            elif choose == 3:
                quit()

    @staticmethod
    def main():
        global stop_thread

        MailReceiver.folderCreater()

        mail_manupilation_thread = threading.Thread(
            target=MailManipulation.mailManupilation
        )
        mail_manupilation_thread.start()

        auto_load_mail_thread = threading.Thread(target=MailReceiver.mailAutoLoader)
        auto_load_mail_thread.start()

        mail_manupilation_thread.join()

        if not mail_manupilation_thread.is_alive():
            stop_thread = True

        auto_load_mail_thread.join()


if __name__ == "__main__":
    MailManipulation.main()