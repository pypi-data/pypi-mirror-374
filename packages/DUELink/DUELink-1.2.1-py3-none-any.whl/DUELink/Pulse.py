from enum import Enum
from DUELink.SerialInterface import SerialInterface


class PulseController:   

    def __init__(self, transport:SerialInterface):
        self.transport = transport


    def Read(self, pin: int, state: int, timeout_ms: int)->int:                
        cmd = f"PulseIn({pin}, {state}, {timeout_ms})"
        self.transport.WriteCommand(cmd)        

        ret = self.transport.ReadResponse()

        if ret.success:            
            try:
                value = int(ret.response)
                return value
            except:
                pass

        return 0

        
        




       



