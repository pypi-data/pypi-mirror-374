from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple,overload
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfDocumentPrivilege(SpireObject):
    """
    Represents the privileges for accessing pdf file.
    """
    @dispatch
    def __init__(self):
        GetDllLibPdf().PdfDocumentPrivilege_Create.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_Create)
        super(PdfDocumentPrivilege, self).__init__(intPtr)


    @staticmethod
    def AllowAll()->'PdfDocumentPrivilege':
        """
        All allowed.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowAll.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_AllowAll)
        ret = None if intPtr==None else PdfDocumentPrivilege(intPtr)
        return ret

    @staticmethod
    def ForbidAll()->'PdfDocumentPrivilege':
        """
        All forbidded.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_ForbidAll.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_ForbidAll)
        ret = None if intPtr==None else PdfDocumentPrivilege(intPtr)
        return ret

    @property
    def AllowPrint(self)->bool:
        """
        Gets or sets the permission which allow print or not.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowPrint.argtypes=[c_void_p]
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowPrint.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_AllowPrint,self.Ptr)
        return ret

    @AllowPrint.setter
    def AllowPrint(self, value:bool):
        GetDllLibPdf().PdfDocumentPrivilege_set_AllowPrint.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_set_AllowPrint,self.Ptr, value)

    @property
    def AllowModifyContents(self)->bool:
        """
        Gets or sets the permission which allow modify contents or not.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowModifyContents.argtypes=[c_void_p]
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowModifyContents.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_AllowModifyContents,self.Ptr)
        return ret

    @AllowModifyContents.setter
    def AllowModifyContents(self, value:bool):
        GetDllLibPdf().PdfDocumentPrivilege_set_AllowModifyContents.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_set_AllowModifyContents,self.Ptr, value)

    @property
    def AllowContentCopying(self)->bool:
        """
        Gets or sets the permission which allow copy contents or not.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowContentCopying.argtypes=[c_void_p]
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowContentCopying.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_AllowContentCopying,self.Ptr)
        return ret

    @AllowContentCopying.setter
    def AllowContentCopying(self, value:bool):
        GetDllLibPdf().PdfDocumentPrivilege_set_AllowContentCopying.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_set_AllowContentCopying,self.Ptr, value)

    @property
    def AllowModifyAnnotations(self)->bool:
        """
        Gets or sets the permission which allow modify annotations or not.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowModifyAnnotations.argtypes=[c_void_p]
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowModifyAnnotations.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_AllowModifyAnnotations,self.Ptr)
        return ret

    @AllowModifyAnnotations.setter
    def AllowModifyAnnotations(self, value:bool):
        GetDllLibPdf().PdfDocumentPrivilege_set_AllowModifyAnnotations.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_set_AllowModifyAnnotations,self.Ptr, value)

    @property
    def AllowFillFormFields(self)->bool:
        """
        Gets or sets the permission which allow fill in form fields or not.
        Note: The RC4_40 algorithm is not supported.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowFillFormFields.argtypes=[c_void_p]
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowFillFormFields.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_AllowFillFormFields,self.Ptr)
        return ret

    @AllowFillFormFields.setter
    def AllowFillFormFields(self, value:bool):
        GetDllLibPdf().PdfDocumentPrivilege_set_AllowFillFormFields.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_set_AllowFillFormFields,self.Ptr, value)

    @property
    def AllowCopyContentAccessibility(self)->bool:
        """
        Gets or sets the permission which allow copy content for accessibility or not.
        Note: The RC4_40 algorithm is not supported.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowCopyContentAccessibility.argtypes=[c_void_p]
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowCopyContentAccessibility.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_AllowCopyContentAccessibility,self.Ptr)
        return ret

    @AllowCopyContentAccessibility.setter
    def AllowCopyContentAccessibility(self, value:bool):
        GetDllLibPdf().PdfDocumentPrivilege_set_AllowCopyContentAccessibility.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_set_AllowCopyContentAccessibility,self.Ptr, value)

    @property
    def AllowAssembly(self)->bool:
        """
        Gets or sets the permission which allow assembly or not.
        Note: The RC4_40 algorithm is not supported.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowAssembly.argtypes=[c_void_p]
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowAssembly.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_AllowAssembly,self.Ptr)
        return ret

    @AllowAssembly.setter
    def AllowAssembly(self, value:bool):
        GetDllLibPdf().PdfDocumentPrivilege_set_AllowAssembly.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_set_AllowAssembly,self.Ptr, value)

    @property
    def AllowDegradedPrinting(self)->bool:
        """
        Gets or sets the permission which allow degraded printing or not.
        Note: The RC4_40 algorithm is not supported.
        """
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowDegradedPrinting.argtypes=[c_void_p]
        GetDllLibPdf().PdfDocumentPrivilege_get_AllowDegradedPrinting.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_get_AllowDegradedPrinting,self.Ptr)
        return ret

    @AllowDegradedPrinting.setter
    def AllowDegradedPrinting(self, value:bool):
        GetDllLibPdf().PdfDocumentPrivilege_set_AllowDegradedPrinting.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfDocumentPrivilege_set_AllowDegradedPrinting,self.Ptr, value)

