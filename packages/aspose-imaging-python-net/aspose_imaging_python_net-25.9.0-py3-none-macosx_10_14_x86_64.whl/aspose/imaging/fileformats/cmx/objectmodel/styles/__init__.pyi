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

class CmxColor:
    '''Represents a color value.'''
    
    def __init__(self):
        ...
    
    @property
    def color_model(self) -> aspose.imaging.fileformats.cmx.objectmodel.enums.ColorModels:
        ...
    
    @color_model.setter
    def color_model(self, value : aspose.imaging.fileformats.cmx.objectmodel.enums.ColorModels):
        ...
    
    @property
    def value(self) -> int:
        '''Gets the color value.'''
        ...
    
    @value.setter
    def value(self, value : int):
        '''Sets the color value.'''
        ...
    
    ...

class CmxFillStyle:
    '''Fill style for shapes.'''
    
    def __init__(self):
        ...
    
    @property
    def fill_type(self) -> aspose.imaging.fileformats.cmx.objectmodel.enums.FillTypes:
        ...
    
    @fill_type.setter
    def fill_type(self, value : aspose.imaging.fileformats.cmx.objectmodel.enums.FillTypes):
        ...
    
    @property
    def color1(self) -> aspose.imaging.fileformats.cmx.objectmodel.styles.CmxColor:
        '''Gets the primary color.'''
        ...
    
    @color1.setter
    def color1(self, value : aspose.imaging.fileformats.cmx.objectmodel.styles.CmxColor):
        '''Sets the primary color.'''
        ...
    
    @property
    def color2(self) -> aspose.imaging.fileformats.cmx.objectmodel.styles.CmxColor:
        '''Gets the secondary color.'''
        ...
    
    @color2.setter
    def color2(self, value : aspose.imaging.fileformats.cmx.objectmodel.styles.CmxColor):
        '''Sets the secondary color.'''
        ...
    
    @property
    def gradient(self) -> aspose.imaging.fileformats.cmx.objectmodel.styles.CmxGradient:
        '''Gets the gradient info.'''
        ...
    
    @gradient.setter
    def gradient(self, value : aspose.imaging.fileformats.cmx.objectmodel.styles.CmxGradient):
        '''Sets the gradient info.'''
        ...
    
    @property
    def image_fill(self) -> aspose.imaging.fileformats.cmx.objectmodel.styles.CmxImageFill:
        ...
    
    @image_fill.setter
    def image_fill(self, value : aspose.imaging.fileformats.cmx.objectmodel.styles.CmxImageFill):
        ...
    
    @property
    def transform(self) -> aspose.imaging.Matrix:
        '''Gets the fill transform.'''
        ...
    
    @transform.setter
    def transform(self, value : aspose.imaging.Matrix):
        '''Sets the fill transform.'''
        ...
    
    ...

class CmxGradient:
    '''Represents a gradient info.'''
    
    def __init__(self):
        ...
    
    @property
    def angle(self) -> float:
        '''Gets the angle.'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''Sets the angle.'''
        ...
    
    @property
    def center_x_offset(self) -> int:
        ...
    
    @center_x_offset.setter
    def center_x_offset(self, value : int):
        ...
    
    @property
    def center_y_offset(self) -> int:
        ...
    
    @center_y_offset.setter
    def center_y_offset(self, value : int):
        ...
    
    @property
    def colors(self) -> List[aspose.imaging.fileformats.cmx.objectmodel.styles.CmxColor]:
        '''Gets the colors.'''
        ...
    
    @colors.setter
    def colors(self, value : List[aspose.imaging.fileformats.cmx.objectmodel.styles.CmxColor]):
        '''Sets the colors.'''
        ...
    
    @property
    def edge_offset(self) -> int:
        ...
    
    @edge_offset.setter
    def edge_offset(self, value : int):
        ...
    
    @property
    def mode(self) -> int:
        '''Gets the mode.'''
        ...
    
    @mode.setter
    def mode(self, value : int):
        '''Sets the mode.'''
        ...
    
    @property
    def offsets(self) -> List[float]:
        '''Gets the offsets.'''
        ...
    
    @offsets.setter
    def offsets(self, value : List[float]):
        '''Sets the offsets.'''
        ...
    
    @property
    def rate_method(self) -> int:
        ...
    
    @rate_method.setter
    def rate_method(self, value : int):
        ...
    
    @property
    def rate_value(self) -> int:
        ...
    
    @rate_value.setter
    def rate_value(self, value : int):
        ...
    
    @property
    def screen(self) -> int:
        '''Gets the screen.'''
        ...
    
    @screen.setter
    def screen(self, value : int):
        '''Sets the screen.'''
        ...
    
    @property
    def steps(self) -> int:
        '''Gets the steps.'''
        ...
    
    @steps.setter
    def steps(self, value : int):
        '''Sets the steps.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.cmx.objectmodel.enums.GradientTypes:
        '''Gets the type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.imaging.fileformats.cmx.objectmodel.enums.GradientTypes):
        '''Sets the type.'''
        ...
    
    ...

