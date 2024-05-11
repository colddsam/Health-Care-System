import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SMTPserver:
    def __init__(self, SMTP_USERNAME,SMTP_PASSWORD) -> None:
        self.SMTP_USERNAME = SMTP_USERNAME
        self.SMTP_PASSWORD = SMTP_PASSWORD
        
    def sendAlert(self, alertText, receiver_email: str) -> str:

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = self.SMTP_USERNAME
        subject = "Urgent medical alert; Immediate action required for patient emergency"
        html = alertText
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        receiver_mail = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html, 'html'))
        msg_str = msg.as_string()
        try:
            with (smtplib.SMTP(smtp_server, smtp_port)) as server:
                server.starttls()
                server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
                server.sendmail(sender_email, receiver_mail, msg_str)
                print("operation successfull")
        except Exception as e:
            print("not successfull")

    def sendID(self, gretingSystem, receiver_email: str) -> str:

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = self.SMTP_USERNAME
        subject = 'You have successfully registered for the application health mate'
        html=gretingSystem
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        receiver_mail = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html, 'html'))
        msg_str = msg.as_string()
        try:
            with (smtplib.SMTP(smtp_server, smtp_port)) as server:
                server.starttls()
                server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
                server.sendmail(sender_email, receiver_mail, msg_str)
                print("operation successfull")
        except Exception as e:
            print("not successfull")
