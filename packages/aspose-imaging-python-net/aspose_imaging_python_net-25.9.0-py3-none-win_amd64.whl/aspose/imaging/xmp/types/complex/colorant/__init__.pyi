"""The namespace contains classes that represent the structures containing the characteristics of a colorant (swatch) used in a document."""
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

class ColorantBase(aspose.imaging.xmp.types.complex.ComplexTypeBase):
    '''Represents XMP Colorant type.'''
    
    def get_xmp_representation(self) -> str:
        '''Gets the string contained value in XMP format.
        
        :returns: Returns the string contained value in XMP format.'''
        ...
    
    def clone(self) -> any:
        '''Clones this instance.
        
        :returns: A memberwise clone.'''
        ...
    
    @property
    def prefix(self) -> str:
        '''Gets the prefix.'''
        ...
    
    @property
    def namespace_uri(self) -> str:
        ...
    
    @property
    def mode(self) -> aspose.imaging.xmp.types.complex.colorant.ColorMode:
        '''Gets .'''
        ...
    
    @property
    def swatch_name(self) -> str:
        ...
    
    @swatch_name.setter
    def swatch_name(self, value : str):
        ...
    
    @property
    def color_type(self) -> aspose.imaging.xmp.types.complex.colorant.ColorType:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.imaging.xmp.types.complex.colorant.ColorType):
        ...
    
    ...

class ColorantCmyk(ColorantBase):
    '''Represents CMYK Colorant.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, black: float, cyan: float, magenta: float, yellow: float):
        '''Initializes a new instance of the  class.
        
        :param black: The black component value.
        :param cyan: The cyan color component value.
        :param magenta: The magenta component value.
        :param yellow: The yellow component value.'''
        ...
    
    def get_xmp_representation(self) -> str:
        '''Gets the string contained value in XMP format.
        
        :returns: Returns the string contained value in XMP format.'''
        ...
    
    def clone(self) -> any:
        '''Clones this instance.
        
        :returns: A memberwise clone.'''
        ...
    
    @property
    def prefix(self) -> str:
        '''Gets the prefix.'''
        ...
    
    @property
    def namespace_uri(self) -> str:
        ...
    
    @property
    def mode(self) -> aspose.imaging.xmp.types.complex.colorant.ColorMode:
        '''Gets .'''
        ...
    
    @property
    def swatch_name(self) -> str:
        ...
    
    @swatch_name.setter
    def swatch_name(self, value : str):
        ...
    
    @property
    def color_type(self) -> aspose.imaging.xmp.types.complex.colorant.ColorType:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.imaging.xmp.types.complex.colorant.ColorType):
        ...
    
    @property
    def black(self) -> float:
        '''Gets the black component value.'''
        ...
    
    @black.setter
    def black(self, value : float):
        '''Sets the black component value.'''
        ...
    
    @property
    def cyan(self) -> float:
        '''Gets the cyan component value.'''
        ...
    
    @cyan.setter
    def cyan(self, value : float):
        '''Sets the cyan component value.'''
        ...
    
    @property
    def magenta(self) -> float:
        '''Gets the magenta component value.'''
        ...
    
    @magenta.setter
    def magenta(self, value : float):
        '''Sets the magenta component value.'''
        ...
    
    @property
    def yellow(self) -> float:
        '''Gets the yellow component value.'''
        ...
    
    @yellow.setter
    def yellow(self, value : float):
        '''Sets the yellow component value.'''
        ...
    
    @classmethod
    @property
    def COLOR_VALUE_MAX(cls) -> float:
        ...
    
    @classmethod
    @property
    def COLOR_VALUE_MIN(cls) -> float:
        ...
    
    ...

class ColorantLab(ColorantBase):
    '''Represents LAB Colorant.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, a: int, b: int, l: float):
        '''Initializes a new instance of the  class.
        
        :param a: A component.
        :param b: B component.
        :param l: L component.'''
        ...
    
    def get_xmp_representation(self) -> str:
        '''Gets the string contained value in XMP format.
        
        :returns: Returns the string contained value in XMP format.'''
        ...
    
    def clone(self) -> any:
        '''Clones this instance.
        
        :returns: A memberwise clone.'''
        ...
    
    @property
    def prefix(self) -> str:
        '''Gets the prefix.'''
        ...
    
    @property
    def namespace_uri(self) -> str:
        ...
    
    @property
    def mode(self) -> aspose.imaging.xmp.types.complex.colorant.ColorMode:
        '''Gets .'''
        ...
    
    @property
    def swatch_name(self) -> str:
        ...
    
    @swatch_name.setter
    def swatch_name(self, value : str):
        ...
    
    @property
    def color_type(self) -> aspose.imaging.xmp.types.complex.colorant.ColorType:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.imaging.xmp.types.complex.colorant.ColorType):
        ...
    
    @property
    def a(self) -> int:
        '''Gets the A component.'''
        ...
    
    @a.setter
    def a(self, value : int):
        '''Sets the A component.'''
        ...
    
    @property
    def b(self) -> int:
        '''Gets the B component.'''
        ...
    
    @b.setter
    def b(self, value : int):
        '''Sets the B component.'''
        ...
    
    @property
    def l(self) -> float:
        '''Gets the L component.'''
        ...
    
    @l.setter
    def l(self, value : float):
        '''Sets the L component.'''
        ...
    
    @classmethod
    @property
    def MIN_A(cls) -> int:
        ...
    
    @classmethod
    @property
    def MAX_A(cls) -> int:
        ...
    
    @classmethod
    @property
    def MIN_B(cls) -> int:
        ...
    
    @classmethod
    @property
    def MAX_B(cls) -> int:
        ...
    
    @classmethod
    @property
    def MIN_L(cls) -> float:
        ...
    
    @classmethod
    @property
    def MAX_L(cls) -> float:
        ...
    
    ...

