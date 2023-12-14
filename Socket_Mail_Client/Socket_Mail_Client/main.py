import Receive
from Receive import MailReceiver
from Send import MailSender

import threading


class MailManipulation:
    def chooseMenu():
        print("Choose Menu:")
        print("1. Sending email")
        print("2. Seeing list of received emails")
        print("3. Quit")

        choose = int(input("Choose: "))

        return choose

    def mailManupilation():
        while True:
            choose = MailManipulation.chooseMenu()

            if choose == 1:
                # Start menu for sender
                MailSender.mailSender()

            elif choose == 2:
                # Load emails from mailbox
                MailReceiver.mailLoader()

                # Start menu for receiver
                MailReceiver.mailReceiver()

            elif choose == 3:
                # Quit program
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
            Receive.stop_thread = True

        auto_load_mail_thread.join()


if __name__ == "__main__":
    MailManipulation.main()