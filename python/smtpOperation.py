import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



class SMTPserver:
    def __init__(self, SMTP_USERNAME,SMTP_PASSWORD) -> None:
        self.SMTP_USERNAME = SMTP_USERNAME
        self.SMTP_PASSWORD = SMTP_PASSWORD
        
    def sendAlert(self, value, receiver_email: str) -> str:

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = self.SMTP_USERNAME
        subject = 'Alert from HealthCare System!!!'

        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = sender_email
        msgRoot['To'] = receiver_email
        msgRoot['Subject'] = subject

        text = """\n
        Your SpO2 level has decreased to {}%.\n
        Please wear the mask the oxygen supply process has started!!!\n
        """.format(str(value))

        message = MIMEText(text, "plain")

        msgRoot.attach(message)
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
                server.sendmail(sender_email, receiver_email,
                                msgRoot.as_string())
                res = 'Email sent successfully'
                return res
        except Exception as err:
            res = f'Email has not sent due to {err}'
            return res

    
    def sendID(self,value, receiver_email: str) -> str:

        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        sender_email = self.SMTP_USERNAME
        subject = 'Alert from HealthCare System!!!'

        msgRoot = MIMEMultipart('related')
        msgRoot['From'] = sender_email
        msgRoot['To'] = receiver_email
        msgRoot['Subject'] = subject

        text = """your unique userID is : \n
        {}
        """.format(str(value))

        message = MIMEText(text, "plain")

        msgRoot.attach(message)
        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(self.SMTP_USERNAME, self.SMTP_PASSWORD)
                server.sendmail(sender_email, receiver_email, msgRoot.as_string())
                res='Email sent successfully'
                return res
        except Exception as err:
            res=f'Email has not sent due to {err}'
            return res
