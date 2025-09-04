"""The namespace contains XMP related helper classes and methods."""
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

class IHasXmpData:
    '''instance container interface.'''
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    ...

class IXmlValue:
    '''Converts xmp values to the XML string representation.'''
    
    def get_xml_value(self) -> str:
        '''Converts XMP value to the XML representation.
        
        :returns: Returns the XMP value converted to the XML representation.'''
        ...
    
    ...

class LangAlt(IXmlValue):
    '''Represents XMP Language Alternative.'''
    
    @overload
    def __init__(self, default_value: str):
        '''Initializes a new instance of the  class.
        
        :param default_value: The default value.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def add_language(self, language: str, value: str):
        '''Adds the language.
        
        :param language: The language.
        :param value: The language value.'''
        ...
    
    def get_xml_value(self) -> str:
        '''Converts XMP value to the XML representation.
        
        :returns: Returns the XMP value converted to the XML representation.'''
        ...
    
    ...

class Namespaces:
    '''Contains namespaces used in RDF document.'''
    
    @classmethod
    @property
    def XMP_GRAPHICS(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_GRAPHICS_THUMBNAIL(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_TYPE_FONT(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_TYPE_DIMENSIONS(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_TYPE_RESOURCE_REF(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_TYPE_RESOURCE_EVENT(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_TYPE_VERSION(cls) -> str:
        ...
    
    @classmethod
    @property
    def XML(cls) -> str:
        '''Xml namespace.'''
        ...
    
    @classmethod
    @property
    def RDF(cls) -> str:
        '''Resource definition framework namespace.'''
        ...
    
    @classmethod
    @property
    def DUBLIN_CORE(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_BASIC(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_RIGHTS(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_MM(cls) -> str:
        ...
    
    @classmethod
    @property
    def XMP_DM(cls) -> str:
        ...
    
    @classmethod
    @property
    def PDF(cls) -> str:
        '''Adobe PDF namespace.'''
        ...
    
    @classmethod
    @property
    def PHOTOSHOP(cls) -> str:
        '''Adobe Photoshop namespace.'''
        ...
    
    @classmethod
    @property
    def DICOM(cls) -> str:
        '''Dicom namespace.'''
        ...
    
    ...

class XmpArray(XmpCollection):
    '''Represents Xmp Array in .'''
    
    def __init__(self, type: aspose.imaging.xmp.XmpArrayType, items: List[str]):
        '''Initializes a new instance of the  class.
        
        :param type: The type of array.
        :param items: The items list.'''
        ...
    
    def add_item(self, item: str):
        '''Adds new item.
        
        :param item: The item to be added to list of items.'''
        ...
    
    def add(self, item: any):
        '''Adds an XMP data item.
        
        :param item: An XMP item.'''
        ...
    
    def get_xmp_representation(self) -> str:
        '''Gets the XMP string value of this.
        
        :returns: Returns the string contained value in XMP format.'''
        ...
    
    def get_xml_value(self) -> str:
        '''Converts XMP value to the XML representation.
        
        :returns: Returns the XMP value converted to the XML representation.'''
        ...
    
    @property
    def values(self) -> List[str]:
        '''Gets array of values inside .'''
        ...
    
    ...

class XmpArrayHelper:
    '''The helper class for processing RDF logic'''
    
    @staticmethod
    def get_rdf_code(xmp_array_type: aspose.imaging.xmp.XmpArrayType) -> str:
        '''Gets the RDF code for specific .
        
        :param xmp_array_type: Type of the XMP array.
        :returns: Returns the RDF code for specific .'''
        ...
    
    ...

class XmpCollection(aspose.imaging.xmp.types.IXmpType):
    '''An XMP element collection.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def add_item(self, item: str):
        '''Adds new item.
        
        :param item: The item to be added to list of items.'''
        ...
    
    def add(self, item: any):
        '''Adds an XMP data item.
        
        :param item: An XMP item.'''
        ...
    
    def get_xmp_representation(self) -> str:
        '''Gets the XMP string value of this.
        
        :returns: Returns the string contained value in XMP format.'''
        ...
    
    def get_xml_value(self) -> str:
        '''Converts XMP value to the XML representation.
        
        :returns: Returns the XMP value converted to the XML representation.'''
        ...
    
    ...

