"""The namespace contains types [MS-EMFPLUS]: Enhanced Metafile Format Plus Extensions
            2.2 EMF+ Objects"""
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

class EmfPlusBaseBitmapData(EmfPlusStructureObjectType):
    '''Base class for bitmap data types.'''
    
    ...

class EmfPlusBaseBrushData(EmfPlusStructureObjectType):
    '''Base class for Brush data types.'''
    
    ...

class EmfPlusBaseImageData(EmfPlusStructureObjectType):
    '''Base class for image data types.'''
    
    ...

class EmfPlusBasePointType:
    '''The base point type.'''
    
    ...

class EmfPlusBitmap(EmfPlusBaseImageData):
    '''The EmfPlusBitmap object specifies a bitmap that contains a graphics image.'''
    
    def __init__(self):
        ...
    
    @property
    def bitmap_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBaseBitmapData:
        ...
    
    @bitmap_data.setter
    def bitmap_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBaseBitmapData):
        ...
    
    @property
    def height(self) -> int:
        '''Gets bitmap height
        Height (4 bytes): A 32-bit signed integer that specifies the height in pixels of the area occupied by the bitmap.
        If the image is compressed, according to the Type field, this value is undefined and MUST be ignored.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets bitmap height
        Height (4 bytes): A 32-bit signed integer that specifies the height in pixels of the area occupied by the bitmap.
        If the image is compressed, according to the Type field, this value is undefined and MUST be ignored.'''
        ...
    
    @property
    def pixel_format(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPixelFormat:
        ...
    
    @pixel_format.setter
    def pixel_format(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPixelFormat):
        ...
    
    @property
    def stride(self) -> int:
        '''Gets stride of the image
        Stride (4 bytes): A 32-bit signed integer that specifies the byte offset between the beginning of one scan-line and
        the next. This value is the number of bytes per pixel, which is specified in the PixelFormat field, multiplied by
        the width in pixels, which is specified in the Width field. The value of this field MUST be a multiple of four.
        If the image is compressed, according to the Type field, this value is undefined and MUST be ignored.'''
        ...
    
    @stride.setter
    def stride(self, value : int):
        '''Sets stride of the image
        Stride (4 bytes): A 32-bit signed integer that specifies the byte offset between the beginning of one scan-line and
        the next. This value is the number of bytes per pixel, which is specified in the PixelFormat field, multiplied by
        the width in pixels, which is specified in the Width field. The value of this field MUST be a multiple of four.
        If the image is compressed, according to the Type field, this value is undefined and MUST be ignored.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBitmapDataType:
        '''Gets type of the image
        Type (4 bytes): A 32-bit unsigned integer that specifies the type of data in the BitmapData field. This value MUST
        be defined in the  enumeration (section 2.1.1.2).'''
        ...
    
    @type.setter
    def type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBitmapDataType):
        '''Sets type of the image
        Type (4 bytes): A 32-bit unsigned integer that specifies the type of data in the BitmapData field. This value MUST
        be defined in the  enumeration (section 2.1.1.2).'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets image Width
        Width (4 bytes): A 32-bit signed integer that specifies the width in pixels of the area occupied by the bitmap.
        If the image is compressed, according to the Type field, this value is undefined and MUST be ignored.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets image Width
        Width (4 bytes): A 32-bit signed integer that specifies the width in pixels of the area occupied by the bitmap.
        If the image is compressed, according to the Type field, this value is undefined and MUST be ignored.'''
        ...
    
    ...

class EmfPlusBitmapData(EmfPlusBaseBitmapData):
    '''The EmfPlusBitmapData object specifies a bitmap image with pixel data.'''
    
    def __init__(self):
        ...
    
    @property
    def colors(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPalette:
        '''Gets the palette colors
        Colors (variable): An optional  object (section 2.2.2.28), which specifies the palette
        of colors used in the pixel data. This field MUST be present if the I flag is set in the PixelFormat field of the
        object.'''
        ...
    
    @colors.setter
    def colors(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPalette):
        '''Sets the palette colors
        Colors (variable): An optional  object (section 2.2.2.28), which specifies the palette
        of colors used in the pixel data. This field MUST be present if the I flag is set in the PixelFormat field of the
        object.'''
        ...
    
    @property
    def pixel_data(self) -> bytes:
        ...
    
    @pixel_data.setter
    def pixel_data(self, value : bytes):
        ...
    
    ...

class EmfPlusBlendBase(EmfPlusStructureObjectType):
    '''Base object for blend objects'''
    
    @property
    def blend_positions(self) -> List[float]:
        ...
    
    @blend_positions.setter
    def blend_positions(self, value : List[float]):
        ...
    
    ...

class EmfPlusBlendColors(EmfPlusBlendBase):
    '''The EmfPlusBlendColors object specifies positions and colors for the blend pattern of a gradient brush.'''
    
    def __init__(self):
        ...
    
    @property
    def blend_positions(self) -> List[float]:
        ...
    
    @blend_positions.setter
    def blend_positions(self, value : List[float]):
        ...
    
    @property
    def blend_argb_32_colors(self) -> List[int]:
        ...
    
    @blend_argb_32_colors.setter
    def blend_argb_32_colors(self, value : List[int]):
        ...
    
    ...

class EmfPlusBlendFactors(EmfPlusBlendBase):
    '''The EmfPlusBlendFactors object specifies positions and factors for the blend pattern of a gradient brush.'''
    
    def __init__(self):
        ...
    
    @property
    def blend_positions(self) -> List[float]:
        ...
    
    @blend_positions.setter
    def blend_positions(self, value : List[float]):
        ...
    
    @property
    def blend_factors(self) -> List[float]:
        ...
    
    @blend_factors.setter
    def blend_factors(self, value : List[float]):
        ...
    
    ...

class EmfPlusBlurEffect(EmfPlusImageEffectsObjectType):
    '''The BlurEffect object specifies a decrease in the difference in intensity between pixels in an image.'''
    
    def __init__(self):
        ...
    
    @property
    def blur_radius(self) -> float:
        ...
    
    @blur_radius.setter
    def blur_radius(self, value : float):
        ...
    
    @property
    def expand_edge(self) -> bool:
        ...
    
    @expand_edge.setter
    def expand_edge(self, value : bool):
        ...
    
    ...

class EmfPlusBoundaryBase(EmfPlusStructureObjectType):
    '''Base class for boundary objects'''
    
    ...

class EmfPlusBoundaryPathData(EmfPlusBoundaryBase):
    '''The EmfPlusBoundaryPathData object specifies a graphics path boundary for a gradient brush.'''
    
    def __init__(self):
        ...
    
    @property
    def boundary_path_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPath:
        ...
    
    @boundary_path_data.setter
    def boundary_path_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPath):
        ...
    
    ...

class EmfPlusBoundaryPointData(EmfPlusBoundaryBase):
    '''The EmfPlusBoundaryPointData object specifies a closed cardinal spline boundary for a gradient brush'''
    
    def __init__(self):
        ...
    
    @property
    def boundary_point_data(self) -> List[aspose.imaging.PointF]:
        ...
    
    @boundary_point_data.setter
    def boundary_point_data(self, value : List[aspose.imaging.PointF]):
        ...
    
    ...

class EmfPlusBrightnessContrastEffect(EmfPlusImageEffectsObjectType):
    '''The BrightnessContrastEffect object specifies an expansion or contraction of the lightest and darkest areas of an image.'''
    
    def __init__(self):
        ...
    
    @property
    def brightness_level(self) -> int:
        ...
    
    @brightness_level.setter
    def brightness_level(self, value : int):
        ...
    
    @property
    def contrast_level(self) -> int:
        ...
    
    @contrast_level.setter
    def contrast_level(self, value : int):
        ...
    
    ...

class EmfPlusBrush(EmfPlusGraphicsObjectType):
    '''The EmfPlusBrush object specifies a graphics brush for filling regions.'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    @property
    def brush_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBaseBrushData:
        ...
    
    @brush_data.setter
    def brush_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBaseBrushData):
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBrushType:
        '''Gets the type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBrushType):
        '''Sets the type.'''
        ...
    
    ...

class EmfPlusCharacterRange(EmfPlusStructureObjectType):
    '''EmfPlusCharacterRange description'''
    
    def __init__(self):
        ...
    
    @property
    def first(self) -> int:
        '''Gets a 32-bit signed integer that
        specifies the first position of this range.'''
        ...
    
    @first.setter
    def first(self, value : int):
        '''Sets a 32-bit signed integer that
        specifies the first position of this range.'''
        ...
    
    @property
    def length(self) -> int:
        '''Gets a 32-bit signed integer that specifies
        the number of positions in this range'''
        ...
    
    @length.setter
    def length(self, value : int):
        '''Sets a 32-bit signed integer that specifies
        the number of positions in this range'''
        ...
    
    ...

class EmfPlusColorBalanceEffect(EmfPlusImageEffectsObjectType):
    '''The ColorBalanceEffect object specifies adjustments to the relative amounts of red, green, and blue in an image.'''
    
    def __init__(self):
        ...
    
    @property
    def cyan_red(self) -> int:
        ...
    
    @cyan_red.setter
    def cyan_red(self, value : int):
        ...
    
    @property
    def magenta_green(self) -> int:
        ...
    
    @magenta_green.setter
    def magenta_green(self, value : int):
        ...
    
    @property
    def yellow_blue(self) -> int:
        ...
    
    @yellow_blue.setter
    def yellow_blue(self, value : int):
        ...
    
    ...

class EmfPlusColorCurveEffect(EmfPlusImageEffectsObjectType):
    '''The ColorCurveEffect object specifies one of eight adjustments to the color curve of an image.'''
    
    def __init__(self):
        ...
    
    @property
    def curve_adjustment(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCurveAdjustments:
        ...
    
    @curve_adjustment.setter
    def curve_adjustment(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCurveAdjustments):
        ...
    
    @property
    def curve_channel(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCurveChannel:
        ...
    
    @curve_channel.setter
    def curve_channel(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCurveChannel):
        ...
    
    @property
    def adjustment_intensity(self) -> int:
        ...
    
    @adjustment_intensity.setter
    def adjustment_intensity(self, value : int):
        ...
    
    ...

class EmfPlusColorLookupTableEffect(EmfPlusImageEffectsObjectType):
    '''The ColorLookupTableEffect object specifies adjustments to the colors in an image.'''
    
    def __init__(self):
        ...
    
    @property
    def blue_lookup_table(self) -> bytes:
        ...
    
    @blue_lookup_table.setter
    def blue_lookup_table(self, value : bytes):
        ...
    
    @property
    def green_lookup_table(self) -> bytes:
        ...
    
    @green_lookup_table.setter
    def green_lookup_table(self, value : bytes):
        ...
    
    @property
    def red_lookup_table(self) -> bytes:
        ...
    
    @red_lookup_table.setter
    def red_lookup_table(self, value : bytes):
        ...
    
    @property
    def alpha_lookup_table(self) -> bytes:
        ...
    
    @alpha_lookup_table.setter
    def alpha_lookup_table(self, value : bytes):
        ...
    
    ...

class EmfPlusColorMatrixEffect(EmfPlusImageEffectsObjectType):
    '''The ColorMatrixEffect object specifies an affine transform to be applied to an image.'''
    
    def __init__(self):
        ...
    
    @property
    def matrix_n0(self) -> List[int]:
        ...
    
    @matrix_n0.setter
    def matrix_n0(self, value : List[int]):
        ...
    
    @property
    def matrix_n1(self) -> List[int]:
        ...
    
    @matrix_n1.setter
    def matrix_n1(self, value : List[int]):
        ...
    
    @property
    def matrix_n2(self) -> List[int]:
        ...
    
    @matrix_n2.setter
    def matrix_n2(self, value : List[int]):
        ...
    
    @property
    def matrix_n3(self) -> List[int]:
        ...
    
    @matrix_n3.setter
    def matrix_n3(self, value : List[int]):
        ...
    
    @property
    def matrix_n4(self) -> List[int]:
        ...
    
    @matrix_n4.setter
    def matrix_n4(self, value : List[int]):
        ...
    
    @property
    def matrix(self) -> List[List[int]]:
        '''Gets the matrix.'''
        ...
    
    @matrix.setter
    def matrix(self, value : List[List[int]]):
        '''Sets the matrix.'''
        ...
    
    ...

class EmfPlusCompoundLineData(EmfPlusStructureObjectType):
    '''The EmfPlusCompoundLineData object specifies line and space data for a compound line.'''
    
    def __init__(self):
        ...
    
    @property
    def compound_line_data(self) -> List[float]:
        ...
    
    @compound_line_data.setter
    def compound_line_data(self, value : List[float]):
        ...
    
    ...

class EmfPlusCompressedImage(EmfPlusBaseBitmapData):
    '''The EmfPlusCompressedImage object specifies an image with compressed data.'''
    
    def __init__(self):
        ...
    
    @property
    def compressed_image_data(self) -> bytes:
        ...
    
    @compressed_image_data.setter
    def compressed_image_data(self, value : bytes):
        ...
    
    ...

class EmfPlusCustomBaseLineCap(EmfPlusStructureObjectType):
    '''Base class for custom line cap types.'''
    
    ...

class EmfPlusCustomEndCapData(EmfPlusStructureObjectType):
    '''The EmfPlusCustomEndCapData object specifies a custom line cap for the end of a line.'''
    
    def __init__(self):
        ...
    
    @property
    def custom_end_cap(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomLineCap:
        ...
    
    @custom_end_cap.setter
    def custom_end_cap(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomLineCap):
        ...
    
    ...

class EmfPlusCustomLineCap(EmfPlusGraphicsObjectType):
    '''The EmfPlusCustomLineCap object specifies the shape to use at the ends of a line drawn by a graphics pen.'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCustomLineCapDataType:
        '''Gets a 32-bit signed integer that specifies the type of custom line cap object,
        which determines the contents of the CustomLineCapData field.'''
        ...
    
    @type.setter
    def type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCustomLineCapDataType):
        '''Sets a 32-bit signed integer that specifies the type of custom line cap object,
        which determines the contents of the CustomLineCapData field.'''
        ...
    
    @property
    def custom_line_cap_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomBaseLineCap:
        ...
    
    @custom_line_cap_data.setter
    def custom_line_cap_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomBaseLineCap):
        ...
    
    ...

