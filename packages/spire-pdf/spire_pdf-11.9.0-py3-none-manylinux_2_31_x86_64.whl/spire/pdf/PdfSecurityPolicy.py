from enum import Enum
from plum import dispatch
from typing import TypeVar,Union,Generic,List,Tuple,overload
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfSecurityPolicy(SpireObject):
    @property
    def EncryptMetadata(self)->bool:
        """
        Gets or sets the value indicating whether to encrypt metadata.
        """
        GetDllLibPdf().PdfSecurityPolicy_get_EncryptMetadata.argtypes=[c_void_p]
        GetDllLibPdf().PdfSecurityPolicy_get_EncryptMetadata.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().PdfSecurityPolicy_get_EncryptMetadata,self.Ptr)
        return ret

    @EncryptMetadata.setter
    def EncryptMetadata(self, value:bool):
        GetDllLibPdf().PdfSecurityPolicy_set_EncryptMetadata.argtypes=[c_void_p, c_bool]
        CallCFunction(GetDllLibPdf().PdfSecurityPolicy_set_EncryptMetadata,self.Ptr, value) 
        
    @property
    def EncryptionAlgorithm(self)->'PdfEncryptionAlgorithm':
        """
        Gets the sets encryption algorithm.
        """
        GetDllLibPdf().PdfSecurityPolicy_get_PdfEncryptionAlgorithm.argtypes=[c_void_p]
        GetDllLibPdf().PdfSecurityPolicy_get_PdfEncryptionAlgorithm.restype=c_int
        ret = CallCFunction(GetDllLibPdf().PdfSecurityPolicy_get_PdfEncryptionAlgorithm,self.Ptr)
        objEncryptionAlgorithm = PdfEncryptionAlgorithm(ret)
        return objEncryptionAlgorithm
    @EncryptionAlgorithm.setter
    def EncryptionAlgorithm(self, EncryptionAlgorithm:PdfEncryptionAlgorithm):
        enumEncryptionAlgorithm:c_int = EncryptionAlgorithm.value
        GetDllLibPdf().PdfSecurityPolicy_set_PdfEncryptionAlgorithm.argtypes=[c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfSecurityPolicy_set_PdfEncryptionAlgorithm,self.Ptr, enumEncryptionAlgorithm) 

    @property
    def DocumentPrivilege(self)->'PdfDocumentPrivilege':
        """
        Gets or sets the document's permission flags
        """
        GetDllLibPdf().PdfSecurityPolicy_get_PdfDocumentPrivilege.argtypes=[c_void_p]
        GetDllLibPdf().PdfSecurityPolicy_get_PdfDocumentPrivilege.restype=c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfSecurityPolicy_get_PdfDocumentPrivilege,self.Ptr)
        ret = None if intPtr==None else PdfDocumentPrivilege(intPtr)
        return ret


    @DocumentPrivilege.setter
    def DocumentPrivilege(self, value):
        intPtrDocumentPrivilege:c_void_p = value.Ptr
        GetDllLibPdf().PdfSecurityPolicy_set_PdfDocumentPrivilege.argtypes=[c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfSecurityPolicy_set_PdfDocumentPrivilege,self.Ptr, intPtrDocumentPrivilege)


