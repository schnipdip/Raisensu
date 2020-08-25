from cryptography.fernet import Fernet

class encrypto():
    def __init__(self, key):

        #keytab file
        self.key = key
        
    def load_key(self):
        
        #open secret key
        return (open(self.key, 'rb').read())

    def encrypt(self, license):
        
        #Encrypt the license
        
        block = encrypto.load_key(self)

        encoded_message = license.encode()

        f = Fernet(block)

        encrypted_message = f.encrypt(encoded_message)

        return encrypted_message

    def decrypt(self, encrypted_message):
    
        #Decrypt the license
    
        block = encrypto.load_key(self)

        f = Fernet(block)
        
        if isinstance(encrypted_message, str):
            encrypted_message = encrypted_message.encode()
        
        decrypted_message = f.decrypt(encrypted_message)

        return (decrypted_message.decode())




