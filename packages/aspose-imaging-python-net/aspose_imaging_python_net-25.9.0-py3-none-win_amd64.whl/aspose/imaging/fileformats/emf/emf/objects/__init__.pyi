"""The namespace contains types [MS-EMF]: Enhanced Metafile Format.
            2.2 EMF Objects"""
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

class EmfBasePen(EmfObject):
    '''The base pen object'''
    
    @property
    def pen_style(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfPenStyle:
        ...
    
    @pen_style.setter
    def pen_style(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfPenStyle):
        ...
    
    @property
    def argb_32_color_ref(self) -> int:
        ...
    
    @argb_32_color_ref.setter
    def argb_32_color_ref(self, value : int):
        ...
    
    ...

class EmfBitFix28To4(EmfObject):
    '''The BitFIX28_4 object defines a numeric value in 28.4 bit FIX notation.'''
    
    def __init__(self, dword_data: int):
        '''Initializes a new instance of the  class.
        
        :param dword_data: The dword data.'''
        ...
    
    @property
    def int_val(self) -> int:
        ...
    
    @int_val.setter
    def int_val(self, value : int):
        ...
    
    @property
    def frac_value(self) -> int:
        ...
    
    @frac_value.setter
    def frac_value(self, value : int):
        ...
    
    @property
    def value(self) -> float:
        '''Gets the resulting float value;'''
        ...
    
    ...

class EmfColorAdjustment(EmfObject):
    '''The ColorAdjustment object defines values for adjusting the colors in source bitmaps in bit-block transfers.'''
    
    def __init__(self):
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 16-bit unsigned integer that specifies the size in bytes of this object. This MUST be 0x0018.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 16-bit unsigned integer that specifies the size in bytes of this object. This MUST be 0x0018.'''
        ...
    
    @property
    def values(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfColorAdjustmentEnum:
        '''Gets a 16-bit unsigned integer that specifies how to prepare the output image. This field can be
        set to NULL or to any combination of values in the ColorAdjustment enumeration (section 2.1.5).'''
        ...
    
    @values.setter
    def values(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfColorAdjustmentEnum):
        '''Sets a 16-bit unsigned integer that specifies how to prepare the output image. This field can be
        set to NULL or to any combination of values in the ColorAdjustment enumeration (section 2.1.5).'''
        ...
    
    @property
    def illuminant_index(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfIlluminant:
        ...
    
    @illuminant_index.setter
    def illuminant_index(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfIlluminant):
        ...
    
    @property
    def red_gamma(self) -> int:
        ...
    
    @red_gamma.setter
    def red_gamma(self, value : int):
        ...
    
    @property
    def green_gamma(self) -> int:
        ...
    
    @green_gamma.setter
    def green_gamma(self, value : int):
        ...
    
    @property
    def blue_gamma(self) -> int:
        ...
    
    @blue_gamma.setter
    def blue_gamma(self, value : int):
        ...
    
    @property
    def reference_black(self) -> int:
        ...
    
    @reference_black.setter
    def reference_black(self, value : int):
        ...
    
    @property
    def reference_white(self) -> int:
        ...
    
    @reference_white.setter
    def reference_white(self, value : int):
        ...
    
    @property
    def contrast(self) -> int:
        '''Gets a 16-bit signed integer that specifies the amount of contrast to be applied to the source object.
        This value SHOULD be in the range from –100 to 100. A value of zero means contrast adjustment MUST NOT be performed.'''
        ...
    
    @contrast.setter
    def contrast(self, value : int):
        '''Sets a 16-bit signed integer that specifies the amount of contrast to be applied to the source object.
        This value SHOULD be in the range from –100 to 100. A value of zero means contrast adjustment MUST NOT be performed.'''
        ...
    
    @property
    def brightness(self) -> int:
        '''Gets a 16-bit signed integer that specifies the amount of brightness to be applied to the source object.
        This value SHOULD be in the range from –100 to 100.
        A value of zero means brightness adjustment MUST NOT be performed.'''
        ...
    
    @brightness.setter
    def brightness(self, value : int):
        '''Sets a 16-bit signed integer that specifies the amount of brightness to be applied to the source object.
        This value SHOULD be in the range from –100 to 100.
        A value of zero means brightness adjustment MUST NOT be performed.'''
        ...
    
    @property
    def colorfullness(self) -> int:
        '''Gets a 16-bit signed integer that specifies the amount of colorfulness to be applied to the source object.
        This value SHOULD be in the range from –100 to 100.
        A value of zero means colorfulness adjustment MUST NOT be performed'''
        ...
    
    @colorfullness.setter
    def colorfullness(self, value : int):
        '''Sets a 16-bit signed integer that specifies the amount of colorfulness to be applied to the source object.
        This value SHOULD be in the range from –100 to 100.
        A value of zero means colorfulness adjustment MUST NOT be performed'''
        ...
    
    @property
    def red_green_tint(self) -> int:
        ...
    
    @red_green_tint.setter
    def red_green_tint(self, value : int):
        ...
    
    ...

class EmfDesignVector(EmfObject):
    '''The DesignVector (section 2.2.3) object defines the design vector, which specifies values for the font axes of a multiple master font.'''
    
    def __init__(self):
        ...
    
    @property
    def signature(self) -> int:
        '''Gets a 32-bit unsigned integer that MUST be set to the value 0x08007664.'''
        ...
    
    @signature.setter
    def signature(self, value : int):
        '''Sets a 32-bit unsigned integer that MUST be set to the value 0x08007664.'''
        ...
    
    @property
    def num_axes(self) -> int:
        ...
    
    @num_axes.setter
    def num_axes(self, value : int):
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets an optional array of 32-bit signed integers that specify the values
        of the font axes of a multiple master, OpenType font. The maximum number of values in the array is 16.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets an optional array of 32-bit signed integers that specify the values
        of the font axes of a multiple master, OpenType font. The maximum number of values in the array is 16.'''
        ...
    
    ...

class EmfEpsData(EmfObject):
    '''The EpsData object is a container for EPS data'''
    
    def __init__(self):
        ...
    
    @property
    def size_data(self) -> int:
        ...
    
    @size_data.setter
    def size_data(self, value : int):
        ...
    
    @property
    def version(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the PostScript language level. This
        value MUST be 0x00000001'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the PostScript language level. This
        value MUST be 0x00000001'''
        ...
    
    @property
    def points(self) -> List[aspose.imaging.fileformats.emf.emf.objects.EmfPoint28To4]:
        '''Gets an array of three Point28_4 objects (section 2.2.23) that defines the
        coordinates of the output parallelogram using 28.4 bit FIX notation'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.fileformats.emf.emf.objects.EmfPoint28To4]):
        '''Sets an array of three Point28_4 objects (section 2.2.23) that defines the
        coordinates of the output parallelogram using 28.4 bit FIX notation'''
        ...
    
    @property
    def post_script_data(self) -> bytes:
        ...
    
    @post_script_data.setter
    def post_script_data(self, value : bytes):
        ...
    
    ...

class EmfFormat(EmfObject):
    '''The EmrFormat object contains information that identifies the format of image data in an
    EMR_COMMENT_MULTIFORMATS record(section 2.3.3.4.3).'''
    
    def __init__(self):
        ...
    
    @property
    def signature(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfFormatSignature:
        '''Gets a 32-bit unsigned integer that specifies the format of the image data.
        This value MUST be in the FormatSignature enumeration (section 2.1.14).'''
        ...
    
    @signature.setter
    def signature(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfFormatSignature):
        '''Sets a 32-bit unsigned integer that specifies the format of the image data.
        This value MUST be in the FormatSignature enumeration (section 2.1.14).'''
        ...
    
    @property
    def version(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the format version number.
        If the Signature field specifies encapsulated PostScript (EPS),
        this value MUST be 0x00000001; otherwise, this value MUST be ignored'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the format version number.
        If the Signature field specifies encapsulated PostScript (EPS),
        this value MUST be 0x00000001; otherwise, this value MUST be ignored'''
        ...
    
    @property
    def size_data(self) -> int:
        ...
    
    @size_data.setter
    def size_data(self, value : int):
        ...
    
    @property
    def off_data(self) -> int:
        ...
    
    @off_data.setter
    def off_data(self, value : int):
        ...
    
    ...

class EmfGradientRectangle(EmfObject):
    '''The GradientRectangle object defines a rectangle using TriVertex objects (section 2.2.26) in an
    EMR_GRADIENTFILL record (section 2.3.5.12).'''
    
    def __init__(self):
        ...
    
    @property
    def upper_left(self) -> int:
        ...
    
    @upper_left.setter
    def upper_left(self, value : int):
        ...
    
    @property
    def lower_right(self) -> int:
        ...
    
    @lower_right.setter
    def lower_right(self, value : int):
        ...
    
    ...

class EmfGradientTriangle(EmfObject):
    '''The GradientTriangle object defines a triangle using TriVertex objects (section 2.2.26) in an
    EMR_GRADIENTFILL record (section 2.3.5.12)'''
    
    def __init__(self):
        ...
    
    @property
    def vertex1(self) -> int:
        '''Gets an index into an array of TriVertex objects that specifies a vertex of a
        triangle. The index MUST be smaller than the size of the array, as defined by the nVer field of
        the EMR_GRADIENTFILL record.'''
        ...
    
    @vertex1.setter
    def vertex1(self, value : int):
        '''Sets an index into an array of TriVertex objects that specifies a vertex of a
        triangle. The index MUST be smaller than the size of the array, as defined by the nVer field of
        the EMR_GRADIENTFILL record.'''
        ...
    
    @property
    def vertex2(self) -> int:
        '''Gets an index into an array of TriVertex objects that specifies a vertex of a
        triangle. The index MUST be smaller than the size of the array, as defined by the nVer field of
        the EMR_GRADIENTFILL record.'''
        ...
    
    @vertex2.setter
    def vertex2(self, value : int):
        '''Sets an index into an array of TriVertex objects that specifies a vertex of a
        triangle. The index MUST be smaller than the size of the array, as defined by the nVer field of
        the EMR_GRADIENTFILL record.'''
        ...
    
    @property
    def vertex3(self) -> int:
        '''Gets an index into an array of TriVertex objects that specifies a vertex of a
        triangle. The index MUST be smaller than the size of the array, as defined by the nVer field of
        the EMR_GRADIENTFILL record.'''
        ...
    
    @vertex3.setter
    def vertex3(self, value : int):
        '''Sets an index into an array of TriVertex objects that specifies a vertex of a
        triangle. The index MUST be smaller than the size of the array, as defined by the nVer field of
        the EMR_GRADIENTFILL record.'''
        ...
    
    ...

class EmfHeaderExtension1(EmfHeaderObject):
    '''The HeaderExtension1 object defines the first extension to the EMF metafile header.
    It adds support for a PixelFormatDescriptor object (section 2.2.22) and OpenGL
    [OPENGL] records (section 2.3.9).'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets a WMF RectL object ([MS-WMF] section 2.2.2.19) that specifies the rectangular inclusive-inclusive
        bounds in device units of the smallest rectangle that can be drawn around the image stored in
        the metafile'''
        ...
    
    @bounds.setter
    def bounds(self, value : aspose.imaging.Rectangle):
        '''Sets a WMF RectL object ([MS-WMF] section 2.2.2.19) that specifies the rectangular inclusive-inclusive
        bounds in device units of the smallest rectangle that can be drawn around the image stored in
        the metafile'''
        ...
    
    @property
    def frame(self) -> aspose.imaging.Rectangle:
        '''Gets a WMF RectL object that specifies the rectangular inclusive-inclusive dimensions, in .01 millimeter
        units, of a rectangle that surrounds the image stored in the metafile'''
        ...
    
    @frame.setter
    def frame(self, value : aspose.imaging.Rectangle):
        '''Sets a WMF RectL object that specifies the rectangular inclusive-inclusive dimensions, in .01 millimeter
        units, of a rectangle that surrounds the image stored in the metafile'''
        ...
    
    @property
    def record_signature(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfFormatSignature:
        ...
    
    @record_signature.setter
    def record_signature(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfFormatSignature):
        ...
    
    @property
    def version(self) -> int:
        '''Gets Version (4 bytes): A 32-bit unsigned integer that specifies EMF metafile interoperability. This SHOULD be 0x00010000'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets Version (4 bytes): A 32-bit unsigned integer that specifies EMF metafile interoperability. This SHOULD be 0x00010000'''
        ...
    
    @property
    def bytes(self) -> int:
        '''Gets  32-bit unsigned integer that specifies the size of the metafile, in bytes.'''
        ...
    
    @bytes.setter
    def bytes(self, value : int):
        '''Sets  32-bit unsigned integer that specifies the size of the metafile, in bytes.'''
        ...
    
    @property
    def records(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the number of records in the metafile'''
        ...
    
    @records.setter
    def records(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the number of records in the metafile'''
        ...
    
    @property
    def handles(self) -> int:
        '''Gets a 16-bit unsigned integer that specifies the number of graphics objects that will be used during the processing of the metafile'''
        ...
    
    @handles.setter
    def handles(self, value : int):
        '''Sets a 16-bit unsigned integer that specifies the number of graphics objects that will be used during the processing of the metafile'''
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets a 16-bit unsigned integer that MUST be 0x0000 and MUST be ignored'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets a 16-bit unsigned integer that MUST be 0x0000 and MUST be ignored'''
        ...
    
    @property
    def n_desription(self) -> int:
        ...
    
    @n_desription.setter
    def n_desription(self, value : int):
        ...
    
    @property
    def off_description(self) -> int:
        ...
    
    @off_description.setter
    def off_description(self, value : int):
        ...
    
    @property
    def n_pal_entries(self) -> int:
        ...
    
    @n_pal_entries.setter
    def n_pal_entries(self, value : int):
        ...
    
    @property
    def device(self) -> aspose.imaging.Size:
        '''Gets a WMF SizeL object ([MS-WMF] section 2.2.2.22) that specifies the size of the reference device, in pixels'''
        ...
    
    @device.setter
    def device(self, value : aspose.imaging.Size):
        '''Sets a WMF SizeL object ([MS-WMF] section 2.2.2.22) that specifies the size of the reference device, in pixels'''
        ...
    
    @property
    def millimeters(self) -> aspose.imaging.Size:
        '''Gets a WMF SizeL object that specifies the size of the reference device, in millimeters'''
        ...
    
    @millimeters.setter
    def millimeters(self, value : aspose.imaging.Size):
        '''Sets a WMF SizeL object that specifies the size of the reference device, in millimeters'''
        ...
    
    @property
    def valid(self) -> bool:
        '''Gets a value indicating whether this  is valid.'''
        ...
    
    @property
    def cb_pixel_format(self) -> int:
        ...
    
    @cb_pixel_format.setter
    def cb_pixel_format(self, value : int):
        ...
    
    @property
    def off_pixel_format(self) -> int:
        ...
    
    @off_pixel_format.setter
    def off_pixel_format(self, value : int):
        ...
    
    @property
    def b_open_gl(self) -> int:
        ...
    
    @b_open_gl.setter
    def b_open_gl(self, value : int):
        ...
    
    ...

class EmfHeaderExtension2(EmfHeaderObject):
    '''The HeaderExtension2 object defines the second extension to the EMF metafile header. It adds the
    ability to measure device surfaces in micrometers, which enhances the resolution and scalability of EMF metafiles.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets a WMF RectL object ([MS-WMF] section 2.2.2.19) that specifies the rectangular inclusive-inclusive
        bounds in device units of the smallest rectangle that can be drawn around the image stored in
        the metafile'''
        ...
    
    @bounds.setter
    def bounds(self, value : aspose.imaging.Rectangle):
        '''Sets a WMF RectL object ([MS-WMF] section 2.2.2.19) that specifies the rectangular inclusive-inclusive
        bounds in device units of the smallest rectangle that can be drawn around the image stored in
        the metafile'''
        ...
    
    @property
    def frame(self) -> aspose.imaging.Rectangle:
        '''Gets a WMF RectL object that specifies the rectangular inclusive-inclusive dimensions, in .01 millimeter
        units, of a rectangle that surrounds the image stored in the metafile'''
        ...
    
    @frame.setter
    def frame(self, value : aspose.imaging.Rectangle):
        '''Sets a WMF RectL object that specifies the rectangular inclusive-inclusive dimensions, in .01 millimeter
        units, of a rectangle that surrounds the image stored in the metafile'''
        ...
    
    @property
    def record_signature(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfFormatSignature:
        ...
    
    @record_signature.setter
    def record_signature(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfFormatSignature):
        ...
    
    @property
    def version(self) -> int:
        '''Gets Version (4 bytes): A 32-bit unsigned integer that specifies EMF metafile interoperability. This SHOULD be 0x00010000'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets Version (4 bytes): A 32-bit unsigned integer that specifies EMF metafile interoperability. This SHOULD be 0x00010000'''
        ...
    
    @property
    def bytes(self) -> int:
        '''Gets  32-bit unsigned integer that specifies the size of the metafile, in bytes.'''
        ...
    
    @bytes.setter
    def bytes(self, value : int):
        '''Sets  32-bit unsigned integer that specifies the size of the metafile, in bytes.'''
        ...
    
    @property
    def records(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the number of records in the metafile'''
        ...
    
    @records.setter
    def records(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the number of records in the metafile'''
        ...
    
    @property
    def handles(self) -> int:
        '''Gets a 16-bit unsigned integer that specifies the number of graphics objects that will be used during the processing of the metafile'''
        ...
    
    @handles.setter
    def handles(self, value : int):
        '''Sets a 16-bit unsigned integer that specifies the number of graphics objects that will be used during the processing of the metafile'''
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets a 16-bit unsigned integer that MUST be 0x0000 and MUST be ignored'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets a 16-bit unsigned integer that MUST be 0x0000 and MUST be ignored'''
        ...
    
    @property
    def n_desription(self) -> int:
        ...
    
    @n_desription.setter
    def n_desription(self, value : int):
        ...
    
    @property
    def off_description(self) -> int:
        ...
    
    @off_description.setter
    def off_description(self, value : int):
        ...
    
    @property
    def n_pal_entries(self) -> int:
        ...
    
    @n_pal_entries.setter
    def n_pal_entries(self, value : int):
        ...
    
    @property
    def device(self) -> aspose.imaging.Size:
        '''Gets a WMF SizeL object ([MS-WMF] section 2.2.2.22) that specifies the size of the reference device, in pixels'''
        ...
    
    @device.setter
    def device(self, value : aspose.imaging.Size):
        '''Sets a WMF SizeL object ([MS-WMF] section 2.2.2.22) that specifies the size of the reference device, in pixels'''
        ...
    
    @property
    def millimeters(self) -> aspose.imaging.Size:
        '''Gets a WMF SizeL object that specifies the size of the reference device, in millimeters'''
        ...
    
    @millimeters.setter
    def millimeters(self, value : aspose.imaging.Size):
        '''Sets a WMF SizeL object that specifies the size of the reference device, in millimeters'''
        ...
    
    @property
    def valid(self) -> bool:
        '''Gets a value indicating whether this  is valid.'''
        ...
    
    @property
    def micrometers_x(self) -> int:
        ...
    
    @micrometers_x.setter
    def micrometers_x(self, value : int):
        ...
    
    @property
    def micrometers_y(self) -> int:
        ...
    
    @micrometers_y.setter
    def micrometers_y(self, value : int):
        ...
    
    ...

class EmfHeaderObject(EmfObject):
    '''The Header object defines the EMF metafile header. It specifies properties of the device on which the image in the metafile was created.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets a WMF RectL object ([MS-WMF] section 2.2.2.19) that specifies the rectangular inclusive-inclusive
        bounds in device units of the smallest rectangle that can be drawn around the image stored in
        the metafile'''
        ...
    
    @bounds.setter
    def bounds(self, value : aspose.imaging.Rectangle):
        '''Sets a WMF RectL object ([MS-WMF] section 2.2.2.19) that specifies the rectangular inclusive-inclusive
        bounds in device units of the smallest rectangle that can be drawn around the image stored in
        the metafile'''
        ...
    
    @property
    def frame(self) -> aspose.imaging.Rectangle:
        '''Gets a WMF RectL object that specifies the rectangular inclusive-inclusive dimensions, in .01 millimeter
        units, of a rectangle that surrounds the image stored in the metafile'''
        ...
    
    @frame.setter
    def frame(self, value : aspose.imaging.Rectangle):
        '''Sets a WMF RectL object that specifies the rectangular inclusive-inclusive dimensions, in .01 millimeter
        units, of a rectangle that surrounds the image stored in the metafile'''
        ...
    
    @property
    def record_signature(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfFormatSignature:
        ...
    
    @record_signature.setter
    def record_signature(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfFormatSignature):
        ...
    
    @property
    def version(self) -> int:
        '''Gets Version (4 bytes): A 32-bit unsigned integer that specifies EMF metafile interoperability. This SHOULD be 0x00010000'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets Version (4 bytes): A 32-bit unsigned integer that specifies EMF metafile interoperability. This SHOULD be 0x00010000'''
        ...
    
    @property
    def bytes(self) -> int:
        '''Gets  32-bit unsigned integer that specifies the size of the metafile, in bytes.'''
        ...
    
    @bytes.setter
    def bytes(self, value : int):
        '''Sets  32-bit unsigned integer that specifies the size of the metafile, in bytes.'''
        ...
    
    @property
    def records(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the number of records in the metafile'''
        ...
    
    @records.setter
    def records(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the number of records in the metafile'''
        ...
    
    @property
    def handles(self) -> int:
        '''Gets a 16-bit unsigned integer that specifies the number of graphics objects that will be used during the processing of the metafile'''
        ...
    
    @handles.setter
    def handles(self, value : int):
        '''Sets a 16-bit unsigned integer that specifies the number of graphics objects that will be used during the processing of the metafile'''
        ...
    
    @property
    def reserved(self) -> int:
        '''Gets a 16-bit unsigned integer that MUST be 0x0000 and MUST be ignored'''
        ...
    
    @reserved.setter
    def reserved(self, value : int):
        '''Sets a 16-bit unsigned integer that MUST be 0x0000 and MUST be ignored'''
        ...
    
    @property
    def n_desription(self) -> int:
        ...
    
    @n_desription.setter
    def n_desription(self, value : int):
        ...
    
    @property
    def off_description(self) -> int:
        ...
    
    @off_description.setter
    def off_description(self, value : int):
        ...
    
    @property
    def n_pal_entries(self) -> int:
        ...
    
    @n_pal_entries.setter
    def n_pal_entries(self, value : int):
        ...
    
    @property
    def device(self) -> aspose.imaging.Size:
        '''Gets a WMF SizeL object ([MS-WMF] section 2.2.2.22) that specifies the size of the reference device, in pixels'''
        ...
    
    @device.setter
    def device(self, value : aspose.imaging.Size):
        '''Sets a WMF SizeL object ([MS-WMF] section 2.2.2.22) that specifies the size of the reference device, in pixels'''
        ...
    
    @property
    def millimeters(self) -> aspose.imaging.Size:
        '''Gets a WMF SizeL object that specifies the size of the reference device, in millimeters'''
        ...
    
    @millimeters.setter
    def millimeters(self, value : aspose.imaging.Size):
        '''Sets a WMF SizeL object that specifies the size of the reference device, in millimeters'''
        ...
    
    @property
    def valid(self) -> bool:
        '''Gets a value indicating whether this  is valid.'''
        ...
    
    ...

class EmfLogBrushEx(EmfObject):
    '''The LogBrushEx object defines the style, color, and pattern of a device-independent brush.'''
    
    def __init__(self):
        ...
    
    @property
    def brush_style(self) -> aspose.imaging.fileformats.wmf.consts.WmfBrushStyle:
        ...
    
    @brush_style.setter
    def brush_style(self, value : aspose.imaging.fileformats.wmf.consts.WmfBrushStyle):
        ...
    
    @property
    def argb_32_color_ref(self) -> int:
        ...
    
    @argb_32_color_ref.setter
    def argb_32_color_ref(self, value : int):
        ...
    
    @property
    def brush_hatch(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfHatchStyle:
        ...
    
    @brush_hatch.setter
    def brush_hatch(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfHatchStyle):
        ...
    
    ...

class EmfLogFont(EmfObject):
    '''The LogFont object specifies the basic attributes of a logical font.'''
    
    def __init__(self):
        ...
    
    @property
    def height(self) -> int:
        '''Gets a 32-bit signed integer that specifies the height, in logical units, of the font's
        character cell or character. The character height value, also known as the em size, is the
        character cell height value minus the internal leading value. The font mapper SHOULD
        interpret the value specified in the Height field in the following manner.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets a 32-bit signed integer that specifies the height, in logical units, of the font's
        character cell or character. The character height value, also known as the em size, is the
        character cell height value minus the internal leading value. The font mapper SHOULD
        interpret the value specified in the Height field in the following manner.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets a 32-bit signed integer that specifies the average width, in logical units, of
        characters in the font. If the Width field value is zero, an appropriate value SHOULD be
        calculated from other LogFont values to find a font that has the typographer's intended
        aspect ratio'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets a 32-bit signed integer that specifies the average width, in logical units, of
        characters in the font. If the Width field value is zero, an appropriate value SHOULD be
        calculated from other LogFont values to find a font that has the typographer's intended
        aspect ratio'''
        ...
    
    @property
    def escapement(self) -> int:
        '''Gets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between the escapement vector and the x-axis of the device. The escapement vector is
        parallel to the baseline of a row of text.'''
        ...
    
    @escapement.setter
    def escapement(self, value : int):
        '''Sets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between the escapement vector and the x-axis of the device. The escapement vector is
        parallel to the baseline of a row of text.'''
        ...
    
    @property
    def orientation(self) -> int:
        '''Gets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between each character's baseline and the x-axis of the device.'''
        ...
    
    @orientation.setter
    def orientation(self, value : int):
        '''Sets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between each character's baseline and the x-axis of the device.'''
        ...
    
    @property
    def weight(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfLogFontWeight:
        '''Gets a 32-bit signed integer that specifies the weight of the font in the range
        zero through 1000. For example, 400 is normal and 700 is bold. If this value is zero, a default
        weight can be used.'''
        ...
    
    @weight.setter
    def weight(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfLogFontWeight):
        '''Sets a 32-bit signed integer that specifies the weight of the font in the range
        zero through 1000. For example, 400 is normal and 700 is bold. If this value is zero, a default
        weight can be used.'''
        ...
    
    @property
    def italic(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies an italic font if set to 0x01; otherwise,
        it MUST be set to 0x00.'''
        ...
    
    @italic.setter
    def italic(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies an italic font if set to 0x01; otherwise,
        it MUST be set to 0x00.'''
        ...
    
    @property
    def underline(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies an underlined font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @underline.setter
    def underline(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies an underlined font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @property
    def strikeout(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies a strikeout font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @strikeout.setter
    def strikeout(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies a strikeout font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @property
    def char_set(self) -> aspose.imaging.fileformats.wmf.consts.WmfCharacterSet:
        ...
    
    @char_set.setter
    def char_set(self, value : aspose.imaging.fileformats.wmf.consts.WmfCharacterSet):
        ...
    
    @property
    def out_precision(self) -> aspose.imaging.fileformats.wmf.consts.WmfOutPrecision:
        ...
    
    @out_precision.setter
    def out_precision(self, value : aspose.imaging.fileformats.wmf.consts.WmfOutPrecision):
        ...
    
    @property
    def clip_precision(self) -> aspose.imaging.fileformats.wmf.consts.WmfClipPrecisionFlags:
        ...
    
    @clip_precision.setter
    def clip_precision(self, value : aspose.imaging.fileformats.wmf.consts.WmfClipPrecisionFlags):
        ...
    
    @property
    def quality(self) -> aspose.imaging.fileformats.wmf.consts.WmfFontQuality:
        '''Gets an 8-bit unsigned integer that specifies the output quality. The output quality
        defines how closely to attempt to match the logical-font attributes to those of an actual
        physical font. It MUST be one of the values in the WMF FontQuality enumeration ([MS-WMF]
        section 2.1.1.10).'''
        ...
    
    @quality.setter
    def quality(self, value : aspose.imaging.fileformats.wmf.consts.WmfFontQuality):
        '''Sets an 8-bit unsigned integer that specifies the output quality. The output quality
        defines how closely to attempt to match the logical-font attributes to those of an actual
        physical font. It MUST be one of the values in the WMF FontQuality enumeration ([MS-WMF]
        section 2.1.1.10).'''
        ...
    
    @property
    def pitch_and_family(self) -> aspose.imaging.fileformats.wmf.objects.WmfPitchAndFamily:
        ...
    
    @pitch_and_family.setter
    def pitch_and_family(self, value : aspose.imaging.fileformats.wmf.objects.WmfPitchAndFamily):
        ...
    
    @property
    def facename(self) -> str:
        '''Gets a Facename (64 bytes):  A string of no more than 32 Unicode characters that specifies the
        typeface name of the font. If the length of this string is less than 32 characters, a terminating
        NULL MUST be present, after which the remainder of this field MUST be ignored.'''
        ...
    
    @facename.setter
    def facename(self, value : str):
        '''Sets a Facename (64 bytes):  A string of no more than 32 Unicode characters that specifies the
        typeface name of the font. If the length of this string is less than 32 characters, a terminating
        NULL MUST be present, after which the remainder of this field MUST be ignored.'''
        ...
    
    ...

class EmfLogFontEx(EmfLogFont):
    '''The LogFontEx object specifies the extended attributes of a logical font.'''
    
    def __init__(self, emf_log_font: aspose.imaging.fileformats.emf.emf.objects.EmfLogFont):
        '''Initializes a new instance of the  class.
        
        :param emf_log_font: The EMF log font.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets a 32-bit signed integer that specifies the height, in logical units, of the font's
        character cell or character. The character height value, also known as the em size, is the
        character cell height value minus the internal leading value. The font mapper SHOULD
        interpret the value specified in the Height field in the following manner.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets a 32-bit signed integer that specifies the height, in logical units, of the font's
        character cell or character. The character height value, also known as the em size, is the
        character cell height value minus the internal leading value. The font mapper SHOULD
        interpret the value specified in the Height field in the following manner.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets a 32-bit signed integer that specifies the average width, in logical units, of
        characters in the font. If the Width field value is zero, an appropriate value SHOULD be
        calculated from other LogFont values to find a font that has the typographer's intended
        aspect ratio'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets a 32-bit signed integer that specifies the average width, in logical units, of
        characters in the font. If the Width field value is zero, an appropriate value SHOULD be
        calculated from other LogFont values to find a font that has the typographer's intended
        aspect ratio'''
        ...
    
    @property
    def escapement(self) -> int:
        '''Gets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between the escapement vector and the x-axis of the device. The escapement vector is
        parallel to the baseline of a row of text.'''
        ...
    
    @escapement.setter
    def escapement(self, value : int):
        '''Sets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between the escapement vector and the x-axis of the device. The escapement vector is
        parallel to the baseline of a row of text.'''
        ...
    
    @property
    def orientation(self) -> int:
        '''Gets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between each character's baseline and the x-axis of the device.'''
        ...
    
    @orientation.setter
    def orientation(self, value : int):
        '''Sets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between each character's baseline and the x-axis of the device.'''
        ...
    
    @property
    def weight(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfLogFontWeight:
        '''Gets a 32-bit signed integer that specifies the weight of the font in the range
        zero through 1000. For example, 400 is normal and 700 is bold. If this value is zero, a default
        weight can be used.'''
        ...
    
    @weight.setter
    def weight(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfLogFontWeight):
        '''Sets a 32-bit signed integer that specifies the weight of the font in the range
        zero through 1000. For example, 400 is normal and 700 is bold. If this value is zero, a default
        weight can be used.'''
        ...
    
    @property
    def italic(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies an italic font if set to 0x01; otherwise,
        it MUST be set to 0x00.'''
        ...
    
    @italic.setter
    def italic(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies an italic font if set to 0x01; otherwise,
        it MUST be set to 0x00.'''
        ...
    
    @property
    def underline(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies an underlined font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @underline.setter
    def underline(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies an underlined font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @property
    def strikeout(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies a strikeout font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @strikeout.setter
    def strikeout(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies a strikeout font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @property
    def char_set(self) -> aspose.imaging.fileformats.wmf.consts.WmfCharacterSet:
        ...
    
    @char_set.setter
    def char_set(self, value : aspose.imaging.fileformats.wmf.consts.WmfCharacterSet):
        ...
    
    @property
    def out_precision(self) -> aspose.imaging.fileformats.wmf.consts.WmfOutPrecision:
        ...
    
    @out_precision.setter
    def out_precision(self, value : aspose.imaging.fileformats.wmf.consts.WmfOutPrecision):
        ...
    
    @property
    def clip_precision(self) -> aspose.imaging.fileformats.wmf.consts.WmfClipPrecisionFlags:
        ...
    
    @clip_precision.setter
    def clip_precision(self, value : aspose.imaging.fileformats.wmf.consts.WmfClipPrecisionFlags):
        ...
    
    @property
    def quality(self) -> aspose.imaging.fileformats.wmf.consts.WmfFontQuality:
        '''Gets an 8-bit unsigned integer that specifies the output quality. The output quality
        defines how closely to attempt to match the logical-font attributes to those of an actual
        physical font. It MUST be one of the values in the WMF FontQuality enumeration ([MS-WMF]
        section 2.1.1.10).'''
        ...
    
    @quality.setter
    def quality(self, value : aspose.imaging.fileformats.wmf.consts.WmfFontQuality):
        '''Sets an 8-bit unsigned integer that specifies the output quality. The output quality
        defines how closely to attempt to match the logical-font attributes to those of an actual
        physical font. It MUST be one of the values in the WMF FontQuality enumeration ([MS-WMF]
        section 2.1.1.10).'''
        ...
    
    @property
    def pitch_and_family(self) -> aspose.imaging.fileformats.wmf.objects.WmfPitchAndFamily:
        ...
    
    @pitch_and_family.setter
    def pitch_and_family(self, value : aspose.imaging.fileformats.wmf.objects.WmfPitchAndFamily):
        ...
    
    @property
    def facename(self) -> str:
        '''Gets a Facename (64 bytes):  A string of no more than 32 Unicode characters that specifies the
        typeface name of the font. If the length of this string is less than 32 characters, a terminating
        NULL MUST be present, after which the remainder of this field MUST be ignored.'''
        ...
    
    @facename.setter
    def facename(self, value : str):
        '''Sets a Facename (64 bytes):  A string of no more than 32 Unicode characters that specifies the
        typeface name of the font. If the length of this string is less than 32 characters, a terminating
        NULL MUST be present, after which the remainder of this field MUST be ignored.'''
        ...
    
    @property
    def full_name(self) -> str:
        ...
    
    @full_name.setter
    def full_name(self, value : str):
        ...
    
    @property
    def style(self) -> str:
        '''Gets a string of 32 Unicode characters that defines the font's style. If the length of
        this string is less than 32 characters, a terminating NULL MUST be present, after which the
        remainder of this field MUST be ignored.'''
        ...
    
    @style.setter
    def style(self, value : str):
        '''Sets a string of 32 Unicode characters that defines the font's style. If the length of
        this string is less than 32 characters, a terminating NULL MUST be present, after which the
        remainder of this field MUST be ignored.'''
        ...
    
    @property
    def script(self) -> str:
        '''Gets a string of 32 Unicode characters that defines the character set of the font.
        If the length of this string is less than 32 characters, a terminating NULL MUST be present,
        after which the remainder of this field MUST be ignored.'''
        ...
    
    @script.setter
    def script(self, value : str):
        '''Sets a string of 32 Unicode characters that defines the character set of the font.
        If the length of this string is less than 32 characters, a terminating NULL MUST be present,
        after which the remainder of this field MUST be ignored.'''
        ...
    
    ...

class EmfLogFontExDv(EmfLogFontEx):
    '''The LogFontExDv object specifies the design vector for an extended logical font.'''
    
    def __init__(self, emf_log_font_ex: aspose.imaging.fileformats.emf.emf.objects.EmfLogFontEx):
        '''Initializes a new instance of the  class.
        
        :param emf_log_font_ex: The EMF log font ex.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets a 32-bit signed integer that specifies the height, in logical units, of the font's
        character cell or character. The character height value, also known as the em size, is the
        character cell height value minus the internal leading value. The font mapper SHOULD
        interpret the value specified in the Height field in the following manner.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets a 32-bit signed integer that specifies the height, in logical units, of the font's
        character cell or character. The character height value, also known as the em size, is the
        character cell height value minus the internal leading value. The font mapper SHOULD
        interpret the value specified in the Height field in the following manner.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets a 32-bit signed integer that specifies the average width, in logical units, of
        characters in the font. If the Width field value is zero, an appropriate value SHOULD be
        calculated from other LogFont values to find a font that has the typographer's intended
        aspect ratio'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets a 32-bit signed integer that specifies the average width, in logical units, of
        characters in the font. If the Width field value is zero, an appropriate value SHOULD be
        calculated from other LogFont values to find a font that has the typographer's intended
        aspect ratio'''
        ...
    
    @property
    def escapement(self) -> int:
        '''Gets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between the escapement vector and the x-axis of the device. The escapement vector is
        parallel to the baseline of a row of text.'''
        ...
    
    @escapement.setter
    def escapement(self, value : int):
        '''Sets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between the escapement vector and the x-axis of the device. The escapement vector is
        parallel to the baseline of a row of text.'''
        ...
    
    @property
    def orientation(self) -> int:
        '''Gets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between each character's baseline and the x-axis of the device.'''
        ...
    
    @orientation.setter
    def orientation(self, value : int):
        '''Sets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between each character's baseline and the x-axis of the device.'''
        ...
    
    @property
    def weight(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfLogFontWeight:
        '''Gets a 32-bit signed integer that specifies the weight of the font in the range
        zero through 1000. For example, 400 is normal and 700 is bold. If this value is zero, a default
        weight can be used.'''
        ...
    
    @weight.setter
    def weight(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfLogFontWeight):
        '''Sets a 32-bit signed integer that specifies the weight of the font in the range
        zero through 1000. For example, 400 is normal and 700 is bold. If this value is zero, a default
        weight can be used.'''
        ...
    
    @property
    def italic(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies an italic font if set to 0x01; otherwise,
        it MUST be set to 0x00.'''
        ...
    
    @italic.setter
    def italic(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies an italic font if set to 0x01; otherwise,
        it MUST be set to 0x00.'''
        ...
    
    @property
    def underline(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies an underlined font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @underline.setter
    def underline(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies an underlined font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @property
    def strikeout(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies a strikeout font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @strikeout.setter
    def strikeout(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies a strikeout font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @property
    def char_set(self) -> aspose.imaging.fileformats.wmf.consts.WmfCharacterSet:
        ...
    
    @char_set.setter
    def char_set(self, value : aspose.imaging.fileformats.wmf.consts.WmfCharacterSet):
        ...
    
    @property
    def out_precision(self) -> aspose.imaging.fileformats.wmf.consts.WmfOutPrecision:
        ...
    
    @out_precision.setter
    def out_precision(self, value : aspose.imaging.fileformats.wmf.consts.WmfOutPrecision):
        ...
    
    @property
    def clip_precision(self) -> aspose.imaging.fileformats.wmf.consts.WmfClipPrecisionFlags:
        ...
    
    @clip_precision.setter
    def clip_precision(self, value : aspose.imaging.fileformats.wmf.consts.WmfClipPrecisionFlags):
        ...
    
    @property
    def quality(self) -> aspose.imaging.fileformats.wmf.consts.WmfFontQuality:
        '''Gets an 8-bit unsigned integer that specifies the output quality. The output quality
        defines how closely to attempt to match the logical-font attributes to those of an actual
        physical font. It MUST be one of the values in the WMF FontQuality enumeration ([MS-WMF]
        section 2.1.1.10).'''
        ...
    
    @quality.setter
    def quality(self, value : aspose.imaging.fileformats.wmf.consts.WmfFontQuality):
        '''Sets an 8-bit unsigned integer that specifies the output quality. The output quality
        defines how closely to attempt to match the logical-font attributes to those of an actual
        physical font. It MUST be one of the values in the WMF FontQuality enumeration ([MS-WMF]
        section 2.1.1.10).'''
        ...
    
    @property
    def pitch_and_family(self) -> aspose.imaging.fileformats.wmf.objects.WmfPitchAndFamily:
        ...
    
    @pitch_and_family.setter
    def pitch_and_family(self, value : aspose.imaging.fileformats.wmf.objects.WmfPitchAndFamily):
        ...
    
    @property
    def facename(self) -> str:
        '''Gets a Facename (64 bytes):  A string of no more than 32 Unicode characters that specifies the
        typeface name of the font. If the length of this string is less than 32 characters, a terminating
        NULL MUST be present, after which the remainder of this field MUST be ignored.'''
        ...
    
    @facename.setter
    def facename(self, value : str):
        '''Sets a Facename (64 bytes):  A string of no more than 32 Unicode characters that specifies the
        typeface name of the font. If the length of this string is less than 32 characters, a terminating
        NULL MUST be present, after which the remainder of this field MUST be ignored.'''
        ...
    
    @property
    def full_name(self) -> str:
        ...
    
    @full_name.setter
    def full_name(self, value : str):
        ...
    
    @property
    def style(self) -> str:
        '''Gets a string of 32 Unicode characters that defines the font's style. If the length of
        this string is less than 32 characters, a terminating NULL MUST be present, after which the
        remainder of this field MUST be ignored.'''
        ...
    
    @style.setter
    def style(self, value : str):
        '''Sets a string of 32 Unicode characters that defines the font's style. If the length of
        this string is less than 32 characters, a terminating NULL MUST be present, after which the
        remainder of this field MUST be ignored.'''
        ...
    
    @property
    def script(self) -> str:
        '''Gets a string of 32 Unicode characters that defines the character set of the font.
        If the length of this string is less than 32 characters, a terminating NULL MUST be present,
        after which the remainder of this field MUST be ignored.'''
        ...
    
    @script.setter
    def script(self, value : str):
        '''Sets a string of 32 Unicode characters that defines the character set of the font.
        If the length of this string is less than 32 characters, a terminating NULL MUST be present,
        after which the remainder of this field MUST be ignored.'''
        ...
    
    @property
    def design_vector(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfDesignVector:
        ...
    
    @design_vector.setter
    def design_vector(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfDesignVector):
        ...
    
    ...

class EmfLogFontPanose(EmfLogFont):
    '''The LogFontPanose object specifies the PANOSE characteristics of a logical font.'''
    
    def __init__(self, emf_log_font: aspose.imaging.fileformats.emf.emf.objects.EmfLogFont):
        '''Initializes a new instance of the  class.
        
        :param emf_log_font: The base log font.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets a 32-bit signed integer that specifies the height, in logical units, of the font's
        character cell or character. The character height value, also known as the em size, is the
        character cell height value minus the internal leading value. The font mapper SHOULD
        interpret the value specified in the Height field in the following manner.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets a 32-bit signed integer that specifies the height, in logical units, of the font's
        character cell or character. The character height value, also known as the em size, is the
        character cell height value minus the internal leading value. The font mapper SHOULD
        interpret the value specified in the Height field in the following manner.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets a 32-bit signed integer that specifies the average width, in logical units, of
        characters in the font. If the Width field value is zero, an appropriate value SHOULD be
        calculated from other LogFont values to find a font that has the typographer's intended
        aspect ratio'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets a 32-bit signed integer that specifies the average width, in logical units, of
        characters in the font. If the Width field value is zero, an appropriate value SHOULD be
        calculated from other LogFont values to find a font that has the typographer's intended
        aspect ratio'''
        ...
    
    @property
    def escapement(self) -> int:
        '''Gets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between the escapement vector and the x-axis of the device. The escapement vector is
        parallel to the baseline of a row of text.'''
        ...
    
    @escapement.setter
    def escapement(self, value : int):
        '''Sets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between the escapement vector and the x-axis of the device. The escapement vector is
        parallel to the baseline of a row of text.'''
        ...
    
    @property
    def orientation(self) -> int:
        '''Gets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between each character's baseline and the x-axis of the device.'''
        ...
    
    @orientation.setter
    def orientation(self, value : int):
        '''Sets a 32-bit signed integer that specifies the angle, in tenths of degrees,
        between each character's baseline and the x-axis of the device.'''
        ...
    
    @property
    def weight(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfLogFontWeight:
        '''Gets a 32-bit signed integer that specifies the weight of the font in the range
        zero through 1000. For example, 400 is normal and 700 is bold. If this value is zero, a default
        weight can be used.'''
        ...
    
    @weight.setter
    def weight(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfLogFontWeight):
        '''Sets a 32-bit signed integer that specifies the weight of the font in the range
        zero through 1000. For example, 400 is normal and 700 is bold. If this value is zero, a default
        weight can be used.'''
        ...
    
    @property
    def italic(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies an italic font if set to 0x01; otherwise,
        it MUST be set to 0x00.'''
        ...
    
    @italic.setter
    def italic(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies an italic font if set to 0x01; otherwise,
        it MUST be set to 0x00.'''
        ...
    
    @property
    def underline(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies an underlined font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @underline.setter
    def underline(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies an underlined font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @property
    def strikeout(self) -> int:
        '''Gets an 8-bit unsigned integer that specifies a strikeout font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @strikeout.setter
    def strikeout(self, value : int):
        '''Sets an 8-bit unsigned integer that specifies a strikeout font if set to 0x01;
        otherwise, it MUST be set to 0x00.'''
        ...
    
    @property
    def char_set(self) -> aspose.imaging.fileformats.wmf.consts.WmfCharacterSet:
        ...
    
    @char_set.setter
    def char_set(self, value : aspose.imaging.fileformats.wmf.consts.WmfCharacterSet):
        ...
    
    @property
    def out_precision(self) -> aspose.imaging.fileformats.wmf.consts.WmfOutPrecision:
        ...
    
    @out_precision.setter
    def out_precision(self, value : aspose.imaging.fileformats.wmf.consts.WmfOutPrecision):
        ...
    
    @property
    def clip_precision(self) -> aspose.imaging.fileformats.wmf.consts.WmfClipPrecisionFlags:
        ...
    
    @clip_precision.setter
    def clip_precision(self, value : aspose.imaging.fileformats.wmf.consts.WmfClipPrecisionFlags):
        ...
    
    @property
    def quality(self) -> aspose.imaging.fileformats.wmf.consts.WmfFontQuality:
        '''Gets an 8-bit unsigned integer that specifies the output quality. The output quality
        defines how closely to attempt to match the logical-font attributes to those of an actual
        physical font. It MUST be one of the values in the WMF FontQuality enumeration ([MS-WMF]
        section 2.1.1.10).'''
        ...
    
    @quality.setter
    def quality(self, value : aspose.imaging.fileformats.wmf.consts.WmfFontQuality):
        '''Sets an 8-bit unsigned integer that specifies the output quality. The output quality
        defines how closely to attempt to match the logical-font attributes to those of an actual
        physical font. It MUST be one of the values in the WMF FontQuality enumeration ([MS-WMF]
        section 2.1.1.10).'''
        ...
    
    @property
    def pitch_and_family(self) -> aspose.imaging.fileformats.wmf.objects.WmfPitchAndFamily:
        ...
    
    @pitch_and_family.setter
    def pitch_and_family(self, value : aspose.imaging.fileformats.wmf.objects.WmfPitchAndFamily):
        ...
    
    @property
    def facename(self) -> str:
        '''Gets a Facename (64 bytes):  A string of no more than 32 Unicode characters that specifies the
        typeface name of the font. If the length of this string is less than 32 characters, a terminating
        NULL MUST be present, after which the remainder of this field MUST be ignored.'''
        ...
    
    @facename.setter
    def facename(self, value : str):
        '''Sets a Facename (64 bytes):  A string of no more than 32 Unicode characters that specifies the
        typeface name of the font. If the length of this string is less than 32 characters, a terminating
        NULL MUST be present, after which the remainder of this field MUST be ignored.'''
        ...
    
    @property
    def full_name(self) -> str:
        ...
    
    @full_name.setter
    def full_name(self, value : str):
        ...
    
    @property
    def style(self) -> str:
        '''Gets a string of 32 Unicode characters that defines the font's style. If the length of
        this string is less than 32 characters, a terminating NULL MUST be present, after which the
        remainder of this field MUST be ignored.'''
        ...
    
    @style.setter
    def style(self, value : str):
        '''Sets a string of 32 Unicode characters that defines the font's style. If the length of
        this string is less than 32 characters, a terminating NULL MUST be present, after which the
        remainder of this field MUST be ignored.'''
        ...
    
    @property
    def version(self) -> int:
        '''Gets This field MUST be ignored.'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets This field MUST be ignored.'''
        ...
    
    @property
    def style_size(self) -> int:
        ...
    
    @style_size.setter
    def style_size(self, value : int):
        ...
    
    @property
    def match(self) -> int:
        '''Gets This field MUST be ignored.'''
        ...
    
    @match.setter
    def match(self, value : int):
        '''Sets This field MUST be ignored.'''
        ...
    
    @property
    def vendor_id(self) -> int:
        ...
    
    @vendor_id.setter
    def vendor_id(self, value : int):
        ...
    
    @property
    def culture(self) -> int:
        '''Gets a 32-bit unsigned integer that MUST be set to zero and MUST be ignored.'''
        ...
    
    @culture.setter
    def culture(self, value : int):
        '''Sets a 32-bit unsigned integer that MUST be set to zero and MUST be ignored.'''
        ...
    
    @property
    def panose(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfPanose:
        '''Gets a Panose object (section 2.2.21) that specifies the PANOSE characteristics
        of the logical font. If all fields of this object are zero, it MUST be ignored.'''
        ...
    
    @panose.setter
    def panose(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfPanose):
        '''Sets a Panose object (section 2.2.21) that specifies the PANOSE characteristics
        of the logical font. If all fields of this object are zero, it MUST be ignored.'''
        ...
    
    @property
    def padding(self) -> int:
        '''Gets a field that exists only to ensure 32-bit alignment of this structure. It MUST be ignored'''
        ...
    
    @padding.setter
    def padding(self, value : int):
        '''Sets a field that exists only to ensure 32-bit alignment of this structure. It MUST be ignored'''
        ...
    
    ...

class EmfLogPalette(EmfObject):
    '''The LogPalette object specifies a logical_palette that contains device-independent color definitions.'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> int:
        '''Gets a 16-bit unsigned integer that specifies the version number of the system.
        This MUST be 0x0300.'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets a 16-bit unsigned integer that specifies the version number of the system.
        This MUST be 0x0300.'''
        ...
    
    @property
    def palette_argb_32_entries(self) -> List[int]:
        ...
    
    @palette_argb_32_entries.setter
    def palette_argb_32_entries(self, value : List[int]):
        ...
    
    ...

class EmfLogPen(EmfBasePen):
    '''The LogPen object defines the style, width, and color of a logical pen.'''
    
    def __init__(self):
        ...
    
    @property
    def pen_style(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfPenStyle:
        ...
    
    @pen_style.setter
    def pen_style(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfPenStyle):
        ...
    
    @property
    def argb_32_color_ref(self) -> int:
        ...
    
    @argb_32_color_ref.setter
    def argb_32_color_ref(self, value : int):
        ...
    
    @property
    def width(self) -> aspose.imaging.Point:
        '''Gets a WMF PointL object ([MS-WMF] section 2.2.2.15) that specifies the width of
        the pen by the value of its x field. The value of its y field MUST be ignored.'''
        ...
    
    @width.setter
    def width(self, value : aspose.imaging.Point):
        '''Sets a WMF PointL object ([MS-WMF] section 2.2.2.15) that specifies the width of
        the pen by the value of its x field. The value of its y field MUST be ignored.'''
        ...
    
    @property
    def affect_width(self) -> int:
        ...
    
    @affect_width.setter
    def affect_width(self, value : int):
        ...
    
    ...

class EmfLogPenEx(EmfBasePen):
    '''The LogPenEx object specifies the style, width, and color of an extended logical pen.'''
    
    def __init__(self):
        ...
    
    @property
    def pen_style(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfPenStyle:
        ...
    
    @pen_style.setter
    def pen_style(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfPenStyle):
        ...
    
    @property
    def argb_32_color_ref(self) -> int:
        ...
    
    @argb_32_color_ref.setter
    def argb_32_color_ref(self, value : int):
        ...
    
    @property
    def width(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the width of the line drawn by the pen.
        If the pen type in the PenStyle field is PS_GEOMETRIC, this value is the width in
        logical units; otherwise, the width is specified in device units.
        If the pen type in the PenStyle field is PS_COSMETIC, this value MUST be 0x00000001.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the width of the line drawn by the pen.
        If the pen type in the PenStyle field is PS_GEOMETRIC, this value is the width in
        logical units; otherwise, the width is specified in device units.
        If the pen type in the PenStyle field is PS_COSMETIC, this value MUST be 0x00000001.'''
        ...
    
    @property
    def brush_style(self) -> aspose.imaging.fileformats.wmf.consts.WmfBrushStyle:
        ...
    
    @brush_style.setter
    def brush_style(self, value : aspose.imaging.fileformats.wmf.consts.WmfBrushStyle):
        ...
    
    @property
    def brush_hatch(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfHatchStyle:
        ...
    
    @brush_hatch.setter
    def brush_hatch(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfHatchStyle):
        ...
    
    @property
    def num_style_entities(self) -> int:
        ...
    
    @property
    def style_entry(self) -> List[int]:
        ...
    
    @style_entry.setter
    def style_entry(self, value : List[int]):
        ...
    
    @property
    def brush_dib_pattern(self) -> aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap:
        ...
    
    @brush_dib_pattern.setter
    def brush_dib_pattern(self, value : aspose.imaging.fileformats.wmf.objects.WmfDeviceIndependentBitmap):
        ...
    
    ...

class EmfObject(aspose.imaging.fileformats.emf.MetaObject):
    '''Base class for Emf objects'''
    
    ...

class EmfPanose(EmfObject):
    '''The Panose object describes the PANOSE font-classification values for a TrueType font. These
    characteristics are used to associate the font with other fonts of similar appearance but different names.'''
    
    def __init__(self):
        ...
    
    @property
    def family_type(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfFamilyType:
        ...
    
    @family_type.setter
    def family_type(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfFamilyType):
        ...
    
    @property
    def serif_style(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfSerifStyle:
        ...
    
    @serif_style.setter
    def serif_style(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfSerifStyle):
        ...
    
    @property
    def weight(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfWeight:
        '''Gets an 8-bit unsigned integer that specifies the weight of the font. The value
        MUST be in the Weight (section 2.1.34) enumeration table.'''
        ...
    
    @weight.setter
    def weight(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfWeight):
        '''Sets an 8-bit unsigned integer that specifies the weight of the font. The value
        MUST be in the Weight (section 2.1.34) enumeration table.'''
        ...
    
    @property
    def proportion(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfProportion:
        '''Gets an 8-bit unsigned integer that specifies the proportion of the font. The
        value MUST be in the Proportion (section 2.1.28) enumeration table.'''
        ...
    
    @proportion.setter
    def proportion(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfProportion):
        '''Sets an 8-bit unsigned integer that specifies the proportion of the font. The
        value MUST be in the Proportion (section 2.1.28) enumeration table.'''
        ...
    
    @property
    def contrast(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfContrast:
        '''Gets an 8-bit unsigned integer that specifies the contrast of the font. The value
        MUST be in the Contrast (section 2.1.8) enumeration table.'''
        ...
    
    @contrast.setter
    def contrast(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfContrast):
        '''Sets an 8-bit unsigned integer that specifies the contrast of the font. The value
        MUST be in the Contrast (section 2.1.8) enumeration table.'''
        ...
    
    @property
    def stroke_variation(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfStrokeVariation:
        ...
    
    @stroke_variation.setter
    def stroke_variation(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfStrokeVariation):
        ...
    
    @property
    def arm_style(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfArmStyle:
        ...
    
    @arm_style.setter
    def arm_style(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfArmStyle):
        ...
    
    @property
    def letterform(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfLetterform:
        '''Gets an 8-bit unsigned integer that specifies the letterform of the font. The
        value MUST be in the Letterform (section 2.1.20) enumeration table'''
        ...
    
    @letterform.setter
    def letterform(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfLetterform):
        '''Sets an 8-bit unsigned integer that specifies the letterform of the font. The
        value MUST be in the Letterform (section 2.1.20) enumeration table'''
        ...
    
    @property
    def midline(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfMidLine:
        '''Gets an 8-bit unsigned integer that specifies the midline of the font. The value
        MUST be in the MidLine (section 2.1.23) enumeration table.'''
        ...
    
    @midline.setter
    def midline(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfMidLine):
        '''Sets an 8-bit unsigned integer that specifies the midline of the font. The value
        MUST be in the MidLine (section 2.1.23) enumeration table.'''
        ...
    
    @property
    def x_height(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfXHeight:
        ...
    
    @x_height.setter
    def x_height(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfXHeight):
        ...
    
    ...

class EmfPixelFormatDescriptor(EmfObject):
    '''The PixelFormatDescriptor object can be used in EMR_HEADER records (section 2.3.4.2) to specify the pixel format of the output surface for the playback device context.'''
    
    def __init__(self):
        ...
    
    @property
    def n_size(self) -> int:
        ...
    
    @n_size.setter
    def n_size(self, value : int):
        ...
    
    @property
    def n_version(self) -> int:
        ...
    
    @n_version.setter
    def n_version(self, value : int):
        ...
    
    @property
    def dw_flags(self) -> int:
        ...
    
    @dw_flags.setter
    def dw_flags(self, value : int):
        ...
    
    @property
    def pixel_type(self) -> int:
        ...
    
    @pixel_type.setter
    def pixel_type(self, value : int):
        ...
    
    @property
    def c_color_bits(self) -> int:
        ...
    
    @c_color_bits.setter
    def c_color_bits(self, value : int):
        ...
    
    @property
    def c_red_bits(self) -> int:
        ...
    
    @c_red_bits.setter
    def c_red_bits(self, value : int):
        ...
    
    @property
    def c_red_shift(self) -> int:
        ...
    
    @c_red_shift.setter
    def c_red_shift(self, value : int):
        ...
    
    @property
    def c_green_bits(self) -> int:
        ...
    
    @c_green_bits.setter
    def c_green_bits(self, value : int):
        ...
    
    @property
    def c_green_shift(self) -> int:
        ...
    
    @c_green_shift.setter
    def c_green_shift(self, value : int):
        ...
    
    @property
    def c_blue_bits(self) -> int:
        ...
    
    @c_blue_bits.setter
    def c_blue_bits(self, value : int):
        ...
    
    @property
    def c_blue_shift(self) -> int:
        ...
    
    @c_blue_shift.setter
    def c_blue_shift(self, value : int):
        ...
    
    @property
    def c_alpha_bits(self) -> int:
        ...
    
    @c_alpha_bits.setter
    def c_alpha_bits(self, value : int):
        ...
    
    @property
    def c_alpha_shift(self) -> int:
        ...
    
    @c_alpha_shift.setter
    def c_alpha_shift(self, value : int):
        ...
    
    @property
    def c_accum_bits(self) -> int:
        ...
    
    @c_accum_bits.setter
    def c_accum_bits(self, value : int):
        ...
    
    @property
    def c_accum_red_bits(self) -> int:
        ...
    
    @c_accum_red_bits.setter
    def c_accum_red_bits(self, value : int):
        ...
    
    @property
    def c_accum_green_bits(self) -> int:
        ...
    
    @c_accum_green_bits.setter
    def c_accum_green_bits(self, value : int):
        ...
    
    @property
    def c_accum_blue_bits(self) -> int:
        ...
    
    @c_accum_blue_bits.setter
    def c_accum_blue_bits(self, value : int):
        ...
    
    @property
    def c_accum_alpha_bits(self) -> int:
        ...
    
    @c_accum_alpha_bits.setter
    def c_accum_alpha_bits(self, value : int):
        ...
    
    @property
    def c_depth_bits(self) -> int:
        ...
    
    @c_depth_bits.setter
    def c_depth_bits(self, value : int):
        ...
    
    @property
    def c_stencil_bits(self) -> int:
        ...
    
    @c_stencil_bits.setter
    def c_stencil_bits(self, value : int):
        ...
    
    @property
    def c_aux_buffers(self) -> int:
        ...
    
    @c_aux_buffers.setter
    def c_aux_buffers(self, value : int):
        ...
    
    @property
    def layer_type(self) -> int:
        ...
    
    @layer_type.setter
    def layer_type(self, value : int):
        ...
    
    @property
    def b_reserved(self) -> int:
        ...
    
    @b_reserved.setter
    def b_reserved(self, value : int):
        ...
    
    @property
    def dw_layer_mask(self) -> int:
        ...
    
    @dw_layer_mask.setter
    def dw_layer_mask(self, value : int):
        ...
    
    @property
    def dw_visible_mask(self) -> int:
        ...
    
    @dw_visible_mask.setter
    def dw_visible_mask(self, value : int):
        ...
    
    @property
    def dw_damage_mask(self) -> int:
        ...
    
    @dw_damage_mask.setter
    def dw_damage_mask(self, value : int):
        ...
    
    ...

class EmfPoint28To4(EmfObject):
    '''The Point28_4 object represents the location of a point on a device surface with coordinates in 28.4 bit FIX notation.'''
    
    def __init__(self):
        ...
    
    @property
    def x(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfBitFix28To4:
        '''Gets a BitFIX28_4 object (section 2.2.1) that represents the horizontal coordinate of the point.'''
        ...
    
    @x.setter
    def x(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfBitFix28To4):
        '''Sets a BitFIX28_4 object (section 2.2.1) that represents the horizontal coordinate of the point.'''
        ...
    
    @property
    def y(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfBitFix28To4:
        '''Gets a BitFIX28_4 object that represents the vertical coordinate of the point.'''
        ...
    
    @y.setter
    def y(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfBitFix28To4):
        '''Sets a BitFIX28_4 object that represents the vertical coordinate of the point.'''
        ...
    
    ...

class EmfRegionData(EmfObject):
    '''The RegionData object specifies data that defines a region, which is made of non-overlapping rectangles.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, rectangle: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param rectangle: The rectangle.'''
        ...
    
    @property
    def region_data_header(self) -> aspose.imaging.fileformats.emf.emf.objects.EmfRegionDataHeader:
        ...
    
    @region_data_header.setter
    def region_data_header(self, value : aspose.imaging.fileformats.emf.emf.objects.EmfRegionDataHeader):
        ...
    
    @property
    def data(self) -> List[aspose.imaging.Rectangle]:
        '''Gets an array of WMF RectL objects ([MS-WMF] section 2.2.2.19); the objects are
        merged to create the region'''
        ...
    
    @data.setter
    def data(self, value : List[aspose.imaging.Rectangle]):
        '''Sets an array of WMF RectL objects ([MS-WMF] section 2.2.2.19); the objects are
        merged to create the region'''
        ...
    
    ...

class EmfRegionDataHeader(EmfObject):
    '''The RegionDataHeader object describes the properties of a RegionData object.'''
    
    def __init__(self):
        ...
    
    @property
    def size(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the size of this object in bytes. This MUST be 0x00000020.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the size of this object in bytes. This MUST be 0x00000020.'''
        ...
    
    @property
    def type(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the region type. This SHOULD be
        RDH_RECTANGLES (0x00000001).'''
        ...
    
    @type.setter
    def type(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the region type. This SHOULD be
        RDH_RECTANGLES (0x00000001).'''
        ...
    
    @property
    def count_rects(self) -> int:
        ...
    
    @count_rects.setter
    def count_rects(self, value : int):
        ...
    
    @property
    def rgn_size(self) -> int:
        ...
    
    @rgn_size.setter
    def rgn_size(self, value : int):
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets a 128-bit WMF RectL object ([MS-WMF] section 2.2.2.19), which specifies
        the bounds of the region.'''
        ...
    
    @bounds.setter
    def bounds(self, value : aspose.imaging.Rectangle):
        '''Sets a 128-bit WMF RectL object ([MS-WMF] section 2.2.2.19), which specifies
        the bounds of the region.'''
        ...
    
    ...

class EmfText(EmfObject):
    '''The EmrText object contains values for text output.'''
    
    def __init__(self):
        ...
    
    @property
    def reference(self) -> aspose.imaging.Point:
        '''Gets a WMF PointL object ([MS-WMF] section 2.2.2.15) that specifies the coordinates of the
        reference point used to position the string. The reference point is defined by the last
        EMR_SETTEXTALIGN record (section 2.3.11.25). If no such record has been set,
        the default alignment is TA_LEFT,TA_TOP.'''
        ...
    
    @reference.setter
    def reference(self, value : aspose.imaging.Point):
        '''Sets a WMF PointL object ([MS-WMF] section 2.2.2.15) that specifies the coordinates of the
        reference point used to position the string. The reference point is defined by the last
        EMR_SETTEXTALIGN record (section 2.3.11.25). If no such record has been set,
        the default alignment is TA_LEFT,TA_TOP.'''
        ...
    
    @property
    def chars(self) -> int:
        '''Gets a 32-bit unsigned integer that specifies the number of characters in the string'''
        ...
    
    @chars.setter
    def chars(self, value : int):
        '''Sets a 32-bit unsigned integer that specifies the number of characters in the string'''
        ...
    
    @property
    def options(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfExtTextOutOptions:
        '''Gets a 32-bit unsigned integer that specifies how to use the rectangle specified in the
        Rectangle field. This field can be a combination of more than one ExtTextOutOptions
        enumeration (section 2.1.11) values'''
        ...
    
    @options.setter
    def options(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfExtTextOutOptions):
        '''Sets a 32-bit unsigned integer that specifies how to use the rectangle specified in the
        Rectangle field. This field can be a combination of more than one ExtTextOutOptions
        enumeration (section 2.1.11) values'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.Rectangle:
        '''Gets an optional WMF RectL object ([MS-WMF] section 2.2.2.19) that defines a clipping
        and/or opaquing rectangle in logical units. This rectangle is applied to the text
        output performed by the containing record.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.Rectangle):
        '''Sets an optional WMF RectL object ([MS-WMF] section 2.2.2.19) that defines a clipping
        and/or opaquing rectangle in logical units. This rectangle is applied to the text
        output performed by the containing record.'''
        ...
    
    @property
    def string_buffer(self) -> str:
        ...
    
    @string_buffer.setter
    def string_buffer(self, value : str):
        ...
    
    @property
    def glyph_index_buffer(self) -> List[int]:
        ...
    
    @glyph_index_buffer.setter
    def glyph_index_buffer(self, value : List[int]):
        ...
    
    @property
    def dx_buffer(self) -> List[int]:
        ...
    
    @dx_buffer.setter
    def dx_buffer(self, value : List[int]):
        ...
    
    ...

class EmfTriVertex(EmfObject):
    '''The TriVertex object specifies color and position information for the definition of a rectangle or
    triangle vertex.'''
    
    def __init__(self):
        ...
    
    @property
    def x(self) -> int:
        '''Gets a 32-bit signed integer that specifies the horizontal position, in logical units.'''
        ...
    
    @x.setter
    def x(self, value : int):
        '''Sets a 32-bit signed integer that specifies the horizontal position, in logical units.'''
        ...
    
    @property
    def y(self) -> int:
        '''Gets a 32-bit signed integer that specifies the vertical position, in logical units.'''
        ...
    
    @y.setter
    def y(self, value : int):
        '''Sets a 32-bit signed integer that specifies the vertical position, in logical units.'''
        ...
    
    @property
    def red(self) -> int:
        '''Gets a 16-bit unsigned integer that specifies the red color value for the point.'''
        ...
    
    @red.setter
    def red(self, value : int):
        '''Sets a 16-bit unsigned integer that specifies the red color value for the point.'''
        ...
    
    @property
    def green(self) -> int:
        '''Gets a 16-bit unsigned integer that specifies the green color value for the point.'''
        ...
    
    @green.setter
    def green(self, value : int):
        '''Sets a 16-bit unsigned integer that specifies the green color value for the point.'''
        ...
    
    @property
    def blue(self) -> int:
        '''Gets a 16-bit unsigned integer that specifies the blue color value for the point.'''
        ...
    
    @blue.setter
    def blue(self, value : int):
        '''Sets a 16-bit unsigned integer that specifies the blue color value for the point.'''
        ...
    
    @property
    def alpha(self) -> int:
        '''Gets a 16-bit unsigned integer that specifies the alpha transparency value for the point.'''
        ...
    
    @alpha.setter
    def alpha(self, value : int):
        '''Sets a 16-bit unsigned integer that specifies the alpha transparency value for the point.'''
        ...
    
    ...

class EmfUniversalFontId(EmfObject):
    '''The UniversalFontId object defines a mechanism for identifying fonts in EMF metafiles.'''
    
    def __init__(self):
        ...
    
    @property
    def checksum(self) -> int:
        '''Gets a 32-bit unsigned integer that is the checksum of the font.
        The checksum value has the following meanings.
        0x00000000  The object is a device font.
        0x00000001  The object is a Type 1 font that has been installed on the client machine and is
        enumerated by the PostScript printer driver as a device font.
        0x00000002  The object is not a font but is a Type 1 rasterizer.
        3 ≤ value   The object is a bitmap, vector, or TrueType font, or a Type 1 rasterized font that
        was created by a Type 1 rasterizer.'''
        ...
    
    @checksum.setter
    def checksum(self, value : int):
        '''Sets a 32-bit unsigned integer that is the checksum of the font.
        The checksum value has the following meanings.
        0x00000000  The object is a device font.
        0x00000001  The object is a Type 1 font that has been installed on the client machine and is
        enumerated by the PostScript printer driver as a device font.
        0x00000002  The object is not a font but is a Type 1 rasterizer.
        3 ≤ value   The object is a bitmap, vector, or TrueType font, or a Type 1 rasterized font that
        was created by a Type 1 rasterizer.'''
        ...
    
    @property
    def index(self) -> int:
        '''Gets a 32-bit unsigned integer that is an index associated with the font object. The
        meaning of this field is determined by the type of font.'''
        ...
    
    @index.setter
    def index(self, value : int):
        '''Sets a 32-bit unsigned integer that is an index associated with the font object. The
        meaning of this field is determined by the type of font.'''
        ...
    
    ...

