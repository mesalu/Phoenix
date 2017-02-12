import unittest
from unittests import wtc, atc
import wx
import os
import sys
#---------------------------------------------------------------------------

class frame_Tests(wtc.WidgetTestCase):

    def test_frameStyles(self):
        wx.FRAME_NO_TASKBAR
        wx.FRAME_TOOL_WINDOW
        wx.FRAME_FLOAT_ON_PARENT
        wx.FRAME_SHAPED


    def test_frameCtors(self):
        f = wx.Frame(None)
        f.Show()
        f.Close()
        f = wx.Frame(self.frame, title="Title", pos=(50,50), size=(100,100))
        f.Show()
        f.Close()
        f = wx.Frame()
        f.Create(None, title='2 phase')
        f.Show()
        f.Close()

    def test_frameTopLevelTweaks(self):
        # test a couple tweaks added in wx.TopLevelWidnow
        f = wx.Frame()
        f.MacSetMetalAppearance(True)
        f.Create(None)
        f.Show()
        f.MacGetTopLevelWindowRef()
        f.Close()


    def test_frameProperties(self):
        f = wx.Frame(None)
        f.Show()

        f.DefaultItem
        f.Icon
        f.Title
        f.TmpDefaultItem
        f.OSXModified
        f.MacMetalAppearance

        f.Close()

    @unittest.skip("Omitting test for now, requires full App.")
    def test_frameRestore(self):
        f = wx.Frame(self.frame, title="Title", pos=(50,50), size=(100,100))
        f.Show()
        f.Maximize()
        self.myYield()
        assert f.IsMaximized()
        f.Restore()
        self.myYield()
        assert not f.IsMaximized()
        f.Close()
#---------------------------------------------------------------------------

# this is the frame that is used for testing Restore functionality
class FrameRestoreTester(wx.Frame, atc.TestWidget):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.NewId(), "Frame Restore Test")
        atc.TestWidget.__init__(self)
        self.SetLabel("Frame Restore Test")

        # enforce a strict schedule
        self.schedule = ("iconize", "restore", "maximize", "restore")

    def test_iconize_restore(self):
        self.Iconize()
        wx.CallLater(250, self.Ensure, "Iconized")

    def test_maximize_restore(self):
        self.Maximize()
        wx.CallLater(250, self.Ensure, "Maximized")

    def Ensure(self, ensurable):
        if ensurable == "Iconized":
            if not self.IsIconized():
                self.TestDone(False)
            self.Restore()
            wx.CallLater(250, self.Ensure, "Restored")
        
        elif ensurable == "Maximized":
            if not self.IsMaximized():
                self.TestDone(False)
            self.Restore()
            wx.CallLater(250, self.Ensure, "Restored")
        

        elif ensurable == "Restored":
            self.TestDone(not self.IsIconized() and not self.IsMaximized())


tc = atc.CreateATC(FrameRestoreTester)

#---------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
