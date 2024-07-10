from twilio.rest import Client
import config

# TODO: Make work for multiple numbers instead of hardcoded
""" For send pricing notifications """
class CarrierPigeon:
    def __init__(self):
        self.client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        print("Carrier Pigeon is ready")

    """ sends a text """
    def send_pigeon(self, message):
        message = self.client.messages.create(
            body = message,
            from_ = config.TWILIO_PHONE_NUMBER,
            to = config.TO_NUMBER
        )
        print('just sent a text')
        return message.sid
    
