class TouchController:
    def __init__(self, serialPort):
        self.transport = serialPort

    def Read(self, pin: int, charge_t: int, charge_s: int, timeout: int):
        cmd = "touch({0}, {1}, {2}, {3})".format(pin, charge_t, charge_s, timeout)
        self.transport.WriteCommand(cmd)

        r,s = self.transport.ReadResponse()
        
        val = False
        if r:
            try:
                return s
            except:
                pass
        return val
