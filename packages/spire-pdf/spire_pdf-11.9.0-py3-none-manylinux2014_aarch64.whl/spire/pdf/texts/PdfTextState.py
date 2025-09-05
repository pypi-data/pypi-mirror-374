from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfTextState(SpireObject):
    """
    Represents the text state of a text
    """
    @property
    def FontName(self) -> str:
        """
        Gets the font name.
        """
        GetDllLibPdf().PdfTextState_get_FontName.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextState_get_FontName.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfTextState_get_FontName,self.Ptr))
        return ret

    @property
    def FontFamily(self) -> str:
        """
        Gets the FontFamily.
        """
        GetDllLibPdf().PdfTextState_get_FontFamily.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextState_get_FontFamily.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().PdfTextState_get_FontFamily,self.Ptr))
        return ret

    @property
    def IsBold(self) -> bool:
        """
        Gets flag specifying whether font is bold.
        """
        GetDllLibPdf().PdfTextState_get_IsBold.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextState_get_IsBold.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfTextState_get_IsBold,self.Ptr)
        return ret

    @property
    def IsSimulateBold(self) -> bool:
        """
        Gets flag specifying whether font is simulate bold.
        """
        GetDllLibPdf().PdfTextState_get_IsSimulateBold.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextState_get_IsSimulateBold.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfTextState_get_IsSimulateBold,self.Ptr)
        return ret

    @property
    def IsItalic(self) -> bool:
        """
        Gets flag specifying whether font is italic.
        """
        GetDllLibPdf().PdfTextState_get_IsItalic.argtypes = [c_void_p]
        GetDllLibPdf().PdfTextState_get_IsItalic.restype = c_bool
        ret = CallCFunction(GetDllLibPdf().PdfTextState_get_IsItalic,self.Ptr)
        return ret

    @property
    def FontSize(self)->float:
        """
        Gets font size of the text.
        """
        GetDllLibPdf().PdfTextState_get_FontSize.argtypes=[c_void_p]
        GetDllLibPdf().PdfTextState_get_FontSize.restype=c_float
        ret = CallCFunction(GetDllLibPdf().PdfTextState_get_FontSize,self.Ptr)
        return ret

    @property
    def ForegroundColor(self)->Color:
        """
        Gets foreground color of the text.
        """
        GetDllLibPdf().PdfTextState_get_ForegroundColor.argtypes=[c_void_p]
        GetDllLibPdf().PdfTextState_get_ForegroundColor.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfTextState_get_ForegroundColor, self.Ptr)
        ret = None if intPtr==None else Color(intPtr)
        return ret

