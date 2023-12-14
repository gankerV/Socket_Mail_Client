import xml.etree.ElementTree as ET

xml_file_path = "Config.xml"


class Config:
    def __init__(self):
        self.xml_file_path = xml_file_path
        self.tree = ET.parse(self.xml_file_path)
        self.root = self.tree.getroot()

        # read  infor general
        self.username = self.root.find(".//General/Username").text
        start_index = self.username.find("<") + 1
        end_index = self.username.find(">")
        self.mail_server = self.username[start_index:end_index]
        self.password = self.root.find(".//General/Password").text
        self.HOST = self.root.find(".//General/MailServer").text
        self.SMTP_PORT = int(self.root.find(".//General/SMTP").text)
        self.POP3_PORT = int(self.root.find(".//General/POP3").text)
        self.auto_load_time = int(self.root.find(".//General/Autoload").text)

        # read infor filter
        self.project_filter = [
            filter_elem.text
            for filter_elem in self.root.findall(
                './/Filters/Filter[ToFolder="Project"]/From'
            )
        ]
        self.important_filter = [
            filter_elem.text
            for filter_elem in self.root.findall(
                './/Filters/Filter[ToFolder="Important"]/Subject'
            )
        ]
        self.work_filter = [
            filter_elem.text
            for filter_elem in self.root.findall(
                './/Filters/Filter[ToFolder="Work"]/Content'
            )
        ]
        self.spam_filter = [
            filter_elem.text
            for filter_elem in self.root.findall(
                './/Filters/Filter[ToFolder="Spam"]/Spam'
            )
        ]

        # read list of file in folder
        self.folders = []
        for filter_element in self.root.findall(".//Filters/Filter"):
            to_folder_element = filter_element.find("ToFolder")
            if to_folder_element is not None:
                folder_name = to_folder_element.text
                if folder_name not in self.folders:
                    self.folders.append(folder_name + "/")
        self.folders.insert(0, "Inbox/")
