# Samuel Dunn
# Application Test Case
# Allows testing wx features within the context of an application

# Benefits: As stated, allows unit testing within a full App mainloop.
#           Allows developers to quickly construct a test case by developing a
#               single widget
#           TestCase class is generated from the widget provided to atc. The
#               generated TestCase class  mimics the widget to allow pytest
#               to behave  normally. This allows  unsquashed testing (jamming
#               plural tests into one runtime)
#           Generated TestCase class should play nice with all unittest features
#           Generated TestCase classes are unique, allowing plural per test
#               module

# Drawbacks: Generated test case class has to be applied to a __main__ module
#               global scope member. Need to look into unittest.TestDiscorvery
#               to correct this behavior
#           Code is currently a bit sloppy, Revisions will be made before a
#               formal PR to improve documentation and clean up the code.
#

# TODO:
#   Ensure full TestCase API is available within the app
#   automatically apply TestCritical decorator to test_ methods in widget
#   Ensure TestCritical decorator plays nice with preserving other decorations
#       such that decoration order does not matter
#   Add stack trace printouts upon TestDone(False) or TestCritical exception


__version__ = "0.0.2"

import functools
import os
import sys
import unittest
import wx
import wx.lib.newevent

TestEvent, EVT_TEST = wx.lib.newevent.NewEvent()

class TestError(Exception):
    pass

def testCritical(func):
    """
    Wraps the provided function to ensure that uncaught exceptions
    will end execution.
    This is done by closing all top level windows and allowing the exception
    to be re-raised once the main event loop ends.
    """
    @functools.wraps(func)
    def method(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print("Unbound exception caught in test procedure:\n%s\n%s" % (e.__class__, str(e)), file = sys.stderr)
            # give full stack trace
            wx.GetApp().exception = e
            for window in wx.GetTopLevelWindows():
                window.Close()

    return method


class TestWidget:
    def __init__(self):
        assert isinstance(self, wx.EvtHandler), "Test widget needs to be an event handler"

        self.Bind(EVT_TEST, self.OnTest)

        if "__WXGTK__" in wx.PlatformInfo:
            self.Bind(wx.EVT_WINDOW_CREATE, self.OnLnxStart)

        else:
            wx.CallAfter(self.OnCommence)

    def OnCommence(self):
        assert wx.GetApp().IsMainLoopRunning(), "Timer ended before mainloop started" # see above comment regarding
                                                                                    # commencing with the timer.
        # start test sequence
        evt = TestEvent()
        evt.case = wx.GetApp().case
        wx.PostEvent(self, evt)

        # set a watchdog incase of test error
        wx.CallLater(300000, self.OnWatchdog) # 5 minutes in millis

    def OnWatchdog(self):
        print("Test Timeout!!!")
        wx.GetApp().exception = RuntimeError("Watchdog timed out")
        for window in wx.GetTopLevelWindows():
            window.Close()

    def OnLnxStart(self, evt):
        """
        Invoked on linux systems to signal mainloop readiness
        """
        wx.CallAfter(self.OnCommence)
        evt.Skip()

    @testCritical   # automatically apply exception blocking to test_ methods.. indirectly
    def OnTest(self, evt):
        testfunc = getattr(self, evt.case)

        print("Testing: %s" % evt.case)
        testfunc()

    def testPassed(self):
        for window in wx.GetTopLevelWindows():
            window.Close()

    def testFailed(self, errmsg =  "A test failed."):
        # do not rely on testCritical being applied to an above method
        wx.GetApp().exception = TestError(errmsg)
        for window in wx.GetTopLevelWindows():
            window.Close()
        
def CreateApp(frame):
    class TestApp(wx.App):
        def OnInit(self):
            self.frame = frame()
            self.frame.Show(True)
            return True

    return TestApp

def CreateFrame(widget):
    # called when the test widget is not a frame.
    class BaseTestFrame(wx.Frame):
        def __init__(self):
            wx.Frame.__init__(self, None, wx.NewId(), "%s Test Frame" % str(type(widget)))

            sizer = wx.BoxSizer()
            self.widget = widget(self)  # assumes need of parent.
            sizer.Add(self.widget, 1, wx.EXPAND)

            self.SetSizer(sizer)
            sizer.Layout()

        # this will only be invoked if the test widget is not a frame.
        def GetTestTarget(self):
            return self.widget

    return BaseTestFrame

def CreateTestMethod(app, case):
    def test_func(obj):
        a = app()
        a.case = case
        a.MainLoop()

        if hasattr(a, "exception"):
            raise a.exception

        elif hasattr(a, "errorcode"):
            sys.exit(a.errorcode)

    return test_func

def createATC(widget):
    # if widget is not instance of TestFrame, generate a quick frame
    # to house the widget
    assert issubclass(widget, TestWidget), "Testing requires the tested widget to derive from TestWidget for now"

    tlw = None
    if not issubclass(widget, wx.Frame):
        # need to stick this widget in a frame
        tlw = CreateFrame(widget)

    else:
        tlw = widget

    app = CreateApp(tlw)

    class ApplicationTestCase(unittest.TestCase):
        pass

    methods = [meth for meth in dir(widget) if (meth.startswith("test_") and callable(getattr(widget, meth)))]

    for meth in methods:
        test_func = CreateTestMethod(app, meth)
        # ensure any other deocrated data is preserved:
        basemeth = getattr(widget, meth)
        for attr in dir(basemeth):
            if not hasattr(test_func, attr):
                setattr(test_func, attr, getattr(basemeth, attr))

        setattr(ApplicationTestCase, meth, test_func)

    return ApplicationTestCase
