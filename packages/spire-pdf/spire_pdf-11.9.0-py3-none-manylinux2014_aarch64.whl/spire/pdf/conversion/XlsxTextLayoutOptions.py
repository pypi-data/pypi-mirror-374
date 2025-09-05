from enum import Enum
from plum import dispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class XlsxTextLayoutOptions(XlsxOptions):
    """
    Pdf to excel, the options use text layout.
    """

    def __init__(self):
        """
        Initializes a new instance of the XlsxTextLayoutOptions class.
        """
        super().__init__()