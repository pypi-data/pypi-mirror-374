from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfCertificate(SpireObject):
    """
    Represents the Certificate object.
    """
    @dispatch
    def __init__(self, pfxPath:str, password:str):
        GetDllLibPdf().PdfCertificate_CreatePdfCertificatePP.argtypes=[c_wchar_p,c_wchar_p]
        GetDllLibPdf().PdfCertificate_CreatePdfCertificatePP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfCertificate_CreatePdfCertificatePP,pfxPath,password)
        super(PdfCertificate, self).__init__(intPtr)
    