class ColorantRgb(ColorantBase):
    '''Represents RGB Colorant.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, red: int, green: int, blue: int):
        '''Initializes a new instance of the  class.
        
        :param red: The red component value.
        :param green: The green component value.
        :param blue: The blue component value.'''
        ...
    
    def get_xmp_representation(self) -> str:
        '''Gets the string contained value in XMP format.
        
        :returns: Returns the string contained value in XMP format.'''
        ...
    
    def clone(self) -> any:
        '''Clones this instance.
        
        :returns: A memberwise clone.'''
        ...
    
    @property
    def prefix(self) -> str:
        '''Gets the prefix.'''
        ...
    
    @property
    def namespace_uri(self) -> str:
        ...
    
    @property
    def mode(self) -> aspose.imaging.xmp.types.complex.colorant.ColorMode:
        '''Gets .'''
        ...
    
    @property
    def swatch_name(self) -> str:
        ...
    
    @swatch_name.setter
    def swatch_name(self, value : str):
        ...
    
    @property
    def color_type(self) -> aspose.imaging.xmp.types.complex.colorant.ColorType:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.imaging.xmp.types.complex.colorant.ColorType):
        ...
    
    @property
    def red(self) -> int:
        '''Gets the red component value.'''
        ...
    
    @red.setter
    def red(self, value : int):
        '''Sets the red component value.'''
        ...
    
    @property
    def green(self) -> int:
        '''Gets the green component value.'''
        ...
    
    @green.setter
    def green(self, value : int):
        '''Sets the green component value.'''
        ...
    
    @property
    def blue(self) -> int:
        '''Gets the blue component value.'''
        ...
    
    @blue.setter
    def blue(self, value : int):
        '''Sets the blue component value.'''
        ...
    
    ...

class ColorMode(enum.Enum):
    CMYK = enum.auto()
    '''CMYK color mode.'''
    RGB = enum.auto()
    '''RGB color mode.'''
    LAB = enum.auto()
    '''LAB color mode.'''

class ColorType(enum.Enum):
    PROCESS = enum.auto()
    '''Process color type.'''
    SPOT = enum.auto()
    '''Spot color type.'''

