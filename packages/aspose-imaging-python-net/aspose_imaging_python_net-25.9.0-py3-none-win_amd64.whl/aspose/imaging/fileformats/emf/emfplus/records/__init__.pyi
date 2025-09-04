"""The namespace contains types [MS-EMFPLUS]: Enhanced Metafile Format Plus Extensions
            2.3 EMF+ Records"""
from typing import List, Optional, Dict, Iterable
import enum
import aspose.pycore
import aspose.pydrawing
import aspose.imaging
import aspose.imaging.apsbuilder
import aspose.imaging.apsbuilder.dib
import aspose.imaging.asynctask
import aspose.imaging.brushes
import aspose.imaging.dithering
import aspose.imaging.exif
import aspose.imaging.exif.enums
import aspose.imaging.extensions
import aspose.imaging.fileformats
import aspose.imaging.fileformats.apng
import aspose.imaging.fileformats.avif
import aspose.imaging.fileformats.bigtiff
import aspose.imaging.fileformats.bmp
import aspose.imaging.fileformats.bmp.structures
import aspose.imaging.fileformats.cdr
import aspose.imaging.fileformats.cdr.const
import aspose.imaging.fileformats.cdr.enum
import aspose.imaging.fileformats.cdr.objects
import aspose.imaging.fileformats.cdr.types
import aspose.imaging.fileformats.cmx
import aspose.imaging.fileformats.cmx.objectmodel
import aspose.imaging.fileformats.cmx.objectmodel.enums
import aspose.imaging.fileformats.cmx.objectmodel.specs
import aspose.imaging.fileformats.cmx.objectmodel.styles
import aspose.imaging.fileformats.core
import aspose.imaging.fileformats.core.vectorpaths
import aspose.imaging.fileformats.dicom
import aspose.imaging.fileformats.djvu
import aspose.imaging.fileformats.dng
import aspose.imaging.fileformats.dng.decoder
import aspose.imaging.fileformats.emf
import aspose.imaging.fileformats.emf.dtyp
import aspose.imaging.fileformats.emf.dtyp.commondatastructures
import aspose.imaging.fileformats.emf.emf
import aspose.imaging.fileformats.emf.emf.consts
import aspose.imaging.fileformats.emf.emf.objects
import aspose.imaging.fileformats.emf.emf.records
import aspose.imaging.fileformats.emf.emfplus
import aspose.imaging.fileformats.emf.emfplus.consts
import aspose.imaging.fileformats.emf.emfplus.objects
import aspose.imaging.fileformats.emf.emfplus.records
import aspose.imaging.fileformats.emf.emfspool
import aspose.imaging.fileformats.emf.emfspool.records
import aspose.imaging.fileformats.emf.graphics
import aspose.imaging.fileformats.eps
import aspose.imaging.fileformats.eps.consts
import aspose.imaging.fileformats.gif
import aspose.imaging.fileformats.gif.blocks
import aspose.imaging.fileformats.ico
import aspose.imaging.fileformats.jpeg
import aspose.imaging.fileformats.jpeg2000
import aspose.imaging.fileformats.opendocument
import aspose.imaging.fileformats.opendocument.enums
import aspose.imaging.fileformats.opendocument.objects
import aspose.imaging.fileformats.opendocument.objects.brush
import aspose.imaging.fileformats.opendocument.objects.font
import aspose.imaging.fileformats.opendocument.objects.graphic
import aspose.imaging.fileformats.opendocument.objects.pen
import aspose.imaging.fileformats.pdf
import aspose.imaging.fileformats.png
import aspose.imaging.fileformats.psd
import aspose.imaging.fileformats.svg
import aspose.imaging.fileformats.svg.graphics
import aspose.imaging.fileformats.tga
import aspose.imaging.fileformats.tiff
import aspose.imaging.fileformats.tiff.enums
import aspose.imaging.fileformats.tiff.filemanagement
import aspose.imaging.fileformats.tiff.filemanagement.bigtiff
import aspose.imaging.fileformats.tiff.instancefactory
import aspose.imaging.fileformats.tiff.pathresources
import aspose.imaging.fileformats.tiff.tifftagtypes
import aspose.imaging.fileformats.webp
import aspose.imaging.fileformats.wmf
import aspose.imaging.fileformats.wmf.consts
import aspose.imaging.fileformats.wmf.graphics
import aspose.imaging.fileformats.wmf.objects
import aspose.imaging.fileformats.wmf.objects.escaperecords
import aspose.imaging.imagefilters
import aspose.imaging.imagefilters.complexutils
import aspose.imaging.imagefilters.convolution
import aspose.imaging.imagefilters.filteroptions
import aspose.imaging.imageloadoptions
import aspose.imaging.imageoptions
import aspose.imaging.interfaces
import aspose.imaging.magicwand
import aspose.imaging.magicwand.imagemasks
import aspose.imaging.masking
import aspose.imaging.masking.options
import aspose.imaging.masking.result
import aspose.imaging.memorymanagement
import aspose.imaging.multithreading
import aspose.imaging.palettehelper
import aspose.imaging.progressmanagement
import aspose.imaging.shapes
import aspose.imaging.shapesegments
import aspose.imaging.sources
import aspose.imaging.watermark
import aspose.imaging.watermark.options
import aspose.imaging.xmp
import aspose.imaging.xmp.schemas
import aspose.imaging.xmp.schemas.dicom
import aspose.imaging.xmp.schemas.dublincore
import aspose.imaging.xmp.schemas.pdf
import aspose.imaging.xmp.schemas.photoshop
import aspose.imaging.xmp.schemas.xmpbaseschema
import aspose.imaging.xmp.schemas.xmpdm
import aspose.imaging.xmp.schemas.xmpmm
import aspose.imaging.xmp.schemas.xmprm
import aspose.imaging.xmp.types
import aspose.imaging.xmp.types.basic
import aspose.imaging.xmp.types.complex
import aspose.imaging.xmp.types.complex.colorant
import aspose.imaging.xmp.types.complex.dimensions
import aspose.imaging.xmp.types.complex.font
import aspose.imaging.xmp.types.complex.resourceevent
import aspose.imaging.xmp.types.complex.resourceref
import aspose.imaging.xmp.types.complex.thumbnail
import aspose.imaging.xmp.types.complex.version
import aspose.imaging.xmp.types.derived

class EmfPlusBeginContainer(EmfPlusStateRecordType):
    '''The EmfPlusBeginContainer record opens a new graphics state container and specifies a transform for it.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def page_unit(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType:
        ...
    
    @property
    def dest_rect(self) -> aspose.imaging.RectangleF:
        ...
    
    @dest_rect.setter
    def dest_rect(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def src_rect(self) -> aspose.imaging.RectangleF:
        ...
    
    @src_rect.setter
    def src_rect(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def stack_index(self) -> int:
        ...
    
    @stack_index.setter
    def stack_index(self, value : int):
        ...
    
    ...

class EmfPlusBeginContainerNoParams(EmfPlusStateRecordType):
    '''The EmfPlusBeginContainerNoParams record opens a new graphics state container.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def stack_index(self) -> int:
        ...
    
    @stack_index.setter
    def stack_index(self, value : int):
        ...
    
    ...

