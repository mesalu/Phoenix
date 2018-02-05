"""
Author: Samuel Dunn
Created: 2/3/2018
Modified: 2/4/2018
"""

import wx
import six

class ArtProvider(object):
    def RenderNbTab(self, dc, rect, content, style):
        """
        This method performs the actual drawing to a given client area.
        This will be called during the relevant paint events.
        :param dc: an instance of wx.DC to use for rendering.
        :param rect: The area that this method call is allowed to draw in.
        :param content: user defined content that the ArtProvider may use to draw.
        :param style: the style of the invoking NoteBook
        :return: wx.Rect indicating the actual space consumed, this is important for
                 the invoking widget to manage space consumption.
        :rtype: wx.Rect
        """
        raise NotImplementedError


class DefaultProvider(ArtProvider):
    # This is currently for trials.. this will absolutely not look professional.
    def RenderNbTab(self, dc, rect, content, style):
        if not isinstance(content, six.string_types):
            raise TypeError("Expected string for content argument")

        contentext = dc.GetTextExtent(content)
        boundingbox = wx.Rect(rect.GetPosition(), wx.Size(contentext.x + 5, rect.height))

        # Draw a bounding box:
        dc.SetPen(wx.Pen(wx.Colour(255, 0 , 0)))
        dc.DrawRectangle(boundingbox)

        dc.DrawText(content, 5, int((rect.height / 2.0) - (contentext.y / 2.0)))

        return boundingbox