class EmfPlusCustomLineCapArrowData(EmfPlusCustomBaseLineCap):
    '''The EmfPlusCustomLineCapArrowData object specifies adjustable arrow data for a custom line cap.'''
    
    def __init__(self):
        ...
    
    @property
    def width(self) -> float:
        '''Gets a 32-bit floating-point value that specifies
        the width of the arrow cap'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets a 32-bit floating-point value that specifies
        the width of the arrow cap'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets a 32-bit floating-point value that specifies
        the height of the arrow cap.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets a 32-bit floating-point value that specifies
        the height of the arrow cap.'''
        ...
    
    @property
    def middle_inset(self) -> float:
        ...
    
    @middle_inset.setter
    def middle_inset(self, value : float):
        ...
    
    @property
    def fill_state(self) -> bool:
        ...
    
    @fill_state.setter
    def fill_state(self, value : bool):
        ...
    
    @property
    def line_start_cap(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType:
        ...
    
    @line_start_cap.setter
    def line_start_cap(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType):
        ...
    
    @property
    def line_end_cap(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType:
        ...
    
    @line_end_cap.setter
    def line_end_cap(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType):
        ...
    
    @property
    def line_join(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineJoinType:
        ...
    
    @line_join.setter
    def line_join(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineJoinType):
        ...
    
    @property
    def line_miter_limit(self) -> float:
        ...
    
    @line_miter_limit.setter
    def line_miter_limit(self, value : float):
        ...
    
    @property
    def width_scale(self) -> float:
        ...
    
    @width_scale.setter
    def width_scale(self, value : float):
        ...
    
    @property
    def fill_hot_spot(self) -> aspose.imaging.PointF:
        ...
    
    @fill_hot_spot.setter
    def fill_hot_spot(self, value : aspose.imaging.PointF):
        ...
    
    @property
    def line_hot_spot(self) -> aspose.imaging.PointF:
        ...
    
    @line_hot_spot.setter
    def line_hot_spot(self, value : aspose.imaging.PointF):
        ...
    
    ...

class EmfPlusCustomLineCapData(EmfPlusCustomBaseLineCap):
    '''The EmfPlusCustomLineCapData object specifies default data for a custom line cap.'''
    
    def __init__(self):
        ...
    
    @property
    def custom_line_cap_data_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCustomLineCapDataFlags:
        ...
    
    @custom_line_cap_data_flags.setter
    def custom_line_cap_data_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusCustomLineCapDataFlags):
        ...
    
    @property
    def base_cap(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType:
        ...
    
    @base_cap.setter
    def base_cap(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType):
        ...
    
    @property
    def base_inset(self) -> float:
        ...
    
    @base_inset.setter
    def base_inset(self, value : float):
        ...
    
    @property
    def stroke_start_cap(self) -> int:
        ...
    
    @stroke_start_cap.setter
    def stroke_start_cap(self, value : int):
        ...
    
    @property
    def stroke_end_cap(self) -> int:
        ...
    
    @stroke_end_cap.setter
    def stroke_end_cap(self, value : int):
        ...
    
    @property
    def stroke_join(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineJoinType:
        ...
    
    @stroke_join.setter
    def stroke_join(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineJoinType):
        ...
    
    @property
    def stroke_miter_limit(self) -> float:
        ...
    
    @stroke_miter_limit.setter
    def stroke_miter_limit(self, value : float):
        ...
    
    @property
    def width_scale(self) -> float:
        ...
    
    @width_scale.setter
    def width_scale(self, value : float):
        ...
    
    @property
    def fill_hot_spot(self) -> aspose.imaging.PointF:
        ...
    
    @fill_hot_spot.setter
    def fill_hot_spot(self, value : aspose.imaging.PointF):
        ...
    
    @property
    def stroke_hot_spot(self) -> aspose.imaging.PointF:
        ...
    
    @stroke_hot_spot.setter
    def stroke_hot_spot(self, value : aspose.imaging.PointF):
        ...
    
    @property
    def optional_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomLineCapOptionalData:
        ...
    
    @optional_data.setter
    def optional_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomLineCapOptionalData):
        ...
    
    ...

class EmfPlusCustomLineCapOptionalData(EmfPlusStructureObjectType):
    '''The EmfPlusCustomLineCapOptionalData object specifies optional fill and outline data for a custom line cap.'''
    
    def __init__(self):
        ...
    
    @property
    def fill_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusFillPath:
        ...
    
    @fill_data.setter
    def fill_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusFillPath):
        ...
    
    @property
    def outline_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusLinePath:
        ...
    
    @outline_data.setter
    def outline_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusLinePath):
        ...
    
    ...

class EmfPlusCustomStartCapData(EmfPlusStructureObjectType):
    '''The EmfPlusCustomStartCapData object specifies a custom line cap for the start of a line.'''
    
    def __init__(self):
        ...
    
    @property
    def custom_start_cap(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomLineCap:
        ...
    
    @custom_start_cap.setter
    def custom_start_cap(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomLineCap):
        ...
    
    ...

class EmfPlusDashedLineData(EmfPlusStructureObjectType):
    '''The EmfPlusDashedLineData object specifies properties of a dashed line for a graphics pen.'''
    
    def __init__(self):
        ...
    
    @property
    def dashed_line_data(self) -> List[float]:
        ...
    
    @dashed_line_data.setter
    def dashed_line_data(self, value : List[float]):
        ...
    
    ...

class EmfPlusFillPath(EmfPlusStructureObjectType):
    '''The EmfPlusFillPath object specifies a graphics path for filling a custom line cap'''
    
    def __init__(self):
        ...
    
    @property
    def fill_path(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPath:
        ...
    
    @fill_path.setter
    def fill_path(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPath):
        ...
    
    ...

class EmfPlusFocusScaleData(EmfPlusStructureObjectType):
    '''The EmfPlusFocusScaleData object specifies focus scales for the blend pattern of a path gradient brush.'''
    
    def __init__(self):
        ...
    
    @property
    def focus_scale_x(self) -> float:
        ...
    
    @focus_scale_x.setter
    def focus_scale_x(self, value : float):
        ...
    
    @property
    def focus_scale_y(self) -> float:
        ...
    
    @focus_scale_y.setter
    def focus_scale_y(self, value : float):
        ...
    
    @property
    def focus_scale_count(self) -> int:
        ...
    
    @focus_scale_count.setter
    def focus_scale_count(self, value : int):
        ...
    
    ...

class EmfPlusFont(EmfPlusGraphicsObjectType):
    '''The EmfPlusFont object specifies properties that determine the appearance of text, including
    typeface, size, and style.'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    @property
    def family_name(self) -> str:
        ...
    
    @family_name.setter
    def family_name(self, value : str):
        ...
    
    @property
    def font_style_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusFontStyleFlags:
        ...
    
    @font_style_flags.setter
    def font_style_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusFontStyleFlags):
        ...
    
    @property
    def size_unit(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType:
        ...
    
    @size_unit.setter
    def size_unit(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType):
        ...
    
    @property
    def em_size(self) -> float:
        ...
    
    @em_size.setter
    def em_size(self, value : float):
        ...
    
    ...

class EmfPlusGraphicsObjectType(EmfPlusObject):
    '''The Graphics Objects specify parameters for graphics output. They are part of the playback device context and are persistent during the playback of an EMF+ metafile.'''
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    ...

class EmfPlusGraphicsVersion(EmfPlusStructureObjectType):
    '''The EmfPlusGraphicsVersion object specifies the version of operating system graphics that is used to create an EMF+
    metafile.'''
    
    def __init__(self):
        ...
    
    @property
    def metafile_signature(self) -> int:
        ...
    
    @metafile_signature.setter
    def metafile_signature(self, value : int):
        ...
    
    @property
    def graphics_version(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusGraphicsVersionEnum:
        ...
    
    @graphics_version.setter
    def graphics_version(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusGraphicsVersionEnum):
        ...
    
    ...

class EmfPlusHatchBrushData(EmfPlusBaseBrushData):
    '''The EmfPlusHatchBrushData object specifies a hatch pattern for a graphics brush.'''
    
    def __init__(self):
        ...
    
    @property
    def back_argb_32_color(self) -> int:
        ...
    
    @back_argb_32_color.setter
    def back_argb_32_color(self, value : int):
        ...
    
    @property
    def fore_argb_32_color(self) -> int:
        ...
    
    @fore_argb_32_color.setter
    def fore_argb_32_color(self, value : int):
        ...
    
    @property
    def hatch_style(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusHatchStyle:
        ...
    
    @hatch_style.setter
    def hatch_style(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusHatchStyle):
        ...
    
    ...

class EmfPlusHueSaturationLightnessEffect(EmfPlusImageEffectsObjectType):
    '''The HueSaturationLightnessEffect object specifies adjustments to the hue, saturation, and lightness of an image.'''
    
    def __init__(self):
        ...
    
    @property
    def hue_level(self) -> int:
        ...
    
    @hue_level.setter
    def hue_level(self, value : int):
        ...
    
    @property
    def saturation_level(self) -> int:
        ...
    
    @saturation_level.setter
    def saturation_level(self, value : int):
        ...
    
    @property
    def lightness_level(self) -> int:
        ...
    
    @lightness_level.setter
    def lightness_level(self, value : int):
        ...
    
    ...

class EmfPlusImage(EmfPlusGraphicsObjectType):
    '''The EmfPlusImage object specifies a graphics image in the form of a bitmap or metafile.'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    @property
    def image_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBaseImageData:
        ...
    
    @image_data.setter
    def image_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBaseImageData):
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusImageDataType:
        '''Gets image type
        A 32-bit unsigned integer that specifies the type of data
        in the ImageData field. This value MUST be defined in the
        ImageDataType enumeration (section 2.1.1.15).'''
        ...
    
    @type.setter
    def type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusImageDataType):
        '''Sets image type
        A 32-bit unsigned integer that specifies the type of data
        in the ImageData field. This value MUST be defined in the
        ImageDataType enumeration (section 2.1.1.15).'''
        ...
    
    ...

class EmfPlusImageAttributes(EmfPlusGraphicsObjectType):
    '''The EmfPlusImageAttributes object specifies how bitmap image
    colors are manipulated during rendering.'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    @property
    def wrap_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusWrapMode:
        ...
    
    @wrap_mode.setter
    def wrap_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusWrapMode):
        ...
    
    @property
    def clamp_argb_32_color(self) -> int:
        ...
    
    @clamp_argb_32_color.setter
    def clamp_argb_32_color(self, value : int):
        ...
    
    @property
    def object_clamp(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusObjectClamp:
        ...
    
    @object_clamp.setter
    def object_clamp(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusObjectClamp):
        ...
    
    ...

class EmfPlusImageEffectsObjectType(EmfPlusObject):
    '''The Image Effects Objects specify parameters for graphics image effects, which can be applied to bitmap images'''
    
    ...

class EmfPlusLanguageIdentifier(EmfPlusStructureObjectType):
    '''The EmfPlusLanguageIdentifier object specifies a language identifier that corresponds to the natural
    language in a locale, including countries, geographical regions, and administrative districts.
    Each language identifier is an encoding of a primary language value and sublanguage value.'''
    
    def __init__(self):
        ...
    
    @property
    def value(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLanguageIdentifierType:
        '''Gets the value of the field
        0 1 2 3 4 5 6 7 8 9 1 0 1 2 3 4 5 6 7 8 9 2 0 1 2 3 4 5 6 7 8 9 3 0 1
        SubLanguageId|   PrimaryLanguageId |
        SubLanguageId (6 bits): The country, geographic region or administrative district for the natural language specified in the PrimaryLanguageId field.
        Sublanguage identifiers are vendor-extensible. Vendor-defined sublanguage identifiers MUST be in the range 0x20 to 0x3F, inclusive.
        PrimaryLanguageId (10 bits): The natural language.
        Primary language identifiers are vendor-extensible. Vendor-defined primary language identifiers MUST be in the range 0x0200 to 0x03FF, inclusive.'''
        ...
    
    @value.setter
    def value(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLanguageIdentifierType):
        '''Sets the value of the field
        0 1 2 3 4 5 6 7 8 9 1 0 1 2 3 4 5 6 7 8 9 2 0 1 2 3 4 5 6 7 8 9 3 0 1
        SubLanguageId|   PrimaryLanguageId |
        SubLanguageId (6 bits): The country, geographic region or administrative district for the natural language specified in the PrimaryLanguageId field.
        Sublanguage identifiers are vendor-extensible. Vendor-defined sublanguage identifiers MUST be in the range 0x20 to 0x3F, inclusive.
        PrimaryLanguageId (10 bits): The natural language.
        Primary language identifiers are vendor-extensible. Vendor-defined primary language identifiers MUST be in the range 0x0200 to 0x03FF, inclusive.'''
        ...
    
    ...

class EmfPlusLevelsEffect(EmfPlusImageEffectsObjectType):
    '''The LevelsEffect object specifies adjustments to the highlights, midtones, and shadows of an image.'''
    
    def __init__(self):
        ...
    
    @property
    def highlight(self) -> int:
        '''Gets the Specifies how much to lighten the highlights of an image. The color
        channel values at the high end of the intensity range are altered more than values near the
        middle or low ends, which means an image can be lightened without losing the contrast
        between the darker portions of the image.
        0 ≤ value < Specifies that highlights with a percent of intensity above this threshold SHOULD
        100 be increased.
        100 Specifies that highlights MUST NOT change.'''
        ...
    
    @highlight.setter
    def highlight(self, value : int):
        '''Sets the Specifies how much to lighten the highlights of an image. The color
        channel values at the high end of the intensity range are altered more than values near the
        middle or low ends, which means an image can be lightened without losing the contrast
        between the darker portions of the image.
        0 ≤ value < Specifies that highlights with a percent of intensity above this threshold SHOULD
        100 be increased.
        100 Specifies that highlights MUST NOT change.'''
        ...
    
    @property
    def mid_tone(self) -> int:
        ...
    
    @mid_tone.setter
    def mid_tone(self, value : int):
        ...
    
    @property
    def shadow(self) -> int:
        '''Gets the Specifies how much to darken the shadows of an image. Color channel
        values at the low end of the intensity range are altered more than values near the middle or
        high ends, which means an image can be darkened without losing the contrast between the
        lighter portions of the image.
        0 Specifies that shadows MUST NOT change.
        0 < value ≤ 100
        Specifies that shadows with a percent of intensity below this threshold are made
        darker.'''
        ...
    
    @shadow.setter
    def shadow(self, value : int):
        '''Sets the Specifies how much to darken the shadows of an image. Color channel
        values at the low end of the intensity range are altered more than values near the middle or
        high ends, which means an image can be darkened without losing the contrast between the
        lighter portions of the image.
        0 Specifies that shadows MUST NOT change.
        0 < value ≤ 100
        Specifies that shadows with a percent of intensity below this threshold are made
        darker.'''
        ...
    
    ...

class EmfPlusLinePath(EmfPlusStructureObjectType):
    '''The EmfPlusLinePath object specifies a graphics path for outlining a custom line cap.'''
    
    def __init__(self):
        ...
    
    @property
    def line_path(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPath:
        ...
    
    @line_path.setter
    def line_path(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPath):
        ...
    
    ...

class EmfPlusLinearGradientBrushData(EmfPlusBaseBrushData):
    '''The EmfPlusLinearGradientBrushData object specifies a linear gradient for a graphics brush.'''
    
    def __init__(self):
        ...
    
    @property
    def brush_data_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBrushDataFlags:
        ...
    
    @brush_data_flags.setter
    def brush_data_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBrushDataFlags):
        ...
    
    @property
    def end_argb_32_color(self) -> int:
        ...
    
    @end_argb_32_color.setter
    def end_argb_32_color(self, value : int):
        ...
    
    @property
    def optional_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusLinearGradientBrushOptionalData:
        ...
    
    @optional_data.setter
    def optional_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusLinearGradientBrushOptionalData):
        ...
    
    @property
    def rect_f(self) -> aspose.imaging.RectangleF:
        ...
    
    @rect_f.setter
    def rect_f(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def start_argb_32_color(self) -> int:
        ...
    
    @start_argb_32_color.setter
    def start_argb_32_color(self, value : int):
        ...
    
    @property
    def wrap_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusWrapMode:
        ...
    
    @wrap_mode.setter
    def wrap_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusWrapMode):
        ...
    
    ...

class EmfPlusLinearGradientBrushOptionalData(EmfPlusStructureObjectType):
    '''The EmfPlusLinearGradientBrushOptionalData object specifies optional data for a linear gradient brush.'''
    
    def __init__(self):
        ...
    
    @property
    def transform_matrix(self) -> aspose.imaging.Matrix:
        ...
    
    @transform_matrix.setter
    def transform_matrix(self, value : aspose.imaging.Matrix):
        ...
    
    @property
    def blend_pattern(self) -> List[aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBlendBase]:
        ...
    
    @blend_pattern.setter
    def blend_pattern(self, value : List[aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBlendBase]):
        ...
    
    @property
    def blend_pattern_as_preset_colors(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBlendColors:
        ...
    
    @property
    def blend_pattern_as_blend_factors_h(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBlendFactors:
        ...
    
    @property
    def blend_pattern_as_blend_factors_v(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBlendFactors:
        ...
    
    ...

class EmfPlusMetafile(EmfPlusBaseImageData):
    '''The EmfPlusMetafileData object specifies a metafile that contains a graphics image'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusMetafileDataType:
        '''Gets 32-bit unsigned integer that specifies the type of metafile that is embedded
        in the MetafileData field. This value MUST be defined in the MetafileDataType
        enumeration (section 2.1.1.21).'''
        ...
    
    @type.setter
    def type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusMetafileDataType):
        '''Sets 32-bit unsigned integer that specifies the type of metafile that is embedded
        in the MetafileData field. This value MUST be defined in the MetafileDataType
        enumeration (section 2.1.1.21).'''
        ...
    
    @property
    def metafile_data_size(self) -> int:
        ...
    
    @metafile_data_size.setter
    def metafile_data_size(self, value : int):
        ...
    
    @property
    def metafile_data(self) -> bytes:
        ...
    
    @metafile_data.setter
    def metafile_data(self, value : bytes):
        ...
    
    ...

