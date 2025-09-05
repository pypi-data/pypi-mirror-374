import sys
from ctypes import *
from spire.pdf.common import *
from spire.pdf.common import dlllib
from spire.pdf.common import dlllibPdf

from spire.pdf.common.SpireObject import SpireObject

from spire.pdf.common.Common import IntPtrArray
from spire.pdf.common.Common import IntPtrWithTypeName
from spire.pdf.common.Common import GetObjVectorFromArray
from spire.pdf.common.Common import GetStrVectorFromArray
from spire.pdf.common.Common import GetVectorFromArray
from spire.pdf.common.Common import GetIntPtrArray
from spire.pdf.common.Common import GetByteArray
from spire.pdf.common.Common import GetIntValue
from spire.pdf.common.Common import GetObjIntPtr

from spire.pdf.common.RegexOptions import RegexOptions
from spire.pdf.common.CultureInfo import CultureInfo
from spire.pdf.common.Boolean import Boolean
from spire.pdf.common.Byte import Byte
from spire.pdf.common.Char import Char
from spire.pdf.common.Int16 import Int16
from spire.pdf.common.Int32 import Int32
from spire.pdf.common.Int64 import Int64
from spire.pdf.common.PixelFormat import PixelFormat
from spire.pdf.common.Size import Size
from spire.pdf.common.SizeF import SizeF
from spire.pdf.common.Point import Point
from spire.pdf.common.PointF import PointF
from spire.pdf.common.Rectangle import Rectangle
from spire.pdf.common.RectangleF import RectangleF
from spire.pdf.common.Single import Single
from spire.pdf.common.TimeSpan import TimeSpan
from spire.pdf.common.UInt16 import UInt16
from spire.pdf.common.UInt32 import UInt32
from spire.pdf.common.UInt64 import UInt64
from spire.pdf.common.Stream import Stream
from spire.pdf.common.License import License
from spire.pdf.common.Color import Color
from spire.pdf.common.DateTime import DateTime
from spire.pdf.common.Double import Double
from spire.pdf.common.EmfType import EmfType
from spire.pdf.common.Encoding import Encoding
from spire.pdf.common.FontStyle import FontStyle
from spire.pdf.common.GraphicsUnit import GraphicsUnit
from spire.pdf.common.ICollection import ICollection
from spire.pdf.common.IDictionary import IDictionary
from spire.pdf.common.IEnumerable import IEnumerable
from spire.pdf.common.IEnumerator import IEnumerator
from spire.pdf.common.IList import IList
from spire.pdf.common.String import String
from spire.pdf.common.Regex import Regex

