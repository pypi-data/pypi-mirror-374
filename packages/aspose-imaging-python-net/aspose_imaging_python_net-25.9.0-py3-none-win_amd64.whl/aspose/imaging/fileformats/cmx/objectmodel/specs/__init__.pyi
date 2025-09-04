"""The namespace handles Tiff file format processing."""
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

class CmxArrowSpec(CmxPathSpec):
    '''Represents geometric info specified for outline arrow (marker).'''
    
    def __init__(self):
        ...
    
    @property
    def points(self) -> List[aspose.imaging.fileformats.cmx.objectmodel.specs.CmxPathPointSpec]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.fileformats.cmx.objectmodel.specs.CmxPathPointSpec]):
        '''Sets the points.'''
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
    def arrow_offset(self) -> float:
        ...
    
    @arrow_offset.setter
    def arrow_offset(self, value : float):
        ...
    
    ...

class CmxEllipseSpec(ICmxObjectSpec):
    '''Represents geometric info specified for an ellipse.'''
    
    def __init__(self):
        ...
    
    @property
    def angle1(self) -> float:
        '''Gets the first angle used for defining of pie sector.
        Does no affect if  is ``false``.
        Measures in radians.'''
        ...
    
    @angle1.setter
    def angle1(self, value : float):
        '''Sets the first angle used for defining of pie sector.
        Does no affect if  is ``false``.
        Measures in radians.'''
        ...
    
    @property
    def angle2(self) -> float:
        '''Gets the second angle used for defining of pie sector.
        Does no affect if  is ``false``.
        Measures in radians.'''
        ...
    
    @angle2.setter
    def angle2(self, value : float):
        '''Sets the second angle used for defining of pie sector.
        Does no affect if  is ``false``.
        Measures in radians.'''
        ...
    
    @property
    def rotation(self) -> float:
        '''Gets the angle of rotation of the ellipse.
        Measures in radians.'''
        ...
    
    @rotation.setter
    def rotation(self, value : float):
        '''Sets the angle of rotation of the ellipse.
        Measures in radians.'''
        ...
    
    @property
    def pie(self) -> bool:
        '''Gets a value indicating whether this  is a pie.'''
        ...
    
    @pie.setter
    def pie(self, value : bool):
        '''Sets a value indicating whether this  is a pie.'''
        ...
    
    @property
    def center_x(self) -> float:
        ...
    
    @center_x.setter
    def center_x(self, value : float):
        ...
    
    @property
    def center_y(self) -> float:
        ...
    
    @center_y.setter
    def center_y(self, value : float):
        ...
    
    @property
    def diameter_x(self) -> float:
        ...
    
    @diameter_x.setter
    def diameter_x(self, value : float):
        ...
    
    @property
    def diameter_y(self) -> float:
        ...
    
    @diameter_y.setter
    def diameter_y(self, value : float):
        ...
    
    @property
    def bounding_box(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounding_box.setter
    def bounding_box(self, value : aspose.imaging.RectangleF):
        ...
    
    ...

class CmxImageSpec(ICmxObjectSpec):
    '''Represents info specified for raster images.'''
    
    def __init__(self):
        ...
    
    @property
    def bound_box(self) -> aspose.imaging.RectangleF:
        ...
    
    @bound_box.setter
    def bound_box(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def crop_box(self) -> aspose.imaging.RectangleF:
        ...
    
    @crop_box.setter
    def crop_box(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def matrix(self) -> aspose.imaging.Matrix:
        '''Gets the transformation matrix.'''
        ...
    
    @matrix.setter
    def matrix(self, value : aspose.imaging.Matrix):
        '''Sets the transformation matrix.'''
        ...
    
    @property
    def image_type(self) -> int:
        ...
    
    @image_type.setter
    def image_type(self, value : int):
        ...
    
    @property
    def images(self) -> List[aspose.imaging.fileformats.cmx.objectmodel.specs.CmxRasterImage]:
        '''Gets the images.'''
        ...
    
    @images.setter
    def images(self, value : List[aspose.imaging.fileformats.cmx.objectmodel.specs.CmxRasterImage]):
        '''Sets the images.'''
        ...
    
    @property
    def is_cmx_3_image(self) -> bool:
        ...
    
    @is_cmx_3_image.setter
    def is_cmx_3_image(self, value : bool):
        ...
    
    ...

class CmxPathPointSpec:
    '''Represents geometric info specified for a path point.'''
    
    def __init__(self):
        ...
    
    @property
    def x(self) -> float:
        '''Gets the X coordinate of the point.
        Measures in common document distance units.'''
        ...
    
    @x.setter
    def x(self, value : float):
        '''Sets the X coordinate of the point.
        Measures in common document distance units.'''
        ...
    
    @property
    def y(self) -> float:
        '''Gets the Y coordinate of the point.
        Measures in common document distance units.'''
        ...
    
    @y.setter
    def y(self, value : float):
        '''Sets the Y coordinate of the point.
        Measures in common document distance units.'''
        ...
    
    @property
    def jump_type(self) -> aspose.imaging.fileformats.cmx.objectmodel.enums.PathJumpTypes:
        ...
    
    @jump_type.setter
    def jump_type(self, value : aspose.imaging.fileformats.cmx.objectmodel.enums.PathJumpTypes):
        ...
    
    @property
    def is_closed_path(self) -> bool:
        ...
    
    @is_closed_path.setter
    def is_closed_path(self, value : bool):
        ...
    
    @property
    def bezier_order(self) -> int:
        ...
    
    @bezier_order.setter
    def bezier_order(self, value : int):
        ...
    
    ...

class CmxPathSpec(ICmxObjectSpec):
    '''Represents geometric info specified for a path.'''
    
    def __init__(self):
        ...
    
    @property
    def points(self) -> List[aspose.imaging.fileformats.cmx.objectmodel.specs.CmxPathPointSpec]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.fileformats.cmx.objectmodel.specs.CmxPathPointSpec]):
        '''Sets the points.'''
        ...
    
    @property
    def type(self) -> int:
        '''Gets the type.'''
        ...
    
    @type.setter
    def type(self, value : int):
        '''Sets the type.'''
        ...
    
    ...

class CmxRasterImage(ICmxObjectSpec):
    '''Represents the data specified for raster images.'''
    
    def __init__(self):
        ...
    
    @property
    def type(self) -> int:
        '''Gets the type of the image.'''
        ...
    
    @type.setter
    def type(self, value : int):
        '''Sets the type of the image.'''
        ...
    
    @property
    def compression(self) -> int:
        '''Gets the compression.'''
        ...
    
    @compression.setter
    def compression(self, value : int):
        '''Sets the compression.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets the size of the image.
        Measures in bytes.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets the size of the image.
        Measures in bytes.'''
        ...
    
    @property
    def compressed_size(self) -> int:
        ...
    
    @compressed_size.setter
    def compressed_size(self, value : int):
        ...
    
    @property
    def is_mask(self) -> bool:
        ...
    
    @is_mask.setter
    def is_mask(self, value : bool):
        ...
    
    @property
    def color_model(self) -> int:
        ...
    
    @color_model.setter
    def color_model(self, value : int):
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width of the image.
        Measures in pixels.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width of the image.
        Measures in pixels.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height of the image.
        Measures in pixels.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height of the image.
        Measures in pixels.'''
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    @bits_per_pixel.setter
    def bits_per_pixel(self, value : int):
        ...
    
    @property
    def bytes_per_line(self) -> int:
        ...
    
    @bytes_per_line.setter
    def bytes_per_line(self, value : int):
        ...
    
    @property
    def color_palette(self) -> List[int]:
        ...
    
    @color_palette.setter
    def color_palette(self, value : List[int]):
        ...
    
    @property
    def raw_data(self) -> bytes:
        ...
    
    @raw_data.setter
    def raw_data(self, value : bytes):
        ...
    
    ...

class CmxRectangleSpec(ICmxObjectSpec):
    '''Represents geometric info specified for a rectangle.'''
    
    def __init__(self):
        ...
    
    @property
    def center_x(self) -> float:
        ...
    
    @center_x.setter
    def center_x(self, value : float):
        ...
    
    @property
    def center_y(self) -> float:
        ...
    
    @center_y.setter
    def center_y(self, value : float):
        ...
    
    @property
    def width(self) -> float:
        '''Gets the width of the rectangle.
        Measures in common document distance units.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the width of the rectangle.
        Measures in common document distance units.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the height of the rectangle.
        Measures in common document distance units.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the height of the rectangle.
        Measures in common document distance units.'''
        ...
    
    @property
    def radius(self) -> float:
        '''Gets the radius of rounded rectangle corners.
        If its value is ``0`` then the rectangle has not rounded corners.
        Measures in common document distance units.'''
        ...
    
    @radius.setter
    def radius(self, value : float):
        '''Sets the radius of rounded rectangle corners.
        If its value is ``0`` then the rectangle has not rounded corners.
        Measures in common document distance units.'''
        ...
    
    @property
    def angle(self) -> float:
        '''Gets the angle of rotation of the rectangle.
        Measures in radians.'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''Sets the angle of rotation of the rectangle.
        Measures in radians.'''
        ...
    
    ...

class CmxTextBlockSpec(ICmxObjectSpec):
    '''Represents info specified for text blocks.'''
    
    def __init__(self):
        ...
    
    @property
    def paragraph_style(self) -> aspose.imaging.fileformats.cmx.objectmodel.styles.CmxParagraphStyle:
        ...
    
    @paragraph_style.setter
    def paragraph_style(self, value : aspose.imaging.fileformats.cmx.objectmodel.styles.CmxParagraphStyle):
        ...
    
    @property
    def font(self) -> aspose.imaging.Font:
        '''Gets the font.'''
        ...
    
    @font.setter
    def font(self, value : aspose.imaging.Font):
        '''Sets the font.'''
        ...
    
    @property
    def matrix(self) -> aspose.imaging.Matrix:
        '''Gets the transformation matrix.'''
        ...
    
    @matrix.setter
    def matrix(self, value : aspose.imaging.Matrix):
        '''Sets the transformation matrix.'''
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
    def char_locations(self) -> List[aspose.imaging.PointF]:
        ...
    
    @char_locations.setter
    def char_locations(self, value : List[aspose.imaging.PointF]):
        ...
    
    ...

class ICmxObjectSpec:
    '''Specification of graphics object'''
    
    ...

