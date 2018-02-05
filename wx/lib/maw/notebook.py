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

    __ALL_ORIENT_SET = (MAW_NB_ORIENT_NORTH, MAW_NB_ORIENT_SOUTH,
                        MAW_NB_ORIENT_WEST,  MAW_NB_ORIENT_EAST)

    __ALL_GRAV = (MAW_NB_GRAV_NORTH | MAW_NB_GRAV_SOUTH |
                  MAW_NB_GRAV_WEST  | MAW_NB_GRAV_EAST)

    __ALL_GRAV_SET = (MAW_NB_GRAV_NORTH, MAW_NB_GRAV_SOUTH,
                      MAW_NB_GRAV_WEST,  MAW_NB_GRAV_EAST)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # The class nesting (though not a language level) implies a particular relationship.
    # clients will not need to subclass, or instance TabContainer or PageInfo directly
    # (especially not the latter). As such the classes are nested to indicate dependence
    # on the enclosing, NoteBook, class. Anyone who tells me that 'Python isn't Java' over this
    # can eat a shoe. Its a valid implication that Python users need to embrace more.
    # (I can also say that the implication is just as valid as using double underscores
    # to imply privacy. Or that using namespaces in C/C++ implies relationships)
    # /endrant.

    class TabContainer(wx.Control):
        """
        This widget manages and
        """
        def __init__(self, parent, artprov, nbstyle):
            wx.Control.__init__(self, parent, wx.NewId(), style = wx.BORDER_SUNKEN)

            if not isinstance(parent, NoteBook):
                raise TypeError("TabContainer must be associated to NoteBook")

            self.__artprov = artprov
            self.__style = nbstyle

            self.SetMaxTabSize(wx.Size(75, 30))
            self.SetMinSize(self.GetMaxTabSize())

            #self.Bind(wx.EVT_PAINT, self.OnPaint)
            #self.Bind(wx.EVT_LEFT_DCLICK, self.OnClick)
            #self.Bind(wx.EVT_SIZE, self.OnSize)

            # Will need to bind drag-'n'-drop behavior too.

        def GetMaxTabSize(self):
            """
            :return: The maximum size that will be allocated to any single tab.
            :rtype: wx.Size
            """
            return self.__maxtabsize

        def SetMaxTabSize(self, size):
            """
            :param wx.Size, tuple size: the size to set.
            :return: None
            """
            if not isinstance(size, (wx.Size, tuple, list)):
                raise TypeError("Expected type castable to wx.Size")
            self.__maxtabsize = wx.Size(size)
            self.SetMinSize(self.__maxtabsize)

        def OnPaint(self, evt):
            """
            :param evt:
            :return:
            """
            dc = wx.BufferedPaintDC(self)
            # Do the magic.
            baseRect = wx.Rect((0, 0), self.GetSize())
            for content in (x.GetContent() for x in self.__pageinfos):
                # Calculate and set ClippingRegion:

                consumed = self.__artprov.RenderNbTab(dc, baseRect, content, self.__style)

                # Destroy last ClippingRegion

                # progress baseRect in relevant direction:


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

        self.__nbstyle = self.__validateNbStyle(nbstyle)

        if artprov:
            if isinstance(artprov, artprovider.ArtProvider):
                self.__artprov = artprov
            else:
                raise TypeError("Instance of wx.lib.maw.artprov.ArtProvider expected for artprov argument")
        else:
            self.__artprov = artprovider.DefaultProvider()

        self.__tabcontainer = NoteBook.TabContainer(self, self.__artprov, self.__nbstyle)
        self.__tabcontainer.SetMinSize((75, 30))

        self.__activeWidget = None
        self.__pages = []

        print("Updating sizer.")
        self.__updateSizer()

    @property
    def tabcontainer(self):
        return self.__tabcontainer

    def AddPage(self, content, page, focus = False):
        """
        Add page to notebook.
        :param content: User defined content to be associated with the page. Usually a string, is sent to
                        the artprovider for use.
                        If using DefaultProvider, it is expected to be a string.
        :param page:    An instance of wx.Window.
        :param focus:   Indicates if the new page should take focus.
        :return:        None
        """
        self.__pages.append(NoteBook.PageInfo(page, content))
        if len(self.__pages) == 1 or focus:
            self.__activeWidget = page

    def RemovePage(self, page):
        raise NotImplementedError

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
        # To do: only perform rearrangements if orientation is changed.
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

        # Note to self: Don't remove all widgets then add them back in the 'correct' order.
        # Just remove tab container and then append/prepend it.

        try:
            sizer = self.__sizer
        except AttributeError:
            print("Initializing sizer.")
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
            sizer.Add(self.__tabcontainer, 0, wx.EXPAND)

            for widget in (x.GetWidget() for x in self.__pages):
                sizer.Add(widget, 1, wx.EXPAND)
                if widget is not self.__activeWidget:
                    sizer.Hide(widget)

        else:
            # tabctrl is second.
            for widget in (x.GetWidget() for x in self.__pages):
                sizer.Add(widget, 1, wx.EXPAND)
                if widget is not self.__activeWidget:
                    sizer.Hide(widget)

            sizer.Add(self.__tabcontainer, 0, wx.EXPAND)

        sizer.Layout()