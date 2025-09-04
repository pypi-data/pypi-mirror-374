"""The namespace handles image masks processing."""
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

class CircleMask(ImageMask):
    '''Describes a circle mask.'''
    
    @overload
    def __init__(self, x: int, y: int, radius: int):
        '''Initializes a new instance of the  class with the specified center point and radius.
        
        :param x: The x-coordinate of the center point of the selected area.
        :param y: The y-coordinate of the center point of the selected area.
        :param radius: Radius of the selected area.'''
        ...
    
    @overload
    def __init__(self, center: aspose.imaging.Point, radius: int):
        '''Initializes a new instance of the  class with the specified center point and radius.
        
        :param center: The center point of the selected area.
        :param radius: Radius of the selected area.'''
        ...
    
    @overload
    def crop(self, rectangle: aspose.imaging.Rectangle) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified rectangle.
        
        :param rectangle: The specified rectangle.
        :returns: A cropped CircleMask or ImageBitMask as ImageMask.
        As ImageBitMask may be returned, fluent call is recommended.'''
        ...
    
    @overload
    def crop(self, size: aspose.imaging.Size) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified size.
        
        :param size: The specified size.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def crop(self, width: int, height: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified width and height.
        
        :param width: The specified width.
        :param height: The specified height.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def union(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def union(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def union(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the subtraction of the provided mask from current.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the source of the current mask subtracted from the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the provided image subtracted from the current mask.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    def get(self, x: int, y: int) -> bool:
        '''Gets the opacity of the specified pixel.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def inflate(self, size: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Inflates this mask by the specified amount.
        
        :param size: The amount to inflate this mask.
        :returns: An inflated CircleMask as ImageMask.'''
        ...
    
    def is_opaque(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is opaque.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def is_transparent(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is transparent.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is transparent; otherwise, false.'''
        ...
    
    def get_byte_opacity(self, x: int, y: int) -> int:
        '''Gets the opacity of the specified pixel with byte precision.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: Byte value, representing the opacity of the specified pixel.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a copy of the current instance.
        
        :returns: A new object that is a copy of this instance.'''
        ...
    
    def get_feathered(self, settings: aspose.imaging.magicwand.imagemasks.FeatheringSettings) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Gets grayscale mask with the border feathered with the specified settings.
        
        :param settings: Feathering settings.
        :returns: with feathered border.'''
        ...
    
    def apply(self):
        '''Applies current mask to the  source, if exists.'''
        ...
    
    def apply_to(self, image: aspose.imaging.RasterImage):
        '''Applies current mask to the specified .
        
        :param image: Image to apply mask to.'''
        ...
    
    def invert(self) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the inversion of the current mask.
        
        :returns: New .'''
        ...
    
    @property
    def source(self) -> aspose.imaging.RasterImage:
        '''Gets the source image used to create this mask, if exists.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width, in pixels, of this mask.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height, in pixels, of this mask.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets the bounds, in pixels, of this mask.'''
        ...
    
    @property
    def selection_bounds(self) -> aspose.imaging.Rectangle:
        ...
    
    ...

class EmptyImageMask(ImageMask):
    '''Describes an empty non-abstract mask.'''
    
    def __init__(self, width: int, height: int):
        '''Initializes a new instance of the  class with the specified width and height.
        
        :param width: Width of the mask.
        :param height: Height of the mask.'''
        ...
    
    @overload
    def crop(self, rectangle: aspose.imaging.Rectangle) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified rectangle.
        
        :param rectangle: The specified rectangle.
        :returns: A cropped EmptyImageMask as ImageMask.'''
        ...
    
    @overload
    def crop(self, size: aspose.imaging.Size) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified size.
        
        :param size: The specified size.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def crop(self, width: int, height: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified width and height.
        
        :param width: The specified width.
        :param height: The specified height.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def union(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def union(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def union(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the subtraction of the provided mask from current.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the source of the current mask subtracted from the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the provided image subtracted from the current mask.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    def get(self, x: int, y: int) -> bool:
        '''Gets the opacity of the specified pixel.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def inflate(self, size: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Inflates this mask by the specified amount.
        
        :param size: The amount to inflate this mask.
        :returns: An inflated EmptyImageMask as ImageMask.'''
        ...
    
    def is_opaque(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is opaque.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def is_transparent(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is transparent.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is transparent; otherwise, false.'''
        ...
    
    def get_byte_opacity(self, x: int, y: int) -> int:
        '''Gets the opacity of the specified pixel with byte precision.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: Byte value, representing the opacity of the specified pixel.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a copy of the current instance.
        
        :returns: A new object that is a copy of this instance.'''
        ...
    
    def get_feathered(self, settings: aspose.imaging.magicwand.imagemasks.FeatheringSettings) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Gets grayscale mask with the border feathered with the specified settings.
        
        :param settings: Feathering settings.
        :returns: with feathered border.'''
        ...
    
    def apply(self):
        '''Applies current mask to the  source, if exists.'''
        ...
    
    def apply_to(self, image: aspose.imaging.RasterImage):
        '''Applies current mask to the specified .
        
        :param image: Image to apply mask to.'''
        ...
    
    def invert(self) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the inversion of the current mask.
        
        :returns: New .'''
        ...
    
    @property
    def source(self) -> aspose.imaging.RasterImage:
        '''Gets the source image used to create this mask, if exists.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width, in pixels, of this mask.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height, in pixels, of this mask.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets the bounds, in pixels, of this mask.'''
        ...
    
    @property
    def selection_bounds(self) -> aspose.imaging.Rectangle:
        ...
    
    ...

class FeatheringSettings:
    '''A feathering settings class.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets the feathering size.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets the feathering size.'''
        ...
    
    @property
    def mode(self) -> aspose.imaging.magicwand.imagemasks.FeatheringMode:
        '''Gets the feathering algorithm mode.'''
        ...
    
    @mode.setter
    def mode(self, value : aspose.imaging.magicwand.imagemasks.FeatheringMode):
        '''Sets the feathering algorithm mode.'''
        ...
    
    ...

class IImageMask:
    '''Describes a mask.'''
    
    def is_opaque(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is opaque.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def is_transparent(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is transparent.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is transparent; otherwise, false.'''
        ...
    
    def get_byte_opacity(self, x: int, y: int) -> int:
        '''Gets the opacity of the specified pixel with byte precision.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: Byte value, representing the opacity of the specified pixel.'''
        ...
    
    def clone(self) -> any:
        ...
    
    @property
    def source(self) -> aspose.imaging.RasterImage:
        '''Gets the source image used to create this mask, if exists.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width, in pixels, of this mask.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height, in pixels, of this mask.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets the bounds, in pixels, of this mask.'''
        ...
    
    @property
    def selection_bounds(self) -> aspose.imaging.Rectangle:
        ...
    
    ...

class ImageBitMask(ImageMask):
    '''Describes a binary image mask.'''
    
    @overload
    def __init__(self, width: int, height: int):
        '''Initializes a new instance of the  class with the specified width and height.
        
        :param width: Width of the mask.
        :param height: Height of the mask.'''
        ...
    
    @overload
    def __init__(self, image: aspose.imaging.RasterImage):
        '''Initializes a new instance of the  class with the size of the specified existing .
        Specified  will be stored as source image.
        
        :param image: Source image.'''
        ...
    
    @overload
    def crop(self, rectangle: aspose.imaging.Rectangle) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified rectangle.
        
        :param rectangle: The specified rectangle.
        :returns: A cropped  as .'''
        ...
    
    @overload
    def crop(self, size: aspose.imaging.Size) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified size.
        
        :param size: The specified size.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def crop(self, width: int, height: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified width and height.
        
        :param width: The specified width.
        :param height: The specified height.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def union(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def union(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def union(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the subtraction of the provided mask from current.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the source of the current mask subtracted from the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the provided image subtracted from the current mask.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    def get(self, x: int, y: int) -> bool:
        '''Gets the opacity of the specified pixel.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def inflate(self, size: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Inflates this mask by the specified amount.
        
        :param size: The amount to inflate this mask.
        :returns: An inflated  as .'''
        ...
    
    def is_opaque(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is opaque.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def is_transparent(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is transparent.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is transparent; otherwise, false.'''
        ...
    
    def get_byte_opacity(self, x: int, y: int) -> int:
        '''Gets the opacity of the specified pixel with byte precision.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: Byte value, representing the opacity of the specified pixel.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a copy of the current instance.
        
        :returns: A new object that is a copy of this instance.'''
        ...
    
    def get_feathered(self, settings: aspose.imaging.magicwand.imagemasks.FeatheringSettings) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Gets grayscale mask with the border feathered with the specified settings.
        
        :param settings: Feathering settings.
        :returns: with feathered border.'''
        ...
    
    def apply(self):
        '''Applies current mask to the  source, if exists.'''
        ...
    
    def apply_to(self, image: aspose.imaging.RasterImage):
        '''Applies current mask to the specified .
        
        :param image: Image to apply mask to.'''
        ...
    
    def invert(self) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the inversion of the current mask.
        
        :returns: New .'''
        ...
    
    def set_mask_pixel(self, x: int, y: int, value: bool):
        '''Sets the opacity to the specified pixel.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :param value: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    @property
    def source(self) -> aspose.imaging.RasterImage:
        '''Gets the source image used to create this mask, if exists.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width, in pixels, of this mask.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height, in pixels, of this mask.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets the bounds, in pixels, of this mask.'''
        ...
    
    @property
    def selection_bounds(self) -> aspose.imaging.Rectangle:
        ...
    
    ...

class ImageGrayscaleMask(IImageMask):
    '''Describes a grayscale image mask.'''
    
    @overload
    def __init__(self, width: int, height: int):
        '''Initializes a new instance of the  class with the specified width and height.
        
        :param width: Width of the mask.
        :param height: Height of the mask.'''
        ...
    
    @overload
    def __init__(self, image: aspose.imaging.RasterImage):
        '''Initializes a new instance of the  class with the size of the specified existing .
        Specified  will be stored as source image.
        
        :param image: Source image.'''
        ...
    
    @overload
    def crop(self, size: aspose.imaging.Size) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Crops mask with the specified size.
        
        :param size: The specified size.
        :returns: An cropped .'''
        ...
    
    @overload
    def crop(self, width: int, height: int) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Crops mask with the specified width and height.
        
        :param width: The specified width.
        :param height: The specified height.
        :returns: An cropped .'''
        ...
    
    @overload
    def crop(self, rectangle: aspose.imaging.Rectangle) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Crops mask with the specified rectangle.
        
        :param rectangle: The specified rectangle.
        :returns: A cropped .'''
        ...
    
    def get(self, x: int, y: int) -> int:
        '''Gets or sets the opacity of the specified pixel.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: Byte value; 0 if transparent; 255 if opaque.'''
        ...
    
    def set(self, x: int, y: int, value: int):
        '''Sets the opacity of the specified pixel.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :param value: Byte value; 0 if transparent; 255 if opaque.'''
        ...
    
    def is_opaque(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is opaque.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def is_transparent(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is transparent.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is transparent; otherwise, false.'''
        ...
    
    def get_byte_opacity(self, x: int, y: int) -> int:
        '''Gets the opacity of the specified pixel with byte precision.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: Byte value, representing the opacity of the specified pixel.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a copy of the current instance.
        
        :returns: A new object that is a copy of this instance.'''
        ...
    
    def apply(self):
        '''Applies current mask to the  source, if exists.'''
        ...
    
    def apply_to(self, image: aspose.imaging.RasterImage):
        '''Applies current mask to the specified .
        
        :param image: Image to apply mask to.'''
        ...
    
    def invert(self) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Gets the inversion of the current mask.
        
        :returns: New .'''
        ...
    
    def union(self, mask: aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Union of two masks.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    def subtract(self, mask: aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Gets the subtraction of the provided mask from current.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    def intersect(self, mask: aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Gets the intersection of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    def exclusive_disjunction(self, mask: aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Gets the exclusive disjunction of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @property
    def source(self) -> aspose.imaging.RasterImage:
        '''Gets the source image used to create this mask, if exists.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width, in pixels, of this mask.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height, in pixels, of this mask.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets the bounds, in pixels, of this mask.'''
        ...
    
    @property
    def selection_bounds(self) -> aspose.imaging.Rectangle:
        ...
    
    ...

class ImageMask(IImageMask):
    '''Describes a binary image mask.'''
    
    @overload
    def crop(self, size: aspose.imaging.Size) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified size.
        
        :param size: The specified size.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def crop(self, width: int, height: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified width and height.
        
        :param width: The specified width.
        :param height: The specified height.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def crop(self, rectangle: aspose.imaging.Rectangle) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified rectangle.
        
        :param rectangle: The specified rectangle.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def union(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def union(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def union(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the subtraction of the provided mask from current.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the source of the current mask subtracted from the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the provided image subtracted from the current mask.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    def get(self, x: int, y: int) -> bool:
        '''Gets the opacity of the specified pixel.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def inflate(self, size: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Inflates this mask by the specified amount.
        
        :param size: The amount to inflate this mask.
        :returns: An ImageMask.'''
        ...
    
    def is_opaque(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is opaque.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def is_transparent(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is transparent.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is transparent; otherwise, false.'''
        ...
    
    def get_byte_opacity(self, x: int, y: int) -> int:
        '''Gets the opacity of the specified pixel with byte precision.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: Byte value, representing the opacity of the specified pixel.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a copy of the current instance.
        
        :returns: A new object that is a copy of this instance.'''
        ...
    
    def get_feathered(self, settings: aspose.imaging.magicwand.imagemasks.FeatheringSettings) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Gets grayscale mask with the border feathered with the specified settings.
        
        :param settings: Feathering settings.
        :returns: with feathered border.'''
        ...
    
    def apply(self):
        '''Applies current mask to the  source, if exists.'''
        ...
    
    def apply_to(self, image: aspose.imaging.RasterImage):
        '''Applies current mask to the specified .
        
        :param image: Image to apply mask to.'''
        ...
    
    def invert(self) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the inversion of the current mask.
        
        :returns: New .'''
        ...
    
    @property
    def source(self) -> aspose.imaging.RasterImage:
        '''Gets the source image used to create this mask, if exists.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width, in pixels, of this mask.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height, in pixels, of this mask.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets the bounds, in pixels, of this mask.'''
        ...
    
    @property
    def selection_bounds(self) -> aspose.imaging.Rectangle:
        ...
    
    ...

class RectangleMask(ImageMask):
    '''Describes a rectangle mask.'''
    
    @overload
    def __init__(self, x: int, y: int, width: int, height: int):
        '''Initializes a new instance of the  class with the specified left-top point, width and height.
        
        :param x: The x-coordinate of the left-top point of the selected area.
        :param y: The y-coordinate of the left-top point of the selected area.
        :param width: Width of the selected area.
        :param height: Height of the selected area.'''
        ...
    
    @overload
    def __init__(self, selected_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class with the specified rectangle.
        
        :param selected_area: Selected area specified as a rectangle.'''
        ...
    
    @overload
    def crop(self, rectangle: aspose.imaging.Rectangle) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified rectangle.
        
        :param rectangle: The specified rectangle.
        :returns: A cropped RectangleMask as ImageMask.'''
        ...
    
    @overload
    def crop(self, size: aspose.imaging.Size) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified size.
        
        :param size: The specified size.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def crop(self, width: int, height: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Crops mask with the specified width and height.
        
        :param width: The specified width.
        :param height: The specified height.
        :returns: An ImageMask.'''
        ...
    
    @overload
    def union(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def union(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def union(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the union of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the subtraction of the provided mask from current.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the source of the current mask subtracted from the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def subtract(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the result of magic wand selection applied to the provided image subtracted from the current mask.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def intersect(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the intersection of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, mask: aspose.imaging.magicwand.imagemasks.ImageMask) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of current mask with provided.
        
        :param mask: Provided mask
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the source of the mask.
        
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    @overload
    def exclusive_disjunction(self, image: aspose.imaging.RasterImage, settings: aspose.imaging.magicwand.MagicWandSettings) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the exclusive disjunction of the current mask with the result of magic wand selection applied to the provided image.
        
        :param image: Image for magic wand.
        :param settings: Magic wand settings.
        :returns: New .'''
        ...
    
    def get(self, x: int, y: int) -> bool:
        '''Gets the opacity of the specified pixel.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def inflate(self, size: int) -> aspose.imaging.magicwand.imagemasks.ImageMask:
        '''Inflates this mask by the specified amount.
        
        :param size: The amount to inflate this mask.
        :returns: An inflated RectangleMask as ImageMask.'''
        ...
    
    def is_opaque(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is opaque.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is opaque; otherwise, false.'''
        ...
    
    def is_transparent(self, x: int, y: int) -> bool:
        '''Checks if the specified pixel is transparent.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: true if the specified pixel is transparent; otherwise, false.'''
        ...
    
    def get_byte_opacity(self, x: int, y: int) -> int:
        '''Gets the opacity of the specified pixel with byte precision.
        
        :param x: The x-coordinate of the pixel.
        :param y: The y-coordinate of the pixel.
        :returns: Byte value, representing the opacity of the specified pixel.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a copy of the current instance.
        
        :returns: A new object that is a copy of this instance.'''
        ...
    
    def get_feathered(self, settings: aspose.imaging.magicwand.imagemasks.FeatheringSettings) -> aspose.imaging.magicwand.imagemasks.ImageGrayscaleMask:
        '''Gets grayscale mask with the border feathered with the specified settings.
        
        :param settings: Feathering settings.
        :returns: with feathered border.'''
        ...
    
    def apply(self):
        '''Applies current mask to the  source, if exists.'''
        ...
    
    def apply_to(self, image: aspose.imaging.RasterImage):
        '''Applies current mask to the specified .
        
        :param image: Image to apply mask to.'''
        ...
    
    def invert(self) -> aspose.imaging.magicwand.imagemasks.ImageBitMask:
        '''Gets the inversion of the current mask.
        
        :returns: New .'''
        ...
    
    @property
    def source(self) -> aspose.imaging.RasterImage:
        '''Gets the source image used to create this mask, if exists.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width, in pixels, of this mask.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height, in pixels, of this mask.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets the bounds, in pixels, of this mask.'''
        ...
    
    @property
    def selection_bounds(self) -> aspose.imaging.Rectangle:
        ...
    
    ...

class FeatheringMode(enum.Enum):
    NONE = enum.auto()
    '''No feathering'''
    MATHEMATICALLY_CORRECT = enum.auto()
    '''Mathematically correct algorithm that will most likely result with a well distinguishable line on the border of the selected area'''
    ADJUSTED = enum.auto()
    '''Adjusted algorithm that will create a smooth border of the selected area'''