class EmfPlusObject(aspose.imaging.fileformats.emf.MetaObject):
    '''Base Emf+ object type.'''
    
    ...

class EmfPlusPalette(EmfPlusStructureObjectType):
    '''The EmfPlusPalette object specifies the colors that make up a palette.'''
    
    def __init__(self):
        ...
    
    @property
    def palette_style_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPaletteStyleFlags:
        ...
    
    @palette_style_flags.setter
    def palette_style_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPaletteStyleFlags):
        ...
    
    @property
    def argb_32_entries(self) -> List[int]:
        ...
    
    @argb_32_entries.setter
    def argb_32_entries(self, value : List[int]):
        ...
    
    ...

class EmfPlusPath(EmfPlusGraphicsObjectType):
    '''The EmfPlusPath object specifies a series of line and curve segments that form a graphics path. The
    order for Bezier data points is the start point, control point 1, control point 2, and end point.For
    more information see[MSDN - DrawBeziers].'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    @property
    def path_point_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPathPointFlags:
        ...
    
    @path_point_flags.setter
    def path_point_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPathPointFlags):
        ...
    
    @property
    def path_points(self) -> List[aspose.imaging.PointF]:
        ...
    
    @path_points.setter
    def path_points(self, value : List[aspose.imaging.PointF]):
        ...
    
    @property
    def path_point_types(self) -> List[aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBasePointType]:
        ...
    
    @path_point_types.setter
    def path_point_types(self, value : List[aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBasePointType]):
        ...
    
    ...

class EmfPlusPathGradientBrushData(EmfPlusBaseBrushData):
    '''The EmfPlusPathGradientBrushData object specifies a path gradient for a graphics brush.'''
    
    def __init__(self):
        ...
    
    @property
    def brush_data_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBrushDataFlags:
        ...
    
    @brush_data_flags.setter
    def brush_data_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBrushDataFlags):
        ...
    
    @property
    def wrap_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusWrapMode:
        ...
    
    @wrap_mode.setter
    def wrap_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusWrapMode):
        ...
    
    @property
    def center_argb_32_color(self) -> int:
        ...
    
    @center_argb_32_color.setter
    def center_argb_32_color(self, value : int):
        ...
    
    @property
    def center_point_f(self) -> aspose.imaging.PointF:
        ...
    
    @center_point_f.setter
    def center_point_f(self, value : aspose.imaging.PointF):
        ...
    
    @property
    def surrounding_argb_32_colors(self) -> List[int]:
        ...
    
    @surrounding_argb_32_colors.setter
    def surrounding_argb_32_colors(self, value : List[int]):
        ...
    
    @property
    def boundary_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBoundaryBase:
        ...
    
    @boundary_data.setter
    def boundary_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBoundaryBase):
        ...
    
    @property
    def optional_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPathGradientBrushOptionalData:
        ...
    
    @optional_data.setter
    def optional_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPathGradientBrushOptionalData):
        ...
    
    ...

class EmfPlusPathGradientBrushOptionalData(EmfPlusStructureObjectType):
    '''The EmfPlusPathGradientBrushOptionalData object specifies optional data for a path gradient brush.'''
    
    def __init__(self):
        ...
    
    @property
    def transform_matrix(self) -> aspose.imaging.Matrix:
        ...
    
    @transform_matrix.setter
    def transform_matrix(self, value : aspose.imaging.Matrix):
        ...
    
    @property
    def blend_pattern(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBlendBase:
        ...
    
    @blend_pattern.setter
    def blend_pattern(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBlendBase):
        ...
    
    @property
    def focus_scale_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusFocusScaleData:
        ...
    
    @focus_scale_data.setter
    def focus_scale_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusFocusScaleData):
        ...
    
    ...

class EmfPlusPathPointType(EmfPlusBasePointType):
    '''The EmfPlusPathPointType object specifies a type value associated with a point on a graphics'''
    
    def __init__(self):
        ...
    
    @property
    def data(self) -> int:
        '''Gets the data.'''
        ...
    
    @data.setter
    def data(self, value : int):
        '''Sets the data.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPathPointTypeEnum:
        '''Gets 4-bit unsigned integer path point type. This value MUST be
        defined in the PathPointType enumeration (section 2.1.1.23).'''
        ...
    
    @type.setter
    def type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPathPointTypeEnum):
        '''Sets 4-bit unsigned integer path point type. This value MUST be
        defined in the PathPointType enumeration (section 2.1.1.23).'''
        ...
    
    @property
    def flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPathPointTypeFlags:
        '''Gets 4-bit flag field that specifies properties of the path point.
        This value MUST be one or more of the PathPointType flags (section 2.1.2.6).'''
        ...
    
    @flags.setter
    def flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPathPointTypeFlags):
        '''Sets 4-bit flag field that specifies properties of the path point.
        This value MUST be one or more of the PathPointType flags (section 2.1.2.6).'''
        ...
    
    ...

