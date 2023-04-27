import smtplib
from secret_codes import sender_email
from secret_codes import sender_password
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class Notification:
    def otp_to_mail(self,receiver_mail,otp):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(sender_email, sender_password)
        message = f'Subject: OTP Verification\n\nYour OTP for Verification is {otp} '
        self.server.sendmail(sender_email, receiver_mail, message)
        self.server.quit()

    def order_notification_mail(self,receiver_mail):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(sender_email, sender_password)
        message = f'Subject: Order Confirmed\n\nyour order has confirmed'
        self.server.sendmail(sender_email, receiver_mail, message)
        self.server.quit()

    def order_cancellation_mail(self,receiver_mail):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(sender_email, sender_password)
        message = f'Subject: Order Cancelled\n\nyour order has cancelled'
        self.server.sendmail(sender_email, receiver_mail, message)
        self.server.quit()

    def account_creation_mail(self,receiver_mail):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(sender_email, sender_password)
        message = f'Subject: Account Created\n\nYour account for senthur traders were created successfully'
        self.server.sendmail(sender_email, receiver_mail, message)
        self.server.quit()

    def account_verified_by_shop(self,receiver_mail):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(sender_email, sender_password)
        message = f'Subject: Account Verified\n\nYour account for senthur traders has verified successfully'
        self.server.sendmail(sender_email, receiver_mail, message)
        self.server.quit()

    def bill_generated_for_your_order(self, receiver_mail, pdf_response):
        # create message object instance
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_mail
        message['Subject'] = 'Invoice Generated'
        
        # add message body
        body = 'Invoice Generated For your Order'
        message.attach(MIMEText(body, 'plain'))
    
        # add pdf file attachment
        pdf_part = MIMEApplication(pdf_response.getvalue(), _subtype='pdf')
        pdf_part.add_header('content-disposition', 'attachment', filename='invoice.pdf')
        message.attach(pdf_part)
    
        # send email
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, receiver_mail, message.as_string())
