# Internal libraries
import os
import csv
import configparser
import sys
import shutil

# External libraries
import boto3
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QFileDialog, QLineEdit

## Constants
# Route to the folder containing the configuration files
APPLICATION_PATH = os.path.dirname(__file__)
CONFIG_FOLDER = os.path.join(APPLICATION_PATH, 'configs')
CSV_TEMPLATE_PATH  = os.path.join(CONFIG_FOLDER, 'customers.csv')
TEMPLATE_FILE_PATH = os.path.join(CONFIG_FOLDER, 'email_template.html')
CONFIG_FILE_PATH = os.path.join(CONFIG_FOLDER, 'config.ini')

# Email subject
MAIL_SUBJECT = "Your Email Subject"
CC_EMAIL = []

# Text for GUI
WINDOW_TITLE_TEXT = "メール送信者"
DOWNLOAD_TEMPLATE_TEXT = "CSVテンプレートファイルをダウンロード"
DOWNLOAD_TITLE_TEXT = "CSVテンプレートの保存"
SELECT_CSV_TEXT = "CSVファイルを選択"
NOT_SELECTED_CSV_TEXT = "CSVファイルが選択されていません!"
SEND_EMAIL_TEXT = "メールを送る"
SELECTED_FILE_TEXT = "選択したファイル:"
DONE_SENDING_MAIL_TEXT = "メールを送信しました!"


def read_csv(file_path: str) -> list:
    """
    This function reads a CSV file and returns a list of dictionaries.
    Each dictionary represents a row in the CSV file with keys 'email', 'name', and 'company'.
    
    :param file_path: The path to the CSV file.
    :return: A list of dictionaries representing the CSV data.
    """
    data = []
    with open(file_path, mode='r', encoding='cp932') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row if present
        for row in reader:
            data.append({'email': row[0], 'name': row[1], 'company': row[2]})
    return data

def format_email(template_path: str, customer_info: dict) -> str:
    """
    Reads an email template file and formats it with customer information.
    
    :param template_path: The path to the email template file.
    :param customer_info: A dictionary containing customer information.
    :return: A formatted email string.
    """
    with open(template_path, 'r', encoding='utf8') as file:
        template = file.read()
    return template.format(**customer_info)

def read_config(config_path: str) -> dict:
    """
    Reads a configuration file and returns the 'aws' section as a dictionary.
    
    :param config_path: The path to the configuration file.
    :return: A dictionary representing the 'aws' section of the configuration file.
    """
    config = configparser.ConfigParser()
    config.read(config_path, encoding='cp932')

    global MAIL_SUBJECT, CC_EMAIL
    MAIL_SUBJECT = config['email']['subject']
    CC_EMAIL = config['email']['cc'].split(',')

    return config['aws']

def send_email_ses(aws_config: dict, body: str, recipient: str) -> dict:
    """
    Sends an email using Amazon SES.
    
    :param aws_config: A dictionary containing AWS configuration.
    :param body: The body of the email.
    :param recipient: The recipient of the email.
    :return: The response from the SES client.
    """
    client = boto3.client(
        'ses',
        aws_access_key_id=aws_config['access_key'],
        aws_secret_access_key=aws_config['secret_key'],
        region_name=aws_config['region']
    )
    response = client.send_email(
        Source='bui.vietduy@hachi-x.com',
        Destination={
            'ToAddresses': [recipient],
            'CcAddresses': CC_EMAIL
            },
        Message={
            'Subject': {'Data': MAIL_SUBJECT},
            'Body': {'Html': {'Data': body}}
        }
    )
    return response

class EmailSenderApp(QWidget):
    """
    A PyQt5 application for sending emails. The application allows users to download a template CSV file,
    select a CSV file with customer data, and send emails to the customers.
    """
    def __init__(self):
        """
        Initialize the EmailSenderApp with a UI.
        """
        super().__init__()
        self.init_UI()

    def init_UI(self):
        """
        Initialize the UI of the EmailSenderApp. The UI includes buttons for downloading a template CSV,
        selecting a CSV file, and sending emails, as well as a label to display the selected CSV file path.
        """
        self.setWindowTitle(WINDOW_TITLE_TEXT)
        layout = QVBoxLayout()

        # Button to download the template CSV
        self.btn_download_template = QPushButton(DOWNLOAD_TEMPLATE_TEXT, self)
        self.btn_download_template.clicked.connect(self.downloadTemplate)
        layout.addWidget(self.btn_download_template)

        # Button to select CSV file
        self.btn_select_csv = QPushButton(SELECT_CSV_TEXT, self)
        self.btn_select_csv.clicked.connect(self.openFileNameDialog)
        layout.addWidget(self.btn_select_csv)

        # Label to show selected CSV file path
        self.selected_csv_label = QLabel(NOT_SELECTED_CSV_TEXT)
        layout.addWidget(self.selected_csv_label)

        # Button to send emails
        self.btn_send_email = QPushButton(SEND_EMAIL_TEXT, self)
        self.btn_send_email.clicked.connect(self.send_emails)
        layout.addWidget(self.btn_send_email)

        self.setLayout(layout)

    def openFileNameDialog(self):
        """
        Open a file dialog to select a CSV file. The selected file path is displayed in the label.
        """
        options = QFileDialog.Options()
        csv_file_path, _ = QFileDialog.getOpenFileName(self, SELECT_CSV_TEXT, "", "CSV Files (*.csv)", options=options)
        if csv_file_path:
            self.selected_csv_label.setText(f"{SELECTED_FILE_TEXT} {csv_file_path}")

    def downloadTemplate(self):
        """
        Download the template CSV file. The user is asked where to save the file.
        """
        try:
            options = QFileDialog.Options()
            # Ask user where to save the template
            destination, _ = QFileDialog.getSaveFileName(self, DOWNLOAD_TITLE_TEXT, "customer.csv", "CSV Files (*.csv)", options=options)
            if destination:
                # Copy the template file to the selected location
                shutil.copy(CSV_TEMPLATE_PATH, destination)
        except Exception as e:
            print(e)

    def send_emails(self):
        """
        Send emails to the customers listed in the selected CSV file. The CSV file is updated with a 'sent' status
        for each customer to whom an email is sent successfully.
        """
        try:
            csv_file_path = self.selected_csv_label.text().replace(f"{SELECTED_FILE_TEXT} ", "")
            if csv_file_path != NOT_SELECTED_CSV_TEXT:
                customers = read_csv(csv_file_path)
                aws_config = read_config(CONFIG_FILE_PATH)
                # Create a new list that includes the 'sent' status
                updated_customers = []

                for customer in customers:
                    email_content = format_email(TEMPLATE_FILE_PATH, customer)
                    response = send_email_ses(aws_config, email_content, customer['email'])
                    print(f"Email sent to {customer['email']}, Response: {response}")
                    # Add the 'X' to indicate email sent successfully
                    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                        customer_row = [customer['email'], customer['name'], customer['company'], 'X']
                    else:
                        customer_row = [customer['email'], customer['name'], customer['company'], '']
                    updated_customers.append(customer_row)

                # Write the updated list back to the CSV file
                with open(csv_file_path, 'w', newline='', encoding='cp932') as file:
                    writer = csv.writer(file)
                    # Write header row
                    writer.writerow(['電子メールアドレス', '顧客名', '会社名', 'メール送信済み'])
                    writer.writerows(updated_customers)
                self.selected_csv_label.setText(DONE_SENDING_MAIL_TEXT)
            else:
                print("CSV file path is not set.")
        except Exception as e:
            print(e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget { font-size: 20px; }")
    ex = EmailSenderApp()
    ex.show()
    sys.exit(app.exec_())