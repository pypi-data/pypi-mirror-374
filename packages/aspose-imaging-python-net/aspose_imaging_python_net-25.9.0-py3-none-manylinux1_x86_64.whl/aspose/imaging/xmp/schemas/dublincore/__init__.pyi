"""The namespace contains Dublin Core metadata related helper classes, constants and methods."""
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

class DublinCorePackage(aspose.imaging.xmp.XmpPackage):
    '''Represents Dublic Core schema.'''
    
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
    
    @overload
    def set_title(self, title: str):
        '''Adds Dublin Core title.
        
        :param title: The title.'''
        ...
    
    @overload
    def set_title(self, title: aspose.imaging.xmp.LangAlt):
        '''Adds Dublin Core title for different languages.
        
        :param title: Instance of .'''
        ...
    
    @overload
    def set_description(self, desc: str):
        '''Adds the description.
        
        :param desc: The description.'''
        ...
    
    @overload
    def set_description(self, desc: aspose.imaging.xmp.LangAlt):
        '''Adds the description.
        
        :param desc: The description.'''
        ...
    
    @overload
    def set_subject(self, subject: str):
        '''Adds the subject.
        
        :param subject: The subject.'''
        ...
    
    @overload
    def set_subject(self, subject: List[str]):
        '''Adds the subject.
        
        :param subject: The subject.'''
        ...
    
    @overload
    def set_author(self, author: str):
        '''Adds the author.
        
        :param author: The author.'''
        ...
    
    @overload
    def set_author(self, author: List[str]):
        '''Adds the author.
        
        :param author: The author.'''
        ...
    
    @overload
    def set_publisher(self, publisher: str):
        '''Adds the publisher.
        
        :param publisher: The publisher.'''
        ...
    
    @overload
    def set_publisher(self, publisher: List[str]):
        '''Adds the publisher.
        
        :param publisher: The publisher.'''
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
    
    def set_title_str(self, title: str):
        '''Adds Dublin Core title.
        
        :param title: The title.'''
        ...
    
    def set_title_lang_alt(self, title: aspose.imaging.xmp.LangAlt):
        '''Adds Dublin Core title for different languages.
        
        :param title: Instance of .'''
        ...
    
    def set_description_str(self, desc: str):
        '''Adds the description.
        
        :param desc: The description.'''
        ...
    
    def set_description_lang_alt(self, desc: aspose.imaging.xmp.LangAlt):
        '''Adds the description.
        
        :param desc: The description.'''
        ...
    
    def set_subject_array(self, subject: List[str]):
        '''Adds the subject.
        
        :param subject: The subject.'''
        ...
    
    def set_author_array(self, author: List[str]):
        '''Adds the author.
        
        :param author: The author.'''
        ...
    
    def set_publisher_array(self, publisher: List[str]):
        '''Adds the publisher.
        
        :param publisher: The publisher.'''
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
    
    ...

