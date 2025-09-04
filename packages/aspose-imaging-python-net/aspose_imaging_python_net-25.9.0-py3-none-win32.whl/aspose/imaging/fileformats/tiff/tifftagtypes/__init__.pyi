"""The namespace contains Tiff file format tag classes."""
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

class TiffASCIIType(aspose.imaging.fileformats.tiff.TiffDataType):
    '''The tiff ascii type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffASCIIType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffASCIIType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def text(self) -> str:
        '''Gets the text.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the text.'''
        ...
    
    ...

class TiffByteType(TiffCommonArrayType):
    '''The tiff byte type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffByteType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffByteType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> bytes:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : bytes):
        '''Sets the values.'''
        ...
    
    ...

class TiffCommonArrayType(aspose.imaging.fileformats.tiff.TiffDataType):
    '''The tiff common array type.'''
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    ...

class TiffDoubleType(TiffCommonArrayType):
    '''The tiff double type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffDoubleType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffDoubleType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[float]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[float]):
        '''Sets the values.'''
        ...
    
    ...

class TiffFloatType(TiffCommonArrayType):
    '''The tiff float type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffFloatType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffFloatType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[float]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[float]):
        '''Sets the values.'''
        ...
    
    ...

class TiffIfd8Type(TiffLong8Type):
    '''The Tiff unsigned 64-bit Image File Directory type.'''
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffIfd8Type:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffIfd8Type:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets the values.'''
        ...
    
    ...

class TiffIfdType(TiffCommonArrayType):
    '''Represents the TIFF Exif image file directory type class.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffIfdType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffIfdType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets the values.'''
        ...
    
    ...

class TiffLong8Type(TiffCommonArrayType):
    '''The Tiff unsigned 64-bit type.'''
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffLong8Type:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffLong8Type:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets the values.'''
        ...
    
    ...

class TiffLongType(TiffCommonArrayType):
    '''The tiff long type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffLongType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffLongType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets the values.'''
        ...
    
    ...

class TiffRationalType(TiffCommonArrayType):
    '''The tiff rational type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffRationalType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffRationalType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[aspose.imaging.fileformats.tiff.TiffRational]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[aspose.imaging.fileformats.tiff.TiffRational]):
        '''Sets the values.'''
        ...
    
    ...

class TiffSByteType(TiffCommonArrayType):
    '''The tiff signed byte type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSByteType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSByteType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets the values.'''
        ...
    
    ...

class TiffSLong8Type(TiffCommonArrayType):
    '''The Tiff unsigned 64-bit type.'''
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSLong8Type:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSLong8Type:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets the values.'''
        ...
    
    ...

class TiffSLongType(TiffCommonArrayType):
    '''The tiff signed long type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSLongType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSLongType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets the values.'''
        ...
    
    ...

class TiffSRationalType(TiffCommonArrayType):
    '''The tiff signed rational type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSRationalType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSRationalType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[aspose.imaging.fileformats.tiff.TiffSRational]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[aspose.imaging.fileformats.tiff.TiffSRational]):
        '''Sets the values.'''
        ...
    
    ...

class TiffSShortType(TiffCommonArrayType):
    '''The tiff signed short type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSShortType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffSShortType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets the values.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets the values.'''
        ...
    
    ...

class TiffShortType(TiffCommonArrayType):
    '''The tiff short type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffShortType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffShortType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def values_container(self) -> System.Array:
        ...
    
    @property
    def values(self) -> List[int]:
        '''Gets the data.'''
        ...
    
    @values.setter
    def values(self, value : List[int]):
        '''Sets the data.'''
        ...
    
    ...

class TiffUndefinedType(aspose.imaging.fileformats.tiff.TiffDataType):
    '''The tiff undefined type.'''
    
    @overload
    def __init__(self, tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @overload
    def __init__(self, tag_id: int):
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @staticmethod
    def create_with_tag(tag_id: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffUndefinedType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @staticmethod
    def create_with_tag_id(tag_id: int) -> aspose.imaging.fileformats.tiff.tifftagtypes.TiffUndefinedType:
        '''Initializes a new instance of the  class.
        
        :param tag_id: The tag id.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def data(self) -> bytes:
        '''Gets the data.'''
        ...
    
    @data.setter
    def data(self, value : bytes):
        '''Sets the data.'''
        ...
    
    ...

class TiffUnknownType(aspose.imaging.fileformats.tiff.TiffDataType):
    '''The unknown tiff type. In case the tiff tag cannot be recognized this type is instantinated.'''
    
    def __init__(self, stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, tag_type: int, tag_id: int, count: int, offset_or_value: int):
        '''Initializes a new instance of the  class.
        
        :param stream: The stream to read from.
        :param tag_type: Type of the tag.
        :param tag_id: The tag id.
        :param count: The count value.
        :param offset_or_value: The offset or value.'''
        ...
    
    @staticmethod
    def read_tag(data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader, position: int) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Reads the tag data.
        
        :param data_stream: The data stream.
        :param position: The tag position.
        :returns: The read tag.'''
        ...
    
    def compare_to(self, obj: any) -> int:
        '''Compares the current instance with another object of the same type and returns an integer that indicates whether the current instance precedes, follows, or occurs in the same position in the sort order as the other object.
        
        :param obj: An object to compare with this instance.
        :returns: A 32-bit signed integer that indicates the relative order of the objects being compared. The return value has these meanings:
        Value
        Meaning
        Less than zero
        This instance is less than ``obj``.
        Zero
        This instance is equal to ``obj``.
        Greater than zero
        This instance is greater than ``obj``.'''
        ...
    
    def get_aligned_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the data size aligned in 4-byte (int) or 8-byte (long) boundary.
        
        :param size_of_tag_value: Size of tag value.
        :returns: The aligned data size in bytes.'''
        ...
    
    def get_additional_data_size(self, size_of_tag_value: int) -> int:
        '''Gets the additional tag value size in bytes (in case the tag can not fit the whole tag value).
        
        :param size_of_tag_value: Size of tag value: 4 or 8 for BigTiff.
        :returns: The additional data size in bytes.'''
        ...
    
    def deep_clone(self) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Performs a deep clone of this instance.
        
        :returns: A deep clone of the current instance.'''
        ...
    
    def write_tag(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter, additional_data_offset: int):
        '''Writes the tag data.
        
        :param data_stream: The data stream.
        :param additional_data_offset: The offset to write additional data to.'''
        ...
    
    def write_additional_data(self, data_stream: aspose.imaging.fileformats.tiff.filemanagement.TiffStreamWriter) -> int:
        '''Writes the additional tag data.
        
        :param data_stream: The data stream.
        :returns: The actual bytes written.'''
        ...
    
    @property
    def element_size(self) -> int:
        ...
    
    @property
    def data_size(self) -> int:
        ...
    
    @property
    def count(self) -> int:
        '''Gets the count of elements.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets tag id as number.'''
        ...
    
    @property
    def tag_id(self) -> aspose.imaging.fileformats.tiff.enums.TiffTags:
        ...
    
    @property
    def tag_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffDataTypes:
        ...
    
    @property
    def value(self) -> any:
        '''Gets the value this data type contains.'''
        ...
    
    @value.setter
    def value(self, value : any):
        '''Sets the value this data type contains.'''
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def offset_or_value(self) -> int:
        ...
    
    @property
    def stream(self) -> aspose.imaging.fileformats.tiff.filemanagement.TiffStreamReader:
        '''Gets the stream to read additional data from.'''
        ...
    
    ...

