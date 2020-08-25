class buildAsset:
    def __init__(self, name, license, quantity):
        self.name       = str(name)
        self.license    = str(license)
        self.quantity   = int(quantity)
    
    def get_name(self):
        # name of the Licensed Product
        return(self.name)

    def get_license(self):
        '''
            TODO: Add encryption
        '''
        
        return (self.license)

    def get_quantity(self):
        return(self.quantity)


class assignAsset:
    def __init__(self, hostname):
        self.hostname   = str(hostname)

    def get_hostname(self):
        # Endpoint hostname the license is assigned to
        return(self.hostname)