class XmpElementBase:
    '''Represents base xmp element contains attributes.'''
    
    def add_attribute(self, attribute: str, value: str):
        '''Adds the attribute.
        
        :param attribute: The attribute.
        :param value: The value.'''
        ...
    
    def get_attribute(self, attribute: str) -> str:
        '''Gets the attribute.
        
        :param attribute: The attribute.
        :returns: Returns the attribute for specified attribute name.'''
        ...
    
    def clear_attributes(self):
        '''Removes all attributes.'''
        ...
    
    def equals(self, other: aspose.imaging.xmp.XmpElementBase) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    ...

class XmpHeaderPi(IXmlValue):
    '''Represents XMP header processing instruction.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, guid: str):
        '''Initializes a new instance of the  class.
        
        :param guid: The unique identifier.'''
        ...
    
    def get_xml_value(self) -> str:
        '''Converts XMP value to the XML representation.
        
        :returns: Returns the XMP value converted to the XML representation.'''
        ...
    
    def equals(self, other: aspose.imaging.xmp.XmpHeaderPi) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    @property
    def guid(self) -> str:
        '''Represents Header Guid.'''
        ...
    
    @guid.setter
    def guid(self, value : str):
        '''Represents Header Guid.'''
        ...
    
    ...

class XmpMeta(XmpElementBase):
    '''Represents xmpmeta. Optional.
    The purpose of this element is to identify XMP metadata within general XML text that might contain other non-XMP uses of RDF.'''
    
    @overload
    def __init__(self, toolkit_version: str):
        '''Initializes a new instance of the  class.
        
        :param toolkit_version: Adobe XMP toolkit version.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def equals(self, other: aspose.imaging.xmp.XmpMeta) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    @overload
    def equals(self, other: aspose.imaging.xmp.XmpElementBase) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    def add_attribute(self, attribute: str, value: str):
        '''Adds the attribute.
        
        :param attribute: The attribute.
        :param value: The value.'''
        ...
    
    def get_attribute(self, attribute: str) -> str:
        '''Gets the attribute.
        
        :param attribute: The attribute.
        :returns: Returns the attribute for specified attribute name.'''
        ...
    
    def clear_attributes(self):
        '''Removes all attributes.'''
        ...
    
    def get_xml_value(self) -> str:
        '''Converts XMP value to the XML representation.
        
        :returns: Returns the XMP value converted to the XML representation.'''
        ...
    
    @property
    def adobe_xmp_toolkit(self) -> str:
        ...
    
    @adobe_xmp_toolkit.setter
    def adobe_xmp_toolkit(self, value : str):
        ...
    
    ...

class XmpPackage(IXmlValue):
    '''Represents base abstraction for XMP package.'''
    
    @overload
    def add_value(self, key: str, value: str):
        '''Adds the value to the specified key.
        
        :param key: The string representation of key that is identified with added value.
        :param value: The value to add to.'''
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

