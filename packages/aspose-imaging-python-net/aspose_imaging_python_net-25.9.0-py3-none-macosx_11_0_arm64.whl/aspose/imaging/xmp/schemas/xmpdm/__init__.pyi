"""The namespace contains XMP related helper classes, constants and methods used by the Adobe dynamic media group."""
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

class AudioChannelType:
    '''Represents audio channel type.'''
    
    @classmethod
    @property
    def mono(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioChannelType:
        '''Gets the mono audio channel.'''
        ...
    
    @classmethod
    @property
    def stereo(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioChannelType:
        '''Gets the stereo audio channel.'''
        ...
    
    @classmethod
    @property
    def audio51(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioChannelType:
        '''Gets the 5.1 audio channel.'''
        ...
    
    @classmethod
    @property
    def audio71(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioChannelType:
        '''Gets the 7.1 audio channel.'''
        ...
    
    @classmethod
    @property
    def audio_16_channel(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioChannelType:
        ...
    
    @classmethod
    @property
    def other_channel(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioChannelType:
        ...
    
    ...

class AudioSampleType:
    '''Represents Audio sample type in .'''
    
    @classmethod
    @property
    def sample_8_int(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioSampleType:
        ...
    
    @classmethod
    @property
    def sample_16_int(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioSampleType:
        ...
    
    @classmethod
    @property
    def sample_24_int(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioSampleType:
        ...
    
    @classmethod
    @property
    def sample_32_int(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioSampleType:
        ...
    
    @classmethod
    @property
    def sample_32_float(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioSampleType:
        ...
    
    @classmethod
    @property
    def compressed(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioSampleType:
        '''Represents Compressed audio sample.'''
        ...
    
    @classmethod
    @property
    def packed(cls) -> aspose.imaging.xmp.schemas.xmpdm.AudioSampleType:
        '''Represents Packed audio sample.'''
        ...
    
    ...

class ProjectLink(aspose.imaging.xmp.types.XmpTypeBase):
    '''Represents path of the project.'''
    
    def __init__(self):
        ...
    
    def get_xmp_representation(self) -> str:
        '''Returns string contained value in XMP format.
        
        :returns: Returns string containing xmp representation.'''
        ...
    
    def clone(self) -> any:
        '''Clones this instance.
        
        :returns: A memberwise clone.'''
        ...
    
    @property
    def path(self) -> str:
        '''Gets full path to the project.'''
        ...
    
    @path.setter
    def path(self, value : str):
        '''Sets full path to the project.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.xmp.schemas.xmpdm.ProjectType:
        '''Gets file type.'''
        ...
    
    @type.setter
    def type(self, value : aspose.imaging.xmp.schemas.xmpdm.ProjectType):
        '''Sets file type.'''
        ...
    
    ...

class Time(aspose.imaging.xmp.types.XmpTypeBase):
    '''Representation of a time value in seconds.'''
    
    def __init__(self, scale: aspose.imaging.xmp.types.derived.Rational, value: int):
        '''Initializes a new instance of the  class.
        
        :param scale: The scale.
        :param value: The value.'''
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
    def scale(self) -> aspose.imaging.xmp.types.derived.Rational:
        '''Gets scale for the time value.'''
        ...
    
    @scale.setter
    def scale(self, value : aspose.imaging.xmp.types.derived.Rational):
        '''Sets scale for the time value.'''
        ...
    
    @property
    def value(self) -> int:
        '''Gets time value in the specified scale.'''
        ...
    
    @value.setter
    def value(self, value : int):
        '''Sets time value in the specified scale.'''
        ...
    
    ...

class TimeFormat:
    '''Represents time format in .'''
    
    def equals(self, other: aspose.imaging.xmp.schemas.xmpdm.TimeFormat) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    @classmethod
    @property
    def timecode24(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        '''Gets the timecode24.'''
        ...
    
    @classmethod
    @property
    def timecode25(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        '''Gets the timecode25.'''
        ...
    
    @classmethod
    @property
    def drop_timecode2997(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        ...
    
    @classmethod
    @property
    def non_drop_timecode2997(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        ...
    
    @classmethod
    @property
    def timecode30(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        '''Gets the timecode30.'''
        ...
    
    @classmethod
    @property
    def timecode50(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        '''Gets the timecode50.'''
        ...
    
    @classmethod
    @property
    def drop_timecode5994(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        ...
    
    @classmethod
    @property
    def non_drop_timecode5994(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        ...
    
    @classmethod
    @property
    def timecode60(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        '''Gets the timecode60.'''
        ...
    
    @classmethod
    @property
    def timecode23976(cls) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        '''Gets the timecode23976.'''
        ...
    
    ...

class Timecode(aspose.imaging.xmp.types.XmpTypeBase):
    '''Represents timecode value in video.'''
    
    def __init__(self, format: aspose.imaging.xmp.schemas.xmpdm.TimeFormat, time_value: str):
        '''Initializes a new instance of the  class.
        
        :param format: The time format.
        :param time_value: The time value.'''
        ...
    
    def get_xmp_representation(self) -> str:
        '''Returns the string contained value in XMP format.
        
        :returns: Returns the string containing xmp representation.'''
        ...
    
    def clone(self) -> any:
        '''Clones this instance.
        
        :returns: A memberwise clone.'''
        ...
    
    def equals(self, other: aspose.imaging.xmp.schemas.xmpdm.Timecode) -> bool:
        '''Indicates whether the current object is equal to another object of the same type.
        
        :param other: An object to compare with this object.
        :returns: true if the current object is equal to the ``other`` parameter; otherwise, false.'''
        ...
    
    @property
    def format(self) -> aspose.imaging.xmp.schemas.xmpdm.TimeFormat:
        '''Gets the format used in the .'''
        ...
    
    @format.setter
    def format(self, value : aspose.imaging.xmp.schemas.xmpdm.TimeFormat):
        '''Sets the format used in the .'''
        ...
    
    @property
    def time_value(self) -> str:
        ...
    
    @time_value.setter
    def time_value(self, value : str):
        ...
    
    ...

class XmpDynamicMediaPackage(aspose.imaging.xmp.XmpPackage):
    '''Represents XMP Dynamic Media namespace.'''
    
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
    
    def set_abs_peak_audio_file_path(self, uri: str):
        '''Sets the absolute peak audio file path.
        
        :param uri: The absolute path to the file’s peak audio file.'''
        ...
    
    def set_alblum(self, album: str):
        '''Sets the alblum.
        
        :param album: The album.'''
        ...
    
    def set_alt_tape_name(self, alt_tape_name: str):
        '''Sets the alternative tape name.
        
        :param alt_tape_name: Alternative tape name.'''
        ...
    
    def set_alt_time_code(self, timecode: aspose.imaging.xmp.schemas.xmpdm.Timecode):
        '''Sets the alternative time code.
        
        :param timecode: Time code.'''
        ...
    
    def set_artist(self, artist: str):
        '''Sets the artist.
        
        :param artist: The artist.'''
        ...
    
    def set_audio_channel_type(self, audio_channel_type: aspose.imaging.xmp.schemas.xmpdm.AudioChannelType):
        '''Sets the audio channel type.
        
        :param audio_channel_type: Audio channel type.'''
        ...
    
    def set_audio_sample_rate(self, rate: int):
        '''Sets the audio sample rate.
        
        :param rate: The audio sample rate.'''
        ...
    
    def set_audio_sample_type(self, audio_sample_type: aspose.imaging.xmp.schemas.xmpdm.AudioSampleType):
        '''Sets the audio sample type.
        
        :param audio_sample_type: The audio sample type.'''
        ...
    
    def set_camera_angle(self, camera_angle: str):
        '''Sets the camera angle.
        
        :param camera_angle: The camera angle.'''
        ...
    
    def set_camera_label(self, camera_label: str):
        '''Sets the camera label.
        
        :param camera_label: The camera label.'''
        ...
    
    def set_camera_move(self, camera_move: str):
        '''Sets the camera move.
        
        :param camera_move: The camera move.'''
        ...
    
    def set_client(self, client: str):
        '''Sets the client.
        
        :param client: The client.'''
        ...
    
    def set_comment(self, comment: str):
        '''Sets the comment.
        
        :param comment: The comment.'''
        ...
    
    def set_composer(self, composer: str):
        '''Sets the composer.
        
        :param composer: The composer.'''
        ...
    
    def set_director(self, director: str):
        '''Sets the director.
        
        :param director: The director.'''
        ...
    
    def set_director_photography(self, director_photography: str):
        '''Sets the director of photography.
        
        :param director_photography: The director of photography.'''
        ...
    
    def set_duration(self, duration: aspose.imaging.xmp.schemas.xmpdm.Time):
        '''Sets the duration.
        
        :param duration: The duration.'''
        ...
    
    def set_engineer(self, engineer: str):
        '''Sets the engineer.
        
        :param engineer: The engineer.'''
        ...
    
    def set_file_data_rate(self, rate: aspose.imaging.xmp.types.derived.Rational):
        '''Sets the file data rate.
        
        :param rate: The file data rate in megabytes per second.'''
        ...
    
    def set_genre(self, genre: str):
        '''Sets the genre.
        
        :param genre: The genre.'''
        ...
    
    def set_good(self, good: bool):
        '''Sets the good.
        
        :param good: if set to ``true`` a shot is a keeper.'''
        ...
    
    def set_instrument(self, instrument: str):
        '''Sets the instrument.
        
        :param instrument: The instrument.'''
        ...
    
    def set_intro_time(self, intro_time: aspose.imaging.xmp.schemas.xmpdm.Time):
        '''Sets the intro time.
        
        :param intro_time: The intro time.'''
        ...
    
    def set_key(self, key: str):
        '''Sets the audio’s musical key.
        
        :param key: The audio’s musical key. One of: C, C#, D, D#, E, F, F#, G, G#, A, A#, and B.'''
        ...
    
    def set_log_comment(self, comment: str):
        '''Sets the user's log comment.
        
        :param comment: The comment.'''
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

class ProjectType(enum.Enum):
    MOVIE = enum.auto()
    '''The movie project type'''
    STILL = enum.auto()
    '''The still project type'''
    AUDIO = enum.auto()
    '''The audio project type'''
    CUSTOM = enum.auto()
    '''The custom project type'''

