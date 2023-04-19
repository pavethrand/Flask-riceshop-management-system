import random

class OTPGenerator:
    def __init__(self):
        self.OTP = None
    
    def generate_otp(self):
        otp = ""
        for i in range(4):
            otp += str(random.randint(0, 9))
        print(otp)
        return otp