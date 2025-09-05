from enum import Enum
from plum import dispatch
from functools import singledispatch
from typing import TypeVar, Union, Generic, List, Tuple
from spire.pdf.common import *
from spire.pdf import *
from ctypes import *
import abc

class LicenseProvider(SpireObject):
    @singledispatch
    @staticmethod
    def SetLicense(licenseFile):
        raise TypeError("Unsupport Type")
    
    @SetLicense.register
    def _SetLicense(licenseFile:str):
        """
            Provides a license by a license file path, which will be used for loading license.
            
            Parameters:
                licenseFileFullPath:
                    License file full path.
        """
        GetDllLibPdf().LicenseProvider_SetLicenseFileFullPath.argtypes=[ c_wchar_p]
        CallCFunction(GetDllLibPdf().LicenseProvider_SetLicenseFileFullPath, licenseFile)

    @SetLicense.register
    def _SetLicense(licenseFile:Stream):
        """
            Provides a license by a license stream, which will be used for loading license.

            Parameters:
                licenseFileStream:
                    License data stream.
        """
        intPtrstream:c_void_p = licenseFile.Ptr
        GetDllLibPdf().LicenseProvider_SetLicenseFileStream.argtypes=[ c_void_p]
        CallCFunction(GetDllLibPdf().LicenseProvider_SetLicenseFileStream, intPtrstream)


    #@staticmethod
    #def SetLicenseFileFullPath(licenseFileFullPath:str):
    #    """
    #    Provides a license by a license file path, which will be used for loading license.
    #    Args:
		  #  licenseFileFullPath: License file full path.
    #    """
    #    GetDllLibPdf().SetLicenseFileFullPath.argtypes=[ c_wchar_p]
    #    CallCFunction(GetDllLibPdf().SetLicenseFileFullPath, licenseFileFullPath)

    @staticmethod
    def SetLicenseFileName(licenseFileName:str):
        """
		Sets the license file name, which will be used for loading license.
        Args:
		    licenseFileName: License file name.
        """
        GetDllLibPdf().LicenseProvider_SetLicenseFileName.argtypes=[ c_wchar_p]
        CallCFunction(GetDllLibPdf().LicenseProvider_SetLicenseFileName, licenseFileName)

  #  @staticmethod
  #  def SetLicenseFileStream(stream:Stream):
  #      """
  #      Provides a license by a license stream, which will be used for loading license.
		#Args:
		#    stream: License data stream.
  #      """
  #      intPtrstream:c_void_p = stream.Ptr
  #      GetDllLibPdf().SetLicenseFileStream.argtypes=[ c_void_p]
  #      CallCFunction(GetDllLibPdf().SetLicenseFileStream, intPtrstream)

    @staticmethod
    def SetLicenseKey(*args, **kwargs):
        """
            Provides a license by a license key, which will be used for loading license.

            Parameters:
                key:
                    The value of the Key attribute of the element License of you license xml file.

                useDevOrTestLicense(could be None):
                    Indicates whether to apply a development or test license.
        """
        if len(args) == 1:
            keyStr = args[0]
            GetDllLibPdf().LicenseProvider_SetLicenseKey.argtypes=[c_wchar_p]
            CallCFunction(GetDllLibPdf().LicenseProvider_SetLicenseKey, keyStr)
        elif len(args) == 2:
            keyStr = args[0]
            useDevOrTestLicense = args[1]
            GetDllLibPdf().LicenseProvider_SetLicenseKeyUseDevOrTestLicense.argtypes=[c_wchar_p, c_bool]
            CallCFunction(GetDllLibPdf().LicenseProvider_SetLicenseKeyUseDevOrTestLicense, keyStr, useDevOrTestLicense)

    #@staticmethod
    #def SetLicenseKey(key:str):
    #    """
    #    Provides a license by a license key, which will be used for loading license.
    #    Args:
		  #  stream: The value of the Key attribute of the element License of you license xml file.
    #    """
    #    GetDllLibPdf().SetLicenseKey.argtypes=[ c_void_p]
    #    CallCFunction(GetDllLibPdf().SetLicenseKey, key)


    #@staticmethod
    #def SetLicenseKeyUseDevOrTestLicense(key:str,useDevOrTestLicense:bool):
    #    """
    #    Sets the license key required for license loading, and specifies whether to use a development or test license.
    #    Args:
		  #  key: The value of the Key attribute of the element License of you license xml file.
    #        useDevOrTestLicense: Indicates whether to apply a development or test license.
    #    """
    #    GetDllLibPdf().SetLicenseKeyUseDevOrTestLicense.argtypes=[ c_wchar_p,c_bool]
    #    CallCFunction(GetDllLibPdf().SetLicenseKeyUseDevOrTestLicense, key,useDevOrTestLicense)

    @staticmethod
    def UnbindDevelopmentOrTestingLicenses()->bool:
        """
		Unbind development or testing licenses. 
        Only development or testing licenses can be unbound, deployment licenses cannot be unbound.
        The approach to lifting development or testing licenses does not allow frequent invocation by the same machine code,
        mandating a two-hour wait period before it can be invoked again.

		Returns:
            Returns true if the unbinding operation was successful; otherwise, false.
        """
        GetDllLibPdf().LicenseProvider_UnbindDevelopmentOrTestingLicenses.restype=c_bool
        ret = CallCFunction(GetDllLibPdf().LicenseProvider_UnbindDevelopmentOrTestingLicenses)
        return ret

    @staticmethod
    def ClearLicense():
        """
        Clear all cached license.
        """
        CallCFunction(GetDllLibPdf().LicenseProvider_ClearLicense)

    @staticmethod
    def LoadLicense():
        """
        Load the license provided by current setting to the license cache.
        """
        CallCFunction(GetDllLibPdf().LicenseProvider_LoadLicense)

    