
# 3rd party imports.
import win32serviceutil
import servicemanager
import win32event
import win32service

class CWindowsServiceBase(win32serviceutil.ServiceFramework):
    '''Base class for creating Windows services running Python

    This class should not be instantiated directly.
    It should be subclassed.
    '''

    # Name of the service. Used for referring to the service using the Windows
    # command line tool sc e.g. sc delete PythonService.
    _svc_name_ = 'PythonService'

    # Display name of the service. This is what will be shown if the service
    # is looked up in the Windows Services interface.
    _svc_display_name_ = 'Python Service'

    # Service description. This text will be displayed alongside the service
    # in the Windows Services interface.
    _svc_description_ = 'Python Service Description'

    @classmethod
    def parse_command_line(cls):
        '''ClassMethod to parse the command line'''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''Constructor of the winservice'''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        '''Called when the service is asked to stop'''
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''Called when the service is asked to start'''
        self.start()
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()

    def start(self):
        '''
        Override to add logic before the start
        eg. running condition
        '''
        pass

    def stop(self):
        '''
        Override to add logic before the stop
        eg. invalidating running condition
        '''
        pass

    def main(self):
        '''
        Main class to be ovverridden to add logic
        '''
        pass