class EmfPlusPathPointTypeRle(EmfPlusBasePointType):
    '''The EmfPlusPathPointTypeRle object specifies type values associated with points on a graphics path using RLE compression.
    0 1 2 3 4 5 6 7 8 9 1 0 1 2 3 4 5 6 7 8 9 2 0 1 2 3 4 5 6 7 8 9 3 0 1
    B|1|RunCount   | PointType       |
    B (1 bit): If set, the path points are on a Bezier curve.
    If clear, the path points are on a graphics line.
    RunCount (6 bits): The run count, which is the number of path points to be associated with the type in the PointType field.
    PointType (1 byte): An EmfPlusPathPointType object (section 2.2.2.31) that specifies the type to associate with the path points.'''
    
    def __init__(self):
        ...
    
    @property
    def data(self) -> int:
        '''Gets the data.'''
        ...
    
    @data.setter
    def data(self, value : int):
        '''Sets the data.'''
        ...
    
    @property
    def bezier(self) -> bool:
        '''Gets a value indicating whether this  is bezier.
        If set, the path points are on a Bezier curve.
        If clear, the path points are on a graphics line.'''
        ...
    
    @bezier.setter
    def bezier(self, value : bool):
        '''Sets a value indicating whether this  is bezier.
        If set, the path points are on a Bezier curve.
        If clear, the path points are on a graphics line.'''
        ...
    
    @property
    def run_count(self) -> int:
        ...
    
    @run_count.setter
    def run_count(self, value : int):
        ...
    
    @property
    def point_type(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPathPointType:
        ...
    
    @point_type.setter
    def point_type(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPathPointType):
        ...
    
    ...

class EmfPlusPen(EmfPlusGraphicsObjectType):
    '''The EmfPlusPen object specifies a graphics pen for the drawing of lines.'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    @property
    def type(self) -> int:
        '''Gets This field MUST be set to zero'''
        ...
    
    @type.setter
    def type(self, value : int):
        '''Sets This field MUST be set to zero'''
        ...
    
    @property
    def pen_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPenData:
        ...
    
    @pen_data.setter
    def pen_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPenData):
        ...
    
    @property
    def brush_object(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBrush:
        ...
    
    @brush_object.setter
    def brush_object(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusBrush):
        ...
    
    ...

class EmfPlusPenData(EmfPlusStructureObjectType):
    '''The EmfPlusPenData object specifies properties of a graphics pen.'''
    
    def __init__(self):
        ...
    
    @property
    def pen_data_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPenDataFlags:
        ...
    
    @pen_data_flags.setter
    def pen_data_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPenDataFlags):
        ...
    
    @property
    def pen_unit(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType:
        ...
    
    @pen_unit.setter
    def pen_unit(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusUnitType):
        ...
    
    @property
    def pen_width(self) -> float:
        ...
    
    @pen_width.setter
    def pen_width(self, value : float):
        ...
    
    @property
    def optional_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPenOptionalData:
        ...
    
    @optional_data.setter
    def optional_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPenOptionalData):
        ...
    
    ...

class EmfPlusPenOptionalData(EmfPlusStructureObjectType):
    '''The EmfPlusPenOptionalData object specifies optional data for a graphics pen'''
    
    def __init__(self):
        ...
    
    @property
    def transform_matrix(self) -> aspose.imaging.Matrix:
        ...
    
    @transform_matrix.setter
    def transform_matrix(self, value : aspose.imaging.Matrix):
        ...
    
    @property
    def start_cap(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType:
        ...
    
    @start_cap.setter
    def start_cap(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType):
        ...
    
    @property
    def end_cap(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType:
        ...
    
    @end_cap.setter
    def end_cap(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineCapType):
        ...
    
    @property
    def join(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineJoinType:
        '''Gets an optional 32-bit signed integer that specifies how to join
        two lines that are drawn by the same pen and whose ends meet.
        This field MUST be present if the PenDataJoin flag is set in
        the PenDataFlags field of the EmfPlusPenData object, and the
        value MUST be defined in the LineJoinType enumeration
        (section 2.1.1.19).'''
        ...
    
    @join.setter
    def join(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineJoinType):
        '''Sets an optional 32-bit signed integer that specifies how to join
        two lines that are drawn by the same pen and whose ends meet.
        This field MUST be present if the PenDataJoin flag is set in
        the PenDataFlags field of the EmfPlusPenData object, and the
        value MUST be defined in the LineJoinType enumeration
        (section 2.1.1.19).'''
        ...
    
    @property
    def miter_limit(self) -> float:
        ...
    
    @miter_limit.setter
    def miter_limit(self, value : float):
        ...
    
    @property
    def line_style(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineStyle:
        ...
    
    @line_style.setter
    def line_style(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLineStyle):
        ...
    
    @property
    def dashed_line_cap_type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusDashedLineCapType:
        ...
    
    @dashed_line_cap_type.setter
    def dashed_line_cap_type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusDashedLineCapType):
        ...
    
    @property
    def dash_offset(self) -> float:
        ...
    
    @dash_offset.setter
    def dash_offset(self, value : float):
        ...
    
    @property
    def dashed_line_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusDashedLineData:
        ...
    
    @dashed_line_data.setter
    def dashed_line_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusDashedLineData):
        ...
    
    @property
    def pen_alignment(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPenAlignment:
        ...
    
    @pen_alignment.setter
    def pen_alignment(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusPenAlignment):
        ...
    
    @property
    def compound_line_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCompoundLineData:
        ...
    
    @compound_line_data.setter
    def compound_line_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCompoundLineData):
        ...
    
    @property
    def custom_start_cap_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomStartCapData:
        ...
    
    @custom_start_cap_data.setter
    def custom_start_cap_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomStartCapData):
        ...
    
    @property
    def custom_end_cap_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomEndCapData:
        ...
    
    @custom_end_cap_data.setter
    def custom_end_cap_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCustomEndCapData):
        ...
    
    ...

class EmfPlusRectF(EmfPlusStructureObjectType):
    '''The EmfPlusRectF object specifies a rectangle's origin, height, and width as 32-bit floating-point values.'''
    
    def __init__(self):
        ...
    
    @property
    def rect(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rect.setter
    def rect(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    ...

class EmfPlusRedEyeCorrectionEffect(EmfPlusImageEffectsObjectType):
    '''The RedEyeCorrectionEffect object specifies areas of an image to which a red-eye correction is applied.'''
    
    def __init__(self):
        ...
    
    @property
    def number_of_areas(self) -> int:
        ...
    
    @number_of_areas.setter
    def number_of_areas(self, value : int):
        ...
    
    @property
    def areas(self) -> List[aspose.imaging.Rectangle]:
        '''Gets the An array of NumberOfAreas WMF RectL objects, specified in [MS-WMF]
        section 2.2.2.19. Each rectangle specifies an area of the bitmap image to which the red-eye
        correction effect SHOULD be applied.'''
        ...
    
    @areas.setter
    def areas(self, value : List[aspose.imaging.Rectangle]):
        '''Sets the An array of NumberOfAreas WMF RectL objects, specified in [MS-WMF]
        section 2.2.2.19. Each rectangle specifies an area of the bitmap image to which the red-eye
        correction effect SHOULD be applied.'''
        ...
    
    ...

class EmfPlusRegion(EmfPlusGraphicsObjectType):
    '''The EmfPlusRegion object specifies line and curve segments that define a non rectilinear shape'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    @property
    def region_node(self) -> List[aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusRegionNode]:
        ...
    
    @region_node.setter
    def region_node(self, value : List[aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusRegionNode]):
        ...
    
    ...

class EmfPlusRegionNode(EmfPlusStructureObjectType):
    '''The EmfPlusRegionNode object specifies nodes of a graphics region.'''
    
    def __init__(self):
        ...
    
    @property
    def region_node_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusStructureObjectType:
        ...
    
    @region_node_data.setter
    def region_node_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusStructureObjectType):
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRegionNodeDataType:
        '''Gets 32-bit unsigned integer that specifies the type of
        data in the RegionNodeData field. This value MUST be defined in the
        RegionNodeDataType enumeration (section 2.1.1.27).'''
        ...
    
    @type.setter
    def type(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusRegionNodeDataType):
        '''Sets 32-bit unsigned integer that specifies the type of
        data in the RegionNodeData field. This value MUST be defined in the
        RegionNodeDataType enumeration (section 2.1.1.27).'''
        ...
    
    ...

class EmfPlusRegionNodeChildNodes(EmfPlusStructureObjectType):
    '''The EmfPlusRegionNodeChildNodes object specifies child nodes of a graphics region node'''
    
    def __init__(self):
        ...
    
    @property
    def operation(self) -> Aspose.Imaging.FileFormats.Emf.EmfPlus.Objects.EmfPlusRegionNodeChildNodes+NodesOperation:
        '''Gets the operation.'''
        ...
    
    @operation.setter
    def operation(self, value : Aspose.Imaging.FileFormats.Emf.EmfPlus.Objects.EmfPlusRegionNodeChildNodes+NodesOperation):
        '''Sets the operation.'''
        ...
    
    @property
    def left(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusRegionNode:
        '''Gets an EmfPlusRegionNode object that specifies the left child node of this region node.'''
        ...
    
    @left.setter
    def left(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusRegionNode):
        '''Sets an EmfPlusRegionNode object that specifies the left child node of this region node.'''
        ...
    
    @property
    def right(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusRegionNode:
        '''Gets an EmfPlusRegionNode object that defines the right child node of this region node.'''
        ...
    
    @right.setter
    def right(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusRegionNode):
        '''Sets an EmfPlusRegionNode object that defines the right child node of this region node.'''
        ...
    
    ...

class EmfPlusRegionNodePath(EmfPlusStructureObjectType):
    '''The EmfPlusRegionNodePath object specifies a graphics path for drawing the boundary of a region node.'''
    
    def __init__(self):
        ...
    
    @property
    def region_node_path(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPath:
        ...
    
    @region_node_path.setter
    def region_node_path(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusPath):
        ...
    
    ...

class EmfPlusSharpenEffect(EmfPlusImageEffectsObjectType):
    '''The SharpenEffect object specifies an increase in the difference in intensity between pixels in an image.'''
    
    def __init__(self):
        ...
    
    @property
    def radius(self) -> float:
        '''Gets A 32-bit floating-point number that specifies the sharpening radius in pixels,
        which determines the number of pixels involved in calculating the new value of a given pixel.
        As this value increases, the number of pixels involved in the calculation increases, and the
        resulting bitmap SHOULD become sharper.'''
        ...
    
    @radius.setter
    def radius(self, value : float):
        '''Sets A 32-bit floating-point number that specifies the sharpening radius in pixels,
        which determines the number of pixels involved in calculating the new value of a given pixel.
        As this value increases, the number of pixels involved in the calculation increases, and the
        resulting bitmap SHOULD become sharper.'''
        ...
    
    @property
    def amount(self) -> float:
        '''Gets A 32-bit floating-point number that specifies the difference in intensity
        between a given pixel and the surrounding pixels.
        0 Specifies that sharpening MUST NOT be performed.
        0 < value ≤ 100
        As this value increases, the difference in intensity between pixels SHOULD
        increase.'''
        ...
    
    @amount.setter
    def amount(self, value : float):
        '''Sets A 32-bit floating-point number that specifies the difference in intensity
        between a given pixel and the surrounding pixels.
        0 Specifies that sharpening MUST NOT be performed.
        0 < value ≤ 100
        As this value increases, the difference in intensity between pixels SHOULD
        increase.'''
        ...
    
    ...

class EmfPlusSolidBrushData(EmfPlusBaseBrushData):
    '''The EmfPlusSolidBrushData object specifies a solid color for a graphics brush.'''
    
    def __init__(self):
        ...
    
    @property
    def solid_argb_32_color(self) -> int:
        ...
    
    @solid_argb_32_color.setter
    def solid_argb_32_color(self, value : int):
        ...
    
    ...

class EmfPlusStringFormat(EmfPlusGraphicsObjectType):
    '''The EmfPlusStringFormat object specifies text layout,
    display manipulations, and language identification'''
    
    def __init__(self):
        ...
    
    @property
    def version(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusGraphicsVersion):
        '''Sets the version.'''
        ...
    
    @property
    def digit_language(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLanguageIdentifierType:
        ...
    
    @digit_language.setter
    def digit_language(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLanguageIdentifierType):
        ...
    
    @property
    def digit_substitution(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringDigitSubstitution:
        ...
    
    @digit_substitution.setter
    def digit_substitution(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringDigitSubstitution):
        ...
    
    @property
    def first_tab_offset(self) -> float:
        ...
    
    @first_tab_offset.setter
    def first_tab_offset(self, value : float):
        ...
    
    @property
    def hotkey_prefix(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusHotkeyPrefix:
        ...
    
    @hotkey_prefix.setter
    def hotkey_prefix(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusHotkeyPrefix):
        ...
    
    @property
    def language(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLanguageIdentifierType:
        '''Gets an EmfPlusLanguageIdentifier object (section 2.2.2.23)
        that specifies the language to use for the string'''
        ...
    
    @language.setter
    def language(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusLanguageIdentifierType):
        '''Sets an EmfPlusLanguageIdentifier object (section 2.2.2.23)
        that specifies the language to use for the string'''
        ...
    
    @property
    def leading_margin(self) -> float:
        ...
    
    @leading_margin.setter
    def leading_margin(self, value : float):
        ...
    
    @property
    def line_align(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringAlignment:
        ...
    
    @line_align.setter
    def line_align(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringAlignment):
        ...
    
    @property
    def range_count(self) -> int:
        ...
    
    @range_count.setter
    def range_count(self, value : int):
        ...
    
    @property
    def string_alignment(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringAlignment:
        ...
    
    @string_alignment.setter
    def string_alignment(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringAlignment):
        ...
    
    @property
    def string_format_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusStringFormatData:
        ...
    
    @string_format_data.setter
    def string_format_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusStringFormatData):
        ...
    
    @property
    def string_format_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringFormatFlags:
        ...
    
    @string_format_flags.setter
    def string_format_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringFormatFlags):
        ...
    
    @property
    def tabstop_count(self) -> int:
        ...
    
    @tabstop_count.setter
    def tabstop_count(self, value : int):
        ...
    
    @property
    def tracking(self) -> float:
        '''Gets a 32-bit floating-point value that specifies the ratio
        of the horizontal space allotted to each character in
        a specified string to the font-defined width of the
        character. Large values for this property specify ample
        space between characters; values less than 1 can produce
        character overlap. The default is 1.03; for typographic
        fonts, the default value is 1.00.'''
        ...
    
    @tracking.setter
    def tracking(self, value : float):
        '''Sets a 32-bit floating-point value that specifies the ratio
        of the horizontal space allotted to each character in
        a specified string to the font-defined width of the
        character. Large values for this property specify ample
        space between characters; values less than 1 can produce
        character overlap. The default is 1.03; for typographic
        fonts, the default value is 1.00.'''
        ...
    
    @property
    def trailing_margin(self) -> float:
        ...
    
    @trailing_margin.setter
    def trailing_margin(self, value : float):
        ...
    
    @property
    def trimming(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringTrimming:
        '''Gets specifies how to trim characters from a string that is
        too large to fit into a layout rectangle. This value
        MUST be defined in the StringTrimming enumeration (section 2.1.1.31).'''
        ...
    
    @trimming.setter
    def trimming(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusStringTrimming):
        '''Sets specifies how to trim characters from a string that is
        too large to fit into a layout rectangle. This value
        MUST be defined in the StringTrimming enumeration (section 2.1.1.31).'''
        ...
    
    ...

class EmfPlusStringFormatData(EmfPlusStructureObjectType):
    '''The EmfPlusStringFormatData object specifies tab stops and character positions for a graphics string.'''
    
    def __init__(self):
        ...
    
    @property
    def tab_stops(self) -> List[float]:
        ...
    
    @tab_stops.setter
    def tab_stops(self, value : List[float]):
        ...
    
    @property
    def char_range(self) -> List[aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCharacterRange]:
        ...
    
    @char_range.setter
    def char_range(self, value : List[aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusCharacterRange]):
        ...
    
    ...

class EmfPlusStructureObjectType(EmfPlusObject):
    '''The Structure Objects specify containers for data structures that are embedded in EMF+ metafile
    records.Structure objects, unlike graphics objects, are not explicitly created; they are components
    that make up more complex structures'''
    
    ...

class EmfPlusTextureBrushData(EmfPlusBaseBrushData):
    '''The EmfPlusTextureBrushData object specifies a texture image for a graphics brush.'''
    
    def __init__(self):
        ...
    
    @property
    def brush_data_flags(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBrushDataFlags:
        ...
    
    @brush_data_flags.setter
    def brush_data_flags(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusBrushDataFlags):
        ...
    
    @property
    def wrap_mode(self) -> aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusWrapMode:
        ...
    
    @wrap_mode.setter
    def wrap_mode(self, value : aspose.imaging.fileformats.emf.emfplus.consts.EmfPlusWrapMode):
        ...
    
    @property
    def optional_data(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusTextureBrushOptionalData:
        ...
    
    @optional_data.setter
    def optional_data(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusTextureBrushOptionalData):
        ...
    
    ...

class EmfPlusTextureBrushOptionalData(EmfPlusStructureObjectType):
    '''he EmfPlusTextureBrushOptionalData object specifies optional data for a texture brush.'''
    
    def __init__(self):
        ...
    
    @property
    def transform_matrix(self) -> aspose.imaging.Matrix:
        ...
    
    @transform_matrix.setter
    def transform_matrix(self, value : aspose.imaging.Matrix):
        ...
    
    @property
    def image_object(self) -> aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusImage:
        ...
    
    @image_object.setter
    def image_object(self, value : aspose.imaging.fileformats.emf.emfplus.objects.EmfPlusImage):
        ...
    
    ...

class EmfPlusTintEffect(EmfPlusImageEffectsObjectType):
    '''The TintEffect object specifies an addition of black or white to a specified hue in an image.'''
    
    def __init__(self):
        ...
    
    @property
    def hue(self) -> int:
        '''Gets a 32-bit signed integer that specifies the hue to which the tint effect is applied.
        -180 ≤ value < 0
        The color at a specified counter-clockwise rotation of the color wheel, starting
        from blue.
        0 A value of 0 specifies the color blue on the color wheel.
        0 < value ≤ 180
        The color at a specified clockwise rotation of the color wheel, starting from blue'''
        ...
    
    @hue.setter
    def hue(self, value : int):
        '''Sets a 32-bit signed integer that specifies the hue to which the tint effect is applied.
        -180 ≤ value < 0
        The color at a specified counter-clockwise rotation of the color wheel, starting
        from blue.
        0 A value of 0 specifies the color blue on the color wheel.
        0 < value ≤ 180
        The color at a specified clockwise rotation of the color wheel, starting from blue'''
        ...
    
    @property
    def amount(self) -> int:
        '''Gets A 32-bit signed integer that specifies how much the hue is strengthened or weakened.
        -100 ≤ value < 0
        Negative values specify how much the hue is weakened, which equates to the
        addition of black.
        0 A value of 0 specifies that the tint MUST NOT change.
        0 < value ≤ 100
        Positive values specify how much the hue is strengthened, which equates to the
        addition of white.'''
        ...
    
    @amount.setter
    def amount(self, value : int):
        '''Sets A 32-bit signed integer that specifies how much the hue is strengthened or weakened.
        -100 ≤ value < 0
        Negative values specify how much the hue is weakened, which equates to the
        addition of black.
        0 A value of 0 specifies that the tint MUST NOT change.
        0 < value ≤ 100
        Positive values specify how much the hue is strengthened, which equates to the
        addition of white.'''
        ...
    
    ...