from spire.pdf.license.LicenseProvider import LicenseProvider 
from spire.pdf.Find_TextFindParameter import Find_TextFindParameter 
from spire.pdf.additions.html.AspectRatio import AspectRatio 
from spire.pdf.document.CompressionLevel import CompressionLevel 
from spire.pdf.security.ConfiguerGraphicType import ConfiguerGraphicType 
from spire.pdf.document.CustomFieldType import CustomFieldType 
from spire.pdf.additions.html.Clip import Clip 
from spire.pdf.widget.DataFormat import DataFormat 
from spire.pdf.FileFormat import FileFormat 
from spire.pdf.document.collections.FileRelatedFieldType import FileRelatedFieldType 
from spire.pdf.interactive.digitalSignatures.GraphicMode import GraphicMode 
from spire.pdf.fileds.HttpMethod import HttpMethod 
from spire.pdf.document.HttpReadType import HttpReadType 
from spire.pdf.document.ImageFormatType import ImageFormatType 
from spire.pdf.graphics.ImageType import ImageType 
from spire.pdf.graphics.LayerExportState import LayerExportState 
from spire.pdf.graphics.LayerPrintState import LayerPrintState 
from spire.pdf.graphics.LayerViewState import LayerViewState 
from spire.pdf.graphics.LineType import LineType 
from spire.pdf.additions.html.LoadHtmlType import LoadHtmlType 
from spire.pdf.interactive.Pdf3DActivationMode import Pdf3DActivationMode 
from spire.pdf.interactive.Pdf3DActivationState import Pdf3DActivationState 
from spire.pdf.interactive.PDF3DAnimationType import PDF3DAnimationType 
from spire.pdf.interactive.Pdf3DDeactivationMode import Pdf3DDeactivationMode 
from spire.pdf.interactive.Pdf3DDeactivationState import Pdf3DDeactivationState 
from spire.pdf.annotations.Pdf3DLightingStyle import Pdf3DLightingStyle 
from spire.pdf.annotations.Pdf3DProjectionClipStyle import Pdf3DProjectionClipStyle 
from spire.pdf.annotations.Pdf3DProjectionOrthoScaleMode import Pdf3DProjectionOrthoScaleMode 
from spire.pdf.annotations.Pdf3DProjectionType import Pdf3DProjectionType 
from spire.pdf.annotations.Pdf3DRenderStyle import Pdf3DRenderStyle 
from spire.pdf.actions.PdfActionDestination import PdfActionDestination 
from spire.pdf.PdfAlignmentStyle import PdfAlignmentStyle 
from spire.pdf.annotations.PdfAnnotationFlags import PdfAnnotationFlags 
from spire.pdf.annotations.PdfAnnotationIntent import PdfAnnotationIntent 
from spire.pdf.annotations.PdfAnnotationWidgetTypes import PdfAnnotationWidgetTypes 
from spire.pdf.annotations.PdfAttachmentIcon import PdfAttachmentIcon 
from spire.pdf.general.PdfAttachmentRelationship import PdfAttachmentRelationship 
from spire.pdf.barcode.PdfBarcodeTextAlignment import PdfBarcodeTextAlignment 
from spire.pdf.graphics.PdfBlendMode import PdfBlendMode 
from spire.pdf.utilities.PdfBookletBindingMode import PdfBookletBindingMode 
from spire.pdf.interactive.annotations.PdfBorderEffect import PdfBorderEffect 
from spire.pdf.PdfBorderOverlapStyle import PdfBorderOverlapStyle 
from spire.pdf.fileds.PdfBorderStyle import PdfBorderStyle 
from spire.pdf.fileds.PdfButtonIconScaleMode import PdfButtonIconScaleMode 
from spire.pdf.fileds.PdfButtonIconScaleReason import PdfButtonIconScaleReason 
from spire.pdf.fileds.PdfButtonLayoutMode import PdfButtonLayoutMode 
from spire.pdf.security.PdfCertificationFlags import PdfCertificationFlags 
from spire.pdf.fileds.PdfCheckBoxStyle import PdfCheckBoxStyle 
from spire.pdf.graphics.PdfCjkFontFamily import PdfCjkFontFamily 
from spire.pdf.colorspace.PdfColorSpace import PdfColorSpace 
from spire.pdf.PdfCompressionLevel import PdfCompressionLevel 
from spire.pdf.PdfConformanceLevel import PdfConformanceLevel 
from spire.pdf.PdfCrossReferenceType import PdfCrossReferenceType 
from spire.pdf.graphics.PdfDashStyle import PdfDashStyle 
from spire.pdf.general.PdfDestinationMode import PdfDestinationMode 
from spire.pdf.PdfDockStyle import PdfDockStyle 
from spire.pdf.PdfEncryptionAlgorithm import PdfEncryptionAlgorithm 
from spire.pdf.security.PdfEncryptionKeySize import PdfEncryptionKeySize 
from spire.pdf.graphics.PdfExtend import PdfExtend 
from spire.pdf.actions.PdfFilePathType import PdfFilePathType 
from spire.pdf.graphics.PdfFillMode import PdfFillMode 
from spire.pdf.graphics.PdfFontFamily import PdfFontFamily 
from spire.pdf.graphics.PdfFontStyle import PdfFontStyle 
from spire.pdf.graphics.PdfFontType import PdfFontType 
from spire.pdf.graphics.PdfGraphicsUnit import PdfGraphicsUnit 
from spire.pdf.tables.PdfHeaderSource import PdfHeaderSource 
from spire.pdf.fileds.PdfHighlightMode import PdfHighlightMode 
from spire.pdf.interactive.annotations.PdfHorizontalAlignment import PdfHorizontalAlignment 
from spire.pdf.grid.PdfHorizontalOverflowType import PdfHorizontalOverflowType 
from spire.pdf.graphics.PdfImageType import PdfImageType 
from spire.pdf.graphics.PdfLayoutBreakType import PdfLayoutBreakType 
from spire.pdf.graphics.PdfLayoutType import PdfLayoutType 
from spire.pdf.graphics.PdfLinearGradientMode import PdfLinearGradientMode 
from spire.pdf.annotations.PdfLineBorderStyle import PdfLineBorderStyle 
from spire.pdf.graphics.PdfLineCap import PdfLineCap 
from spire.pdf.annotations.PdfLineCaptionType import PdfLineCaptionType 
from spire.pdf.annotations.PdfLineEndingStyle import PdfLineEndingStyle 
from spire.pdf.annotations.PdfLineIntent import PdfLineIntent 
from spire.pdf.graphics.PdfLineJoin import PdfLineJoin 
from spire.pdf.lists.PdfListMarkerAlignment import PdfListMarkerAlignment 
from spire.pdf.graphics.PdfMatrixOrder import PdfMatrixOrder 
from spire.pdf.PdfNumberStyle import PdfNumberStyle 
from spire.pdf.PdfPageLayout import PdfPageLayout 
from spire.pdf.PdfPageMode import PdfPageMode 
from spire.pdf.PdfPageOrientation import PdfPageOrientation 
from spire.pdf.PdfPageRotateAngle import PdfPageRotateAngle 
from spire.pdf.security.PdfPermissionsFlags import PdfPermissionsFlags 
from spire.pdf.annotations.PdfPopupIcon import PdfPopupIcon 
from spire.pdf.annotations.PdfRubberStampAnnotationIcon import PdfRubberStampAnnotationIcon 
from spire.pdf.pdfprint.PdfSinglePageScalingMode import PdfSinglePageScalingMode 
from spire.pdf.general.PdfSoundChannels import PdfSoundChannels 
from spire.pdf.general.PdfSoundEncoding import PdfSoundEncoding 
from spire.pdf.annotations.PdfSoundIcon import PdfSoundIcon 
from spire.pdf.actions.PdfSubmitFormFlags import PdfSubmitFormFlags 
from spire.pdf.graphics.PdfSubSuperScript import PdfSubSuperScript 
from spire.pdf.tables.PdfTableDataSourceType import PdfTableDataSourceType 
from spire.pdf.graphics.PdfTextAlignment import PdfTextAlignment 
from spire.pdf.annotations.PdfTextAnnotationIcon import PdfTextAnnotationIcon 
from spire.pdf.annotations.PdfTextMarkupAnnotationType import PdfTextMarkupAnnotationType 
from spire.pdf.bookmarks.PdfTextStyle import PdfTextStyle 
from spire.pdf.PdfTransitionDimension import PdfTransitionDimension 
from spire.pdf.PdfTransitionDirection import PdfTransitionDirection 
from spire.pdf.PdfTransitionMotion import PdfTransitionMotion 
from spire.pdf.PdfTransitionStyle import PdfTransitionStyle 
from spire.pdf.lists.PdfUnorderedMarkerStyle import PdfUnorderedMarkerStyle 
from spire.pdf.PdfVersion import PdfVersion 
from spire.pdf.graphics.PdfVerticalAlignment import PdfVerticalAlignment 
from spire.pdf.graphics.layer.PdfVisibility import PdfVisibility 
from spire.pdf.graphics.PdfWordWrapType import PdfWordWrapType 
from spire.pdf.PrintScalingMode import PrintScalingMode 
from spire.pdf.security.Security_GraphicMode import Security_GraphicMode 
from spire.pdf.security.Security_SignImageLayout import Security_SignImageLayout 
from spire.pdf.security.SignatureConfiguerText import SignatureConfiguerText 
from spire.pdf.interactive.digitalSignatures.SignImageLayout import SignImageLayout 
from spire.pdf.security.SignInfoType import SignInfoType 
from spire.pdf.security.SignTextAlignment import SignTextAlignment 
from spire.pdf.security.StoreType import StoreType 
from spire.pdf.fileds.SubmitDataFormat import SubmitDataFormat 
from spire.pdf.tables.TableWidthType import TableWidthType 
from spire.pdf.TabOrder import TabOrder 
from spire.pdf.texts.TextAlign import TextAlign 
from spire.pdf.texts.TextFindParameter import TextFindParameter 
from spire.pdf.barcode.TextLocation import TextLocation 
from spire.pdf.PdfPageLabels import PdfPageLabels 
from spire.pdf.PdfApplicationData import PdfApplicationData 
from spire.pdf.PdfPieceInfo import PdfPieceInfo 
from spire.pdf.PdfConvertOptions import PdfConvertOptions 
from spire.pdf.texts.ReplaceActionType import ReplaceActionType 

