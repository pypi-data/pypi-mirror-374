"""The namespace handles MagicWand processing."""
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

class ColorYUV:
    '''Represents an YUV color.'''
    
    @overload
    def __init__(self, y: int, u: int, v: int):
        '''Initializes a new instance of the  structure with the specified luminance component, blue and red projection components.
        
        :param y: The luminance component value.
        :param u: The blue projection component value.
        :param v: The red projection component value.'''
        ...
    
    @overload
    def __init__(self, color: aspose.imaging.Color):
        '''Initializes a new instance of the  structure from the specified existing .
        
        :param color: The Color from which to create the new .'''
        ...
    
    @overload
    def __init__(self):
        ...
    
    @property
    def y(self) -> float:
        '''Gets the luminance component value of this  structure.'''
        ...
    
    @property
    def u(self) -> float:
        '''Gets the blue projection component value of this  structure.'''
        ...
    
    @property
    def v(self) -> float:
        '''Gets the red projection component value of this  structure.'''
        ...
    
    ...

class MagicWandSettings:
    '''A magic wand selection settings class.'''
    
    @overload
    def __init__(self, point: aspose.imaging.Point):
        '''Initializes a new instance of the  class.
        
        :param point: The reference point.'''
        ...
    
    @overload
    def __init__(self, x: int, y: int):
        '''Initializes a new instance of the  class.
        
        :param x: The x-coordinate of the reference point.
        :param y: The y-coordinate of the reference point.'''
        ...
    
    @property
    def area_of_interest(self) -> aspose.imaging.Rectangle:
        ...
    
    @area_of_interest.setter
    def area_of_interest(self, value : aspose.imaging.Rectangle):
        ...
    
    @property
    def point(self) -> aspose.imaging.Point:
        '''Gets the reference point for algorithm work.'''
        ...
    
    @property
    def threshold(self) -> int:
        '''Gets the tolerance level for pixels color comparison.'''
        ...
    
    @threshold.setter
    def threshold(self, value : int):
        '''Sets the tolerance level for pixels color comparison.'''
        ...
    
    @property
    def contiguous_mode(self) -> bool:
        ...
    
    @contiguous_mode.setter
    def contiguous_mode(self, value : bool):
        ...
    
    @property
    def directional_mode(self) -> aspose.imaging.magicwand.FloodFillDirectionalMode:
        ...
    
    @directional_mode.setter
    def directional_mode(self, value : aspose.imaging.magicwand.FloodFillDirectionalMode):
        ...
    
    @property
    def color_compare_mode(self) -> aspose.imaging.magicwand.ColorComparisonMode:
        ...
    
    @color_compare_mode.setter
    def color_compare_mode(self, value : aspose.imaging.magicwand.ColorComparisonMode):
        ...
    
    ...

class MagicWandTool(aspose.imaging.IPartialArgb32PixelLoader):
    '''The class for magic wand algorithm main logic.'''
    
    @staticmethod
    def select(source: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Creates a new  based on  and source .
        
        :param source: Raster image for the algorithm to work over.
        :param settings: Settings of magic wand algorithm used in creating mask.
        :returns: New .'''
        ...
    
    def process(self, pixels_rectangle: aspose.imaging.Rectangle, pixels: List[int], start: aspose.imaging.Point, end: aspose.imaging.Point):
        '''Processes the loaded pixels .
        
        :param pixels_rectangle: The pixels rectangle.
        :param pixels: The 32-bit ARGB pixels.
        :param start: The start pixels point. If not equal to (left,top) meaning that it is not full rectangle we have.
        :param end: The end pixels point. If not equal to (right,bottom) meaning that it is not full rectangle we have.'''
        ...
    
    ...

class RasterImageExtension:
    '''Class with masks extension methods for .'''
    
    @staticmethod
    def select_mask(source: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Creates a  with selection of pixels with colors similar to the color of the reference point based on .
        
        :param source: Raster image for the algorithm to work over.
        :param settings: The settings used to process the selection, includes the reference point.
        :returns: New .'''
        ...
    
    @staticmethod
    def apply_mask(image: aspose.imaging.RasterImage, mask: aspose.imaging.magicwand.imagemasks.IImageMask):
        '''Applies  to the .
        
        :param image: Image to apply mask to.
        :param mask: The mask to be applied.'''
        ...
    
    ...

class ColorComparisonMode(enum.Enum):
    RGB_DEFAULT = enum.auto()
    '''Colors are compared in the RGB color space.
    Every color difference must satisfy the threshold.'''
    YUV_DEFAULT = enum.auto()
    '''Colors are compared in the YUV color space.
    Every color difference must satisfy the threshold.'''
    YUV_LESS_LUMA_SENSITIVE = enum.auto()
    '''Colors are compared in the YUV color space.
    Color information differences must satisfy the threshold, the threshold for luminance component is doubled.'''
    CUSTOM = enum.auto()
    '''Color comparison algorithm is defined by user.'''

class FloodFillDirectionalMode(enum.Enum):
    FOUR_DIRECTIONAL = enum.auto()
    '''Fill spreads only horizontally and vertically.'''
    EIGHT_DIRECTIONAL = enum.auto()
    '''Fill spreads in all directions (including diagonally).'''

