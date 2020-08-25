class buildAsset:
    def __init__(self, name, license, quantity, expire):
        self.name       = str(name)
        self.license    = str(license)
        self.quantity   = int(quantity)
        self.expire     = str(expire)
    
    def get_name(self):
        #name of the Licensed Product
        return(self.name)

    def get_license(self):
        return (self.license)

    def get_quantity(self):
        return(self.quantity)

    def get_expire(self):
        return(self.expire)

class assignAsset:
    def __init__(self, hostname):
        self.hostname   = str(hostname)

    def get_hostname(self):
        #Endpoint hostname the license is assigned to
        return(self.hostname)