from spire.pdf.PdfFileInfo import PdfFileInfo 

from spire.pdf.PdfPageTransition import PdfPageTransition 
from spire.pdf.PdfCollection import PdfCollection 
 
from spire.pdf.PdfDocumentPrivilege import PdfDocumentPrivilege 
from spire.pdf.PdfSecurityPolicy import PdfSecurityPolicy 
from spire.pdf.PdfPasswordSecurityPolicy import PdfPasswordSecurityPolicy 

from spire.pdf.PdfDocumentInformation import PdfDocumentInformation 
from spire.pdf.PdfViewerPreferences import PdfViewerPreferences 
from spire.pdf.PdfPageSize import PdfPageSize 

from spire.pdf.conversion.compression.ImageQuality import ImageQuality 

from spire.pdf.document.collections.PdfDocumentPageCollection import PdfDocumentPageCollection 
from spire.pdf.graphics.PdfMargins import PdfMargins 

from spire.pdf.PdfPageSettings import PdfPageSettings 

from spire.pdf.PdfBorders import PdfBorders 
from spire.pdf.PdfEdges import PdfEdges 
from spire.pdf.PdfPaddings import PdfPaddings 
 
from spire.pdf.tables.PdfColumnCollection import PdfColumnCollection 
from spire.pdf.tables.PdfColumn import PdfColumn 
from spire.pdf.tables.PdfRow import PdfRow 
from spire.pdf.tables.PdfRowCollection import PdfRowCollection 

from spire.pdf.graphics.PdfStringFormat import PdfStringFormat 
from spire.pdf.graphics.PdfFontBase import PdfFontBase 
from spire.pdf.lists.PdfMarkerBase import PdfMarkerBase 
from spire.pdf.lists.PdfOrderedMarker import PdfOrderedMarker 
from spire.pdf.lists.PdfMarker import PdfMarker 
from spire.pdf.lists.PdfListItem import PdfListItem 

from spire.pdf.lists.PdfListItemCollection import PdfListItemCollection 


from spire.pdf.graphics.PdfHtmlLayoutFormat import PdfHtmlLayoutFormat 
from spire.pdf.graphics.PdfBlendBase import PdfBlendBase 
from spire.pdf.graphics.PdfBlend import PdfBlend 

from spire.pdf.graphics.PdfBrush import PdfBrush 
from spire.pdf.graphics.PdfBrushes import PdfBrushes 
from spire.pdf.graphics.PdfColorBlend import PdfColorBlend 
from spire.pdf.graphics.PdfTextLayout import PdfTextLayout 

from spire.pdf.grid.PdfGridLayoutFormat import PdfGridLayoutFormat 
from spire.pdf.grid.PdfGridStyleBase import PdfGridStyleBase 
from spire.pdf.grid.PdfGridStyle import PdfGridStyle 
from spire.pdf.grid.PdfGridRowStyle import PdfGridRowStyle 
from spire.pdf.grid.PdfGridCellStyle import PdfGridCellStyle 
from spire.pdf.grid.PdfGridCell import PdfGridCell 
from spire.pdf.grid.PdfGridCellCollection import PdfGridCellCollection 
from spire.pdf.grid.PdfGridColumn import PdfGridColumn 
from spire.pdf.grid.PdfGridColumnCollection import PdfGridColumnCollection 
from spire.pdf.grid.PdfGridRow import PdfGridRow 
from spire.pdf.grid.PdfGridRowCollection import PdfGridRowCollection 
from spire.pdf.grid.PdfGridHeaderCollection import PdfGridHeaderCollection 

from spire.pdf.grid.PdfGridCellContent import PdfGridCellContent 
from spire.pdf.grid.PdfGridCellContentList import PdfGridCellContentList 

from spire.pdf.tables.PdfTableLayoutFormat import PdfTableLayoutFormat 


from spire.pdf.graphics.PdfRGBColor import PdfRGBColor 
from spire.pdf.colorspace.PdfColorSpaces import PdfColorSpaces 
from spire.pdf.colorspace.PdfComplexColor import PdfComplexColor
from spire.pdf.colorspace.PdfCalGrayColor import PdfCalGrayColor 
from spire.pdf.colorspace.PdfCalGrayColorSpace import PdfCalGrayColorSpace 
from spire.pdf.colorspace.PdfCalRGBColor import PdfCalRGBColor 
from spire.pdf.colorspace.PdfCalRGBColorSpace import PdfCalRGBColorSpace 

