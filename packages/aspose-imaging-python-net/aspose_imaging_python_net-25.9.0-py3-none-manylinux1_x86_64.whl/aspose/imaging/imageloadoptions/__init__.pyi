"""The namespace contains different file format load options."""
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

class CdrLoadOptions(aspose.imaging.LoadOptions):
    '''The Cdr load options'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def data_recovery_mode(self) -> aspose.imaging.DataRecoveryMode:
        ...
    
    @data_recovery_mode.setter
    def data_recovery_mode(self, value : aspose.imaging.DataRecoveryMode):
        ...
    
    @property
    def data_background_color(self) -> aspose.imaging.Color:
        ...
    
    @data_background_color.setter
    def data_background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def use_icc_profile_conversion(self) -> bool:
        ...
    
    @use_icc_profile_conversion.setter
    def use_icc_profile_conversion(self, value : bool):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def concurrent_image_processing(self) -> bool:
        ...
    
    @concurrent_image_processing.setter
    def concurrent_image_processing(self, value : bool):
        ...
    
    @property
    def default_font(self) -> aspose.imaging.Font:
        ...
    
    @default_font.setter
    def default_font(self, value : aspose.imaging.Font):
        ...
    
    @property
    def optimal_memory_usage(self) -> bool:
        ...
    
    @optimal_memory_usage.setter
    def optimal_memory_usage(self, value : bool):
        ...
    
    ...

class CmxLoadOptions(aspose.imaging.LoadOptions):
    '''The CMX load options'''
    
    def __init__(self):
        '''Initializes a new instance of the .'''
        ...
    
    @property
    def data_recovery_mode(self) -> aspose.imaging.DataRecoveryMode:
        ...
    
    @data_recovery_mode.setter
    def data_recovery_mode(self, value : aspose.imaging.DataRecoveryMode):
        ...
    
    @property
    def data_background_color(self) -> aspose.imaging.Color:
        ...
    
    @data_background_color.setter
    def data_background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def use_icc_profile_conversion(self) -> bool:
        ...
    
    @use_icc_profile_conversion.setter
    def use_icc_profile_conversion(self, value : bool):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def concurrent_image_processing(self) -> bool:
        ...
    
    @concurrent_image_processing.setter
    def concurrent_image_processing(self, value : bool):
        ...
    
    @property
    def optimal_memory_usage(self) -> bool:
        ...
    
    @optimal_memory_usage.setter
    def optimal_memory_usage(self, value : bool):
        ...
    
    ...

class DngLoadOptions(aspose.imaging.LoadOptions):
    '''The DNG load options'''
    
    def __init__(self):
        '''Initializes a new instance of the .'''
        ...
    
    @property
    def data_recovery_mode(self) -> aspose.imaging.DataRecoveryMode:
        ...
    
    @data_recovery_mode.setter
    def data_recovery_mode(self, value : aspose.imaging.DataRecoveryMode):
        ...
    
    @property
    def data_background_color(self) -> aspose.imaging.Color:
        ...
    
    @data_background_color.setter
    def data_background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def use_icc_profile_conversion(self) -> bool:
        ...
    
    @use_icc_profile_conversion.setter
    def use_icc_profile_conversion(self, value : bool):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def concurrent_image_processing(self) -> bool:
        ...
    
    @concurrent_image_processing.setter
    def concurrent_image_processing(self, value : bool):
        ...
    
    @property
    def fbdd(self) -> aspose.imaging.imageloadoptions.NoiseReductionType:
        '''Gets the FBDD.'''
        ...
    
    @fbdd.setter
    def fbdd(self, value : aspose.imaging.imageloadoptions.NoiseReductionType):
        '''Sets the FBDD.'''
        ...
    
    @property
    def adjust_white_balance(self) -> bool:
        ...
    
    @adjust_white_balance.setter
    def adjust_white_balance(self, value : bool):
        ...
    
    ...

class Jpeg2000LoadOptions(aspose.imaging.LoadOptions):
    '''JPEG2000 load options'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def data_recovery_mode(self) -> aspose.imaging.DataRecoveryMode:
        ...
    
    @data_recovery_mode.setter
    def data_recovery_mode(self, value : aspose.imaging.DataRecoveryMode):
        ...
    
    @property
    def data_background_color(self) -> aspose.imaging.Color:
        ...
    
    @data_background_color.setter
    def data_background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def use_icc_profile_conversion(self) -> bool:
        ...
    
    @use_icc_profile_conversion.setter
    def use_icc_profile_conversion(self, value : bool):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def concurrent_image_processing(self) -> bool:
        ...
    
    @concurrent_image_processing.setter
    def concurrent_image_processing(self, value : bool):
        ...
    
    @property
    def maximum_decoding_time(self) -> int:
        ...
    
    @maximum_decoding_time.setter
    def maximum_decoding_time(self, value : int):
        ...
    
    @property
    def maximum_decoding_time_for_tile(self) -> int:
        ...
    
    @maximum_decoding_time_for_tile.setter
    def maximum_decoding_time_for_tile(self, value : int):
        ...
    
    ...

