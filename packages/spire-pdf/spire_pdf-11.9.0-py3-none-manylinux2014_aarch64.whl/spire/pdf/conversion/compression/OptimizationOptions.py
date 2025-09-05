from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class OptimizationOptions (SpireObject) :
    """
    Initializes a new instance of the class.
    """
    @dispatch
    def __init__(self):
        GetDllLibPdf().OptimizationOptions_CreateOptimizationOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().OptimizationOptions_CreateOptimizationOptions)
        super(OptimizationOptions, self).__init__(intPtr)

    @dispatch
    def SetIsCompressContents(self ,IsCompressContents:bool):
        """
        Indicates whether to compress page contents.

        Args:
            IsCompressContents (bool): Indicates whether to compress page contents.
        """        
        GetDllLibPdf().OptimizationOptions_set_ISCompressContents.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPdf().OptimizationOptions_set_ISCompressContents,self.Ptr, IsCompressContents)

    @dispatch
    def SetIsCompressFonts(self ,IsCompressFonts:bool):
        """
        Indicates whether to compress font resources. Default value is true.

        Args:
            IsCompressFonts (bool): Indicates whether to compress font resources. Default value is true.
        """        
        GetDllLibPdf().OptimizationOptions_set_ISCompressFonts.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPdf().OptimizationOptions_set_ISCompressFonts,self.Ptr, IsCompressFonts)

    @dispatch
    def SetIsUnembedFonts(self ,IsUnembedFonts:bool):
        """
        Indicates whether to unembed fonts. Default value is false.
        Note: The resulting document may have errors when the font is not normally encoded.

        Args:
            IsUnembedFonts (bool): Indicates whether to unembed fonts. Default value is false.
        """        
        GetDllLibPdf().OptimizationOptions_set_ISUnembedFonts.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPdf().OptimizationOptions_set_ISUnembedFonts,self.Ptr, IsUnembedFonts)

    @dispatch
    def SetIsCompressImage(self ,IsCompressImage:bool):
        """
        Indicates whether compress image. Default value is true.

        Args:
            IsCompressImage (bool): Indicates whether compress image. Default value is true.
        """        
        GetDllLibPdf().OptimizationOptions_set_ISCompressImage.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPdf().OptimizationOptions_set_ISCompressImage,self.Ptr, IsCompressImage)

    @dispatch
    def SetResizeImages(self ,IsResizeImages:bool):
        """
        Indicates whether resize image.

        Args:
            IsResizeImages (bool): Indicates whether resize image.
        """        
        GetDllLibPdf().OptimizationOptions_set_ISResizeImages.argtypes=[c_void_p ,c_bool]
        CallCFunction(GetDllLibPdf().OptimizationOptions_set_ISResizeImages,self.Ptr, IsResizeImages)

    @dispatch
    def SetImageQuality(self ,imageQuality:ImageQuality):
        """
        Indicates whether resize image.

        Args:
            imageQuality (enum): ImageQuality.
        """        
        enumimageQuality:c_int = imageQuality.value
        GetDllLibPdf().OptimizationOptions_set_ImageQuality.argtypes=[c_void_p ,c_int]
        CallCFunction(GetDllLibPdf().OptimizationOptions_set_ImageQuality,self.Ptr, enumimageQuality)