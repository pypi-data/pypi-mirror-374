"""The  contains types [MS-WMF]: Windows
                Metafile Format 2.2 WMF Objects"""
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

class WmfAnimatePalette(WmfObject):
    '''The META_ANIMATEPALETTE record redefines entries in the logical palette
    that is defined in the playback device context with the specified
    Palette object (section 2.2.1.3).'''
    
    def __init__(self):
        ...
    
    @property
    def log_palette(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfLogPalette:
        ...
    
    @log_palette.setter
    def log_palette(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfLogPalette):
        ...
    
    @property
    def start(self) -> int:
        '''Gets the start.'''
        ...
    
    @start.setter
    def start(self, value : int):
        '''Sets the start.'''
        ...
    
    ...

class WmfArc(WmfRectangle):
    '''The META_ARC record draws an elliptical arc.'''
    
    def __init__(self):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    @property
    def end_arc(self) -> aspose.imaging.Point:
        ...
    
    @end_arc.setter
    def end_arc(self, value : aspose.imaging.Point):
        ...
    
    @property
    def start_arc(self) -> aspose.imaging.Point:
        ...
    
    @start_arc.setter
    def start_arc(self, value : aspose.imaging.Point):
        ...
    
    ...

class WmfBitBlt(WmfStretchBlt):
    '''The META_BITBLT record specifies the transfer of a block of pixels
    according to a raster operation. The destination of the transfer is the
    current output region in the playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def raster_operation(self) -> aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation:
        ...
    
    @raster_operation.setter
    def raster_operation(self, value : aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation):
        ...
    
    @property
    def src_height(self) -> int:
        ...
    
    @src_height.setter
    def src_height(self, value : int):
        ...
    
    @property
    def src_width(self) -> int:
        ...
    
    @src_width.setter
    def src_width(self, value : int):
        ...
    
    @property
    def src_position(self) -> aspose.imaging.Point:
        ...
    
    @src_position.setter
    def src_position(self, value : aspose.imaging.Point):
        ...
    
    @property
    def dest_height(self) -> int:
        ...
    
    @dest_height.setter
    def dest_height(self, value : int):
        ...
    
    @property
    def dest_width(self) -> int:
        ...
    
    @dest_width.setter
    def dest_width(self, value : int):
        ...
    
    @property
    def dst_position(self) -> aspose.imaging.Point:
        ...
    
    @dst_position.setter
    def dst_position(self, value : aspose.imaging.Point):
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets the reserved.'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets the reserved.'''
        ...
    
    @property
    def bitmap(self) -> aspose.imaging.fileformats.wmf.objects.WmfBitmap16:
        '''Gets the bitmap.'''
        ...
    
    @bitmap.setter
    def bitmap(self, value : aspose.imaging.fileformats.wmf.objects.WmfBitmap16):
        '''Sets the bitmap.'''
        ...
    
    ...

class WmfBitmap16(aspose.imaging.fileformats.emf.MetaObject):
    '''The Bitmap16 Object specifies information about the dimensions and color
    format of a bitmap.'''
    
    def __init__(self):
        ...
    
    @property
    def type(self) -> int:
        '''Gets the type.'''
        ...
    
    @type.setter
    def type(self, value : int):
        '''Sets the type.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height.'''
        ...
    
    @property
    def width_bytes(self) -> int:
        ...
    
    @width_bytes.setter
    def width_bytes(self, value : int):
        ...
    
    @property
    def planes(self) -> int:
        '''Gets the planes.'''
        ...
    
    @planes.setter
    def planes(self, value : int):
        '''Sets the planes.'''
        ...
    
    @property
    def bits_pixel(self) -> int:
        ...
    
    @bits_pixel.setter
    def bits_pixel(self, value : int):
        ...
    
    @property
    def bits(self) -> bytes:
        '''Gets the bits.'''
        ...
    
    @bits.setter
    def bits(self, value : bytes):
        '''Sets the bits.'''
        ...
    
    ...

class WmfBitmapBaseHeader(aspose.imaging.fileformats.emf.MetaObject):
    '''The base bitmap header class.'''
    
    @property
    def header_size(self) -> int:
        ...
    
    @header_size.setter
    def header_size(self, value : int):
        ...
    
    @property
    def planes(self) -> int:
        '''Gets a 16-bit unsigned integer that defines the number of
        for the target device. This value MUST be
        0x0001.'''
        ...
    
    @planes.setter
    def planes(self, value : int):
        '''Sets a 16-bit unsigned integer that defines the number of
        for the target device. This value MUST be
        0x0001.'''
        ...
    
    @property
    def bit_count(self) -> aspose.imaging.apsbuilder.dib.DibBitCount:
        ...
    
    @bit_count.setter
    def bit_count(self, value : aspose.imaging.apsbuilder.dib.DibBitCount):
        ...
    
    ...

class WmfBitmapCoreHeader(WmfBitmapBaseHeader):
    '''The BitmapCoreHeader Object contains information about the dimensions
    and color format of a device-independent bitmap(DIB).'''
    
    def __init__(self):
        ...
    
    @property
    def header_size(self) -> int:
        ...
    
    @header_size.setter
    def header_size(self, value : int):
        ...
    
    @property
    def planes(self) -> int:
        '''Gets a 16-bit unsigned integer that defines the number of
        for the target device. This value MUST be
        0x0001.'''
        ...
    
    @planes.setter
    def planes(self, value : int):
        '''Sets a 16-bit unsigned integer that defines the number of
        for the target device. This value MUST be
        0x0001.'''
        ...
    
    @property
    def bit_count(self) -> aspose.imaging.apsbuilder.dib.DibBitCount:
        ...
    
    @bit_count.setter
    def bit_count(self, value : aspose.imaging.apsbuilder.dib.DibBitCount):
        ...
    
    @property
    def width(self) -> int:
        '''Gets a 16-bit unsigned integer that defines the
        of the DIB, in pixels'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets a 16-bit unsigned integer that defines the
        of the DIB, in pixels'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets a 16-bit unsigned integer that defines the
        of the DIB, in pixels'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets a 16-bit unsigned integer that defines the
        of the DIB, in pixels'''
        ...
    
    ...

class WmfBitmapInfoHeader(WmfBitmapBaseHeader):
    '''The BitmapInfoHeader Object contains information about the dimensions and color format of a device-independent
    bitmap (DIB).'''
    
    def __init__(self):
        ...
    
    @property
    def header_size(self) -> int:
        ...
    
    @header_size.setter
    def header_size(self, value : int):
        ...
    
    @property
    def planes(self) -> int:
        '''Gets a 16-bit unsigned integer that defines the number of
        for the target device. This value MUST be
        0x0001.'''
        ...
    
    @planes.setter
    def planes(self, value : int):
        '''Sets a 16-bit unsigned integer that defines the number of
        for the target device. This value MUST be
        0x0001.'''
        ...
    
    @property
    def bit_count(self) -> aspose.imaging.apsbuilder.dib.DibBitCount:
        ...
    
    @bit_count.setter
    def bit_count(self, value : aspose.imaging.apsbuilder.dib.DibBitCount):
        ...
    
    @property
    def width(self) -> int:
        '''Gets a 32-bit signed integer that defines the width of the DIB, in pixels. This value MUST be positive.
        This field SHOULD specify the width of the decompressed image file, if the Compression value specifies JPEG or PNG
        format.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets a 32-bit signed integer that defines the width of the DIB, in pixels. This value MUST be positive.
        This field SHOULD specify the width of the decompressed image file, if the Compression value specifies JPEG or PNG
        format.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets  32-bit signed integer that defines the height of the DIB, in pixels. This value MUST NOT be zero.
        If this value is positive, the DIB is a bottom-up bitmap, and its origin is the lower-left corner.
        If this value is negative, the DIB is a top-down bitmap, and its origin is the upper-left corner. Top-down bitmaps
        do not support compression.
        This field SHOULD specify the height of the decompressed image file, if the Compression value specifies JPEG or PNG
        format.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets  32-bit signed integer that defines the height of the DIB, in pixels. This value MUST NOT be zero.
        If this value is positive, the DIB is a bottom-up bitmap, and its origin is the lower-left corner.
        If this value is negative, the DIB is a top-down bitmap, and its origin is the upper-left corner. Top-down bitmaps
        do not support compression.
        This field SHOULD specify the height of the decompressed image file, if the Compression value specifies JPEG or PNG
        format.'''
        ...
    
    @property
    def compression(self) -> aspose.imaging.fileformats.wmf.consts.WmfCompression:
        '''Gets a 32-bit unsigned integer that defines the compression mode of the DIB. This value MUST be in the
        Compression Enumeration (section 2.1.1.7).
        This value MUST NOT specify a compressed format if the DIB is a top-down bitmap, as indicated by the Height value.'''
        ...
    
    @compression.setter
    def compression(self, value : aspose.imaging.fileformats.wmf.consts.WmfCompression):
        '''Sets a 32-bit unsigned integer that defines the compression mode of the DIB. This value MUST be in the
        Compression Enumeration (section 2.1.1.7).
        This value MUST NOT specify a compressed format if the DIB is a top-down bitmap, as indicated by the Height value.'''
        ...
    
    @property
    def image_size(self) -> int:
        ...
    
    @image_size.setter
    def image_size(self, value : int):
        ...
    
    @property
    def x_pels_per_meter(self) -> int:
        ...
    
    @x_pels_per_meter.setter
    def x_pels_per_meter(self, value : int):
        ...
    
    @property
    def y_pels_per_meter(self) -> int:
        ...
    
    @y_pels_per_meter.setter
    def y_pels_per_meter(self, value : int):
        ...
    
    @property
    def color_used(self) -> int:
        ...
    
    @color_used.setter
    def color_used(self, value : int):
        ...
    
    @property
    def color_important(self) -> int:
        ...
    
    @color_important.setter
    def color_important(self, value : int):
        ...
    
    @classmethod
    @property
    def STRUCTURE_SIZE(cls) -> int:
        ...
    
    ...

class WmfChord(WmfRectangle):
    '''The META_CHORD record draws a chord, which is defined by a region
    bounded by the intersection of an ellipse with a line segment. The chord
    is outlined using the pen and filled using the brush that are defined in
    the playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    @property
    def radial2(self) -> aspose.imaging.Point:
        '''Gets the radial2.'''
        ...
    
    @radial2.setter
    def radial2(self, value : aspose.imaging.Point):
        '''Sets the radial2.'''
        ...
    
    @property
    def radial1(self) -> aspose.imaging.Point:
        '''Gets the radial1.'''
        ...
    
    @radial1.setter
    def radial1(self, value : aspose.imaging.Point):
        '''Sets the radial1.'''
        ...
    
    ...

class WmfCieXyz:
    '''The CIEXYZ Object defines information about the CIEXYZ chromaticity
    object.'''
    
    def __init__(self):
        ...
    
    @property
    def ciexyz_x(self) -> int:
        ...
    
    @ciexyz_x.setter
    def ciexyz_x(self, value : int):
        ...
    
    @property
    def ciexyz_y(self) -> int:
        ...
    
    @ciexyz_y.setter
    def ciexyz_y(self, value : int):
        ...
    
    @property
    def ciexyz_z(self) -> int:
        ...
    
    @ciexyz_z.setter
    def ciexyz_z(self, value : int):
        ...
    
    ...

class WmfCieXyzTriple:
    '''The CIEXYZTriple Object defines information about the CIEXYZTriple color
    object.'''
    
    def __init__(self):
        ...
    
    @property
    def ciexyz_red(self) -> aspose.imaging.fileformats.wmf.objects.WmfCieXyz:
        ...
    
    @ciexyz_red.setter
    def ciexyz_red(self, value : aspose.imaging.fileformats.wmf.objects.WmfCieXyz):
        ...
    
    @property
    def ciexyz_green(self) -> aspose.imaging.fileformats.wmf.objects.WmfCieXyz:
        ...
    
    @ciexyz_green.setter
    def ciexyz_green(self, value : aspose.imaging.fileformats.wmf.objects.WmfCieXyz):
        ...
    
    @property
    def ciexyz_blue(self) -> aspose.imaging.fileformats.wmf.objects.WmfCieXyz:
        ...
    
    @ciexyz_blue.setter
    def ciexyz_blue(self, value : aspose.imaging.fileformats.wmf.objects.WmfCieXyz):
        ...
    
    ...

class WmfCreateBrushInDirect(WmfGraphicObject):
    '''The Create brush in direct'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def index(self) -> int:
        '''Gets the index.'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Sets the index.'''
        ...
    
    @property
    def log_brush(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfLogBrushEx:
        ...
    
    @log_brush.setter
    def log_brush(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfLogBrushEx):
        ...
    
    ...

class WmfCreateFontInDirect(WmfGraphicObject):
    '''The Create font'''
    
    def __init__(self):
        '''WMFs the record.'''
        ...
    
    @property
    def index(self) -> int:
        '''Gets the index.'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Sets the index.'''
        ...
    
    @property
    def log_font(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfLogFont:
        ...
    
    @log_font.setter
    def log_font(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfLogFont):
        ...
    
    @property
    def extended_bytes(self) -> bytes:
        ...
    
    @extended_bytes.setter
    def extended_bytes(self, value : bytes):
        ...
    
    ...

class WmfCreatePalette(WmfGraphicObject):
    '''The META_CREATEPALETTE record creates a Palette Object (section 2.2.1.3).'''
    
    def __init__(self):
        '''WMFs the record.'''
        ...
    
    @property
    def index(self) -> int:
        '''Gets the index.'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Sets the index.'''
        ...
    
    @property
    def log_palette(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfLogPalette:
        ...
    
    @log_palette.setter
    def log_palette(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfLogPalette):
        ...
    
    @classmethod
    @property
    def PALETTE_START(cls) -> int:
        ...
    
    ...

class WmfCreatePatternBrush(WmfGraphicObject):
    '''The META_CREATEPATTERNBRUSH record creates a brush object with a pattern
    specified by a bitmap.'''
    
    def __init__(self):
        '''WMFs the record.'''
        ...
    
    @property
    def index(self) -> int:
        '''Gets the index.'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Sets the index.'''
        ...
    
    @property
    def bitmap(self) -> aspose.imaging.fileformats.wmf.objects.WmfBitmap16:
        '''Gets the bitmap.'''
        ...
    
    @bitmap.setter
    def bitmap(self, value : aspose.imaging.fileformats.wmf.objects.WmfBitmap16):
        '''Sets the bitmap.'''
        ...
    
    @property
    def reserved(self) -> bytes:
        '''Gets the reserved.'''
        ...
    
    @reserved.setter
    def reserved(self, value : bytes):
        '''Sets the reserved.'''
        ...
    
    @property
    def pattern(self) -> bytes:
        '''Gets the pattern.'''
        ...
    
    @pattern.setter
    def pattern(self, value : bytes):
        '''Sets the pattern.'''
        ...
    
    ...

class WmfCreatePenInDirect(WmfGraphicObject):
    '''The create pen in direct'''
    
    def __init__(self):
        '''WMFs the record.'''
        ...
    
    @property
    def index(self) -> int:
        '''Gets the index.'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Sets the index.'''
        ...
    
    @property
    def log_pen(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfLogPen:
        ...
    
    @log_pen.setter
    def log_pen(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfLogPen):
        ...
    
    ...

class WmfCreateRegion(WmfGraphicObject):
    '''The META_CREATEREGION record creates a Region Object (section 2.2.1.5).'''
    
    def __init__(self):
        '''WMFs the record.'''
        ...
    
    @property
    def index(self) -> int:
        '''Gets the index.'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Sets the index.'''
        ...
    
    @property
    def region(self) -> aspose.imaging.fileformats.wmf.objects.WmfRegion:
        '''Gets the region.'''
        ...
    
    @region.setter
    def region(self, value : aspose.imaging.fileformats.wmf.objects.WmfRegion):
        '''Sets the region.'''
        ...
    
    ...

class WmfDeleteObject(WmfObject):
    '''The Delete object'''
    
    @overload
    def __init__(self, deleted_object: aspose.imaging.fileformats.wmf.objects.WmfGraphicObject):
        '''Initializes a new instance of the  class.
        
        :param deleted_object: The deleted object.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def object_index(self) -> int:
        ...
    
    @object_index.setter
    def object_index(self, value : int):
        ...
    
    ...

class WmfDeviceIndependentBitmap(aspose.imaging.fileformats.emf.MetaObject):
    '''The DeviceIndependentBitmap Object defines an image in
    device-independent bitmap (DIB) format'''
    
    def __init__(self):
        ...
    
    @property
    def header(self) -> aspose.imaging.fileformats.wmf.objects.WmfBitmapBaseHeader:
        '''Gets either a BitmapCoreHeader Object (section 2.2.2.2) or a
        BitmapInfoHeader Object (section 2.2.2.3) that specifies information
        about the image'''
        ...
    
    @header.setter
    def header(self, value : aspose.imaging.fileformats.wmf.objects.WmfBitmapBaseHeader):
        '''Sets either a BitmapCoreHeader Object (section 2.2.2.2) or a
        BitmapInfoHeader Object (section 2.2.2.3) that specifies information
        about the image'''
        ...
    
    @property
    def colors_data(self) -> bytes:
        ...
    
    @colors_data.setter
    def colors_data(self, value : bytes):
        ...
    
    @property
    def a_data(self) -> bytes:
        ...
    
    @a_data.setter
    def a_data(self, value : bytes):
        ...
    
    @property
    def cached_image(self) -> bytes:
        ...
    
    @cached_image.setter
    def cached_image(self, value : bytes):
        ...
    
    ...

class WmfDibBitBlt(WmfObject):
    '''The META_DIBBITBLT record specifies the transfer of a block of pixels in
    device-independent format according to a raster operation.'''
    
    def __init__(self):
        ...
    
    @property
    def raster_operation(self) -> aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation:
        ...
    
    @raster_operation.setter
    def raster_operation(self, value : aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation):
        ...
    
    @property
    def src_pos(self) -> aspose.imaging.Point:
        ...
    
    @src_pos.setter
    def src_pos(self, value : aspose.imaging.Point):
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width.'''
        ...
    
    @property
    def dst_pos(self) -> aspose.imaging.Point:
        ...
    
    @dst_pos.setter
    def dst_pos(self, value : aspose.imaging.Point):
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets the reserved.'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets the reserved.'''
        ...
    
    @property
    def source(self) -> aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap:
        '''Gets the source.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap):
        '''Sets the source.'''
        ...
    
    ...

class WmfDibCreatePatternBrush(WmfGraphicObject):
    '''The META_DIBCREATEPATTERNBRUSH record creates a Brush Object (section
    2.2.1.1) with a pattern specified by a DeviceIndependentBitmap (DIB)
    Object (section 2.2.2.9).'''
    
    def __init__(self):
        ...
    
    @property
    def index(self) -> int:
        '''Gets the index.'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Sets the index.'''
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.wmf.consts.WmfBrushStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.wmf.consts.WmfBrushStyle):
        '''Sets the style.'''
        ...
    
    @property
    def color_usage(self) -> aspose.imaging.fileformats.wmf.consts.WmfColorUsageEnum:
        ...
    
    @color_usage.setter
    def color_usage(self, value : aspose.imaging.fileformats.wmf.consts.WmfColorUsageEnum):
        ...
    
    @property
    def source_bitmap(self) -> aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap:
        ...
    
    @source_bitmap.setter
    def source_bitmap(self, value : aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap):
        ...
    
    ...

class WmfDibStrechBlt(WmfObject):
    '''The META_DIBSTRETCHBLT record specifies the transfer of a block of
    pixels in device-independent format according to a raster operation,
    with possible expansion or contraction.'''
    
    def __init__(self):
        '''WMFs the record.'''
        ...
    
    @property
    def raster_operation(self) -> aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation:
        ...
    
    @raster_operation.setter
    def raster_operation(self, value : aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation):
        ...
    
    @property
    def src_height(self) -> int:
        ...
    
    @src_height.setter
    def src_height(self, value : int):
        ...
    
    @property
    def src_width(self) -> int:
        ...
    
    @src_width.setter
    def src_width(self, value : int):
        ...
    
    @property
    def y_src(self) -> int:
        ...
    
    @y_src.setter
    def y_src(self, value : int):
        ...
    
    @property
    def x_src(self) -> int:
        ...
    
    @x_src.setter
    def x_src(self, value : int):
        ...
    
    @property
    def dest_height(self) -> int:
        ...
    
    @dest_height.setter
    def dest_height(self, value : int):
        ...
    
    @property
    def dest_width(self) -> int:
        ...
    
    @dest_width.setter
    def dest_width(self, value : int):
        ...
    
    @property
    def y_dest(self) -> int:
        ...
    
    @y_dest.setter
    def y_dest(self, value : int):
        ...
    
    @property
    def x_dest(self) -> int:
        ...
    
    @x_dest.setter
    def x_dest(self, value : int):
        ...
    
    @property
    def source_bitmap(self) -> aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap:
        ...
    
    @source_bitmap.setter
    def source_bitmap(self, value : aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap):
        ...
    
    ...

class WmfEllipse(WmfRectangle):
    '''The META_ELLIPSE record draws an ellipse. The center of the ellipse is
    the center of the specified bounding rectangle. The ellipse is outlined
    by using the pen and is filled by using the brush; these are defined in
    the playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    ...

class WmfEof(WmfObject):
    '''The Eof object.'''
    
    def __init__(self):
        ...
    
    ...

class WmfEscape(WmfObject):
    '''The wmf escape object.'''
    
    def __init__(self):
        ...
    
    @property
    def escape_type(self) -> aspose.imaging.fileformats.wmf.consts.WmfMetafileEscapes:
        ...
    
    @escape_type.setter
    def escape_type(self, value : aspose.imaging.fileformats.wmf.consts.WmfMetafileEscapes):
        ...
    
    @property
    def escape_record(self) -> aspose.imaging.fileformats.wmf.objects.escaperecords.WmfEscapeRecordBase:
        ...
    
    @escape_record.setter
    def escape_record(self, value : aspose.imaging.fileformats.wmf.objects.escaperecords.WmfEscapeRecordBase):
        ...
    
    ...

class WmfExcludeClipRect(WmfRectangle):
    '''The META_EXCLUDECLIPRECT record sets the clipping region in the playback
    device context to the existing clipping region minus the specified
    rectangle.'''
    
    def __init__(self):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    ...

class WmfExtFloodFill(WmfFloodFill):
    '''The META_EXTFLOODFILL record fills an area with the brush that is
    defined in the playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def color_ref(self) -> int:
        ...
    
    @color_ref.setter
    def color_ref(self, value : int):
        ...
    
    @property
    def y_start(self) -> int:
        ...
    
    @y_start.setter
    def y_start(self, value : int):
        ...
    
    @property
    def x_start(self) -> int:
        ...
    
    @x_start.setter
    def x_start(self, value : int):
        ...
    
    @property
    def mode(self) -> aspose.imaging.fileformats.wmf.consts.WmfFloodFillMode:
        '''Gets the mode.'''
        ...
    
    @mode.setter
    def mode(self, value : aspose.imaging.fileformats.wmf.consts.WmfFloodFillMode):
        '''Sets the mode.'''
        ...
    
    ...

class WmfExtTextOut(WmfPointObject):
    '''Wmf ext text out'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    @property
    def string_length(self) -> int:
        ...
    
    @string_length.setter
    def string_length(self, value : int):
        ...
    
    @property
    def fw_opts(self) -> int:
        ...
    
    @fw_opts.setter
    def fw_opts(self, value : int):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text.'''
        ...
    
    @property
    def dx(self) -> List[int]:
        '''Gets the dx.'''
        ...
    
    @dx.setter
    def dx(self, value : List[int]):
        '''Sets the dx.'''
        ...
    
    @property
    def extended_byte(self) -> int:
        ...
    
    @extended_byte.setter
    def extended_byte(self, value : int):
        ...
    
    ...

class WmfFillRegion(WmfObject):
    '''The META_FILLREGION record fills a region using a specified brush.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, region: aspose.imaging.fileformats.wmf.objects.WmfGraphicObject, brush: aspose.imaging.fileformats.wmf.objects.WmfGraphicObject):
        '''Initializes a new instance of the  class.
        
        :param region: The region.
        :param brush: The brush.'''
        ...
    
    @property
    def region_index(self) -> int:
        ...
    
    @region_index.setter
    def region_index(self, value : int):
        ...
    
    @property
    def brush_index(self) -> int:
        ...
    
    @brush_index.setter
    def brush_index(self, value : int):
        ...
    
    ...

class WmfFloodFill(WmfObject):
    '''The META_FLOODFILL record fills an area of the output surface with the
    brush that is defined in the playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def color_ref(self) -> int:
        ...
    
    @color_ref.setter
    def color_ref(self, value : int):
        ...
    
    @property
    def y_start(self) -> int:
        ...
    
    @y_start.setter
    def y_start(self, value : int):
        ...
    
    @property
    def x_start(self) -> int:
        ...
    
    @x_start.setter
    def x_start(self, value : int):
        ...
    
    ...

class WmfFrameRegion(WmfObject):
    '''The wmf frame region object.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, region: aspose.imaging.fileformats.wmf.objects.WmfGraphicObject, brush: aspose.imaging.fileformats.wmf.objects.WmfGraphicObject):
        '''Initializes a new instance of the  class.
        
        :param region: The region.
        :param brush: The brush.'''
        ...
    
    @property
    def region_index(self) -> int:
        ...
    
    @region_index.setter
    def region_index(self, value : int):
        ...
    
    @property
    def brush_index(self) -> int:
        ...
    
    @brush_index.setter
    def brush_index(self, value : int):
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width.'''
        ...
    
    ...

class WmfGraphicObject(WmfObject):
    '''The WMF Graphics Objects specify parameters for graphics output.'''
    
    def __init__(self):
        ...
    
    @property
    def index(self) -> int:
        '''Gets the index.'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Sets the index.'''
        ...
    
    ...

class WmfIntersectClipRect(WmfObject):
    '''The META_INTERSECTCLIPRECT record sets the clipping region in the
    playback device context to the intersection of the existing clipping
    region and the specified rectangle.'''
    
    def __init__(self):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    ...

class WmfInvertRegion(WmfObject):
    '''The META_INVERTREGION record draws a region in which the colors are
    inverted.'''
    
    @overload
    def __init__(self, region: aspose.imaging.fileformats.wmf.objects.WmfGraphicObject):
        '''Initializes a new instance of the  class.
        
        :param region: The region.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def region_index(self) -> int:
        ...
    
    @region_index.setter
    def region_index(self, value : int):
        ...
    
    ...

class WmfLineTo(WmfPointObject):
    '''The META_LINETO record draws a line from the drawing position that is
    defined in the playback device context up to, but not including, the
    specified point.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfLogColorSpace(aspose.imaging.fileformats.emf.MetaObject):
    '''The LogColorSpace object specifies a logical color space for the
    playback device context, which can be the name of a color profile in
    ASCII characters.'''
    
    def __init__(self):
        ...
    
    @property
    def signature(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the
        of color space objects; it MUST be set to
        the value 0x50534F43, which is the ASCII encoding of the string
        "PSOC".'''
        ...
    
    @signature.setter
    def signature(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the
        of color space objects; it MUST be set to
        the value 0x50534F43, which is the ASCII encoding of the string
        "PSOC".'''
        ...
    
    @property
    def version(self) -> int:
        '''Gets a 32-bit unsigned integer that defines a
        number; it MUST be0x00000400.'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets a 32-bit unsigned integer that defines a
        number; it MUST be0x00000400.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that defines the
        of this object, in bytes.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that defines the
        of this object, in bytes.'''
        ...
    
    @property
    def color_space_type(self) -> aspose.imaging.fileformats.wmf.consts.WmfLogicalColorSpaceEnum:
        ...
    
    @color_space_type.setter
    def color_space_type(self, value : aspose.imaging.fileformats.wmf.consts.WmfLogicalColorSpaceEnum):
        ...
    
    @property
    def intent(self) -> aspose.imaging.fileformats.wmf.consts.WmfGamutMappingIntent:
        '''Gets a 32-bit signed integer that defines the gamut mapping
        intent. It MUST be defined in the GamutMappingIntent enumeration
        (section 2.1.1.11).'''
        ...
    
    @intent.setter
    def intent(self, value : aspose.imaging.fileformats.wmf.consts.WmfGamutMappingIntent):
        '''Sets a 32-bit signed integer that defines the gamut mapping
        intent. It MUST be defined in the GamutMappingIntent enumeration
        (section 2.1.1.11).'''
        ...
    
    @property
    def endpoints(self) -> aspose.imaging.fileformats.wmf.objects.WmfCieXyzTriple:
        '''Gets a CIEXYZTriple object (section 2.2.2.7) that defines
        the CIE chromaticity x, y, and z coordinates of the three colors
        that correspond to the RGB  for the logical
        color space associated with the bitmap. If the
        field does not specify
        LCS_CALIBRATED_RGB, this field MUST be ignored.'''
        ...
    
    @endpoints.setter
    def endpoints(self, value : aspose.imaging.fileformats.wmf.objects.WmfCieXyzTriple):
        '''Sets a CIEXYZTriple object (section 2.2.2.7) that defines
        the CIE chromaticity x, y, and z coordinates of the three colors
        that correspond to the RGB  for the logical
        color space associated with the bitmap. If the
        field does not specify
        LCS_CALIBRATED_RGB, this field MUST be ignored.'''
        ...
    
    @property
    def gamma_red(self) -> int:
        ...
    
    @gamma_red.setter
    def gamma_red(self, value : int):
        ...
    
    @property
    def gamma_green(self) -> int:
        ...
    
    @gamma_green.setter
    def gamma_green(self, value : int):
        ...
    
    @property
    def gamma_blue(self) -> int:
        ...
    
    @gamma_blue.setter
    def gamma_blue(self, value : int):
        ...
    
    @property
    def filename(self) -> str:
        '''Gets an optional, ASCII charactger string that specifies the
        name of a file that contains a color profile. If a file name is
        specified, and the  field is set to
        LCS_CALIBRATED_RGB, the other fields of this structure SHOULD be
        ignored.'''
        ...
    
    @filename.setter
    def filename(self, value : str):
        '''Sets an optional, ASCII charactger string that specifies the
        name of a file that contains a color profile. If a file name is
        specified, and the  field is set to
        LCS_CALIBRATED_RGB, the other fields of this structure SHOULD be
        ignored.'''
        ...
    
    ...

class WmfLogColorSpaceW(aspose.imaging.fileformats.emf.MetaObject):
    '''The LogColorSpaceW object specifies a logical color space, which can be
    defined by a color profile file with a name consisting of Unicode 16-bit
    characters.'''
    
    def __init__(self):
        ...
    
    @property
    def signature(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the
        of color space objects; it MUST be set to
        the value 0x50534F43, which is the ASCII encoding of the string
        "PSOC".'''
        ...
    
    @signature.setter
    def signature(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the
        of color space objects; it MUST be set to
        the value 0x50534F43, which is the ASCII encoding of the string
        "PSOC".'''
        ...
    
    @property
    def version(self) -> int:
        '''Gets a 32-bit unsigned integer that defines a
        number; it MUST be0x00000400.'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets a 32-bit unsigned integer that defines a
        number; it MUST be0x00000400.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that defines the
        of this object, in bytes.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that defines the
        of this object, in bytes.'''
        ...
    
    @property
    def color_space_type(self) -> aspose.imaging.fileformats.wmf.consts.WmfLogicalColorSpaceEnum:
        ...
    
    @color_space_type.setter
    def color_space_type(self, value : aspose.imaging.fileformats.wmf.consts.WmfLogicalColorSpaceEnum):
        ...
    
    @property
    def intent(self) -> aspose.imaging.fileformats.wmf.consts.WmfGamutMappingIntent:
        '''Gets a 32-bit signed integer that defines the gamut mapping
        intent. It MUST be defined in the GamutMappingIntent enumeration
        (section 2.1.1.11).'''
        ...
    
    @intent.setter
    def intent(self, value : aspose.imaging.fileformats.wmf.consts.WmfGamutMappingIntent):
        '''Sets a 32-bit signed integer that defines the gamut mapping
        intent. It MUST be defined in the GamutMappingIntent enumeration
        (section 2.1.1.11).'''
        ...
    
    @property
    def endpoints(self) -> aspose.imaging.fileformats.wmf.objects.WmfCieXyzTriple:
        '''Gets a CIEXYZTriple object (section 2.2.2.7) that defines
        the CIE chromaticity x, y, and z coordinates of the three colors
        that correspond to the RGB  for the logical
        color space associated with the bitmap. If the
        field does not specify
        LCS_CALIBRATED_RGB, this field MUST be ignored.'''
        ...
    
    @endpoints.setter
    def endpoints(self, value : aspose.imaging.fileformats.wmf.objects.WmfCieXyzTriple):
        '''Sets a CIEXYZTriple object (section 2.2.2.7) that defines
        the CIE chromaticity x, y, and z coordinates of the three colors
        that correspond to the RGB  for the logical
        color space associated with the bitmap. If the
        field does not specify
        LCS_CALIBRATED_RGB, this field MUST be ignored.'''
        ...
    
    @property
    def gamma_red(self) -> int:
        ...
    
    @gamma_red.setter
    def gamma_red(self, value : int):
        ...
    
    @property
    def gamma_green(self) -> int:
        ...
    
    @gamma_green.setter
    def gamma_green(self, value : int):
        ...
    
    @property
    def gamma_blue(self) -> int:
        ...
    
    @gamma_blue.setter
    def gamma_blue(self, value : int):
        ...
    
    @property
    def filename(self) -> str:
        '''Gets an optional, null-terminated Unicode UTF16-LE character
        string, which specifies the name of a file that contains a color
        profile. If a file name is specified, and the
        field is set to LCS_CALIBRATED_RGB, the
        other fields of this structure SHOULD be ignored.'''
        ...
    
    @filename.setter
    def filename(self, value : str):
        '''Sets an optional, null-terminated Unicode UTF16-LE character
        string, which specifies the name of a file that contains a color
        profile. If a file name is specified, and the
        field is set to LCS_CALIBRATED_RGB, the
        other fields of this structure SHOULD be ignored.'''
        ...
    
    ...

class WmfMoveTo(WmfPointObject):
    '''The META_MOVETO record sets the output position in the playback device
    context to a specified point.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfObject(aspose.imaging.fileformats.emf.MetaObject):
    '''The base wmf object.'''
    
    ...

class WmfOffsetClipRgn(WmfPointObject):
    '''The META_OFFSETCLIPRGN record moves the clipping region in the playback
    device context by the specified offsets.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfOffsetViewPortOrg(WmfPointObject):
    '''The META_OFFSETVIEWPORTORG record moves the viewport origin in the
    playback device context by specified horizontal and vertical offsets.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfOffsetWindowOrg(WmfPointObject):
    '''The META_OFFSETWINDOWORG record moves the output window origin in the
    playback device context by specified horizontal and vertical offsets.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfPaintRegion(WmfObject):
    '''The META_PAINTREGION record paints the specified region by using the
    brush that is defined in the playback device context.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, region: aspose.imaging.fileformats.wmf.objects.WmfGraphicObject):
        '''Initializes a new instance of the  class.
        
        :param region: The region.'''
        ...
    
    @property
    def region_index(self) -> int:
        ...
    
    @region_index.setter
    def region_index(self, value : int):
        ...
    
    ...

class WmfPatBlt(WmfPointObject):
    '''The META_PATBLT record paints a specified rectangle using the brush that
    is defined in the playback device context. The brush color and the
    surface color or colors are combined using the specified raster
    operation.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    @property
    def raster_operation(self) -> aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation:
        ...
    
    @raster_operation.setter
    def raster_operation(self, value : aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation):
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width.'''
        ...
    
    ...

class WmfPie(WmfRectangle):
    '''The META_PIE record draws a pie-shaped wedge bounded by the intersection
    of an ellipse and two radials. The pie is outlined by using the pen and
    filled by using the brush that are defined in the playback device
    context.'''
    
    def __init__(self):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    @property
    def radial2(self) -> aspose.imaging.Point:
        '''Gets the radial2.'''
        ...
    
    @radial2.setter
    def radial2(self, value : aspose.imaging.Point):
        '''Sets the radial2.'''
        ...
    
    @property
    def radial1(self) -> aspose.imaging.Point:
        '''Gets the radial1.'''
        ...
    
    @radial1.setter
    def radial1(self, value : aspose.imaging.Point):
        '''Sets the radial1.'''
        ...
    
    ...

class WmfPitchAndFamily:
    '''The PitchAndFamily object specifies the pitch and family properties of a
    Font object (section 2.2.1.2). Pitch refers to the width of the
    characters, and family refers to the general appearance of a font.'''
    
    @overload
    def __init__(self, byte_data: int):
        '''Initializes a new instance of the
        struct.
        
        :param byte_data: The  data.'''
        ...
    
    @overload
    def __init__(self, pitch: aspose.imaging.fileformats.wmf.consts.WmfPitchFont, family: aspose.imaging.fileformats.wmf.consts.WmfFamilyFont):
        '''Initializes a new instance of the
        struct.
        
        :param pitch: The pitch.
        :param family: The family.'''
        ...
    
    @overload
    def __init__(self):
        ...
    
    def to_byte(self) -> int:
        '''To the byte.
        
        :returns: The byte value.'''
        ...
    
    @property
    def family(self) -> aspose.imaging.fileformats.wmf.consts.WmfFamilyFont:
        '''Gets A property of a font that describes its general appearance.
        This MUST be a value in the FamilyFont enumeration'''
        ...
    
    @property
    def pitch(self) -> aspose.imaging.fileformats.wmf.consts.WmfPitchFont:
        '''Gets A property of a font that describes the pitch, of the
        characters. This MUST be a value in the PitchFont enumeration.'''
        ...
    
    @property
    def byte_data(self) -> int:
        ...
    
    @byte_data.setter
    def byte_data(self, value : int):
        ...
    
    ...

class WmfPointObject(WmfObject):
    '''The Point object.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfPolyLine(WmfObject):
    '''The poly line object.'''
    
    def __init__(self):
        ...
    
    @property
    def number_of_point(self) -> int:
        ...
    
    @number_of_point.setter
    def number_of_point(self, value : int):
        ...
    
    @property
    def a_points(self) -> List[aspose.imaging.Point]:
        ...
    
    @a_points.setter
    def a_points(self, value : List[aspose.imaging.Point]):
        ...
    
    ...

class WmfPolyPolygon(WmfObject):
    '''The PolyPolygon Object defines a series of closed polygons.'''
    
    def __init__(self):
        ...
    
    @property
    def number_of_polygons(self) -> int:
        ...
    
    @number_of_polygons.setter
    def number_of_polygons(self, value : int):
        ...
    
    @property
    def a_points_per_polygon(self) -> List[int]:
        ...
    
    @a_points_per_polygon.setter
    def a_points_per_polygon(self, value : List[int]):
        ...
    
    @property
    def a_points(self) -> List[List[aspose.imaging.Point]]:
        ...
    
    @a_points.setter
    def a_points(self, value : List[List[aspose.imaging.Point]]):
        ...
    
    ...

class WmfPolygon(WmfObject):
    '''The polygon object'''
    
    def __init__(self):
        ...
    
    @property
    def number_of_point(self) -> int:
        ...
    
    @number_of_point.setter
    def number_of_point(self, value : int):
        ...
    
    @property
    def a_points(self) -> List[aspose.imaging.Point]:
        ...
    
    @a_points.setter
    def a_points(self, value : List[aspose.imaging.Point]):
        ...
    
    ...

class WmfRealizePalette(WmfObject):
    '''The META_REALIZEPALETTE record maps entries from the logical palette
    that is defined in the playback device context to the system palette.'''
    
    def __init__(self):
        ...
    
    ...

class WmfRecord(aspose.imaging.fileformats.emf.MetaObject):
    '''The Wmf Record'''
    
    def __init__(self):
        ...
    
    @property
    def size(self) -> int:
        '''Gets the size.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets the size.'''
        ...
    
    @property
    def record_type(self) -> aspose.imaging.fileformats.wmf.consts.WmfRecordType:
        ...
    
    @record_type.setter
    def record_type(self, value : aspose.imaging.fileformats.wmf.consts.WmfRecordType):
        ...
    
    ...

class WmfRectangle(WmfObject):
    '''The META_RECTANGLE record paints a rectangle. The rectangle is outlined
    by using the pen and filled by using the brush that are defined in the
    playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    ...

class WmfRegion(aspose.imaging.fileformats.emf.MetaObject):
    '''The Region Object defines a potentially non-rectilinear shape defined by
    an array of scanlines.'''
    
    def __init__(self):
        ...
    
    @property
    def next_in_chain(self) -> int:
        ...
    
    @next_in_chain.setter
    def next_in_chain(self, value : int):
        ...
    
    @property
    def object_type(self) -> int:
        ...
    
    @object_type.setter
    def object_type(self, value : int):
        ...
    
    @property
    def object_count(self) -> int:
        ...
    
    @object_count.setter
    def object_count(self, value : int):
        ...
    
    @property
    def region_size(self) -> int:
        ...
    
    @region_size.setter
    def region_size(self, value : int):
        ...
    
    @property
    def scan_count(self) -> int:
        ...
    
    @scan_count.setter
    def scan_count(self, value : int):
        ...
    
    @property
    def max_scan(self) -> int:
        ...
    
    @max_scan.setter
    def max_scan(self, value : int):
        ...
    
    @property
    def bounding_rectangle(self) -> aspose.imaging.Rectangle:
        ...
    
    @bounding_rectangle.setter
    def bounding_rectangle(self, value : aspose.imaging.Rectangle):
        ...
    
    @property
    def a_scans(self) -> List[aspose.imaging.fileformats.wmf.objects.WmfScanObject]:
        ...
    
    @a_scans.setter
    def a_scans(self, value : List[aspose.imaging.fileformats.wmf.objects.WmfScanObject]):
        ...
    
    ...

class WmfResizePalette(WmfObject):
    '''The META_RESIZEPALETTE record redefines the size of the logical palette
    that is defined in the playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def number_of_entries(self) -> int:
        ...
    
    @number_of_entries.setter
    def number_of_entries(self, value : int):
        ...
    
    ...

class WmfRestoreDc(WmfObject):
    '''The restore DC object'''
    
    def __init__(self):
        ...
    
    @property
    def n_saved_dc(self) -> int:
        ...
    
    @n_saved_dc.setter
    def n_saved_dc(self, value : int):
        ...
    
    ...

class WmfRoundRect(WmfRectangle):
    '''The rectangle object.'''
    
    def __init__(self):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width.'''
        ...
    
    ...

class WmfSaveDc(WmfObject):
    '''The META_SAVEDC record saves the playback device context for later
    retrieval.'''
    
    def __init__(self):
        ...
    
    ...

class WmfScaleViewportExt(WmfScaleWindowExt):
    '''The META_SCALEVIEWPORTEXT record scales the horizontal and vertical
    extents of the viewport that is defined in the playback device context
    by using the ratios formed by the specified multiplicands and divisors.'''
    
    def __init__(self):
        ...
    
    @property
    def y_denom(self) -> int:
        ...
    
    @y_denom.setter
    def y_denom(self, value : int):
        ...
    
    @property
    def y_num(self) -> int:
        ...
    
    @y_num.setter
    def y_num(self, value : int):
        ...
    
    @property
    def x_denom(self) -> int:
        ...
    
    @x_denom.setter
    def x_denom(self, value : int):
        ...
    
    @property
    def x_num(self) -> int:
        ...
    
    @x_num.setter
    def x_num(self, value : int):
        ...
    
    ...

class WmfScaleWindowExt(WmfObject):
    '''The META_SCALEWINDOWEXT record scales the horizontal and vertical
    extents of the output window that is defined in the playback device
    context by using the ratios formed by specified multiplicands and
    divisors.'''
    
    def __init__(self):
        ...
    
    @property
    def y_denom(self) -> int:
        ...
    
    @y_denom.setter
    def y_denom(self, value : int):
        ...
    
    @property
    def y_num(self) -> int:
        ...
    
    @y_num.setter
    def y_num(self, value : int):
        ...
    
    @property
    def x_denom(self) -> int:
        ...
    
    @x_denom.setter
    def x_denom(self, value : int):
        ...
    
    @property
    def x_num(self) -> int:
        ...
    
    @x_num.setter
    def x_num(self, value : int):
        ...
    
    ...

class WmfScanObject(aspose.imaging.fileformats.emf.MetaObject):
    '''The Scan Object specifies a collection of scanlines.'''
    
    def __init__(self):
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count.'''
        ...
    
    @count.setter
    def count(self, value : int):
        '''Sets the count.'''
        ...
    
    @property
    def top(self) -> int:
        '''Gets the top.'''
        ...
    
    @top.setter
    def top(self, value : int):
        '''Sets the top.'''
        ...
    
    @property
    def bottom(self) -> int:
        '''Gets the bottom.'''
        ...
    
    @bottom.setter
    def bottom(self, value : int):
        '''Sets the bottom.'''
        ...
    
    @property
    def scan_lines(self) -> List[aspose.imaging.Point]:
        ...
    
    @scan_lines.setter
    def scan_lines(self, value : List[aspose.imaging.Point]):
        ...
    
    @property
    def count2(self) -> int:
        '''Gets the count2.'''
        ...
    
    @count2.setter
    def count2(self, value : int):
        '''Sets the count2.'''
        ...
    
    ...

class WmfSelectClipRegion(WmfObject):
    '''The META_SELECTCLIPREGION record specifies a Region Object (section 2.2.1.5) to be the current clipping region.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, region: aspose.imaging.fileformats.wmf.objects.WmfGraphicObject):
        '''Initializes a new instance of the  class.
        
        :param region: The region.'''
        ...
    
    @property
    def object_index(self) -> int:
        ...
    
    @object_index.setter
    def object_index(self, value : int):
        ...
    
    ...

class WmfSelectObject(WmfObject):
    '''The select object.'''
    
    @overload
    def __init__(self, wmf_object: aspose.imaging.fileformats.wmf.objects.WmfGraphicObject):
        '''Initializes a new instance of the  class.
        
        :param wmf_object: The WMF object.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def object_index(self) -> int:
        ...
    
    @object_index.setter
    def object_index(self, value : int):
        ...
    
    ...

class WmfSelectPalette(WmfObject):
    '''The META_SELECTPALETTE record defines the current logical palette with a
    specified Palette Object.'''
    
    def __init__(self):
        ...
    
    @property
    def object_index(self) -> int:
        ...
    
    @object_index.setter
    def object_index(self, value : int):
        ...
    
    ...

class WmfSetBkColor(WmfObject):
    '''The META_SETBKCOLOR record sets the background color in the playback
    device context to a specified color, or to the nearest physical color if
    the device cannot represent the specified color.'''
    
    def __init__(self):
        ...
    
    @property
    def color_ref(self) -> int:
        ...
    
    @color_ref.setter
    def color_ref(self, value : int):
        ...
    
    ...

class WmfSetBkMode(WmfObject):
    '''The set bk mode.'''
    
    def __init__(self):
        ...
    
    @property
    def bk_mode(self) -> aspose.imaging.fileformats.wmf.consts.WmfMixMode:
        ...
    
    @bk_mode.setter
    def bk_mode(self, value : aspose.imaging.fileformats.wmf.consts.WmfMixMode):
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets the reserved.'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets the reserved.'''
        ...
    
    ...

class WmfSetDibToDev(WmfObject):
    '''The META_SETDIBTODEV record sets a block of pixels in the playback
    device context using device-independent color data. The source of the
    color data is a DIB.'''
    
    def __init__(self):
        ...
    
    @property
    def color_usage(self) -> aspose.imaging.fileformats.wmf.consts.WmfColorUsageEnum:
        ...
    
    @color_usage.setter
    def color_usage(self, value : aspose.imaging.fileformats.wmf.consts.WmfColorUsageEnum):
        ...
    
    @property
    def scan_count(self) -> int:
        ...
    
    @scan_count.setter
    def scan_count(self, value : int):
        ...
    
    @property
    def start_scan(self) -> int:
        ...
    
    @start_scan.setter
    def start_scan(self, value : int):
        ...
    
    @property
    def dib_pos(self) -> aspose.imaging.Point:
        ...
    
    @dib_pos.setter
    def dib_pos(self, value : aspose.imaging.Point):
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width.'''
        ...
    
    @property
    def dest_pos(self) -> aspose.imaging.Point:
        ...
    
    @dest_pos.setter
    def dest_pos(self, value : aspose.imaging.Point):
        ...
    
    @property
    def dib(self) -> aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap:
        '''Gets the dib.'''
        ...
    
    @dib.setter
    def dib(self, value : aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap):
        '''Sets the dib.'''
        ...
    
    ...

class WmfSetLayout(WmfObject):
    '''The META_SETLAYOUT record defines the layout orientation in the playback
    device context. The layout orientation determines the direction in which
    text and graphics are drawn'''
    
    def __init__(self):
        ...
    
    @property
    def layout_mode(self) -> Aspose.Imaging.FileFormats.Emf.Emf.Records.EmfSetLayout+LayoutModeEnum:
        ...
    
    @layout_mode.setter
    def layout_mode(self, value : Aspose.Imaging.FileFormats.Emf.Emf.Records.EmfSetLayout+LayoutModeEnum):
        ...
    
    ...

class WmfSetMapMode(WmfObject):
    '''The set map mode.'''
    
    def __init__(self):
        ...
    
    @property
    def map_mode(self) -> aspose.imaging.fileformats.wmf.consts.WmfMapMode:
        ...
    
    @map_mode.setter
    def map_mode(self, value : aspose.imaging.fileformats.wmf.consts.WmfMapMode):
        ...
    
    ...

class WmfSetMapperFlags(WmfObject):
    '''The META_SETMAPPERFLAGS record defines the algorithm that the font
    mapper uses when it maps logical fonts to physical fonts.'''
    
    def __init__(self):
        ...
    
    @property
    def mapper_values(self) -> int:
        ...
    
    @mapper_values.setter
    def mapper_values(self, value : int):
        ...
    
    ...

class WmfSetPalentries(WmfObject):
    '''The META_SETPALENTRIES record defines RGB color values in a range of
    entries in the logical palette that is defined in the playback device
    context.'''
    
    def __init__(self):
        ...
    
    @property
    def log_palette(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfLogPalette:
        ...
    
    @log_palette.setter
    def log_palette(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfLogPalette):
        ...
    
    @property
    def start(self) -> int:
        '''Gets the start.'''
        ...
    
    @start.setter
    def start(self, value : int):
        '''Sets the start.'''
        ...
    
    ...

class WmfSetPixel(WmfPointObject):
    '''The META_SETPIXEL record sets the pixel at the specified coordinates to
    the specified color.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    @property
    def color_ref(self) -> int:
        ...
    
    @color_ref.setter
    def color_ref(self, value : int):
        ...
    
    ...

class WmfSetPolyFillMode(WmfObject):
    '''The set poly fill mode.'''
    
    def __init__(self):
        ...
    
    @property
    def poly_fill_mode(self) -> aspose.imaging.fileformats.wmf.consts.WmfPolyFillMode:
        ...
    
    @poly_fill_mode.setter
    def poly_fill_mode(self, value : aspose.imaging.fileformats.wmf.consts.WmfPolyFillMode):
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets the reserved.'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets the reserved.'''
        ...
    
    ...

class WmfSetRelabs(WmfObject):
    '''The META_SETRELABS record is reserved and not supported.'''
    
    def __init__(self):
        ...
    
    @property
    def parameters(self) -> List[int]:
        '''Gets the parameter.'''
        ...
    
    @parameters.setter
    def parameters(self, value : List[int]):
        '''Sets the parameter.'''
        ...
    
    ...

class WmfSetRop2(WmfObject):
    '''The set rop2'''
    
    def __init__(self):
        ...
    
    @property
    def draw_mode(self) -> aspose.imaging.fileformats.wmf.consts.WmfBinaryRasterOperation:
        ...
    
    @draw_mode.setter
    def draw_mode(self, value : aspose.imaging.fileformats.wmf.consts.WmfBinaryRasterOperation):
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets the reserved.'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets the reserved.'''
        ...
    
    ...

class WmfSetStretchbltMode(WmfObject):
    '''The META_SETSTRETCHBLTMODE record defines the bitmap stretching mode in
    the playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def stretch_mode(self) -> aspose.imaging.fileformats.wmf.consts.StretchMode:
        ...
    
    @stretch_mode.setter
    def stretch_mode(self, value : aspose.imaging.fileformats.wmf.consts.StretchMode):
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets the reserved.'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets the reserved.'''
        ...
    
    ...

class WmfSetTextAlign(WmfObject):
    '''The Set text align'''
    
    def __init__(self):
        ...
    
    @property
    def text_align(self) -> aspose.imaging.fileformats.wmf.consts.WmfTextAlignmentModeFlags:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.imaging.fileformats.wmf.consts.WmfTextAlignmentModeFlags):
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets the reserved.'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets the reserved.'''
        ...
    
    ...

class WmfSetTextCharExtra(WmfObject):
    '''The META_SETTEXTCHAREXTRA record defines inter-character spacing for
    text justification in the playback device context. Spacing is added to
    the white space between each character, including
    characters, when a line of justified text is
    output.'''
    
    def __init__(self):
        ...
    
    @property
    def char_extra(self) -> int:
        ...
    
    @char_extra.setter
    def char_extra(self, value : int):
        ...
    
    ...

class WmfSetTextColor(WmfObject):
    '''The Set text color.'''
    
    def __init__(self):
        ...
    
    @property
    def color_ref(self) -> int:
        ...
    
    @color_ref.setter
    def color_ref(self, value : int):
        ...
    
    @property
    def extended_byte(self) -> int:
        ...
    
    @extended_byte.setter
    def extended_byte(self, value : int):
        ...
    
    ...

class WmfSetTextJustification(WmfObject):
    '''The META_SETTEXTJUSTIFICATION record defines the amount of space to add
    to  characters in a string of justified text.'''
    
    def __init__(self):
        ...
    
    @property
    def break_count(self) -> int:
        ...
    
    @break_count.setter
    def break_count(self, value : int):
        ...
    
    @property
    def break_extra(self) -> int:
        ...
    
    @break_extra.setter
    def break_extra(self, value : int):
        ...
    
    ...

class WmfSetViewportExt(WmfPointObject):
    '''The META_SETVIEWPORTEXT record sets the horizontal and vertical extents
    of the viewport in the playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfSetViewportOrg(WmfPointObject):
    '''The META_SETVIEWPORTORG record defines the viewport origin in the
    playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfSetWindowExt(WmfPointObject):
    '''The set window object.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfSetWindowOrg(WmfPointObject):
    '''The set window org object'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    ...

class WmfStretchBlt(WmfObject):
    '''The META_STRETCHBLT record specifies the transfer of a block of pixels
    according to a raster operation, with possible expansion or contraction.'''
    
    def __init__(self):
        ...
    
    @property
    def raster_operation(self) -> aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation:
        ...
    
    @raster_operation.setter
    def raster_operation(self, value : aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation):
        ...
    
    @property
    def src_height(self) -> int:
        ...
    
    @src_height.setter
    def src_height(self, value : int):
        ...
    
    @property
    def src_width(self) -> int:
        ...
    
    @src_width.setter
    def src_width(self, value : int):
        ...
    
    @property
    def src_position(self) -> aspose.imaging.Point:
        ...
    
    @src_position.setter
    def src_position(self, value : aspose.imaging.Point):
        ...
    
    @property
    def dest_height(self) -> int:
        ...
    
    @dest_height.setter
    def dest_height(self, value : int):
        ...
    
    @property
    def dest_width(self) -> int:
        ...
    
    @dest_width.setter
    def dest_width(self, value : int):
        ...
    
    @property
    def dst_position(self) -> aspose.imaging.Point:
        ...
    
    @dst_position.setter
    def dst_position(self, value : aspose.imaging.Point):
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets the reserved.'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets the reserved.'''
        ...
    
    @property
    def bitmap(self) -> aspose.imaging.fileformats.wmf.objects.WmfBitmap16:
        '''Gets the bitmap.'''
        ...
    
    @bitmap.setter
    def bitmap(self, value : aspose.imaging.fileformats.wmf.objects.WmfBitmap16):
        '''Sets the bitmap.'''
        ...
    
    ...

class WmfStretchDib(WmfObject):
    '''The wmf Stretch DIB objetc.'''
    
    def __init__(self):
        '''WMFs the record.'''
        ...
    
    @property
    def raster_operation(self) -> aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation:
        ...
    
    @raster_operation.setter
    def raster_operation(self, value : aspose.imaging.fileformats.wmf.consts.WmfTernaryRasterOperation):
        ...
    
    @property
    def color_usage(self) -> aspose.imaging.fileformats.wmf.consts.WmfColorUsageEnum:
        ...
    
    @color_usage.setter
    def color_usage(self, value : aspose.imaging.fileformats.wmf.consts.WmfColorUsageEnum):
        ...
    
    @property
    def src_height(self) -> int:
        ...
    
    @src_height.setter
    def src_height(self, value : int):
        ...
    
    @property
    def src_width(self) -> int:
        ...
    
    @src_width.setter
    def src_width(self, value : int):
        ...
    
    @property
    def y_src(self) -> int:
        ...
    
    @y_src.setter
    def y_src(self, value : int):
        ...
    
    @property
    def x_src(self) -> int:
        ...
    
    @x_src.setter
    def x_src(self, value : int):
        ...
    
    @property
    def dest_height(self) -> int:
        ...
    
    @dest_height.setter
    def dest_height(self, value : int):
        ...
    
    @property
    def dest_width(self) -> int:
        ...
    
    @dest_width.setter
    def dest_width(self, value : int):
        ...
    
    @property
    def y_dest(self) -> int:
        ...
    
    @y_dest.setter
    def y_dest(self, value : int):
        ...
    
    @property
    def x_dest(self) -> int:
        ...
    
    @x_dest.setter
    def x_dest(self, value : int):
        ...
    
    @property
    def source_bitmap(self) -> aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap:
        ...
    
    @source_bitmap.setter
    def source_bitmap(self, value : aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap):
        ...
    
    ...

class WmfTextOut(WmfExtTextOut):
    '''The META_EXTTEXTOUT record outputs text by using the font, background
    color, and text color that are defined in the playback device context.
    Optionally, dimensions can be provided for clipping, opaquing, or both.'''
    
    def __init__(self):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.Point):
        '''Sets the point.'''
        ...
    
    @property
    def string_length(self) -> int:
        ...
    
    @string_length.setter
    def string_length(self, value : int):
        ...
    
    @property
    def fw_opts(self) -> int:
        ...
    
    @fw_opts.setter
    def fw_opts(self, value : int):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets the rectangle.'''
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text.'''
        ...
    
    @property
    def dx(self) -> List[int]:
        '''Gets the dx.'''
        ...
    
    @dx.setter
    def dx(self, value : List[int]):
        '''Sets the dx.'''
        ...
    
    @property
    def extended_byte(self) -> int:
        ...
    
    @extended_byte.setter
    def extended_byte(self, value : int):
        ...
    
    ...

class WmfUntyped(WmfObject):
    '''The wmf untyped object'''
    
    def __init__(self):
        ...
    
    @property
    def parameters(self) -> List[int]:
        '''Gets the parameters.'''
        ...
    
    @parameters.setter
    def parameters(self, value : List[int]):
        '''Sets the parameters.'''
        ...
    
    ...