class OdLoadOptions(aspose.imaging.LoadOptions):
    '''The Open Dcocument Load Options'''
    
    def __init__(self):
        '''Initializes a new instance of the .'''
        ...
    
    @property
    def data_recovery_mode(self) -> aspose.imaging.DataRecoveryMode:
        ...
    
    @data_recovery_mode.setter
    def data_recovery_mode(self, value : aspose.imaging.DataRecoveryMode):
        ...
    
    @property
    def data_background_color(self) -> aspose.imaging.Color:
        ...
    
    @data_background_color.setter
    def data_background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def use_icc_profile_conversion(self) -> bool:
        ...
    
    @use_icc_profile_conversion.setter
    def use_icc_profile_conversion(self, value : bool):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def concurrent_image_processing(self) -> bool:
        ...
    
    @concurrent_image_processing.setter
    def concurrent_image_processing(self, value : bool):
        ...
    
    @property
    def password(self) -> str:
        '''Gets the password.'''
        ...
    
    @password.setter
    def password(self, value : str):
        '''Sets the password.'''
        ...
    
    ...

class PngLoadOptions(aspose.imaging.LoadOptions):
    '''The png load options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def data_recovery_mode(self) -> aspose.imaging.DataRecoveryMode:
        ...
    
    @data_recovery_mode.setter
    def data_recovery_mode(self, value : aspose.imaging.DataRecoveryMode):
        ...
    
    @property
    def data_background_color(self) -> aspose.imaging.Color:
        ...
    
    @data_background_color.setter
    def data_background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def use_icc_profile_conversion(self) -> bool:
        ...
    
    @use_icc_profile_conversion.setter
    def use_icc_profile_conversion(self, value : bool):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def concurrent_image_processing(self) -> bool:
        ...
    
    @concurrent_image_processing.setter
    def concurrent_image_processing(self, value : bool):
        ...
    
    @property
    def strict_mode(self) -> bool:
        ...
    
    @strict_mode.setter
    def strict_mode(self, value : bool):
        ...
    
    ...

class SvgLoadOptions(aspose.imaging.LoadOptions):
    '''The Svg load options.'''
    
    def __init__(self):
        '''Initializes a new instance of the .'''
        ...
    
    @property
    def data_recovery_mode(self) -> aspose.imaging.DataRecoveryMode:
        ...
    
    @data_recovery_mode.setter
    def data_recovery_mode(self, value : aspose.imaging.DataRecoveryMode):
        ...
    
    @property
    def data_background_color(self) -> aspose.imaging.Color:
        ...
    
    @data_background_color.setter
    def data_background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def use_icc_profile_conversion(self) -> bool:
        ...
    
    @use_icc_profile_conversion.setter
    def use_icc_profile_conversion(self, value : bool):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def concurrent_image_processing(self) -> bool:
        ...
    
    @concurrent_image_processing.setter
    def concurrent_image_processing(self, value : bool):
        ...
    
    @property
    def default_width(self) -> int:
        ...
    
    @default_width.setter
    def default_width(self, value : int):
        ...
    
    @property
    def default_height(self) -> int:
        ...
    
    @default_height.setter
    def default_height(self, value : int):
        ...
    
    ...

class NoiseReductionType(enum.Enum):
    NONE = enum.auto()
    '''The None, do not use FBDD noise reduction'''
    LIGHT = enum.auto()
    '''The light, light FBDD reduction'''
    FULL = enum.auto()
    '''The full, full FBDD reduction'''

