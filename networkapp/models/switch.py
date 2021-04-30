

class cisco_switch():

    def __init__(self, hostname, user, psswd, device_type):
        self.hostname = hostname
        self.user = user
        self.psswd = psswd
        self.platform = device_type