class XmpPackageBaseCollection:
    '''Represents collection of .'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def add(self, package: aspose.imaging.xmp.XmpPackage):
        '''Adds new instance of .
        
        :param package: The XMP package to add.'''
        ...
    
    def remove(self, package: aspose.imaging.xmp.XmpPackage):
        '''Removes the specified XMP package.
        
        :param package: The XMP package to remove.'''
        ...
    
    def get_packages(self) -> List[aspose.imaging.xmp.XmpPackage]:
        '''Get array of .
        
        :returns: Returns an array of XMP packages.'''
        ...
    
    def get_package(self, namespace_uri: str) -> aspose.imaging.xmp.XmpPackage:
        '''Gets  by it's namespaceURI.
        
        :param namespace_uri: The namespace URI to get package for.
        :returns: Returns XMP package for specified namespace Uri.'''
        ...
    
    def clear(self):
        '''Clear all  inside collection.'''
        ...
    
    @property
    def count(self) -> int:
        '''Gets the number of elements in the collection.'''
        ...
    
    ...

class XmpPacketWrapper(IXmlValue):
    '''Contains serialized xmp package including header and trailer.'''
    
    @overload
    def __init__(self, header: aspose.imaging.xmp.XmpHeaderPi, trailer: aspose.imaging.xmp.XmpTrailerPi, xmp_meta: aspose.imaging.xmp.XmpMeta):
        '''Initializes a new instance of the  class.
        
        :param header: The XMP header of processing instruction.
        :param trailer: The XMP trailer of processing instruction.
        :param xmp_meta: The XMP metadata.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def add_package(self, package: aspose.imaging.xmp.XmpPackage):
        '''Adds the package.
        
        :param package: The package.'''
        ...
    
    def get_package(self, namespace_uri: str) -> aspose.imaging.xmp.XmpPackage:
        '''Gets package by namespace URI.
        
        :param namespace_uri: The package schema URI.
        :returns: Returns the XMP package for specified namespace URI.'''
        ...
    
    def contains_package(self, namespace_uri: str) -> bool:
        '''Determines whethere package is exist in xmp wrapper.
        
        :param namespace_uri: Package schema uri.
        :returns: Returns true if package with specified namespace Uri exist in XMP wrapper.'''
        ...
    
    def remove_package(self, package: aspose.imaging.xmp.XmpPackage):
        '''Removes the XMP package.
        
        :param package: The package.'''
        ...
    
    def clear_packages(self):
        '''Removes all  inside XMP.'''
        ...
    
    def get_xml_value(self) -> str:
        '''Converts XMP value to the XML representation.
        
        :returns: Returns converted XMP value to XML.'''
        ...
    
    @property
    def header_pi(self) -> aspose.imaging.xmp.XmpHeaderPi:
        ...
    
    @property
    def meta(self) -> aspose.imaging.xmp.XmpMeta:
        '''Gets the XMP meta. Optional.'''
        ...
    
    @meta.setter
    def meta(self, value : aspose.imaging.xmp.XmpMeta):
        '''Gets the XMP meta. Optional.'''
        ...
    
    @property
    def trailer_pi(self) -> aspose.imaging.xmp.XmpTrailerPi:
        ...
    
    @property
    def packages(self) -> List[aspose.imaging.xmp.XmpPackage]:
        '''Gets array of  inside XMP.'''
        ...
    
    @property
    def packages_count(self) -> int:
        ...
    
    ...

class XmpRdfRoot(XmpElementBase):
    '''Represents rdf:RDF element.
    A single XMP packet shall be serialized using a single rdf:RDF XML element. The rdf:RDF element content shall consist of only zero or more rdf:Description elements.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def add_attribute(self, attribute: str, value: str):
        '''Adds the attribute.
        
        :param attribute: The attribute.
        :param value: The value.'''
        ...
    
    def get_attribute(self, attribute: str) -> str:
        '''Gets the attribute.
        
        :param attribute: The attribute.
        :returns: Returns the attribute for specified attribute name.'''
        ...
    
    def clear_attributes(self):
        '''Removes all attributes.'''
        ...
    
    def equals(self, other: aspose.imaging.xmp.XmpElementBase) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    def register_namespace_uri(self, prefix: str, namespace_uri: str):
        '''Adds namespace uri by prefix. Prefix may start without xmlns.
        
        :param prefix: The prefix.
        :param namespace_uri: Package schema uri.'''
        ...
    
    def get_namespace_uri(self, prefix: str) -> str:
        '''Gets namespace URI by specific prefix. Prefix may start without xmlns.
        
        :param prefix: The prefix.
        :returns: Returns a package schema URI.'''
        ...
    
    def get_xml_value(self) -> str:
        '''Converts xmp value to the xml representation.
        
        :returns: Returns XMP value converted to XML string.'''
        ...
    
    ...

class XmpTrailerPi(IXmlValue):
    '''Represents XMP trailer processing instruction.'''
    
    @overload
    def __init__(self, is_writable: bool):
        '''Initializes a new instance of the  class.
        
        :param is_writable: Inditacates whether trailer is writable.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def get_xml_value(self) -> str:
        '''Converts xmp value to the xml representation.
        
        :returns: Returns XML representation of XMP.'''
        ...
    
    def equals(self, other: aspose.imaging.xmp.XmpTrailerPi) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    @property
    def is_writable(self) -> bool:
        ...
    
    @is_writable.setter
    def is_writable(self, value : bool):
        ...
    
    ...

class XmpArrayType(enum.Enum):
    UNORDERED = enum.auto()
    '''The unordered array.'''
    ORDERED = enum.auto()
    '''The ordered array.'''
    ALTERNATIVE = enum.auto()
    '''The alternative array.'''