from spire.pdf.colorspace.PdfDeviceColorSpace import PdfDeviceColorSpace 
from spire.pdf.colorspace.PdfICCColor import PdfICCColor 
from spire.pdf.colorspace.PdfICCColorSpace import PdfICCColorSpace 
from spire.pdf.colorspace.PdfKnownColor import PdfKnownColor 
from spire.pdf.colorspace.PdfKnownColorSpace import PdfKnownColorSpace 
from spire.pdf.colorspace.PdfLabColor import PdfLabColor 
from spire.pdf.colorspace.PdfLabColorSpace import PdfLabColorSpace 
from spire.pdf.colorspace.PdfSeparationColor import PdfSeparationColor 
from spire.pdf.colorspace.PdfSeparationColorSpace import PdfSeparationColorSpace 

from spire.pdf.graphics.PdfGraphicsState import PdfGraphicsState 

from spire.pdf.graphics.PdfUnitConvertor import PdfUnitConvertor 

from spire.pdf.graphics.PdfGradientBrush import PdfGradientBrush 
from spire.pdf.graphics.PdfLinearGradientBrush import PdfLinearGradientBrush 
from spire.pdf.graphics.PdfRadialGradientBrush import PdfRadialGradientBrush 
from spire.pdf.graphics.PdfSolidBrush import PdfSolidBrush 

from spire.pdf.graphics.PdfPen import PdfPen
from spire.pdf.graphics.PdfPens import PdfPens 

from spire.pdf.tables.PdfCellStyle import PdfCellStyle 
from spire.pdf.tables.PdfTableStyle import PdfTableStyle

from spire.pdf.texts.PdfTextState import PdfTextState
from spire.pdf.texts.PdfTextFragment import PdfTextFragment 
from spire.pdf.texts.PdfTextFindOptions import PdfTextFindOptions 


from spire.pdf.texts.PdfTextExtractOptions import PdfTextExtractOptions

from spire.pdf.texts.SimpleTextExtractionStrategy import SimpleTextExtractionStrategy 

from spire.pdf.graphics.PdfCanvas import PdfCanvas

from spire.pdf.PdfPageTemplateElement import PdfPageTemplateElement 

from spire.pdf.PdfStampCollection import PdfStampCollection
from spire.pdf.PdfDocumentTemplate import PdfDocumentTemplate 
from spire.pdf.PdfSectionTemplate import PdfSectionTemplate 

from spire.pdf.graphics.PdfTilingBrush import PdfTilingBrush 

from spire.pdf.graphics.PdfLayoutResult import PdfLayoutResult

from spire.pdf.graphics.PdfGraphicsWidget import PdfGraphicsWidget
from spire.pdf.graphics.PdfLayoutWidget import PdfLayoutWidget
from spire.pdf.graphics.PdfShapeWidget import PdfShapeWidget

from spire.pdf.graphics.PdfTemplate import PdfTemplate 

from spire.pdf.graphics.PdfImage import PdfImage

from spire.pdf.PdfPageBase import PdfPageBase
from spire.pdf.texts.PdfTextReplaceOptions import PdfTextReplaceOptions 
from spire.pdf.texts.PdfTextReplacer import PdfTextReplacer 
from spire.pdf.texts.PdfTextExtractor import PdfTextExtractor
from spire.pdf.texts.PdfTextFinder import PdfTextFinder 
from spire.pdf.tables.PdfTableLayoutResult import PdfTableLayoutResult 
from spire.pdf.graphics.PdfLayoutHTMLResult import PdfLayoutHTMLResult 
from spire.pdf.grid.PdfGridLayoutResult import PdfGridLayoutResult 

from spire.pdf.grid.PdfGrid import PdfGrid 
from spire.pdf.lists.PdfListBase import PdfListBase
from spire.pdf.lists.PdfSortedList import PdfSortedList 
from spire.pdf.lists.PdfList import PdfList 
from spire.pdf.tables.PdfTable import PdfTable 
from spire.pdf.graphics.PdfMetafileLayoutFormat import PdfMetafileLayoutFormat 
 
from spire.pdf.graphics.PdfDrawWidget import PdfDrawWidget 
from spire.pdf.graphics.PdfFillElement import PdfFillElement
from spire.pdf.graphics.PdfPath import PdfPath 

from spire.pdf.graphics.PdfMask import PdfMask 
from spire.pdf.graphics.PdfColorMask import PdfColorMask

from spire.pdf.graphics.PdfBitmap import PdfBitmap
from spire.pdf.graphics.PdfTextLayoutResult import PdfTextLayoutResult 
from spire.pdf.graphics.PdfHTMLTextElement import PdfHTMLTextElement 
from spire.pdf.graphics.PdfTextWidget import PdfTextWidget 

from spire.pdf.graphics.PdfCjkStandardFont import PdfCjkStandardFont 
from spire.pdf.graphics.PdfTrueTypeFont import PdfTrueTypeFont 
from spire.pdf.graphics.LineInfo import LineInfo 
from spire.pdf.graphics.PdfStringLayoutResult import PdfStringLayoutResult 
from spire.pdf.graphics.PdfStringLayouter import PdfStringLayouter 
from spire.pdf.graphics.PdfMatrix import PdfMatrix 

