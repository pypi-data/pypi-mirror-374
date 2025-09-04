"""The namespace contains related helper classes, constants and methods used by Adobe Photoshop."""
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

class Layer(aspose.imaging.xmp.types.XmpTypeBase):
    '''Represents Photoshop text layer.'''
    
    @overload
    def __init__(self, layer_name: str, layer_text: str):
        '''Initializes a new instance of the  class.
        
        :param layer_name: Name of the layer.
        :param layer_text: The layer text.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def get_xmp_representation(self) -> str:
        '''Returns string contained value in XMP format.
        
        :returns: Returns string containing xmp representation.'''
        ...
    
    def clone(self) -> any:
        '''Clones this instance.
        
        :returns: A memberwise clone.'''
        ...
    
    def equals(self, other: aspose.imaging.xmp.schemas.photoshop.Layer) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name of the text layer.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name of the text layer.'''
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text content of the layer.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text content of the layer.'''
        ...
    
    ...

class PhotoshopPackage(aspose.imaging.xmp.XmpPackage):
    '''Represents Adobe Photoshop namespace.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def add_value(self, key: str, value: str):
        '''Adds string property.
        
        :param key: The string representation of key that is identified with added value.
        :param value: The string value.'''
        ...
    
    @overload
    def add_value(self, key: str, value: any):
        '''Adds the value to the specified key.
        
        :param key: The string representation of key that is identified with added value.
        :param value: The value to add to.'''
        ...
    
    @overload
    def set_value(self, key: str, value: aspose.imaging.xmp.IXmlValue):
        '''Sets the value.
        
        :param key: The string representation of key that is identified with added value.
        :param value: The value to add to.'''
        ...
    
    @overload
    def set_value(self, key: str, value: aspose.imaging.xmp.types.IXmpType):
        '''Sets the value.
        
        :param key: The string representation of key that is identified with added value.
        :param value: The value to add to.'''
        ...
    
    def contains_key(self, key: str) -> bool:
        '''Determines whether this collection specified key.
        
        :param key: The key to be checked.
        :returns: if the  contains the specified key; otherwise, .'''
        ...
    
    def get_prop_value(self, key: str) -> any:
        '''Gets the  with the specified key.
        
        :param key: The key that identifies value.
        :returns: Returns the  with the specified key.'''
        ...
    
    def set_prop_value(self, key: str, value: any):
        '''Gets or sets the  with the specified key.
        
        :param key: The key that identifies value.
        :param value: The  with the specified key.'''
        ...
    
    def try_get_value(self, key: str, value: Any) -> bool:
        '''Gets the value by the ``key``.
        
        :param key: The XMP element key.
        :param value: The XMP value.
        :returns: , if the  contains the ``key``; otherwise, .'''
        ...
    
    def remove(self, key: str) -> bool:
        '''Remove the value with the specified key.
        
        :param key: The string representation of key that is identified with removed value.
        :returns: Returns true if the value with the specified key was removed.'''
        ...
    
    def clear(self):
        '''Clears this instance.'''
        ...
    
    def set_xmp_type_value(self, key: str, value: aspose.imaging.xmp.types.XmpTypeBase):
        '''Sets the XMP type value.
        
        :param key: The string representation of key that is identified with set value.
        :param value: The value to set to.'''
        ...
    
    def get_xml_value(self) -> str:
        '''Converts XMP value to the XML representation.
        
        :returns: Returns the XMP value converted to the XML representation.'''
        ...
    
    def set_authors_position(self, authors_position: str):
        '''Sets the authors position.
        
        :param authors_position: The authors position.'''
        ...
    
    def set_caption_writer(self, caption_writer: str):
        '''Sets the caption writer.
        
        :param caption_writer: The caption writer.'''
        ...
    
    def set_category(self, category: str):
        '''Sets the category.
        
        :param category: The category.'''
        ...
    
    def set_city(self, city: str):
        '''Sets the city.
        
        :param city: The city name.'''
        ...
    
    def set_color_mode(self, color_mode: aspose.imaging.xmp.schemas.photoshop.ColorMode):
        '''Sets the color mode.
        
        :param color_mode: The color mode.'''
        ...
    
    def set_country(self, country: str):
        '''Sets the country.
        
        :param country: The country.'''
        ...
    
    def set_credit(self, credit: str):
        '''Sets the credit.
        
        :param credit: The credit.'''
        ...
    
    def set_created_date(self, created_date: System.DateTime):
        '''Sets created date.
        
        :param created_date: The created date.'''
        ...
    
    def set_document_ancestors(self, ancestors: List[str]):
        '''Sets the document ancestors.
        
        :param ancestors: The ancestors.'''
        ...
    
    def set_headline(self, headline: str):
        '''Sets the headline.
        
        :param headline: The headline.'''
        ...
    
    def set_history(self, history: str):
        '''Sets the history.
        
        :param history: The history.'''
        ...
    
    def set_icc_profile(self, icc_profile: str):
        '''Sets the icc profile.
        
        :param icc_profile: The icc profile.'''
        ...
    
    def set_instructions(self, instructions: str):
        '''Sets the instructions.
        
        :param instructions: The instructions.'''
        ...
    
    def set_source(self, source: str):
        '''Sets the source.
        
        :param source: The source.'''
        ...
    
    def set_state(self, state: str):
        '''Sets the state.
        
        :param state: The state.'''
        ...
    
    def set_supplemental_categories(self, supplemental_categories: List[str]):
        '''Sets supplemental categories.
        
        :param supplemental_categories: The supplemental categories.'''
        ...
    
    def set_transmission_reference(self, transmission_reference: str):
        '''Sets the transmission reference.
        
        :param transmission_reference: The transmission reference.'''
        ...
    
    def set_urgency(self, urgency: int):
        '''Sets the urgency.
        
        :param urgency: The urgency.'''
        ...
    
    @property
    def xml_namespace(self) -> str:
        ...
    
    @property
    def prefix(self) -> str:
        '''Gets the prefix.'''
        ...
    
    @property
    def namespace_uri(self) -> str:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the XMP key count.'''
        ...
    
    @classmethod
    @property
    def URGENCY_MAX(cls) -> int:
        ...
    
    @classmethod
    @property
    def URGENCY_MIN(cls) -> int:
        ...
    
    ...

class ColorMode(enum.Enum):
    BITMAP = enum.auto()
    '''Bitmap color mode.'''
    GRAY_SCALE = enum.auto()
    '''Gray scale color mode.'''
    INDEXED_COLOR = enum.auto()
    '''The indexed color.'''
    RGB = enum.auto()
    '''RGB color.'''
    CMYK = enum.auto()
    '''CMYK color mode.'''
    MULTI_CHANNEL = enum.auto()
    '''Multi-channel color.'''
    DUOTONE = enum.auto()
    '''Duo-tone color.'''
    LAB_COLOR = enum.auto()
    '''LAB color.'''

