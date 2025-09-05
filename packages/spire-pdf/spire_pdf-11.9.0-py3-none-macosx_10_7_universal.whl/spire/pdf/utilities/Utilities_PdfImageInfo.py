from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class Utilities_PdfImageInfo(SpireObject):
    """
    This class represents information about a PDF image.
    """

    @property
    def Bounds(self) -> 'RectangleF':
        """
        Gets the image boundary location.

        Returns:
            RectangleF: The image boundary location.
        """
        GetDllLibPdf().Utilities_PdfImageInfo_get_Bounds.argtypes = [c_void_p]
        GetDllLibPdf().Utilities_PdfImageInfo_get_Bounds.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().Utilities_PdfImageInfo_get_Bounds,self.Ptr)
        ret = None if intPtr == None else RectangleF(intPtr)
        return ret

    @property
    def Image(self) -> 'Stream':
        """
        Gets the image and saves it to a stream.

        Returns:
            Image: The image.
        """
        GetDllLibPdf().Utilities_PdfImageInfo_get_Image.argtypes = [c_void_p]
        GetDllLibPdf().Utilities_PdfImageInfo_get_Image.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().Utilities_PdfImageInfo_get_Image,self.Ptr)
        ret = None if intPtr == None else Stream(intPtr)
        return ret

    @property
    def ResourceName(self) -> str:
        """
        Gets or sets the ResourceName.
        """
        GetDllLibPdf().Utilities_PdfImageInfo_get_ResourceName.argtypes = [c_void_p]
        GetDllLibPdf().Utilities_PdfImageInfo_get_ResourceName.restype = c_void_p
        ret = PtrToStr(CallCFunction(GetDllLibPdf().Utilities_PdfImageInfo_get_ResourceName,self.Ptr))
        return ret

    @ResourceName.setter
    def ResourceName(self, value: str):
        GetDllLibPdf().Utilities_PdfImageInfo_set_ResourceName.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().Utilities_PdfImageInfo_set_ResourceName,self.Ptr, value)

    @dispatch
    def TryCompressImage(self)->bool:
        """
        the compress image(except inline image).
			
        Returns:
            bool: If success, return true; otherwise false.
        """ 
        GetDllLibPdf().Utilities_PdfImageInfo_TryCompressImage.argtypes=[ c_void_p]
        GetDllLibPdf().Utilities_PdfImageInfo_TryCompressImage.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().Utilities_PdfImageInfo_TryCompressImage, self.Ptr)
        return ret