
class PulseController:   

    def __init__(self, serialPort):
        self.transport = serialPort


    def Read(self, pin: int, state: int, timeout_ms: int)->int:                
        cmd = f"PulseIn({pin}, {state}, {timeout_ms})"
        self.transport.WriteCommand(cmd)        

        r,s = self.transport.ReadResponse()

        if r:            
            try:
                value = int(s)
                return value
            except:
                pass

        return 0

        
        




       