class EmfPlusClear(EmfPlusDrawingRecordType):
    '''The EmfPlusClear record clears the output coordinate space and initializes it with a background color and transparency'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def argb_32_color(self) -> int:
        ...
    
    @argb_32_color.setter
    def argb_32_color(self, value : int):
        ...
    
    ...

class EmfPlusClippingRecordType(EmfPlusRecord):
    '''The clipping record types specify clipping regions and operations.'''
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusComment(EmfPlusRecord):
    '''The EmfPlusComment record specifies arbitrary private data.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that is not used. This field SHOULD be set to zero
        and MUST be ignored upon receipt'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that is not used. This field SHOULD be set to zero
        and MUST be ignored upon receipt'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def private_data(self) -> bytes:
        ...
    
    @private_data.setter
    def private_data(self, value : bytes):
        ...
    
    ...

class EmfPlusControlRecordType(EmfPlusRecord):
    '''The control record types specify global parameters for EMF+ metafile processing.'''
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusDrawArc(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawArc record specifies drawing the arc of an ellipse.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets the size.
        A 32-bit unsigned integer that specifies the 32-bit-aligned number of
        bytes in the entire record, including the 12-byte record header and
        record-specific data. For this record type, the value MUST be one of the following:
        0x0000001C  If the C bit is set in the Flags field.
        0x00000024  If the C bit is clear in the Flags field'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets the size.
        A 32-bit unsigned integer that specifies the 32-bit-aligned number of
        bytes in the entire record, including the 12-byte record header and
        record-specific data. For this record type, the value MUST be one of the following:
        0x0000001C  If the C bit is set in the Flags field.
        0x00000024  If the C bit is clear in the Flags field'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def rect_float(self) -> bool:
        ...
    
    @rect_float.setter
    def rect_float(self, value : bool):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @start_angle.setter
    def start_angle(self, value : float):
        ...
    
    @property
    def sweep_angle(self) -> float:
        ...
    
    @sweep_angle.setter
    def sweep_angle(self, value : float):
        ...
    
    @property
    def rectangle_data(self) -> aspose.imaging.RectangleF:
        ...
    
    @rectangle_data.setter
    def rectangle_data(self, value : aspose.imaging.RectangleF):
        ...
    
    ...

class EmfPlusDrawBeziers(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawBeziers record specifies drawing a sequence of connected Bezier curves.
    The order for Bezier data points is the start point, control point 1,
    control point 2 and end point. For more information see [MSDN-DrawBeziers].'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether the PointData is compressed.
        If set, PointData specifies absolute locations in the coordinate space with
        16-bit integer coordinates. If clear, PointData specifies absolute locations
        in the coordinate space with 32-bit floating-point coordinates.
        Note If the Relative flag (below) is set, this flag is undefined and MUST be ignored.'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether the PointData is compressed.
        If set, PointData specifies absolute locations in the coordinate space with
        16-bit integer coordinates. If clear, PointData specifies absolute locations
        in the coordinate space with 32-bit floating-point coordinates.
        Note If the Relative flag (below) is set, this flag is undefined and MUST be ignored.'''
        ...
    
    @property
    def relative(self) -> bool:
        '''Gets a value indicating whether the PointData is relative.
        If set, each element in PointData specifies a location in the coordinate space
        that is relative to the location specified by the previous element in the array.
        In the case of the first element in PointData, a previous location at coordinates
        (0,0) is assumed. If clear, PointData specifies absolute locations according
        to the C flag.
        Note If this flag is set, the C flag (above) is undefined and MUST be ignored.'''
        ...
    
    @relative.setter
    def relative(self, value : bool):
        '''Sets a value indicating whether the PointData is relative.
        If set, each element in PointData specifies a location in the coordinate space
        that is relative to the location specified by the previous element in the array.
        In the case of the first element in PointData, a previous location at coordinates
        (0,0) is assumed. If clear, PointData specifies absolute locations according
        to the C flag.
        Note If this flag is set, the C flag (above) is undefined and MUST be ignored.'''
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def point_data(self) -> List[aspose.imaging.PointF]:
        ...
    
    @point_data.setter
    def point_data(self, value : List[aspose.imaging.PointF]):
        ...
    
    ...

class EmfPlusDrawClosedCurve(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawClosedCurve record specifies drawing a closed cardinal spline'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        RecordType - A 16-bit unsigned integer that identifies this record type as EmfPlusDrawClosedCurve
        from the RecordType enumeration (section 2.1.1.1). The value MUST be 0x4017.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether this  is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit integer coordinates.
        If clear, PointData specifies absolute locations in the coordinate space with 32-bit floating-point coordinates
        Note If the Relative flag (below) is set, this flag is undefined and MUST be ignored'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether this  is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit integer coordinates.
        If clear, PointData specifies absolute locations in the coordinate space with 32-bit floating-point coordinates
        Note If the Relative flag (below) is set, this flag is undefined and MUST be ignored'''
        ...
    
    @property
    def relative(self) -> bool:
        '''Gets a value indicating whether this  is relative.
        This bit indicates whether the PointData field specifies relative or absolute locations.
        If set, each element in PointData specifies a location in the coordinate space that is relative
        to the location specified by the previous element in the array. In the case of the first
        element in PointData, a previous location at coordinates (0,0) is assumed. If clear,
        PointData specifies absolute locations according to the C flag.
        Note If this flag is set, the Compressed flag (above) is undefined and MUST be ignored'''
        ...
    
    @relative.setter
    def relative(self, value : bool):
        '''Sets a value indicating whether this  is relative.
        This bit indicates whether the PointData field specifies relative or absolute locations.
        If set, each element in PointData specifies a location in the coordinate space that is relative
        to the location specified by the previous element in the array. In the case of the first
        element in PointData, a previous location at coordinates (0,0) is assumed. If clear,
        PointData specifies absolute locations according to the C flag.
        Note If this flag is set, the Compressed flag (above) is undefined and MUST be ignored'''
        ...
    
    @property
    def tension(self) -> float:
        '''Gets the tension
        A 32-bit floating point number that specifies how tightly the spline
        bends as it passes through the points. A value of 0 specifies that
        the spline is a sequence of straight lines. As the value increases,
        the curve becomes more rounded. For more information, see [SPLINE77] and [PETZOLD].'''
        ...
    
    @tension.setter
    def tension(self, value : float):
        '''Sets the tension
        A 32-bit floating point number that specifies how tightly the spline
        bends as it passes through the points. A value of 0 specifies that
        the spline is a sequence of straight lines. As the value increases,
        the curve becomes more rounded. For more information, see [SPLINE77] and [PETZOLD].'''
        ...
    
    @property
    def point_data(self) -> List[aspose.imaging.PointF]:
        ...
    
    @point_data.setter
    def point_data(self, value : List[aspose.imaging.PointF]):
        ...
    
    ...

class EmfPlusDrawCurve(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawCurve record specifies drawing a cardinal spline
    NOTE: ObjectID (1 byte): The index of an EmfPlusPen object (section 2.2.1.7)
    in the EMF+ Object Table to draw the curve. The value MUST be zero to 63, inclusive.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether this  is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit integer coordinates.
        If clear, PointData specifies absolute locations in the coordinate space with 32-bit floating-point coordinates
        Note If the Relative flag (below) is set, this flag is undefined and MUST be ignored'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether this  is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit integer coordinates.
        If clear, PointData specifies absolute locations in the coordinate space with 32-bit floating-point coordinates
        Note If the Relative flag (below) is set, this flag is undefined and MUST be ignored'''
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def tension(self) -> float:
        '''Gets the tension
        A 32-bit floating point number that specifies how tightly the spline
        bends as it passes through the points. A value of 0 specifies that
        the spline is a sequence of straight lines. As the value increases,
        the curve becomes more rounded. For more information, see [SPLINE77] and [PETZOLD].'''
        ...
    
    @tension.setter
    def tension(self, value : float):
        '''Sets the tension
        A 32-bit floating point number that specifies how tightly the spline
        bends as it passes through the points. A value of 0 specifies that
        the spline is a sequence of straight lines. As the value increases,
        the curve becomes more rounded. For more information, see [SPLINE77] and [PETZOLD].'''
        ...
    
    @property
    def num_segments(self) -> int:
        ...
    
    @num_segments.setter
    def num_segments(self, value : int):
        ...
    
    @property
    def point_data(self) -> List[aspose.imaging.PointF]:
        ...
    
    @point_data.setter
    def point_data(self, value : List[aspose.imaging.PointF]):
        ...
    
    ...

class EmfPlusDrawDriverString(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawDriverString record specifies text output with character positions.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def brush_id(self) -> int:
        ...
    
    @brush_id.setter
    def brush_id(self, value : int):
        ...
    
    @property
    def driver_string_options_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusDriverStringOptionsFlags:
        ...
    
    @driver_string_options_flags.setter
    def driver_string_options_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusDriverStringOptionsFlags):
        ...
    
    @property
    def glyph_count(self) -> int:
        ...
    
    @glyph_count.setter
    def glyph_count(self, value : int):
        ...
    
    @property
    def glyph_pos(self) -> List[aspose.imaging.PointF]:
        ...
    
    @glyph_pos.setter
    def glyph_pos(self, value : List[aspose.imaging.PointF]):
        ...
    
    @property
    def glyphs(self) -> List[int]:
        '''Gets the glyphs array
        An array of 16-bit values that define the text string to draw.
        If the DriverStringOptionsCmapLookup flag in the DriverStringOptionsFlags field is set, each value in this
        array specifies a Unicode character. Otherwise, each value specifies an index to a
        character glyph in the EmfPlusFont object specified by the ObjectId value in Flags field.'''
        ...
    
    @glyphs.setter
    def glyphs(self, value : List[int]):
        '''Sets the glyphs array
        An array of 16-bit values that define the text string to draw.
        If the DriverStringOptionsCmapLookup flag in the DriverStringOptionsFlags field is set, each value in this
        array specifies a Unicode character. Otherwise, each value specifies an index to a
        character glyph in the EmfPlusFont object specified by the ObjectId value in Flags field.'''
        ...
    
    @property
    def is_color(self) -> bool:
        ...
    
    @is_color.setter
    def is_color(self, value : bool):
        ...
    
    @property
    def matrix_present(self) -> int:
        ...
    
    @matrix_present.setter
    def matrix_present(self, value : int):
        ...
    
    @property
    def transform_matrix(self) -> aspose.imaging.Matrix:
        ...
    
    @transform_matrix.setter
    def transform_matrix(self, value : aspose.imaging.Matrix):
        ...
    
    ...

class EmfPlusDrawEllipse(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawEllipse record specifies drawing an ellipse.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @property
    def rect_data(self) -> aspose.imaging.RectangleF:
        ...
    
    @rect_data.setter
    def rect_data(self, value : aspose.imaging.RectangleF):
        ...
    
    ...

class EmfPlusDrawImage(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawImage record specifies drawing a scaled image.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def image_attributes_id(self) -> int:
        ...
    
    @image_attributes_id.setter
    def image_attributes_id(self, value : int):
        ...
    
    @property
    def rect_data(self) -> aspose.imaging.RectangleF:
        ...
    
    @rect_data.setter
    def rect_data(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def src_rect(self) -> aspose.imaging.RectangleF:
        ...
    
    @src_rect.setter
    def src_rect(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def src_unit(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType:
        ...
    
    @src_unit.setter
    def src_unit(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType):
        ...
    
    ...

class EmfPlusDrawImagePoints(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawImagePoints record specifies drawing a scaled image inside a parallelogram.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether the PointData is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit integer
        coordinates. If clear, PointData specifies absolute locations in the coordinate space with
        32-bit floating-point coordinates.
        Note If the P flag (below) is set, this flag is undefined and MUST be ignored.'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether the PointData is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit integer
        coordinates. If clear, PointData specifies absolute locations in the coordinate space with
        32-bit floating-point coordinates.
        Note If the P flag (below) is set, this flag is undefined and MUST be ignored.'''
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def applying_an_effect(self) -> bool:
        ...
    
    @applying_an_effect.setter
    def applying_an_effect(self, value : bool):
        ...
    
    @property
    def relative(self) -> bool:
        '''Gets a value indicating whether this  is relative.
        This bit indicates whether the PointData field specifies relative or absolute locations.
        If set, each element in PointData specifies a location in the coordinate space that is
        relative to the location specified by the previous element in the array. In the case of the
        first element in PointData, a previous location at coordinates (0,0) is assumed. If clear,
        PointData specifies absolute locations according to the C flag.
        Note If this flag is set, the C flag (above) is undefined and MUST be ignored.'''
        ...
    
    @relative.setter
    def relative(self, value : bool):
        '''Sets a value indicating whether this  is relative.
        This bit indicates whether the PointData field specifies relative or absolute locations.
        If set, each element in PointData specifies a location in the coordinate space that is
        relative to the location specified by the previous element in the array. In the case of the
        first element in PointData, a previous location at coordinates (0,0) is assumed. If clear,
        PointData specifies absolute locations according to the C flag.
        Note If this flag is set, the C flag (above) is undefined and MUST be ignored.'''
        ...
    
    @property
    def image_attributes_id(self) -> int:
        ...
    
    @image_attributes_id.setter
    def image_attributes_id(self, value : int):
        ...
    
    @property
    def src_unit(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType:
        ...
    
    @src_unit.setter
    def src_unit(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType):
        ...
    
    @property
    def src_rect(self) -> aspose.imaging.RectangleF:
        ...
    
    @src_rect.setter
    def src_rect(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def point_data(self) -> List[aspose.imaging.PointF]:
        ...
    
    @point_data.setter
    def point_data(self, value : List[aspose.imaging.PointF]):
        ...
    
    ...

class EmfPlusDrawLines(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawlLines record specifies drawing a series of connected lines'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether this  is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit integer coordinates.
        If clear, PointData specifies absolute locations in the coordinate space with 32-bit floating-point coordinates
        Note If the Relative flag (below) is set, this flag is undefined and MUST be ignored'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether this  is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit integer coordinates.
        If clear, PointData specifies absolute locations in the coordinate space with 32-bit floating-point coordinates
        Note If the Relative flag (below) is set, this flag is undefined and MUST be ignored'''
        ...
    
    @property
    def relative(self) -> bool:
        '''Gets a value indicating whether this  is relative.
        This bit indicates whether the PointData field specifies relative or absolute locations.
        If set, each element in PointData specifies a location in the coordinate space that is relative
        to the location specified by the previous element in the array. In the case of the first
        element in PointData, a previous location at coordinates (0,0) is assumed. If clear,
        PointData specifies absolute locations according to the C flag.
        Note If this flag is set, the Compressed flag (above) is undefined and MUST be ignored'''
        ...
    
    @relative.setter
    def relative(self, value : bool):
        '''Sets a value indicating whether this  is relative.
        This bit indicates whether the PointData field specifies relative or absolute locations.
        If set, each element in PointData specifies a location in the coordinate space that is relative
        to the location specified by the previous element in the array. In the case of the first
        element in PointData, a previous location at coordinates (0,0) is assumed. If clear,
        PointData specifies absolute locations according to the C flag.
        Note If this flag is set, the Compressed flag (above) is undefined and MUST be ignored'''
        ...
    
    @property
    def closed_shape(self) -> bool:
        ...
    
    @closed_shape.setter
    def closed_shape(self, value : bool):
        ...
    
    @property
    def point_data(self) -> List[aspose.imaging.PointF]:
        ...
    
    @point_data.setter
    def point_data(self, value : List[aspose.imaging.PointF]):
        ...
    
    ...

class EmfPlusDrawPath(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawPath record specifies drawing a graphics path.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def pen_id(self) -> int:
        ...
    
    @pen_id.setter
    def pen_id(self, value : int):
        ...
    
    ...

class EmfPlusDrawPie(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawPie record specifies drawing a section of the interior of an ellipse.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @start_angle.setter
    def start_angle(self, value : float):
        ...
    
    @property
    def sweep_angle(self) -> float:
        ...
    
    @sweep_angle.setter
    def sweep_angle(self, value : float):
        ...
    
    @property
    def rect_data(self) -> aspose.imaging.RectangleF:
        ...
    
    @rect_data.setter
    def rect_data(self, value : aspose.imaging.RectangleF):
        ...
    
    ...

class EmfPlusDrawRects(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawRects record specifies drawing a series of rectangles'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def rect_data(self) -> List[aspose.imaging.RectangleF]:
        ...
    
    @rect_data.setter
    def rect_data(self, value : List[aspose.imaging.RectangleF]):
        ...
    
    ...

class EmfPlusDrawString(EmfPlusDrawingRecordType):
    '''The EmfPlusDrawString record specifies text output with string formatting'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def is_color(self) -> bool:
        ...
    
    @is_color.setter
    def is_color(self, value : bool):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def brush_id(self) -> int:
        ...
    
    @brush_id.setter
    def brush_id(self, value : int):
        ...
    
    @property
    def format_id(self) -> int:
        ...
    
    @format_id.setter
    def format_id(self, value : int):
        ...
    
    @property
    def length(self) -> int:
        '''Gets the length
        32-bit unsigned integer that specifies the number of characters in the string.'''
        ...
    
    @length.setter
    def length(self, value : int):
        '''Sets the length
        32-bit unsigned integer that specifies the number of characters in the string.'''
        ...
    
    @property
    def layout_rect(self) -> aspose.imaging.RectangleF:
        ...
    
    @layout_rect.setter
    def layout_rect(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def string_data(self) -> str:
        ...
    
    @string_data.setter
    def string_data(self, value : str):
        ...
    
    ...

class EmfPlusDrawingRecordType(EmfPlusRecord):
    '''The drawing record types specify graphics output.'''
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusEndContainer(EmfPlusStateRecordType):
    '''The EmfPlusEndContainer record closes a graphics state container that was previously opened by a begin container operation.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def stack_index(self) -> int:
        ...
    
    @stack_index.setter
    def stack_index(self, value : int):
        ...
    
    ...

class EmfPlusEndOfFile(EmfPlusControlRecordType):
    '''The EmfPlusEndOfFile record specifies the end of EMF+ data in the metafile.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that is not used. This field SHOULD be set to zero
        and MUST be ignored upon receipt'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that is not used. This field SHOULD be set to zero
        and MUST be ignored upon receipt'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusFillClosedCurve(EmfPlusDrawingRecordType):
    '''The EmfPlusFillClosedCurve record specifies filling the interior of a closed cardinal spline'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def is_color(self) -> bool:
        ...
    
    @is_color.setter
    def is_color(self, value : bool):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether this  is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit
        integer coordinates. If clear, PointData specifies absolute locations in the
        coordinate space with 32-bit floating-point coordinates.
        ----------------------
        A "winding" fill operation fills areas according to the "even-odd parity" rule.
        According to this rule, a test point can be determined to be inside or outside a
        closed curve as follows: Draw a line from the test point to a point that is distant
        from the curve. If that line crosses the curve an odd number of times, the test
        point is inside the curve; otherwise, the test point is outside the curve.
        ---------------------
        An "alternate" fill operation fills areas according to the "non-zero" rule.
        According to this rule, a test point can be determined to be inside or outside
        a closed curve as follows: Draw a line from a test point to a point that is
        distant from the curve. Count the number of times the curve crosses the test
        line from left to right, and count the number of times the curve crosses the
        test line from right to left. If those two numbers are the same, the test point
        is outside the curve; otherwise, the test point is inside the curve.'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether this  is compressed.
        This bit indicates whether the PointData field specifies compressed data.
        If set, PointData specifies absolute locations in the coordinate space with 16-bit
        integer coordinates. If clear, PointData specifies absolute locations in the
        coordinate space with 32-bit floating-point coordinates.
        ----------------------
        A "winding" fill operation fills areas according to the "even-odd parity" rule.
        According to this rule, a test point can be determined to be inside or outside a
        closed curve as follows: Draw a line from the test point to a point that is distant
        from the curve. If that line crosses the curve an odd number of times, the test
        point is inside the curve; otherwise, the test point is outside the curve.
        ---------------------
        An "alternate" fill operation fills areas according to the "non-zero" rule.
        According to this rule, a test point can be determined to be inside or outside
        a closed curve as follows: Draw a line from a test point to a point that is
        distant from the curve. Count the number of times the curve crosses the test
        line from left to right, and count the number of times the curve crosses the
        test line from right to left. If those two numbers are the same, the test point
        is outside the curve; otherwise, the test point is inside the curve.'''
        ...
    
    @property
    def winding(self) -> bool:
        '''Gets a value indicating whether this  is winding.
        This bit indicates how to perform the fill operation.
        If set, the fill is a "winding" fill. If clear, the fill is an "alternate" fill.'''
        ...
    
    @winding.setter
    def winding(self, value : bool):
        '''Sets a value indicating whether this  is winding.
        This bit indicates how to perform the fill operation.
        If set, the fill is a "winding" fill. If clear, the fill is an "alternate" fill.'''
        ...
    
    @property
    def relative(self) -> bool:
        '''Gets a value indicating whether this  is relative.
        This bit indicates whether the PointData field specifies relative or absolute locations.
        If set, each element in PointData specifies a location in the coordinate space that is
        relative to the location specified by the previous element in the array. In the case
        of the first element in PointData, a previous location at coordinates (0,0) is assumed.
        If clear, PointData specifies absolute locations according to the C flag.
        Note If this flag is set, the C flag (above) is undefined and MUST be ignored.'''
        ...
    
    @relative.setter
    def relative(self, value : bool):
        '''Sets a value indicating whether this  is relative.
        This bit indicates whether the PointData field specifies relative or absolute locations.
        If set, each element in PointData specifies a location in the coordinate space that is
        relative to the location specified by the previous element in the array. In the case
        of the first element in PointData, a previous location at coordinates (0,0) is assumed.
        If clear, PointData specifies absolute locations according to the C flag.
        Note If this flag is set, the C flag (above) is undefined and MUST be ignored.'''
        ...
    
    @property
    def brush_id(self) -> int:
        ...
    
    @brush_id.setter
    def brush_id(self, value : int):
        ...
    
    @property
    def tension(self) -> float:
        '''Gets the tension
        A 32-bit floating point value that specifies how tightly the spline bends as it passes
        through the points. A value of 0.0 specifies that the spline is a sequence of straight
        lines. As the value increases, the curve becomes more rounded. For more information,
        see [SPLINE77] and [PETZOLD].'''
        ...
    
    @tension.setter
    def tension(self, value : float):
        '''Sets the tension
        A 32-bit floating point value that specifies how tightly the spline bends as it passes
        through the points. A value of 0.0 specifies that the spline is a sequence of straight
        lines. As the value increases, the curve becomes more rounded. For more information,
        see [SPLINE77] and [PETZOLD].'''
        ...
    
    @property
    def point_data(self) -> List[aspose.imaging.PointF]:
        ...
    
    @point_data.setter
    def point_data(self, value : List[aspose.imaging.PointF]):
        ...
    
    ...

class EmfPlusFillEllipse(EmfPlusDrawingRecordType):
    '''The EmfPlusFillEllipse record specifies filling the interior of an ellipse'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def is_color(self) -> bool:
        ...
    
    @is_color.setter
    def is_color(self, value : bool):
        ...
    
    @property
    def is_compressed(self) -> bool:
        ...
    
    @is_compressed.setter
    def is_compressed(self, value : bool):
        ...
    
    @property
    def brush_id(self) -> int:
        ...
    
    @brush_id.setter
    def brush_id(self, value : int):
        ...
    
    @property
    def rect_data(self) -> aspose.imaging.RectangleF:
        ...
    
    @rect_data.setter
    def rect_data(self, value : aspose.imaging.RectangleF):
        ...
    
    ...

class EmfPlusFillPath(EmfPlusDrawingRecordType):
    '''Fill path record
    FLAGS:
    16-bit unsigned integer that provides information about how the operation is to be performed,
    and about the structure of the record.
    0 1 2 3 4 5 6 7 8 9 1 0 1 2 3 4 5 6 7 8 9 2 0 1 2 3 4 5 6 7 8 9 3 0 1
    S X X X X X X X |   ObjectId    |
    S (1 bit): This bit indicates the type of data in the BrushId field.
    If set, BrushId specifies a color as an EmfPlusARGB object (section 2.2.2.1). If clear, BrushId contains the index of an EmfPlusBrush object (section 2.2.1.1) in the EMF+ Object Table.
    X (1 bit): Reserved and MUST be ignored.
    ObjectId (1 byte): The index of the EmfPlusPath object (section 2.2.1.6) to fill, in the EMF+ Object Table. The value MUST be zero to 63, inclusive.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def is_color(self) -> bool:
        ...
    
    @is_color.setter
    def is_color(self, value : bool):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def brush_id(self) -> int:
        ...
    
    @brush_id.setter
    def brush_id(self, value : int):
        ...
    
    ...

class EmfPlusFillPie(EmfPlusDrawingRecordType):
    '''The EmfPlusFillPie record specifies filling a section of the interior of an ellipse'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether the PointData is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38).
        If clear, RectData contains an EmfPlusRectF object (section 2.2.2.39).'''
        ...
    
    @property
    def is_color(self) -> bool:
        ...
    
    @is_color.setter
    def is_color(self, value : bool):
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @start_angle.setter
    def start_angle(self, value : float):
        ...
    
    @property
    def sweep_angle(self) -> float:
        ...
    
    @sweep_angle.setter
    def sweep_angle(self, value : float):
        ...
    
    @property
    def rect_data(self) -> aspose.imaging.RectangleF:
        ...
    
    @rect_data.setter
    def rect_data(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def brush_id(self) -> int:
        ...
    
    @brush_id.setter
    def brush_id(self, value : int):
        ...
    
    ...

class EmfPlusFillPolygon(EmfPlusDrawingRecordType):
    '''The EmfPlusFillPolygon record specifies filling the interior of a polygon.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def is_color(self) -> bool:
        ...
    
    @is_color.setter
    def is_color(self, value : bool):
        ...
    
    @property
    def is_compressed(self) -> bool:
        ...
    
    @is_compressed.setter
    def is_compressed(self, value : bool):
        ...
    
    @property
    def is_relative(self) -> bool:
        ...
    
    @is_relative.setter
    def is_relative(self, value : bool):
        ...
    
    @property
    def brush_id(self) -> int:
        ...
    
    @brush_id.setter
    def brush_id(self, value : int):
        ...
    
    @property
    def point_data(self) -> List[aspose.imaging.PointF]:
        ...
    
    @point_data.setter
    def point_data(self, value : List[aspose.imaging.PointF]):
        ...
    
    ...

class EmfPlusFillRects(EmfPlusDrawingRecordType):
    '''The EmfPlusFillRects record specifies filling the interiors of a series of rectangles'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def is_color(self) -> bool:
        ...
    
    @is_color.setter
    def is_color(self, value : bool):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether this  is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38). If clear, RectData
        contains an EmfPlusRectF object (section 2.2.2.39) object'''
        ...
    
    @compressed.setter
    def compressed(self, value : bool):
        '''Sets a value indicating whether this  is compressed.
        If set, RectData contains an EmfPlusRect object (section 2.2.2.38). If clear, RectData
        contains an EmfPlusRectF object (section 2.2.2.39) object'''
        ...
    
    @property
    def brush_id(self) -> int:
        ...
    
    @brush_id.setter
    def brush_id(self, value : int):
        ...
    
    @property
    def rect_data(self) -> List[aspose.imaging.RectangleF]:
        ...
    
    @rect_data.setter
    def rect_data(self, value : List[aspose.imaging.RectangleF]):
        ...
    
    ...

class EmfPlusFillRegion(EmfPlusDrawingRecordType):
    '''The EmfPlusFillRegion record specifies filling the interior of a graphics region'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def is_color(self) -> bool:
        ...
    
    @is_color.setter
    def is_color(self, value : bool):
        ...
    
    @property
    def brush_id(self) -> int:
        ...
    
    @brush_id.setter
    def brush_id(self, value : int):
        ...
    
    ...

class EmfPlusGetDc(EmfPlusControlRecordType):
    '''The EmfPlusGetDC record specifies that subsequent EMF records encountered in the metafile SHOULD be processed.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that is not used. This field SHOULD be set to zero
        and MUST be ignored upon receipt'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that is not used. This field SHOULD be set to zero
        and MUST be ignored upon receipt'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusHeader(EmfPlusControlRecordType):
    '''The EmfPlusHeader record specifies the start of EMF+ data in the metafile.
    The EmfPlusHeader record MUST be embedded in an EMF EMR_COMMENT_EMFPLUS record,
    which MUST be the record immediately following the EMF header in the metafile.
    The EMR_COMMENT_EMFPLUS record is specified in [MS-EMF] section 2.3.3.2.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def dual_mode(self) -> bool:
        ...
    
    @dual_mode.setter
    def dual_mode(self, value : bool):
        ...
    
    @property
    def video_display(self) -> bool:
        ...
    
    @video_display.setter
    def video_display(self, value : bool):
        ...
    
    @property
    def emf_plus_flags(self) -> int:
        ...
    
    @emf_plus_flags.setter
    def emf_plus_flags(self, value : int):
        ...
    
    @property
    def logical_dpi_x(self) -> int:
        ...
    
    @logical_dpi_x.setter
    def logical_dpi_x(self, value : int):
        ...
    
    @property
    def logical_dpi_y(self) -> int:
        ...
    
    @logical_dpi_y.setter
    def logical_dpi_y(self, value : int):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.
        An EmfPlusGraphicsVersion object (section 2.2.2.19) that specifies the version of operating
        system graphics that was used to create this metafile.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.
        An EmfPlusGraphicsVersion object (section 2.2.2.19) that specifies the version of operating
        system graphics that was used to create this metafile.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    ...

class EmfPlusMultiplyWorldTransform(EmfPlusTerminalServerRecordType):
    '''The EmfPlusMultiplyWorldTransform record multiplies the current world space transform by a
    specified transform matrix.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def post_multiplied_matrix(self) -> bool:
        ...
    
    @property
    def matrix_data(self) -> aspose.imaging.Matrix:
        ...
    
    @matrix_data.setter
    def matrix_data(self, value : aspose.imaging.Matrix):
        ...
    
    ...

class EmfPlusObject(EmfPlusObjectRecordType):
    '''The EmfPlusObject record specifies an object for use in graphics operations. The object definition
    can span multiple records, which is indicated by the value of the Flags field.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def is_continuable(self) -> bool:
        ...
    
    @is_continuable.setter
    def is_continuable(self, value : bool):
        ...
    
    @property
    def object_type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusObjectType:
        ...
    
    @object_type.setter
    def object_type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusObjectType):
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    @property
    def total_object_size(self) -> int:
        ...
    
    @total_object_size.setter
    def total_object_size(self, value : int):
        ...
    
    @property
    def object_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsObjectType:
        ...
    
    @object_data.setter
    def object_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsObjectType):
        ...
    
    ...

class EmfPlusObjectRecordType(EmfPlusRecord):
    '''The Object Record Types define reusable graphics objects.'''
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusOffsetClip(EmfPlusClippingRecordType):
    '''The EmfPlusOffsetClip record applies a translation transform on the current clipping region for the world space.
    The new current clipping region is set to the result of the translation transform.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def dx(self) -> float:
        '''Gets a 32-bit floating-point value that specifies the horizontal offset for the translation.'''
        ...
    
    @dx.setter
    def dx(self, value : float):
        '''Sets a 32-bit floating-point value that specifies the horizontal offset for the translation.'''
        ...
    
    @property
    def dy(self) -> float:
        '''Gets a 32-bit floating-point value that specifies the vertical offset for the translation.'''
        ...
    
    @dy.setter
    def dy(self, value : float):
        '''Sets a 32-bit floating-point value that specifies the vertical offset for the translation.'''
        ...
    
    ...

class EmfPlusPropertyRecordType(EmfPlusRecord):
    '''The Property Record Types specify properties of the playback device context.'''
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusRecord(aspose.imaging.fileformats.emf.MetaObject):
    '''The Emf+ base record type.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusResetClip(EmfPlusClippingRecordType):
    '''The EmfPlusResetClip record resets the current clipping region for the world space to infinity.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusResetWorldTransform(EmfPlusTerminalServerRecordType):
    '''The EmfPlusResetWorldTransform record resets the current world space transform to the identify matrix.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusRestore(EmfPlusStateRecordType):
    '''The EmfPlusRestore record restores the graphics state, identified by a specified index, from a stack of saved graphics states.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def stack_index(self) -> int:
        ...
    
    @stack_index.setter
    def stack_index(self, value : int):
        ...
    
    ...

class EmfPlusRotateWorldTransform(EmfPlusTerminalServerRecordType):
    '''The EmfPlusRotateWorldTransform record performs a rotation on the current world space transform.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def post_multiplied_matrix(self) -> bool:
        ...
    
    @property
    def angle(self) -> float:
        '''Gets a 32-bit floating-point value that specifies the angle of rotation in degrees.
        The operation is performed by constructing a new transform matrix from the following
        diagram:
        ---------------------------------
        |  sin(Angle) |  cos(Angle) | 0 |
        |  cos(Angle) |  sin(Angle) | 0 |
        ---------------------------------
        Figure 2: Rotation Transform Matrix
        The current world space transform is multiplied by this matrix, and the result becomes the
        new current world space transform. The Flags field determines the order of multiplication.'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''Sets a 32-bit floating-point value that specifies the angle of rotation in degrees.
        The operation is performed by constructing a new transform matrix from the following
        diagram:
        ---------------------------------
        |  sin(Angle) |  cos(Angle) | 0 |
        |  cos(Angle) |  sin(Angle) | 0 |
        ---------------------------------
        Figure 2: Rotation Transform Matrix
        The current world space transform is multiplied by this matrix, and the result becomes the
        new current world space transform. The Flags field determines the order of multiplication.'''
        ...
    
    ...

class EmfPlusSave(EmfPlusStateRecordType):
    '''The EmfPlusSave record saves the graphics state, identified by a specified index, on a stack of saved graphics states.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def stack_index(self) -> int:
        ...
    
    @stack_index.setter
    def stack_index(self, value : int):
        ...
    
    ...

class EmfPlusScaleWorldTransform(EmfPlusTerminalServerRecordType):
    '''The EmfPlusScaleWorldTransform record performs a scaling on the current world space transform.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def post_multiplied_matrix(self) -> bool:
        ...
    
    @property
    def sx(self) -> float:
        '''Gets a 32-bit floating-point value that defines the horizontal scale factor. The scaling
        is performed by constructing a new transform matrix from the Sx and Sy field values, as
        shown in the following table.
        -----------------
        |  Sx |   0 | 0 |
        |   0 |  Sx | 0 |
        -----------------
        Figure 3: Scale Transform Matrix'''
        ...
    
    @sx.setter
    def sx(self, value : float):
        '''Sets a 32-bit floating-point value that defines the horizontal scale factor. The scaling
        is performed by constructing a new transform matrix from the Sx and Sy field values, as
        shown in the following table.
        -----------------
        |  Sx |   0 | 0 |
        |   0 |  Sx | 0 |
        -----------------
        Figure 3: Scale Transform Matrix'''
        ...
    
    @property
    def sy(self) -> float:
        '''Gets a 32-bit floating-point value that defines the vertical scale factor.'''
        ...
    
    @sy.setter
    def sy(self, value : float):
        '''Sets a 32-bit floating-point value that defines the vertical scale factor.'''
        ...
    
    ...

class EmfPlusSerializableObject(EmfPlusObjectRecordType):
    '''The EmfPlusSerializableObject record defines an image effects parameter block that has been
    serialized into a data buffer.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that is not used. This field SHOULD be set to zero
        and MUST be ignored upon receipt.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that is not used. This field SHOULD be set to zero
        and MUST be ignored upon receipt.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def object_guid(self) -> aspose.imaging.fileformats.emf.dtyp.commondatastructures.GuidPacketRepresentation:
        ...
    
    @object_guid.setter
    def object_guid(self, value : aspose.imaging.fileformats.emf.dtyp.commondatastructures.GuidPacketRepresentation):
        ...
    
    @property
    def buffer_size(self) -> int:
        ...
    
    @buffer_size.setter
    def buffer_size(self, value : int):
        ...
    
    @property
    def buffer(self) -> bytes:
        '''Gets an array of BufferSize bytes that contain the serialized image effects
        parameter block that corresponds to the GUID in the ObjectGUID field. This MUST be one of
        the Image Effects objects (section 2.2.3).'''
        ...
    
    @buffer.setter
    def buffer(self, value : bytes):
        '''Sets an array of BufferSize bytes that contain the serialized image effects
        parameter block that corresponds to the GUID in the ObjectGUID field. This MUST be one of
        the Image Effects objects (section 2.2.3).'''
        ...
    
    @property
    def image_effect(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusImageEffectsObjectType:
        ...
    
    @image_effect.setter
    def image_effect(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusImageEffectsObjectType):
        ...
    
    ...

class EmfPlusSetAntiAliasMode(EmfPlusPropertyRecordType):
    '''The EmfPlusSetAntiAliasMode record specifies the anti-aliasing mode for text output.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusSmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusSmoothingMode):
        ...
    
    @property
    def anti_aliasing(self) -> bool:
        ...
    
    @anti_aliasing.setter
    def anti_aliasing(self, value : bool):
        ...
    
    ...

class EmfPlusSetClipPath(EmfPlusClippingRecordType):
    '''The EmfPlusSetClipPath record combines the current clipping region with a graphics path.
    The new current clipping region is set to the result of the CombineMode operation.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def cm(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCombineMode:
        '''Gets the CM (4 bits): Specifies the logical operation for combining two regions. See the
        CombineMode enumeration (section 2.1.1.4) for the meanings of the values.'''
        ...
    
    @cm.setter
    def cm(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCombineMode):
        '''Sets the CM (4 bits): Specifies the logical operation for combining two regions. See the
        CombineMode enumeration (section 2.1.1.4) for the meanings of the values.'''
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    ...

class EmfPlusSetClipRect(EmfPlusClippingRecordType):
    '''The EmfPlusSetClipRect record combines the current clipping region with a rectangle.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def cm(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCombineMode:
        '''Gets the CM (4 bits): Specifies the logical operation for combining two regions. See the
        CombineMode enumeration (section 2.1.1.4) for the meanings of the values.'''
        ...
    
    @cm.setter
    def cm(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCombineMode):
        '''Sets the CM (4 bits): Specifies the logical operation for combining two regions. See the
        CombineMode enumeration (section 2.1.1.4) for the meanings of the values.'''
        ...
    
    @property
    def clip_rect(self) -> aspose.imaging.RectangleF:
        ...
    
    @clip_rect.setter
    def clip_rect(self, value : aspose.imaging.RectangleF):
        ...
    
    ...

class EmfPlusSetClipRegion(EmfPlusClippingRecordType):
    '''The EmfPlusSetClipRegion record combines the current clipping region with another graphics region.
    The new current clipping region is set to the result of performing the CombineMode operation on
    the previous current clipping region and the specified EmfPlusRegion object.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def cm(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCombineMode:
        '''Gets the CM (4 bits): Specifies the logical operation for combining two regions. See the
        CombineMode enumeration (section 2.1.1.4) for the meanings of the values.'''
        ...
    
    @cm.setter
    def cm(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCombineMode):
        '''Sets the CM (4 bits): Specifies the logical operation for combining two regions. See the
        CombineMode enumeration (section 2.1.1.4) for the meanings of the values.'''
        ...
    
    @property
    def object_id(self) -> int:
        ...
    
    @object_id.setter
    def object_id(self, value : int):
        ...
    
    ...

class EmfPlusSetCompositingMode(EmfPlusPropertyRecordType):
    '''The EmfPlusSetCompositingMode record specifies how source colors are combined with background colors.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compositing_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCompositingMode:
        ...
    
    @compositing_mode.setter
    def compositing_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCompositingMode):
        ...
    
    ...

class EmfPlusSetCompositingQuality(EmfPlusPropertyRecordType):
    '''The EmfPlusSetCompositingQuality record specifies the desired level of quality for creating
    composite images from multiple objects.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compositing_quality(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCompositingQuality:
        ...
    
    @compositing_quality.setter
    def compositing_quality(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCompositingQuality):
        ...
    
    ...

class EmfPlusSetInterpolationMode(EmfPlusPropertyRecordType):
    '''The EmfPlusSetInterpolationMode record specifies how image scaling, including stretching and shrinking, is performed.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def interpolation_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusInterpolationMode:
        ...
    
    @interpolation_mode.setter
    def interpolation_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusInterpolationMode):
        ...
    
    ...

class EmfPlusSetPageTransform(EmfPlusTerminalServerRecordType):
    '''The EmfPlusSetPageTransform record specifies scaling factors and units for converting page space
    coordinates to device space coordinates.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def page_unit(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType:
        ...
    
    @property
    def page_scale(self) -> float:
        ...
    
    @page_scale.setter
    def page_scale(self, value : float):
        ...
    
    ...

class EmfPlusSetPixelOffsetMode(EmfPlusPropertyRecordType):
    '''The EmfPlusSetPixelOffsetMode record specifies how pixels are centered with respect to the
    coordinates of the drawing surface.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def pixel_offset_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPixelOffsetMode:
        ...
    
    @pixel_offset_mode.setter
    def pixel_offset_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPixelOffsetMode):
        ...
    
    ...

class EmfPlusSetRenderingOrigin(EmfPlusPropertyRecordType):
    '''The EmfPlusSetRenderingOrigin record specifies the rendering origin for graphics output.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def x(self) -> int:
        '''Gets a 32-bit unsigned integer that defines the horizontal coordinate value of the rendering origin.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Sets a 32-bit unsigned integer that defines the horizontal coordinate value of the rendering origin.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets a 32-bit unsigned integer that defines the vertical coordinate value of the rendering origin.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Sets a 32-bit unsigned integer that defines the vertical coordinate value of the rendering origin.'''
        ...
    
    ...

class EmfPlusSetTextContrast(EmfPlusPropertyRecordType):
    '''The EmfPlusSetTextContrast record specifies text contrast according to the gamma correction value.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def text_contrast(self) -> int:
        ...
    
    @text_contrast.setter
    def text_contrast(self, value : int):
        ...
    
    ...

class EmfPlusSetTextRenderingHint(EmfPlusPropertyRecordType):
    '''The EmfPlusSetTextRenderingHint record specifies the quality of text rendering, including the type of anti-aliasing.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusTextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusTextRenderingHint):
        ...
    
    ...

class EmfPlusSetTsClip(EmfPlusTerminalServerRecordType):
    '''The EmfPlusSetTSClip record specifies clipping areas in the graphics device context for a terminal server.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def compressed(self) -> bool:
        '''Gets a value indicating whether this  is compressed.
        This bit specifies the format of the rectangle data in the rects field. If set, each
        rectangle is defined in 4 bytes. If clear, each rectangle is defined in 8 bytes.'''
        ...
    
    @property
    def num_rects(self) -> int:
        ...
    
    @property
    def rects(self) -> List[aspose.imaging.Rectangle]:
        '''Gets an array of NumRects rectangles that define clipping areas. The format of
        this data is determined by the C bit in the Flags field.'''
        ...
    
    @rects.setter
    def rects(self, value : List[aspose.imaging.Rectangle]):
        '''Sets an array of NumRects rectangles that define clipping areas. The format of
        this data is determined by the C bit in the Flags field.'''
        ...
    
    ...

class EmfPlusSetTsGraphics(EmfPlusTerminalServerRecordType):
    '''The EmfPlusSetTSGraphics record specifies the state of a graphics device context for a terminal server.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def basic_vga_colors(self) -> bool:
        ...
    
    @property
    def have_palette(self) -> bool:
        ...
    
    @property
    def anti_alias_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusSmoothingMode:
        ...
    
    @anti_alias_mode.setter
    def anti_alias_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusSmoothingMode):
        ...
    
    @property
    def text_render_hint(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusTextRenderingHint:
        ...
    
    @text_render_hint.setter
    def text_render_hint(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusTextRenderingHint):
        ...
    
    @property
    def compositing_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCompositingMode:
        ...
    
    @compositing_mode.setter
    def compositing_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCompositingMode):
        ...
    
    @property
    def compositing_quality(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCompositingQuality:
        ...
    
    @compositing_quality.setter
    def compositing_quality(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCompositingQuality):
        ...
    
    @property
    def render_origin_x(self) -> int:
        ...
    
    @render_origin_x.setter
    def render_origin_x(self, value : int):
        ...
    
    @property
    def render_origin_y(self) -> int:
        ...
    
    @render_origin_y.setter
    def render_origin_y(self, value : int):
        ...
    
    @property
    def text_contrast(self) -> int:
        ...
    
    @text_contrast.setter
    def text_contrast(self, value : int):
        ...
    
    @property
    def filter_type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusFilterType:
        ...
    
    @filter_type.setter
    def filter_type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusFilterType):
        ...
    
    @property
    def pixel_offset(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPixelOffsetMode:
        ...
    
    @pixel_offset.setter
    def pixel_offset(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPixelOffsetMode):
        ...
    
    @property
    def world_to_device(self) -> aspose.imaging.Matrix:
        ...
    
    @world_to_device.setter
    def world_to_device(self, value : aspose.imaging.Matrix):
        ...
    
    @property
    def palette(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPalette:
        '''Gets an optional EmfPlusPalette object.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPalette):
        '''Sets an optional EmfPlusPalette object.'''
        ...
    
    ...

class EmfPlusSetWorldTransform(EmfPlusTerminalServerRecordType):
    '''The EmfPlusSetWorldTransform record sets the world transform according to the values in a
    specified transform matrix.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def matrix_data(self) -> aspose.imaging.Matrix:
        ...
    
    @matrix_data.setter
    def matrix_data(self, value : aspose.imaging.Matrix):
        ...
    
    ...

class EmfPlusStateRecordType(EmfPlusRecord):
    '''The State Record Types specify operations on the state of the playback device context.'''
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusTerminalServerRecordType(EmfPlusRecord):
    '''The Terminal Server Record Types specify graphics processing on a terminal server. The following
    are EMF+ terminal server record types.'''
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusTransformRecordType(EmfPlusRecord):
    '''The Transform Record Types specify properties and transforms on coordinate spaces.'''
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    ...

class EmfPlusTranslateWorldTransform(EmfPlusTerminalServerRecordType):
    '''The EmfPlusTranslateWorldTransform record performs a translation on the current world space transform.'''
    
    def __init__(self, source: aspose.imaging.fileformats.emf.emfplus.records.EmfPlusRecord):
        '''Initializes a new instance of the  class.
        
        :param source: The source.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRecordType:
        '''Gets a 16-bit unsigned integer that identifies the record type.'''
        ...
    
    @property
    def flags(self) -> int:
        '''Gets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @flags.setter
    def flags(self, value : int):
        '''Sets a 16-bit unsigned integer that contains information for some records on how
        the operation is to be performed and on the structure of the record.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the 32-bit-aligned number of bytes
        in the entire record, including the 12-byte record header and record-specific data.'''
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @data_size.setter
    def data_size(self, value : int):
        ...
    
    @property
    def post_multiplied_matrix(self) -> bool:
        ...
    
    @property
    def dx(self) -> float:
        '''Gets a 32-bit floating-point value that defines the horizontal distance. The translation
        is performed by constructing a new world transform matrix from the dx and dy fields'''
        ...
    
    @dx.setter
    def dx(self, value : float):
        '''Sets a 32-bit floating-point value that defines the horizontal distance. The translation
        is performed by constructing a new world transform matrix from the dx and dy fields'''
        ...
    
    @property
    def dy(self) -> float:
        '''Gets a 32-bit floating-point value that defines the vertical distance value.'''
        ...
    
    @dy.setter
    def dy(self, value : float):
        '''Sets a 32-bit floating-point value that defines the vertical distance value.'''
        ...
    
    ...

