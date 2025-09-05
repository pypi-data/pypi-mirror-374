from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfCompareOptions(SpireObject):
    @property
    def OldPageStartIndex(self)->int:
        """
        <summary>
        The start index of old document range.
        </summary>
        """
        GetDllLibPdf().PdfCompareOptions_get_OldPageStartIndex.argtypes=[c_void_p]
        GetDllLibPdf().PdfCompareOptions_get_OldPageStartIndex.restype=c_long
        ret = GetDllLibPdf().PdfCompareOptions_get_OldPageStartIndex(self.Ptr)
        return ret

    @property
    def OldPageEndIndex(self)->int:
        """
        <summary>
        The end index of old document range.
        </summary>
        """
        GetDllLibPdf().PdfCompareOptions_get_OldPageEndIndex.argtypes=[c_void_p]
        GetDllLibPdf().PdfCompareOptions_get_OldPageEndIndex.restype=c_long
        ret = GetDllLibPdf().PdfCompareOptions_get_OldPageEndIndex(self.Ptr)
        return ret

    @property
    def NewPageStartIndex(self)->int:
        """
        <summary>
        The start index of new document range.
        </summary>
        """
        GetDllLibPdf().PdfCompareOptions_get_NewPageStartIndex.argtypes=[c_void_p]
        GetDllLibPdf().PdfCompareOptions_get_NewPageStartIndex.restype=c_long
        ret = GetDllLibPdf().PdfCompareOptions_get_NewPageStartIndex(self.Ptr)
        return ret

    @property
    def NewPageEndIndex(self)->int:
        """
        <summary>
        The end index of new document range.
        </summary>
        """
        GetDllLibPdf().PdfCompareOptions_get_NewPageEndIndex.argtypes=[c_void_p]
        GetDllLibPdf().PdfCompareOptions_get_NewPageEndIndex.restype=c_long
        ret = GetDllLibPdf().PdfCompareOptions_get_NewPageEndIndex(self.Ptr)
        return ret

    @property
    def OnlyCompareText(self)->bool:
        """
        Whether is only compare text.
        """
        GetDllLibPdf().PdfCompareOptions_get_OnlyCompareText.argtypes=[c_void_p]
        GetDllLibPdf().PdfCompareOptions_get_OnlyCompareText.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfCompareOptions_get_OnlyCompareText,self.Ptr)
        return ret

    @dispatch
    def SetPageRanges(self ,oldStartIndex:int,oldEndIndex:int,newStartIndex:int,newEndIndex:int):
        """
        Set the compared documents page ranges.

        Args:
            oldStartIndex(int):The old document page start index.
            oldEndIndex(int):The old document page end index.
            newStartIndex(int):The new document page start index.
            newEndIndex(int):The new document page end index.
        """         
        GetDllLibPdf().PdfCompareOptions_set_SetPageRanges.argtypes=[c_void_p,c_int,c_int,c_int,c_int]
        CallCFunction(GetDllLibPdf().PdfCompareOptions_set_SetPageRanges,self.Ptr, oldStartIndex,oldEndIndex,newStartIndex,newEndIndex)