from spire.pdf.utilities.PdfImageMask import PdfImageMask 
from spire.pdf.graphics.PdfMetafile import PdfMetafile 
from spire.pdf.graphics.layer.PdfLayer import PdfLayer 
from spire.pdf.graphics.layer.PdfLayerCollection import PdfLayerCollection 
from spire.pdf.graphics.layer.PdfLayerOutline import PdfLayerOutline 
from spire.pdf.graphics.fonts.PdfUsedFont import PdfUsedFont 
from spire.pdf.widget.XFAForm import XFAForm 
from spire.pdf.widget.XfaField import XfaField 
from spire.pdf.widget.XfaTextField import XfaTextField 
from spire.pdf.widget.XfaCheckButtonField import XfaCheckButtonField 
from spire.pdf.widget.XfaDateTimeField import XfaDateTimeField 
from spire.pdf.widget.XfaChoiceListField import XfaChoiceListField 
from spire.pdf.widget.XfaSignatureField import XfaSignatureField 
from spire.pdf.widget.XfaButtonField import XfaButtonField 
from spire.pdf.widget.XfaImageField import XfaImageField 
from spire.pdf.widget.XfaBarcodeField import XfaBarcodeField 
from spire.pdf.widget.XfaIntField import XfaIntField 
from spire.pdf.widget.XfaFloatField import XfaFloatField 
from spire.pdf.widget.XfaDoubleField import XfaDoubleField 
from spire.pdf.widget.PdfPageCollection import PdfPageCollection 
from spire.pdf.widget.PdfPageWidgetEnumerator import PdfPageWidgetEnumerator 
from spire.pdf.annotations.PdfAnnotation import PdfAnnotation 
 
from spire.pdf.widget.IPdfTextBoxField import IPdfTextBoxField 

from spire.pdf.fileds.PdfField import PdfField 

from spire.pdf.widget.PdfFieldWidget import PdfFieldWidget 

from spire.pdf.actions.PdfAction import PdfAction
from spire.pdf.actions.PdfJavaScriptAction import PdfJavaScriptAction
from spire.pdf.actions.PdfFieldActions import PdfFieldActions

from spire.pdf.widget.PdfStyledFieldWidget import PdfStyledFieldWidget 

from spire.pdf.widget.PdfFieldWidgetItem import PdfFieldWidgetItem 

from spire.pdf.widget.PdfStateWidgetItemCollection import PdfStateWidgetItemCollection

from spire.pdf.widget.PdfButtonWidgetWidgetItem import PdfButtonWidgetWidgetItem 
from spire.pdf.widget.PdfButtonWidgetItemCollection import PdfButtonWidgetItemCollection 
from spire.pdf.fileds.PdfButtonIconLayout import PdfButtonIconLayout 
from spire.pdf.widget.PdfButtonWidgetFieldWidget import PdfButtonWidgetFieldWidget

from spire.pdf.widget.PdfStateFieldWidget import PdfStateFieldWidget 
from spire.pdf.widget.PdfStateWidgetItem import PdfStateWidgetItem 
from spire.pdf.widget.PdfCheckBoxWidgetFieldWidget import PdfCheckBoxWidgetFieldWidget 
from spire.pdf.widget.PdfCheckBoxWidgetWidgetItemCollection import PdfCheckBoxWidgetWidgetItemCollection 
from spire.pdf.widget.PdfCheckBoxWidgetWidgetItem import PdfCheckBoxWidgetWidgetItem 
from spire.pdf.widget.PdfComboBoxWidgetWidgetItem import PdfComboBoxWidgetWidgetItem 
from spire.pdf.widget.PdfComboBoxWidgetItemCollection import PdfComboBoxWidgetItemCollection 
from spire.pdf.widget.PdfStateItemCollection import PdfStateItemCollection 

from spire.pdf.fileds.PdfForm import PdfForm 

from spire.pdf.fileds.PdfFieldCollection import PdfFieldCollection

from spire.pdf.annotations.PdfAnnotationWidget import PdfAnnotationWidget

from spire.pdf.annotations.PdfStyledAnnotationWidget import PdfStyledAnnotationWidget

from spire.pdf.annotations.PdfMarkUpAnnotationWidget import PdfMarkUpAnnotationWidget

from spire.pdf.fileds.PdfRadioButtonListFieldWidget import PdfRadioButtonListFieldWidget 
from spire.pdf.widget.PdfTextBoxFieldWidget import PdfTextBoxFieldWidget 
from spire.pdf.annotations.PdfRubberStampAnnotationWidget import PdfRubberStampAnnotationWidget


from spire.pdf.widget.PdfListFieldWidgetItem import PdfListFieldWidgetItem 
from spire.pdf.widget.PdfListWidgetFieldItemCollection import PdfListWidgetFieldItemCollection 
from spire.pdf.widget.PdfListWidgetItem import PdfListWidgetItem 
from spire.pdf.widget.PdfListWidgetItemCollection import PdfListWidgetItemCollection 
from spire.pdf.widget.PdfRadioButtonWidgetItem import PdfRadioButtonWidgetItem
from spire.pdf.widget.PdfRadioButtonWidgetWidgetItemCollection import PdfRadioButtonWidgetWidgetItemCollection 
from spire.pdf.widget.PdfChoiceWidgetFieldWidget import PdfChoiceWidgetFieldWidget 
from spire.pdf.widget.PdfListBoxWidgetFieldWidget import PdfListBoxWidgetFieldWidget
from spire.pdf.widget.PdfComboBoxWidgetFieldWidget import PdfComboBoxWidgetFieldWidget

from spire.pdf.widget.PdfSignatureFieldWidget import PdfSignatureFieldWidget
from spire.pdf.widget.PdfFormFieldWidgetCollection import PdfFormFieldWidgetCollection 
from spire.pdf.widget.PdfFormWidget import PdfFormWidget 

from spire.pdf.fileds.PdfFormFieldCollection import PdfFormFieldCollection 

from spire.pdf.widget.PdfFieldWidgetImportError import PdfFieldWidgetImportError 
 
from spire.pdf.widget.PdfTexBoxWidgetItem import PdfTexBoxWidgetItem 
from spire.pdf.widget.PdfTextBoxWidgetItemCollection import PdfTextBoxWidgetItemCollection 
from spire.pdf.fileds.IPdfComboBoxField import IPdfComboBoxField 
from spire.pdf.fileds.PdfSignatureStyledField import PdfSignatureStyledField 



from spire.pdf.fileds.PdfStyledField import PdfStyledField
from spire.pdf.fileds.PdfCheckFieldBase import PdfCheckFieldBase 

