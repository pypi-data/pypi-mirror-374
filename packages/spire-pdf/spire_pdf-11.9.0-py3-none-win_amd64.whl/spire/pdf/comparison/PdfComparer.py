from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfComparer(SpireObject):
    @dispatch
    def __init__(self, oldDocument: PdfDocument, newDocument: PdfDocument):
        """
        Initializes a new instance of the PdfComparer class with the PdfDocument.

        Args:
            oldDocument (PdfDocument): The old pdf document.
            newDocument (PdfDocument): The new pdf document.
        """
        ptroldpdf: c_void_p = oldDocument.Ptr
        ptrnewpdf: c_void_p = newDocument.Ptr
        GetDllLibPdf().PdfComparer_CreatePdfComparer.argtypes = [c_void_p,c_void_p]
        GetDllLibPdf().PdfComparer_CreatePdfComparer.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfComparer_CreatePdfComparer,ptroldpdf,ptrnewpdf)
        super(PdfComparer, self).__init__(intPtr)

    @property
    def PdfCompareOptions(self) -> 'PdfCompareOptions':
        """
        The compare options.

        Returns:
            PdfCompareOptions: The options for compare PdfDocument.
        """
        GetDllLibPdf().PdfComparer_get_CompareOptions.argtypes = [c_void_p]
        GetDllLibPdf().PdfComparer_get_CompareOptions.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfComparer_get_CompareOptions,self.Ptr)
        ret = None if intPtr == None else PdfCompareOptions(intPtr)
        return ret

    @dispatch
    def Compare(self, filename: str):
        """
        Compare the old/new pdf docments,generate diff pdf document.

        Args:
            filename (str): The output file name.
        """
        GetDllLibPdf().PdfComparer_CompareToFile.argtypes = [c_void_p, c_wchar_p]
        CallCFunction(GetDllLibPdf().PdfComparer_CompareToFile,self.Ptr, filename)

    @dispatch
    def Compare(self, fileStream: Stream):
        """
        Compare the old/new pdf docments,generate diff pdf document.

        Args:
            fileStream (Stream): The output file stream.
        """
        intPtrfileStream: c_void_p = fileStream.Ptr

        GetDllLibPdf().PdfComparer_CompareToStream.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfComparer_CompareToStream,self.Ptr, intPtrfileStream)

