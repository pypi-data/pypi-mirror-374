from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class PdfListItemCollection(PdfCollection):
    """
    Represents collection of list items.
    """

    def get_Item(self, index: int) -> 'PdfListItem':
        """
        Gets the PdfListItem from collection at the specified index.
        """
        GetDllLibPdf().PdfListItemCollection_get_Item.argtypes = [c_void_p, c_int]
        GetDllLibPdf().PdfListItemCollection_get_Item.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfListItemCollection_get_Item,self.Ptr, index)
        ret = None if intPtr == None else PdfListItem(intPtr)
        return ret

    @dispatch
    def Add(self, item: PdfListItem) -> int:
        """
        Adds the specified item.
        Args: item: The item.
        Returns: The item index in collection.
        """
        intPtritem: c_void_p = item.Ptr
        GetDllLibPdf().PdfListItemCollection_Add.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfListItemCollection_Add.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfListItemCollection_Add,self.Ptr, intPtritem)
        return ret

    @dispatch
    def Add(self, item: PdfListItem, itemIndent: float) -> int:
        """
        Adds the specified item.
        Args: item: The item.
        Args: itemIndent: The item indent.
        """
        intPtritem: c_void_p = item.Ptr
        GetDllLibPdf().PdfListItemCollection_AddII.argtypes = [c_void_p, c_void_p, c_float]
        GetDllLibPdf().PdfListItemCollection_AddII.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfListItemCollection_AddII,self.Ptr, intPtritem, itemIndent)
        return ret

    @dispatch
    def Add(self, text: str) -> PdfListItem:
        """
        Adds the item with a specified text.
        Args: text: The text.
        Returns:
        """
        GetDllLibPdf().PdfListItemCollection_AddT.argtypes = [c_void_p, c_wchar_p]
        GetDllLibPdf().PdfListItemCollection_AddT.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfListItemCollection_AddT,self.Ptr, text)
        ret = None if intPtr == None else PdfListItem(intPtr)
        return ret

    @dispatch
    def Add(self, text: str, itemIndent: float) -> PdfListItem:
        """
        Adds the specified text.
        Args: text: The text.
        Args: itemIndent: The item indent.
        Returns: List item.
        """
        GetDllLibPdf().PdfListItemCollection_AddTI.argtypes = [c_void_p, c_wchar_p, c_float]
        GetDllLibPdf().PdfListItemCollection_AddTI.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfListItemCollection_AddTI,self.Ptr, text, itemIndent)
        ret = None if intPtr == None else PdfListItem(intPtr)
        return ret

    @dispatch
    def Add(self, text: str, font: PdfFontBase) -> PdfListItem:
        """
        Adds the specified text.
        Args: text: The text.
        Args: font: The font.
        Returns: The item index in collection.
        """
        intPtrfont: c_void_p = font.Ptr
        GetDllLibPdf().PdfListItemCollection_AddTF.argtypes = [c_void_p, c_wchar_p, c_void_p]
        GetDllLibPdf().PdfListItemCollection_AddTF.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfListItemCollection_AddTF,self.Ptr, text, intPtrfont)
        ret = None if intPtr == None else PdfListItem(intPtr)
        return ret

    @dispatch
    def Add(self, text: str, font: PdfFontBase, itemIndent: float) -> PdfListItem:
        """
        Adds the specified text.
        Args: text: The text.
        Args: font: The font.
        Args: itemIndent: The item indent.
        Returns: List item.
        """
        intPtrfont: c_void_p = font.Ptr
        GetDllLibPdf().PdfListItemCollection_AddTFI.argtypes = [c_void_p, c_wchar_p, c_void_p, c_float]
        GetDllLibPdf().PdfListItemCollection_AddTFI.restype = c_void_p
        intPtr = CallCFunction(GetDllLibPdf().PdfListItemCollection_AddTFI,self.Ptr, text, intPtrfont, itemIndent)
        ret = None if intPtr == None else PdfListItem(intPtr)
        return ret

    @dispatch
    def Insert(self, index: int, item: PdfListItem):
        """
        Inserts item at the specified index.
        Args: index: The specified index.
        Args: item: The item.
        Returns: The item index
        """
        intPtritem: c_void_p = item.Ptr
        GetDllLibPdf().PdfListItemCollection_Insert.argtypes = [c_void_p, c_int, c_void_p]
        CallCFunction(GetDllLibPdf().PdfListItemCollection_Insert,self.Ptr, index, intPtritem)

    @dispatch
    def Insert(self, index: int, item: PdfListItem, itemIndent: float):
        """
        Inserts the specified index.
        Args: index: The index.
        Args: item: The item.
        Args: itemIndent: The item indent.
        """
        intPtritem: c_void_p = item.Ptr
        GetDllLibPdf().PdfListItemCollection_InsertIII.argtypes = [c_void_p, c_int, c_void_p, c_float]
        CallCFunction(GetDllLibPdf().PdfListItemCollection_InsertIII,self.Ptr, index, intPtritem, itemIndent)

    def Remove(self, item: 'PdfListItem'):
        """
        Removes the specified item from the list.
        Args: item: The specified item.
        """
        intPtritem: c_void_p = item.Ptr
        GetDllLibPdf().PdfListItemCollection_Remove.argtypes = [c_void_p, c_void_p]
        CallCFunction(GetDllLibPdf().PdfListItemCollection_Remove,self.Ptr, intPtritem)

    def RemoveAt(self, index: int):
        """
        Removes the item at the specified index from the list.
        Args: index: The specified index.
        """
        GetDllLibPdf().PdfListItemCollection_RemoveAt.argtypes = [c_void_p, c_int]
        CallCFunction(GetDllLibPdf().PdfListItemCollection_RemoveAt,self.Ptr, index)

    def IndexOf(self, item: 'PdfListItem') -> int:
        """
        Determines the index of a specific item in the list.
        Args: item: The item to locate in the list.
        Returns: The index of item if found in the list; otherwise, -1.
        """
        intPtritem: c_void_p = item.Ptr
        GetDllLibPdf().PdfListItemCollection_IndexOf.argtypes = [c_void_p, c_void_p]
        GetDllLibPdf().PdfListItemCollection_IndexOf.restype = c_int
        ret = CallCFunction(GetDllLibPdf().PdfListItemCollection_IndexOf,self.Ptr, intPtritem)
        return ret

    def Clear(self):
        """
        Clears collection.
        """
        GetDllLibPdf().PdfListItemCollection_Clear.argtypes = [c_void_p]
        CallCFunction(GetDllLibPdf().PdfListItemCollection_Clear,self.Ptr)