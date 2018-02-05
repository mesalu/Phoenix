"""
Author: Samuel Dunn
Created: 2/3/2018
Modified: 2/4/2018
"""
import wx

from . import InvalidStyle
from . import artprov as artprovider


class NoteBook(wx.Control):
    """
    Doc-y doc docs here

    Try to conform to normal wx.Notebook events, etc.
    """
    MAW_NB_ORIENT_NORTH = 0x1
    MAW_NB_ORIENT_SOUTH = 0x2
    MAW_NB_ORIENT_WEST  = 0x4
    MAW_NB_ORIENT_EAST  = 0x8

    MAW_NB_GRAV_NORTH   = 0x10
    MAW_NB_GRAV_SOUTH   = 0x20
    MAW_NB_GRAV_WEST    = 0x40
    MAW_NB_GRAV_EAST    = 0X80

    __ALL_ORIENT = (MAW_NB_ORIENT_NORTH | MAW_NB_ORIENT_SOUTH |
                    MAW_NB_ORIENT_WEST  | MAW_NB_ORIENT_EAST)

    __ALL_GRAV = (MAW_NB_GRAV_NORTH | MAW_NB_GRAV_SOUTH |
                  MAW_NB_GRAV_WEST  | MAW_NB_GRAV_EAST)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    class TabContainer(wx.Control):
        def __init__(self, parent, artprov):
            wx.Control.__init__(self, parent, wx.NewId(), style = wx.BORDER_SUNKEN)

            self.__artprov = artprov

            self.Bind(wx.EVT_PAINT, self.OnPaint)
            self.Bind(wx.EVT_LEFT_DCLICK, self.OnClick)
            self.Bind(wx.EVT_SIZE, self.OnSize)

            # Will need to bind drag-n-drop behavior too.

        def OnPaint(self, evt):
            """
            :param evt:
            :return:
            """
            # Do the magic.

        def OnClick(self, evt):
            """
            Look for a tab at event location
            :param evt:
            :return:
            """

        def OnSize(self, evt):
            """

            :param evt:
            :return:
            """
            evt.Skip()

            # Determine which tabs (if any) are damaged and need to be redrawn.

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    class PageInfo(object):
        """
        Instances of this class are used to communicate and adapt information regarding
        a notebook page.
        """
        def __init__(self, window, tabcontent):
            if not isinstance(window, wx.Window):
                raise TypeError("Expected Window derivative.")

            self.__tc = tabcontent
            self.__wnd = window

        def GetWidget(self):
            return self.__wnd

        def GetContent(self):
            return self.__tc

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, parent, id = -1, artprov = None,  nbstyle = 0, style = 0):
        wx.Control.__init__(self, parent, id, style = style)

        if artprov:
            if isinstance(artprov, artprovider.ArtProvider):
                self.__artprov = artprov
            else:
                raise TypeError("Instance of wx.lib.maw.artprov.ArtProvider expected for artprov argument")
        else:
            self.__artprov = artprovider.DefaultProvider()

        self.__tabcontainer = NoteBook.TabContainer(self, self.__artprov)
        self.__activeWidget = None
        self.__pages = []

        self.SetNbStyle(nbstyle)


    def AddPage(self, content, page):
        """
        Add page to notebook.
        :param content: User defined content to be associated with the page. Usually a string, is sent to
                        the artprovider for use.
                        If using DefaultProvider, it is expected to be a string.
        :param page:    An instance of wx.Window.
        :return:        None
        """
        self.__pages.append(NoteBook.PageInfo(page, content))

    def GetTabContainer(self):
        return self.__tabcontainer

    def GetNbStyle(self):
        """
        :return: The style that is currently set.
        :rtype: int
        """
        return self.__nbstyle

    def SetNbStyle(self, style):
        """

        :param int style:
        :return: None
        :raises InvalidStyle: if given style is invalid
        """
        self.__nbstyle = self.__validateNbStyle(style)
        self.__updateSizer()

    def __validateNbStyle(self, style):
        """
        :param style: Input style
        :return: A style that has been validated and cleaned of unnecessary values.
        :rtype: int

        :raises InvalidStyle: if given style is invalid
        """
        # To do: only perform rearrangements if orient is changed.
        if not style:
            return NoteBook.MAW_NB_ORIENT_NORTH | NoteBook.MAW_NB_GRAV_SOUTH
        if not (style & NoteBook.__ALL_GRAV) in NoteBook.__ALL_GRAV:
            raise InvalidStyle("Too many grav styles specified.")

        if not (style & NoteBook.__ALL_ORIENT) in NoteBook.__ALL_ORIENT:
            raise InvalidStyle("Too many orient styles specified.")

        return style & (NoteBook.__ALL_ORIENT & NoteBook.__ALL_GRAV)

    def __updateSizer(self):
        """
        :return: None
        """
        try:
            sizer = self.__sizer
        except AttributeError:
            self.__sizer = wx.BoxSizer()
            self.SetSizer(self.__sizer)
            sizer = self.__sizer
        else:
            for item in sizer.GetChildren():
                sizer.Detatch(item)

        sizer.SetOrientation(wx.VERTICAL if self.__nbstyle & (NoteBook.MAW_NB_ORIENT_NORTH | NoteBook.MAW_NB_ORIENT_SOUTH)
                             else wx.HORIZONTAL)

        if self.__nbstyle & (NoteBook.MAW_NB_ORIENT_NORTH | NoteBook.MAW_NB_ORIENT_WEST):
            # Insert tabcontainer first, then other widgets.
            sizer.Add(self.__tabcontainer, wx.EXPAND)

            #sizer.AddMany([x.GetWidget() for x in self.__pages])
            for widget in (x.GetWidget() for x in self.__pages):
                sizer.Add(widget, wx.EXPAND)
                if widget is not self.__activeWidget:
                    sizer.Hide(widget)

        else:
            # tabctrl is second.
            for widget in (x.GetWidget() for x in self.__pages):
                sizer.Add(widget, wx.EXPAND)
                if widget is not self.__activeWidget:
                    sizer.Hide(widget)

            sizer.Add(self.__tabcontainer, wx.EXPAND)

        sizer.Layout()