from spire.pdf.fileds.PdfAppearanceField import PdfAppearanceField 
from spire.pdf.fileds.PdfButtonField import PdfButtonField 

from spire.pdf.fileds.PdfCheckBoxField import PdfCheckBoxField 
 
from spire.pdf.fileds.PdfListFieldItem import PdfListFieldItem 
from spire.pdf.fileds.PdfListFieldItemCollection import PdfListFieldItemCollection
from spire.pdf.fileds.PdfListField import PdfListField
from spire.pdf.fileds.PdfComboBoxField import PdfComboBoxField

from spire.pdf.fileds.PdfListBoxField import PdfListBoxField

from spire.pdf.fileds.PdfRadioButtonItemCollection import PdfRadioButtonItemCollection 
from spire.pdf.fileds.PdfRadioButtonListField import PdfRadioButtonListField 
from spire.pdf.fileds.PdfRadioButtonListItem import PdfRadioButtonListItem 

from spire.pdf.fileds.PdfSignatureAppearanceField import PdfSignatureAppearanceField 
from spire.pdf.fileds.PdfSignatureField import PdfSignatureField 
 
from spire.pdf.fileds.PdfTextBoxField import PdfTextBoxField 
from spire.pdf.general.PdfDestination import PdfDestination 

#class PdfBookmarkCollection (  IEnumerable) :
#    pass
from spire.pdf.bookmarks.PdfBookmark import PdfBookmark
from spire.pdf.bookmarks.PdfBookmarkCollection import PdfBookmarkCollection 
 
from spire.pdf.bookmarks.PdfBookmarkWidget import PdfBookmarkWidget
from spire.pdf.collections.PdfFolder import PdfFolder 
 
from spire.pdf.automaticfields.PdfAutomaticField import PdfAutomaticField
 
from spire.pdf.automaticfields.PdfDynamicField import PdfDynamicField 
 
from spire.pdf.automaticfields.PdfMultipleValueField import PdfMultipleValueField
from spire.pdf.automaticfields.PdfCompositeField import PdfCompositeField
from spire.pdf.automaticfields.PdfMultipleNumberValueField import PdfMultipleNumberValueField 
 
from spire.pdf.automaticfields.PdfPageNumberField import PdfPageNumberField 
from spire.pdf.automaticfields.PdfSectionNumberField import PdfSectionNumberField 
from spire.pdf.automaticfields.PdfSectionPageCountField import PdfSectionPageCountField 
from spire.pdf.automaticfields.PdfSectionPageNumberField import PdfSectionPageNumberField 
from spire.pdf.automaticfields.PdfSingleValueField import PdfSingleValueField 
from spire.pdf.automaticfields.PdfPageCountField import PdfPageCountField
from spire.pdf.automaticfields.PdfDocumentAuthorField import PdfDocumentAuthorField
from spire.pdf.automaticfields.PdfStaticField import PdfStaticField 
 
from spire.pdf.automaticfields.PdfCreationDateField import PdfCreationDateField 
from spire.pdf.automaticfields.PdfDateTimeField import PdfDateTimeField 
from spire.pdf.automaticfields.PdfDestinationPageNumberField import PdfDestinationPageNumberField

from spire.pdf.general.PdfFileSpecificationBase import PdfFileSpecificationBase
from spire.pdf.general.PdfEmbeddedFileSpecification import PdfEmbeddedFileSpecification

from spire.pdf.barcode.PdfBarcodeQuietZones import PdfBarcodeQuietZones 
from spire.pdf.barcode.PdfBarcode import PdfBarcode 
from spire.pdf.barcode.PdfBarcodeException import PdfBarcodeException 

from spire.pdf.barcode.PdfUnidimensionalBarcode import PdfUnidimensionalBarcode
from spire.pdf.barcode.PdfCodabarBarcode import PdfCodabarBarcode 
from spire.pdf.barcode.PdfCode11Barcode import PdfCode11Barcode 
from spire.pdf.barcode.PdfCode128ABarcode import PdfCode128ABarcode 
from spire.pdf.barcode.PdfCode128BBarcode import PdfCode128BBarcode 
from spire.pdf.barcode.PdfCode128CBarcode import PdfCode128CBarcode 
from spire.pdf.barcode.PdfCode39Barcode import PdfCode39Barcode 
from spire.pdf.barcode.PdfCode32Barcode import PdfCode32Barcode 

from spire.pdf.barcode.PdfCode39ExtendedBarcode import PdfCode39ExtendedBarcode 
from spire.pdf.barcode.PdfCode93Barcode import PdfCode93Barcode 
from spire.pdf.barcode.PdfCode93ExtendedBarcode import PdfCode93ExtendedBarcode 
 
from spire.pdf.lists.PdfList import PdfList 

from spire.pdf.graphics.PdfFont import PdfFont 
from spire.pdf.conversion.PdfToHtmlParameter import PdfToHtmlParameter 
from spire.pdf.annotations.Pdf3DActivation import Pdf3DActivation 
from spire.pdf.annotations.Pdf3DAnimation import Pdf3DAnimation 
from spire.pdf.annotations.Pdf3DBackground import Pdf3DBackground 
from spire.pdf.annotations.Pdf3DCrossSection import Pdf3DCrossSection 
from spire.pdf.annotations.Pdf3DCrossSectionCollection import Pdf3DCrossSectionCollection 
from spire.pdf.annotations.Pdf3DLighting import Pdf3DLighting 
from spire.pdf.annotations.Pdf3DNode import Pdf3DNode 
from spire.pdf.annotations.Pdf3DNodeCollection import Pdf3DNodeCollection 
from spire.pdf.annotations.Pdf3DProjection import Pdf3DProjection 
from spire.pdf.annotations.Pdf3DRendermode import Pdf3DRendermode 
from spire.pdf.annotations.Pdf3DView import Pdf3DView 
from spire.pdf.annotations.Pdf3DViewCollection import Pdf3DViewCollection 

