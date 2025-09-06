class TouchController:
    def __init__(self, transport):
        self.transport = transport

    def Read(self, pin: int, charge_t: int, charge_s: int, timeout: int):
        cmd = "touch({0}, {1}, {2}, {3})".format(pin, charge_t, charge_s, timeout)
        self.transport.WriteCommand(cmd)

        res = self.transport.ReadResponse()
        
        val = False
        if res.success:
            try:
                return res.response
            except:
                pass
        return val
