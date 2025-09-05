from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfOrdinarySignatureMaker(PdfSignatureMaker):
    """
    Pdf ordinary signature maker.

    A document can contain one or more ordinary signatures.
    """
    @dispatch
    def __init__(self, document:PdfDocument,certificate:PdfCertificate):
        intPtrDoc:c_void_p = document.Ptr
        intPtrCert:c_void_p = certificate.Ptr

        GetDllLibPdf().PdfOrdinarySignatureMaker_CreatePdfOrdinarySignatureMakerDC.argtypes=[c_void_p,c_void_p]
        GetDllLibPdf().PdfOrdinarySignatureMaker_CreatePdfOrdinarySignatureMakerDC.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfOrdinarySignatureMaker_CreatePdfOrdinarySignatureMakerDC,intPtrDoc,intPtrCert)
        super(PdfOrdinarySignatureMaker, self).__init__(intPtr)

    @dispatch
    def __init__(self, document:PdfDocument,pfxPath:str, password:str):
        intPtrDoc:c_void_p = document.Ptr

        GetDllLibPdf().PdfOrdinarySignatureMaker_CreatePdfOrdinarySignatureMakerDPP.argtypes=[c_void_p,c_wchar_p,c_wchar_p]
        GetDllLibPdf().PdfOrdinarySignatureMaker_CreatePdfOrdinarySignatureMakerDPP.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfOrdinarySignatureMaker_CreatePdfOrdinarySignatureMakerDPP,intPtrDoc,pfxPath,password)
        super(PdfOrdinarySignatureMaker, self).__init__(intPtr)