from spire.pdf.annotations.LineBorder import LineBorder 

from spire.pdf.annotations.PdfLinkAnnotation import PdfLinkAnnotation 
from spire.pdf.annotations.PdfActionLinkAnnotation import PdfActionLinkAnnotation 
from spire.pdf.annotations.PdfActionAnnotation import PdfActionAnnotation
from spire.pdf.annotations.PdfFreeTextAnnotation import PdfFreeTextAnnotation 
from spire.pdf.annotations.PdfLineAnnotation import PdfLineAnnotation 
 


from spire.pdf.annotations.PdfFileAnnotation import PdfFileAnnotation
from spire.pdf.annotations.Pdf3DAnnotation import Pdf3DAnnotation 
from spire.pdf.annotations.PdfInkAnnotation import PdfInkAnnotation 
from spire.pdf.annotations.PdfInkAnnotationWidget import PdfInkAnnotationWidget 
from spire.pdf.annotations.PdfPolygonAnnotation import PdfPolygonAnnotation 
from spire.pdf.annotations.PdfPolyLineAnnotation import PdfPolyLineAnnotation 
from spire.pdf.annotations.PdfRubberStampAnnotation import PdfRubberStampAnnotation 
from spire.pdf.annotations.PdfWatermarkAnnotation import PdfWatermarkAnnotation 
from spire.pdf.annotations.PdfTextWebLink import PdfTextWebLink 
from spire.pdf.annotations.PdfTextMarkupAnnotation import PdfTextMarkupAnnotation 
 
from spire.pdf.annotations.PdfAttachmentAnnotationWidget import PdfAttachmentAnnotationWidget 
from spire.pdf.annotations.PdfCaretAnnotationWidget import PdfCaretAnnotationWidget 
from spire.pdf.annotations.PdfDocumentLinkAnnotationWidget import PdfDocumentLinkAnnotationWidget 
from spire.pdf.annotations.PdfFileLinkAnnotationWidget import PdfFileLinkAnnotationWidget 
from spire.pdf.annotations.PdfFreeTextAnnotationWidget import PdfFreeTextAnnotationWidget 
from spire.pdf.annotations.PdfLineAnnotationWidget import PdfLineAnnotationWidget 
 
from spire.pdf.annotations.PdfPolygonAndPolyLineAnnotationWidget import PdfPolygonAndPolyLineAnnotationWidget 
from spire.pdf.annotations.PdfPolygonAnnotationWidget import PdfPolygonAnnotationWidget 
from spire.pdf.annotations.PdfPolyLineAnnotationWidget import PdfPolyLineAnnotationWidget 
from spire.pdf.annotations.PdfPopupAnnotationWidget import PdfPopupAnnotationWidget 
from spire.pdf.annotations.PdfSoundAnnotationWidget import PdfSoundAnnotationWidget 
from spire.pdf.annotations.PdfSquareAnnotationWidget import PdfSquareAnnotationWidget 
 
from spire.pdf.annotations.PdfTextAnnotationWidget import PdfTextAnnotationWidget 
from spire.pdf.annotations.PdfTextMarkupAnnotationWidget import PdfTextMarkupAnnotationWidget 
from spire.pdf.annotations.PdfTextWebLinkAnnotationWidget import PdfTextWebLinkAnnotationWidget 
from spire.pdf.annotations.PdfUriAnnotationWidget import PdfUriAnnotationWidget 
from spire.pdf.annotations.PdfWatermarkAnnotationWidget import PdfWatermarkAnnotationWidget 
from spire.pdf.annotations.PdfWebLinkAnnotationWidget import PdfWebLinkAnnotationWidget 
from spire.pdf.annotations.PdfAnnotationBorder import PdfAnnotationBorder 
from spire.pdf.annotations.PdfAttachmentAnnotation import PdfAttachmentAnnotation 
from spire.pdf.annotations.PdfDocumentLinkAnnotation import PdfDocumentLinkAnnotation 
 
from spire.pdf.annotations.PdfFileLinkAnnotation import PdfFileLinkAnnotation 
from spire.pdf.annotations.PdfPopupAnnotation import PdfPopupAnnotation 
from spire.pdf.annotations.PdfSoundAnnotation import PdfSoundAnnotation 
from spire.pdf.annotations.PdfUriAnnotation import PdfUriAnnotation 
from spire.pdf.annotations.appearance.PdfAppearanceState import PdfAppearanceState 
from spire.pdf.annotations.appearance.PdfAppearance import PdfAppearance 
from spire.pdf.annotations.appearance.PdfExtendedAppearance import PdfExtendedAppearance 
 
from spire.pdf.annotations.PdfAnnotationCollection import PdfAnnotationCollection 
from spire.pdf.annotations.PdfAnnotationWidgetCollection import PdfAnnotationWidgetCollection

 
from spire.pdf.actions.PdfActionCollection import PdfActionCollection
from spire.pdf.actions.PdfFormAction import PdfFormAction 
from spire.pdf.actions.PdfGoToAction import PdfGoToAction 
from spire.pdf.actions.PdfGotoNameAction import PdfGotoNameAction 
 
from spire.pdf.actions.PdfJavaScript import PdfJavaScript 
from spire.pdf.actions.PdfLaunchAction import PdfLaunchAction 
from spire.pdf.actions.PdfNamedAction import PdfNamedAction 
from spire.pdf.actions.PdfAnnotationActions import PdfAnnotationActions 
from spire.pdf.actions.PdfDocumentActions import PdfDocumentActions 
from spire.pdf.actions.PdfEmbeddedGoToAction import PdfEmbeddedGoToAction 
 
from spire.pdf.actions.PdfResetAction import PdfResetAction 

