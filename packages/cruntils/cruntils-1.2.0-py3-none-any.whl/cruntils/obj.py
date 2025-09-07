
class CActiveObject:
    def __init__(self, name):
        self.Name = name


        self.MsgsIn  = []
        self.MsgsOut = []

        self.Running = False

    def Start(self):
        self.Running = True

    def RxMsg(self, msg):
        self.MsgsIn.append(msg)