class CmxImageFill:
    '''Image fill info'''
    
    def __init__(self):
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
    def procedure(self) -> aspose.imaging.fileformats.cmx.objectmodel.CmxProcedure:
        '''Gets the procedure.'''
        ...
    
    @procedure.setter
    def procedure(self, value : aspose.imaging.fileformats.cmx.objectmodel.CmxProcedure):
        '''Sets the procedure.'''
        ...
    
    @property
    def tile_offset_x(self) -> float:
        ...
    
    @tile_offset_x.setter
    def tile_offset_x(self, value : float):
        ...
    
    @property
    def tile_offset_y(self) -> float:
        ...
    
    @tile_offset_y.setter
    def tile_offset_y(self, value : float):
        ...
    
    @property
    def rcp_offset(self) -> float:
        ...
    
    @rcp_offset.setter
    def rcp_offset(self, value : float):
        ...
    
    @property
    def offset_type(self) -> aspose.imaging.fileformats.cmx.objectmodel.enums.TileOffsetTypes:
        ...
    
    @offset_type.setter
    def offset_type(self, value : aspose.imaging.fileformats.cmx.objectmodel.enums.TileOffsetTypes):
        ...
    
    @property
    def pattern_width(self) -> float:
        ...
    
    @pattern_width.setter
    def pattern_width(self, value : float):
        ...
    
    @property
    def pattern_height(self) -> float:
        ...
    
    @pattern_height.setter
    def pattern_height(self, value : float):
        ...
    
    @property
    def is_relative(self) -> bool:
        ...
    
    @is_relative.setter
    def is_relative(self, value : bool):
        ...
    
    @property
    def rotate180(self) -> bool:
        '''Gets a value indicating whether this  is upside down.'''
        ...
    
    @rotate180.setter
    def rotate180(self, value : bool):
        '''Sets a value indicating whether this  is upside down.'''
        ...
    
    ...

class CmxOutline:
    '''Represents an outline style.'''
    
    def __init__(self):
        ...
    
    @property
    def line_type(self) -> aspose.imaging.fileformats.cmx.objectmodel.enums.LineTypes:
        ...
    
    @line_type.setter
    def line_type(self, value : aspose.imaging.fileformats.cmx.objectmodel.enums.LineTypes):
        ...
    
    @property
    def caps_type(self) -> aspose.imaging.fileformats.cmx.objectmodel.enums.CapsTypes:
        ...
    
    @caps_type.setter
    def caps_type(self, value : aspose.imaging.fileformats.cmx.objectmodel.enums.CapsTypes):
        ...
    
    @property
    def join_type(self) -> aspose.imaging.fileformats.cmx.objectmodel.enums.JoinTypes:
        ...
    
    @join_type.setter
    def join_type(self, value : aspose.imaging.fileformats.cmx.objectmodel.enums.JoinTypes):
        ...
    
    @property
    def line_width(self) -> float:
        ...
    
    @line_width.setter
    def line_width(self, value : float):
        ...
    
    @property
    def stretch(self) -> float:
        '''Gets the stretch value.'''
        ...
    
    @stretch.setter
    def stretch(self, value : float):
        '''Sets the stretch value.'''
        ...
    
    @property
    def angle(self) -> float:
        '''Gets the angle.'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''Sets the angle.'''
        ...
    
    @property
    def color(self) -> aspose.imaging.fileformats.cmx.objectmodel.styles.CmxColor:
        '''Gets the outline color.'''
        ...
    
    @color.setter
    def color(self, value : aspose.imaging.fileformats.cmx.objectmodel.styles.CmxColor):
        '''Sets the outline color.'''
        ...
    
    @property
    def stroke(self) -> List[int]:
        '''Gets the stroke pattern.'''
        ...
    
    @stroke.setter
    def stroke(self, value : List[int]):
        '''Sets the stroke pattern.'''
        ...
    
    @property
    def start_arrowhead(self) -> aspose.imaging.fileformats.cmx.objectmodel.specs.CmxArrowSpec:
        ...
    
    @start_arrowhead.setter
    def start_arrowhead(self, value : aspose.imaging.fileformats.cmx.objectmodel.specs.CmxArrowSpec):
        ...
    
    @property
    def end_arrowhead(self) -> aspose.imaging.fileformats.cmx.objectmodel.specs.CmxArrowSpec:
        ...
    
    @end_arrowhead.setter
    def end_arrowhead(self, value : aspose.imaging.fileformats.cmx.objectmodel.specs.CmxArrowSpec):
        ...
    
    ...

class CmxParagraphStyle:
    '''The paragraph style.'''
    
    def __init__(self):
        ...
    
    @property
    def character_spacing(self) -> float:
        ...
    
    @character_spacing.setter
    def character_spacing(self, value : float):
        ...
    
    @property
    def language_spacing(self) -> float:
        ...
    
    @language_spacing.setter
    def language_spacing(self, value : float):
        ...
    
    @property
    def word_spacing(self) -> float:
        ...
    
    @word_spacing.setter
    def word_spacing(self, value : float):
        ...
    
    @property
    def line_spacing(self) -> float:
        ...
    
    @line_spacing.setter
    def line_spacing(self, value : float):
        ...
    
    @property
    def horizontal_alignment(self) -> aspose.imaging.fileformats.cmx.objectmodel.enums.ParagraphHorizontalAlignment:
        ...
    
    @horizontal_alignment.setter
    def horizontal_alignment(self, value : aspose.imaging.fileformats.cmx.objectmodel.enums.ParagraphHorizontalAlignment):
        ...
    
    ...