from spire.pdf.general.PdfSound import PdfSound 
from spire.pdf.actions.PdfSoundAction import PdfSoundAction 
from spire.pdf.actions.PdfSubmitAction import PdfSubmitAction 
from spire.pdf.actions.PdfUriAction import PdfUriAction 
from spire.pdf.utilities.BookletOptions import BookletOptions 
from spire.pdf.utilities.MergerOptions import MergerOptions 
 
from spire.pdf.utilities.Utilities_PdfImageInfo import Utilities_PdfImageInfo 
from spire.pdf.utilities.PdfImageHelper import PdfImageHelper 
from spire.pdf.utilities.PdfMerger import PdfMerger 
from spire.pdf.utilities.Utilities_PdfTable import Utilities_PdfTable 
 
from spire.pdf.interchange.taggedpdf import PdfTaggedContent 
from spire.pdf.interchange.taggedpdf.PdfStructureTreeRoot import PdfStructureTreeRoot 
from spire.pdf.interchange.taggedpdf.ArtifactPropertyList import ArtifactPropertyList 
from spire.pdf.interchange.taggedpdf.PdfStandardStructTypes import PdfStandardStructTypes 
from spire.pdf.interchange.taggedpdf.PdfAttributeOwner import PdfAttributeOwner 
from spire.pdf.interchange.taggedpdf.PdfStructureAttributes import PdfStructureAttributes 
from spire.pdf.interchange.taggedpdf.PdfStructContentItem import PdfStructContentItem 
from spire.pdf.interchange.taggedpdf.IStructureNode import IStructureNode 
from spire.pdf.interchange.taggedpdf.PdfStructureElement import PdfStructureElement 
from spire.pdf.interactive.digitalSignatures.PdfSignatureProperties import PdfSignatureProperties 
from spire.pdf.interactive.digitalSignatures.IPdfSignatureFormatter import IPdfSignatureFormatter 
from spire.pdf.security.Security_IPdfSignatureFormatter import Security_IPdfSignatureFormatter
from spire.pdf.interactive.digitalSignatures.PdfPKCS1Formatter import PdfPKCS1Formatter 
from spire.pdf.interactive.digitalSignatures.PdfPKCS7Formatter import PdfPKCS7Formatter 

from spire.pdf.interactive.digitalSignatures.ITSAService import ITSAService
from spire.pdf.interactive.digitalSignatures.TSAHttpService import TSAHttpService 
from spire.pdf.interactive.digitalSignatures.IOCSPService import IOCSPService
from spire.pdf.interactive.digitalSignatures.OCSPHttpService import OCSPHttpService 

from spire.pdf.interactive.digitalSignatures.IPdfSignatureAppearance import IPdfSignatureAppearance
from spire.pdf.interactive.digitalSignatures.PdfSignature import PdfSignature 
from spire.pdf.interactive.digitalSignatures.PdfSignatureMaker import PdfSignatureMaker
 
from spire.pdf.interactive.digitalSignatures.PdfSignatureAppearance import PdfSignatureAppearance 
from spire.pdf.interactive.digitalSignatures.PdfCustomAppearance import PdfCustomAppearance 



from spire.pdf.conversion.DocxOptions import DocxOptions 
from spire.pdf.conversion.OfdConverter import OfdConverter 
from spire.pdf.conversion.PdfToDocConverter import PdfToDocConverter 
from spire.pdf.conversion.PdfToWordConverter import PdfToWordConverter 
from spire.pdf.conversion.PdfToLinearizedPdfConverter import PdfToLinearizedPdfConverter 
from spire.pdf.conversion.PdfGrayConverter import PdfGrayConverter 
from spire.pdf.conversion.PdfStandardsConverter import PdfStandardsConverter 

from spire.pdf.conversion.XlsxOptions import XlsxOptions
from spire.pdf.conversion.XlsxLineLayoutOptions import XlsxLineLayoutOptions 
 
from spire.pdf.conversion.XlsxTextLayoutOptions import XlsxTextLayoutOptions 

from spire.pdf.conversion.compression.OptimizationOptions import OptimizationOptions 
from spire.pdf.conversion.compression.PdfCompressor import PdfCompressor 

from spire.pdf.exceptions.PdfException import PdfException 
from spire.pdf.exceptions.PdfDocumentException import PdfDocumentException 
from spire.pdf.tables.PdfTableException import PdfTableException 
from spire.pdf.exceptions.PdfConformanceException import PdfConformanceException 
from spire.pdf.annotations.PdfAnnotationException import PdfAnnotationException 
 
from spire.pdf.security.PdfCertificate import PdfCertificate 
from spire.pdf.security.PdfSecurity import PdfSecurity 

from spire.pdf.PdfPageWidget import PdfPageWidget 
from spire.pdf.PdfNewPage import PdfNewPage 
from spire.pdf.PdfSectionPageCollection import PdfSectionPageCollection 
from spire.pdf.PdfSection import PdfSection 
from spire.pdf.PdfSectionCollection import PdfSectionCollection 

from spire.pdf.attachments.PdfAttachment import PdfAttachment 
from spire.pdf.document.collections.Collections_PdfCollection import Collections_PdfCollection 
from spire.pdf.attachments.PdfAttachmentCollection import PdfAttachmentCollection

from spire.pdf.PdfDocumentBase import PdfDocumentBase 
from spire.pdf.PdfDocument import PdfDocument 

from spire.pdf.tables.PdfTableExtractor import PdfTableExtractor 
from spire.pdf.utilities.PdfBookletCreator import PdfBookletCreator

from spire.pdf.PdfNewDocument import PdfNewDocument

from spire.pdf.comparison.PdfCompareOptions import PdfCompareOptions 
from spire.pdf.comparison.PdfComparer import PdfComparer 
from spire.pdf.interactive.digitalSignatures.PdfOrdinarySignatureMaker import PdfOrdinarySignatureMaker 
from spire.pdf.interactive.digitalSignatures.PdfMDPSignatureMaker import PdfMDPSignatureMaker

from spire.pdf.security.Security_PdfSignature import Security_PdfSignature 
 