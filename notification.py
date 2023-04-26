import smtplib
from secret_codes import sender_email
from secret_codes import sender_password

class Notification:
    def otp_to_mail(self,receiver_mail,otp):
        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.starttls()
        self.server.login(sender_email, sender_password)
        message = f'Subject: OTP Verification\n\nYour OTP for Verification is {otp} '
        self.server.sendmail(sender_email, receiver_mail, message)
        self.server.quit()
