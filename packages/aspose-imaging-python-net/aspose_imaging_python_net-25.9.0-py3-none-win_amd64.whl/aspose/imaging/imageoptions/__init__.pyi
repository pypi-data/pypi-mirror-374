"""The namespace contains classes suitable for export, save or creation of different file formats."""
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

class ApngOptions(PngOptions):
    '''The API for Animated PNG (Animated Portable Network Graphics) image file format
    creation is a dynamic tool for developers seeking to generate captivating
    animated images. With customizable options such as frame duration and the
    number of times to loop, this API allows for fine-tuning animated content
    according to specific needs. Whether creating engaging web graphics or
    interactive visuals, you can leverage this API to seamlessly incorporate
    APNG images with precise control over animation parameters.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def color_type(self) -> aspose.imaging.fileformats.png.PngColorType:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.imaging.fileformats.png.PngColorType):
        ...
    
    @property
    def progressive(self) -> bool:
        '''Gets a value indicating whether a  is progressive.'''
        ...
    
    @progressive.setter
    def progressive(self, value : bool):
        '''Sets a value indicating whether a  is progressive.'''
        ...
    
    @property
    def filter_type(self) -> aspose.imaging.fileformats.png.PngFilterType:
        ...
    
    @filter_type.setter
    def filter_type(self, value : aspose.imaging.fileformats.png.PngFilterType):
        ...
    
    @property
    def compression_level(self) -> int:
        ...
    
    @compression_level.setter
    def compression_level(self, value : int):
        ...
    
    @property
    def png_compression_level(self) -> aspose.imaging.imageoptions.PngCompressionLevel:
        ...
    
    @png_compression_level.setter
    def png_compression_level(self, value : aspose.imaging.imageoptions.PngCompressionLevel):
        ...
    
    @property
    def bit_depth(self) -> int:
        ...
    
    @bit_depth.setter
    def bit_depth(self, value : int):
        ...
    
    @classmethod
    @property
    def DEFAULT_COMPRESSION_LEVEL(cls) -> aspose.imaging.imageoptions.PngCompressionLevel:
        ...
    
    @property
    def num_plays(self) -> int:
        ...
    
    @num_plays.setter
    def num_plays(self, value : int):
        ...
    
    @property
    def default_frame_time(self) -> int:
        '''The default frame duration, in milliseconds'''
        ...
    
    @default_frame_time.setter
    def default_frame_time(self, value : int):
        '''The default frame duration, in milliseconds'''
        ...
    
    ...

class BigTiffOptions(TiffOptions):
    '''The API for BigTIFF raster image format creation is specifically designed
    to serve to the unique requirements of applications utilizing large-scale
    imaging data from scanners. This API facilitates the seamless generation
    of BigTIFF format, which combines multiple TIFF images into a single,
    comprehensive image. It ensures efficient processing of extensive image
    data, providing developers with a powerful tool for creating and
    manipulating high-resolution, multi-image formats.'''
    
    @overload
    def __init__(self, expected_format: aspose.imaging.fileformats.tiff.enums.TiffExpectedFormat):
        '''Initializes a new instance of the  class. By default little endian convention is used.
        
        :param expected_format: The expected Tiff file format.'''
        ...
    
    @overload
    def __init__(self, options: aspose.imaging.imageoptions.TiffOptions):
        '''Initializes a new instance of the  class.
        
        :param options: The options source.'''
        ...
    
    @overload
    def __init__(self, tags: List[aspose.imaging.fileformats.tiff.TiffDataType]):
        '''Initializes a new instance of the  class.
        
        :param tags: The tags for options initialization.'''
        ...
    
    @overload
    def __init__(self, expected_format: aspose.imaging.fileformats.tiff.enums.TiffExpectedFormat, byte_order: aspose.imaging.fileformats.tiff.enums.TiffByteOrder):
        '''Initializes a new instance of the  class.
        
        :param expected_format: The expected Tiff file format.
        :param byte_order: The tiff file format byte order to use.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Clones this instance.
        
        :returns: Returns a deep clone.'''
        ...
    
    @staticmethod
    def create_with_format(expected_format: aspose.imaging.fileformats.tiff.enums.TiffExpectedFormat) -> aspose.imaging.imageoptions.BigTiffOptions:
        '''Initializes a new instance of the  class. By default little endian convention is used.
        
        :param expected_format: The expected Tiff file format.
        :returns: A new BigTiffOptions object.'''
        ...
    
    @staticmethod
    def create_with_options(options: aspose.imaging.imageoptions.TiffOptions) -> aspose.imaging.imageoptions.BigTiffOptions:
        '''Initializes a new instance of the  class.
        
        :param options: The options source.
        :returns: A copy of options.'''
        ...
    
    @staticmethod
    def create_with_tags(tags: List[aspose.imaging.fileformats.tiff.TiffDataType]) -> aspose.imaging.imageoptions.BigTiffOptions:
        '''Initializes a new instance of the  class.
        
        :param tags: The tags for options initialization.
        :returns: A new BigTiffOptions object with tags.'''
        ...
    
    def is_tag_present(self, tag: aspose.imaging.fileformats.tiff.enums.TiffTags) -> bool:
        '''Determines whether tag is present in the options or not.
        
        :param tag: The tag id to check.
        :returns: ``true`` if tag is present; otherwise, ``false``.'''
        ...
    
    @staticmethod
    def get_valid_tags_count(tags: List[aspose.imaging.fileformats.tiff.TiffDataType]) -> int:
        '''Gets the valid tags count.
        
        :param tags: The tags to validate.
        :returns: The valid tags count.'''
        ...
    
    def remove_tag(self, tag: aspose.imaging.fileformats.tiff.enums.TiffTags) -> bool:
        '''Removes the tag.
        
        :param tag: The tag to remove.
        :returns: true if successfully removed'''
        ...
    
    def remove_tags(self, tags: List[aspose.imaging.fileformats.tiff.enums.TiffTags]) -> bool:
        '''Removes the tags.
        
        :param tags: The tags to remove.
        :returns: if tag collection size changed.'''
        ...
    
    def validate(self):
        '''Validates if options have valid combination of tags'''
        ...
    
    def add_tags(self, tags_to_add: List[aspose.imaging.fileformats.tiff.TiffDataType]):
        '''Adds the tags.
        
        :param tags_to_add: The tags to add.'''
        ...
    
    def add_tag(self, tag_to_add: aspose.imaging.fileformats.tiff.TiffDataType):
        '''Adds a new tag.
        
        :param tag_to_add: The tag to add.'''
        ...
    
    def get_tag_by_type(self, tag_key: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Gets the instance of the tag by type.
        
        :param tag_key: The tag key.
        :returns: Instance of the tag if exists or null otherwise.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def tag_count(self) -> int:
        ...
    
    @property
    def file_standard(self) -> aspose.imaging.fileformats.tiff.enums.TiffFileStandards:
        ...
    
    @file_standard.setter
    def file_standard(self, value : aspose.imaging.fileformats.tiff.enums.TiffFileStandards):
        ...
    
    @property
    def default_memory_allocation_limit(self) -> int:
        ...
    
    @default_memory_allocation_limit.setter
    def default_memory_allocation_limit(self, value : int):
        ...
    
    @property
    def premultiply_components(self) -> bool:
        ...
    
    @premultiply_components.setter
    def premultiply_components(self, value : bool):
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def y_cb_cr_subsampling(self) -> List[int]:
        ...
    
    @y_cb_cr_subsampling.setter
    def y_cb_cr_subsampling(self, value : List[int]):
        ...
    
    @property
    def y_cb_cr_coefficients(self) -> List[aspose.imaging.fileformats.tiff.TiffRational]:
        ...
    
    @y_cb_cr_coefficients.setter
    def y_cb_cr_coefficients(self, value : List[aspose.imaging.fileformats.tiff.TiffRational]):
        ...
    
    @property
    def is_tiled(self) -> bool:
        ...
    
    @property
    def artist(self) -> str:
        '''Gets the artist.'''
        ...
    
    @artist.setter
    def artist(self, value : str):
        '''Sets the artist.'''
        ...
    
    @property
    def byte_order(self) -> aspose.imaging.fileformats.tiff.enums.TiffByteOrder:
        ...
    
    @byte_order.setter
    def byte_order(self, value : aspose.imaging.fileformats.tiff.enums.TiffByteOrder):
        ...
    
    @property
    def disable_icc_export(self) -> bool:
        ...
    
    @disable_icc_export.setter
    def disable_icc_export(self, value : bool):
        ...
    
    @property
    def bits_per_sample(self) -> List[int]:
        ...
    
    @bits_per_sample.setter
    def bits_per_sample(self, value : List[int]):
        ...
    
    @property
    def extra_samples(self) -> List[int]:
        ...
    
    @property
    def compression(self) -> aspose.imaging.fileformats.tiff.enums.TiffCompressions:
        '''Gets the compression.'''
        ...
    
    @compression.setter
    def compression(self, value : aspose.imaging.fileformats.tiff.enums.TiffCompressions):
        '''Sets the compression.'''
        ...
    
    @property
    def compressed_quality(self) -> int:
        ...
    
    @compressed_quality.setter
    def compressed_quality(self, value : int):
        ...
    
    @property
    def copyright(self) -> str:
        '''Gets the copyright.'''
        ...
    
    @copyright.setter
    def copyright(self, value : str):
        '''Sets the copyright.'''
        ...
    
    @property
    def color_map(self) -> List[int]:
        ...
    
    @color_map.setter
    def color_map(self, value : List[int]):
        ...
    
    @property
    def date_time(self) -> str:
        ...
    
    @date_time.setter
    def date_time(self, value : str):
        ...
    
    @property
    def document_name(self) -> str:
        ...
    
    @document_name.setter
    def document_name(self, value : str):
        ...
    
    @property
    def alpha_storage(self) -> aspose.imaging.fileformats.tiff.enums.TiffAlphaStorage:
        ...
    
    @alpha_storage.setter
    def alpha_storage(self, value : aspose.imaging.fileformats.tiff.enums.TiffAlphaStorage):
        ...
    
    @property
    def is_extra_samples_present(self) -> bool:
        ...
    
    @property
    def fill_order(self) -> aspose.imaging.fileformats.tiff.enums.TiffFillOrders:
        ...
    
    @fill_order.setter
    def fill_order(self, value : aspose.imaging.fileformats.tiff.enums.TiffFillOrders):
        ...
    
    @property
    def half_tone_hints(self) -> List[int]:
        ...
    
    @half_tone_hints.setter
    def half_tone_hints(self, value : List[int]):
        ...
    
    @property
    def image_description(self) -> str:
        ...
    
    @image_description.setter
    def image_description(self, value : str):
        ...
    
    @property
    def ink_names(self) -> str:
        ...
    
    @ink_names.setter
    def ink_names(self, value : str):
        ...
    
    @property
    def scanner_manufacturer(self) -> str:
        ...
    
    @scanner_manufacturer.setter
    def scanner_manufacturer(self, value : str):
        ...
    
    @property
    def max_sample_value(self) -> List[int]:
        ...
    
    @max_sample_value.setter
    def max_sample_value(self, value : List[int]):
        ...
    
    @property
    def min_sample_value(self) -> List[int]:
        ...
    
    @min_sample_value.setter
    def min_sample_value(self, value : List[int]):
        ...
    
    @property
    def scanner_model(self) -> str:
        ...
    
    @scanner_model.setter
    def scanner_model(self, value : str):
        ...
    
    @property
    def orientation(self) -> aspose.imaging.fileformats.tiff.enums.TiffOrientations:
        '''Gets the orientation.'''
        ...
    
    @orientation.setter
    def orientation(self, value : aspose.imaging.fileformats.tiff.enums.TiffOrientations):
        '''Sets the orientation.'''
        ...
    
    @property
    def page_name(self) -> str:
        ...
    
    @page_name.setter
    def page_name(self, value : str):
        ...
    
    @property
    def page_number(self) -> List[int]:
        ...
    
    @page_number.setter
    def page_number(self, value : List[int]):
        ...
    
    @property
    def photometric(self) -> aspose.imaging.fileformats.tiff.enums.TiffPhotometrics:
        '''Gets the photometric.'''
        ...
    
    @photometric.setter
    def photometric(self, value : aspose.imaging.fileformats.tiff.enums.TiffPhotometrics):
        '''Sets the photometric.'''
        ...
    
    @property
    def planar_configuration(self) -> aspose.imaging.fileformats.tiff.enums.TiffPlanarConfigs:
        ...
    
    @planar_configuration.setter
    def planar_configuration(self, value : aspose.imaging.fileformats.tiff.enums.TiffPlanarConfigs):
        ...
    
    @property
    def resolution_unit(self) -> aspose.imaging.fileformats.tiff.enums.TiffResolutionUnits:
        ...
    
    @resolution_unit.setter
    def resolution_unit(self, value : aspose.imaging.fileformats.tiff.enums.TiffResolutionUnits):
        ...
    
    @property
    def rows_per_strip(self) -> int:
        ...
    
    @rows_per_strip.setter
    def rows_per_strip(self, value : int):
        ...
    
    @property
    def tile_width(self) -> int:
        ...
    
    @tile_width.setter
    def tile_width(self, value : int):
        ...
    
    @property
    def tile_length(self) -> int:
        ...
    
    @tile_length.setter
    def tile_length(self, value : int):
        ...
    
    @property
    def sample_format(self) -> List[aspose.imaging.fileformats.tiff.enums.TiffSampleFormats]:
        ...
    
    @sample_format.setter
    def sample_format(self, value : List[aspose.imaging.fileformats.tiff.enums.TiffSampleFormats]):
        ...
    
    @property
    def samples_per_pixel(self) -> int:
        ...
    
    @property
    def smax_sample_value(self) -> List[int]:
        ...
    
    @smax_sample_value.setter
    def smax_sample_value(self, value : List[int]):
        ...
    
    @property
    def smin_sample_value(self) -> List[int]:
        ...
    
    @smin_sample_value.setter
    def smin_sample_value(self, value : List[int]):
        ...
    
    @property
    def software_type(self) -> str:
        ...
    
    @software_type.setter
    def software_type(self, value : str):
        ...
    
    @property
    def strip_byte_counts(self) -> List[int]:
        ...
    
    @strip_byte_counts.setter
    def strip_byte_counts(self, value : List[int]):
        ...
    
    @property
    def strip_offsets(self) -> List[int]:
        ...
    
    @strip_offsets.setter
    def strip_offsets(self, value : List[int]):
        ...
    
    @property
    def tile_byte_counts(self) -> List[int]:
        ...
    
    @tile_byte_counts.setter
    def tile_byte_counts(self, value : List[int]):
        ...
    
    @property
    def tile_offsets(self) -> List[int]:
        ...
    
    @tile_offsets.setter
    def tile_offsets(self, value : List[int]):
        ...
    
    @property
    def sub_file_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffNewSubFileTypes:
        ...
    
    @sub_file_type.setter
    def sub_file_type(self, value : aspose.imaging.fileformats.tiff.enums.TiffNewSubFileTypes):
        ...
    
    @property
    def target_printer(self) -> str:
        ...
    
    @target_printer.setter
    def target_printer(self, value : str):
        ...
    
    @property
    def threshholding(self) -> aspose.imaging.fileformats.tiff.enums.TiffThresholds:
        '''Gets the threshholding.'''
        ...
    
    @threshholding.setter
    def threshholding(self, value : aspose.imaging.fileformats.tiff.enums.TiffThresholds):
        '''Sets the threshholding.'''
        ...
    
    @property
    def total_pages(self) -> int:
        ...
    
    @property
    def xposition(self) -> aspose.imaging.fileformats.tiff.TiffRational:
        '''Gets the x position.'''
        ...
    
    @xposition.setter
    def xposition(self, value : aspose.imaging.fileformats.tiff.TiffRational):
        '''Sets the x position.'''
        ...
    
    @property
    def xresolution(self) -> aspose.imaging.fileformats.tiff.TiffRational:
        '''Gets the x resolution.'''
        ...
    
    @xresolution.setter
    def xresolution(self, value : aspose.imaging.fileformats.tiff.TiffRational):
        '''Sets the x resolution.'''
        ...
    
    @property
    def yposition(self) -> aspose.imaging.fileformats.tiff.TiffRational:
        '''Gets the y position.'''
        ...
    
    @yposition.setter
    def yposition(self, value : aspose.imaging.fileformats.tiff.TiffRational):
        '''Sets the y position.'''
        ...
    
    @property
    def yresolution(self) -> aspose.imaging.fileformats.tiff.TiffRational:
        '''Gets the y resolution.'''
        ...
    
    @yresolution.setter
    def yresolution(self, value : aspose.imaging.fileformats.tiff.TiffRational):
        '''Sets the y resolution.'''
        ...
    
    @property
    def fax_t4_options(self) -> aspose.imaging.fileformats.tiff.enums.Group3Options:
        ...
    
    @fax_t4_options.setter
    def fax_t4_options(self, value : aspose.imaging.fileformats.tiff.enums.Group3Options):
        ...
    
    @property
    def predictor(self) -> aspose.imaging.fileformats.tiff.enums.TiffPredictor:
        '''Gets the predictor for LZW compression.'''
        ...
    
    @predictor.setter
    def predictor(self, value : aspose.imaging.fileformats.tiff.enums.TiffPredictor):
        '''Sets the predictor for LZW compression.'''
        ...
    
    @property
    def image_length(self) -> int:
        ...
    
    @image_length.setter
    def image_length(self, value : int):
        ...
    
    @property
    def image_width(self) -> int:
        ...
    
    @image_width.setter
    def image_width(self, value : int):
        ...
    
    @property
    def exif_ifd(self) -> aspose.imaging.fileformats.tiff.TiffExifIfd:
        ...
    
    @property
    def tags(self) -> List[aspose.imaging.fileformats.tiff.TiffDataType]:
        '''Gets the tags.'''
        ...
    
    @tags.setter
    def tags(self, value : List[aspose.imaging.fileformats.tiff.TiffDataType]):
        '''Sets the tags.'''
        ...
    
    @property
    def valid_tag_count(self) -> int:
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    @property
    def xp_title(self) -> str:
        ...
    
    @xp_title.setter
    def xp_title(self, value : str):
        ...
    
    @property
    def xp_comment(self) -> str:
        ...
    
    @xp_comment.setter
    def xp_comment(self, value : str):
        ...
    
    @property
    def xp_author(self) -> str:
        ...
    
    @xp_author.setter
    def xp_author(self, value : str):
        ...
    
    @property
    def xp_keywords(self) -> str:
        ...
    
    @xp_keywords.setter
    def xp_keywords(self, value : str):
        ...
    
    @property
    def xp_subject(self) -> str:
        ...
    
    @xp_subject.setter
    def xp_subject(self, value : str):
        ...
    
    @property
    def exif_data(self) -> aspose.imaging.exif.ExifData:
        ...
    
    @exif_data.setter
    def exif_data(self, value : aspose.imaging.exif.ExifData):
        ...
    
    ...

class BmpOptions(aspose.imaging.ImageOptionsBase):
    '''The API for BMP and DIB raster image format creation options provides developers
    with a versatile toolset for generating custom Bitmap (BMP) and Device
    Independent Bitmap (DIB) images. With this API, you can precisely define
    image characteristics such as bits per pixel, compression level and compression
    type, tailoring the output to meet specific requirements. This feature-rich
    API empowers developers to create high-quality, customized raster images
    with ease and flexibility for diverse applications.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, bmp_options: aspose.imaging.imageoptions.BmpOptions):
        '''Initializes a new instance of the  class.
        
        :param bmp_options: The BMP options.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    @bits_per_pixel.setter
    def bits_per_pixel(self, value : int):
        ...
    
    @property
    def compression(self) -> aspose.imaging.fileformats.bmp.BitmapCompression:
        '''Gets the compression type. The default compression type is , that allows saving a  with transparency.'''
        ...
    
    @compression.setter
    def compression(self, value : aspose.imaging.fileformats.bmp.BitmapCompression):
        '''Sets the compression type. The default compression type is , that allows saving a  with transparency.'''
        ...
    
    ...

class CdrRasterizationOptions(VectorRasterizationOptions):
    '''With the ability to perform CDR image rasterization and set scale factors
    for both X and Y dimensions, this API provides precise control over the
    transformation process. Whether scaling for specific output requirements
    or converting vector graphics to raster formats, you can leverage this
    API for efficient and customizable CDR vector to raster image conversion.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies to.
        
        :param vector_rasterization_options: The vector rasterization options.'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    @property
    def scale_x(self) -> float:
        ...
    
    @scale_x.setter
    def scale_x(self, value : float):
        ...
    
    @property
    def scale_y(self) -> float:
        ...
    
    @scale_y.setter
    def scale_y(self, value : float):
        ...
    
    ...

class CmxRasterizationOptions(VectorRasterizationOptions):
    '''the CMX exporter options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies to.
        
        :param vector_rasterization_options: The vector rasterization options.'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    ...

class DicomOptions(aspose.imaging.ImageOptionsBase):
    '''The API for Digital Imaging and Communications in Medicine (DICOM) raster image
    format creation is a specialized tool tailored for medical device applications.
    It enables the seamless generation of DICOM images, crucial for storing medical
    data and containing vital identification information. With features to
    and set compression, define color types, and embed XMP metadata, developers
    can ensure compliance and flexibility in managing DICOM images for medical
    imaging purposes.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def compression(self) -> aspose.imaging.fileformats.dicom.Compression:
        '''Gets the compression.'''
        ...
    
    @compression.setter
    def compression(self, value : aspose.imaging.fileformats.dicom.Compression):
        '''Sets the compression.'''
        ...
    
    @property
    def color_type(self) -> aspose.imaging.fileformats.dicom.ColorType:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.imaging.fileformats.dicom.ColorType):
        ...
    
    ...

class DjvuMultiPageOptions(MultiPageOptions):
    '''The API for DjVu graphics file format provides developers with seamless access
    to DjVu documents, ideal for scanned documents and books. With image loading
    options, developers can effortlessly integrate DjVu files into their applications,
    unlocking the potential to work with multi-page content, including text,
    drawings, and images, for versatile document processing solutions.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, pages: List[int]):
        '''Initializes a new instance of the  class.
        
        :param pages: The pages indexes.'''
        ...
    
    @overload
    def __init__(self, pages: List[int], export_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param pages: The pages indexes.
        :param export_area: The export area.'''
        ...
    
    @overload
    def __init__(self, range: aspose.imaging.IntRange):
        '''Initializes a new instance of the  class.
        
        :param range: The range.'''
        ...
    
    @overload
    def __init__(self, range: aspose.imaging.IntRange, export_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param range: The range.
        :param export_area: The export area.'''
        ...
    
    @overload
    def __init__(self, ranges: List[aspose.imaging.IntRange]):
        '''Initializes a new instance of the  class.
        
        :param ranges: The range.'''
        ...
    
    @overload
    def __init__(self, ranges: List[aspose.imaging.IntRange], export_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param ranges: The range.
        :param export_area: The export area.'''
        ...
    
    @overload
    def __init__(self, page: int):
        '''Initializes a new instance of the  class.
        
        :param page: The page index.'''
        ...
    
    @overload
    def __init__(self, page: int, export_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param page: The page index.
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_page_numbers(pages: List[int]) -> aspose.imaging.imageoptions.DjvuMultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param pages: The pages indexes.'''
        ...
    
    @staticmethod
    def create_with_page_numbers_rect(pages: List[int], export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.DjvuMultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param pages: The pages indexes.
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_page_titles(page_titles: List[str]) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param page_titles: The page titles.'''
        ...
    
    @staticmethod
    def create_with_page_titles_rect(page_titles: List[str], export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param page_titles: The page titles.
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_int_ranges(ranges: List[aspose.imaging.IntRange]) -> aspose.imaging.imageoptions.DjvuMultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param ranges: The range.'''
        ...
    
    @staticmethod
    def create_with_int_ranges_rect(ranges: List[aspose.imaging.IntRange], export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.DjvuMultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param ranges: The range.
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_int_range(range: aspose.imaging.IntRange) -> aspose.imaging.imageoptions.DjvuMultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param range: The range.'''
        ...
    
    @staticmethod
    def create_with_int_range_rect(range: aspose.imaging.IntRange, export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.DjvuMultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param range: The range.
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_page_number(page: int) -> aspose.imaging.imageoptions.DjvuMultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param page: The page index.'''
        ...
    
    @staticmethod
    def create_with_page_number_rect(page: int, export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.DjvuMultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param page: The page index.
        :param export_area: The export area.'''
        ...
    
    def init_pages(self, ranges: List[aspose.imaging.IntRange]):
        '''Initializes the pages from ranges array
        
        :param ranges: The ranges.'''
        ...
    
    @property
    def pages(self) -> List[int]:
        '''Gets the pages.'''
        ...
    
    @pages.setter
    def pages(self, value : List[int]):
        '''Sets the pages.'''
        ...
    
    @property
    def page_titles(self) -> List[str]:
        ...
    
    @page_titles.setter
    def page_titles(self, value : List[str]):
        ...
    
    @property
    def time_interval(self) -> aspose.imaging.imageoptions.TimeInterval:
        ...
    
    @time_interval.setter
    def time_interval(self, value : aspose.imaging.imageoptions.TimeInterval):
        ...
    
    @property
    def page_rasterization_options(self) -> List[aspose.imaging.imageoptions.VectorRasterizationOptions]:
        ...
    
    @page_rasterization_options.setter
    def page_rasterization_options(self, value : List[aspose.imaging.imageoptions.VectorRasterizationOptions]):
        ...
    
    @property
    def export_area(self) -> aspose.imaging.Rectangle:
        ...
    
    @export_area.setter
    def export_area(self, value : aspose.imaging.Rectangle):
        ...
    
    @property
    def mode(self) -> aspose.imaging.imageoptions.MultiPageMode:
        '''Gets the mode.'''
        ...
    
    @mode.setter
    def mode(self, value : aspose.imaging.imageoptions.MultiPageMode):
        '''Sets the mode.'''
        ...
    
    @property
    def output_layers_names(self) -> List[str]:
        ...
    
    @output_layers_names.setter
    def output_layers_names(self, value : List[str]):
        ...
    
    @property
    def merge_layers(self) -> bool:
        ...
    
    @merge_layers.setter
    def merge_layers(self, value : bool):
        ...
    
    ...

class DxfOptions(aspose.imaging.ImageOptionsBase):
    '''API for Drawing Interchange Format (DXF) vector image creation offers
    tailored solutions for generating AutoCAD drawing files with precision and
    flexibility. Designed specifically for working with text lines and Bezier
    curves, developers can efficiently manipulate these elements, count Bezier
    points, and convert curves into polylines for seamless exporting, ensuring
    compatibility and fidelity in DXF vector images.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def bezier_point_count(self) -> int:
        ...
    
    @bezier_point_count.setter
    def bezier_point_count(self, value : int):
        ...
    
    @property
    def convert_text_beziers(self) -> bool:
        ...
    
    @convert_text_beziers.setter
    def convert_text_beziers(self, value : bool):
        ...
    
    @property
    def text_as_lines(self) -> bool:
        ...
    
    @text_as_lines.setter
    def text_as_lines(self, value : bool):
        ...
    
    ...

class EmfOptions(MetafileOptions):
    '''The Emf options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def compress(self) -> bool:
        '''Gets a value indicating whether this  is compressed.'''
        ...
    
    @compress.setter
    def compress(self, value : bool):
        '''Sets a value indicating whether this  is compressed.'''
        ...
    
    ...

class EmfRasterizationOptions(MetafileRasterizationOptions):
    '''The Emf rasterization options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies this to ``vectorRasterizationOptions``.
        
        :param vector_rasterization_options: vectorRasterizationOptions'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    @property
    def render_mode(self) -> aspose.imaging.fileformats.emf.EmfRenderMode:
        ...
    
    @render_mode.setter
    def render_mode(self, value : aspose.imaging.fileformats.emf.EmfRenderMode):
        ...
    
    ...

class EpsRasterizationOptions(VectorRasterizationOptions):
    '''The Eps rasterization options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies to.
        
        :param vector_rasterization_options: The vector rasterization options.'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    @property
    def preview_to_export(self) -> aspose.imaging.fileformats.eps.EpsPreviewFormat:
        ...
    
    @preview_to_export.setter
    def preview_to_export(self, value : aspose.imaging.fileformats.eps.EpsPreviewFormat):
        ...
    
    ...

class GifOptions(aspose.imaging.ImageOptionsBase):
    '''The API for Graphical Interchange Format (GIF) raster image file creation offers
    developers comprehensive options for generating GIF images with precise
    control. With features to set background color, color palette, resolution,
    interlaced type, transparent color, XMP metadata container, and image
    compression, this API ensures flexibility and efficiency in creating optimized
    and visually appealing GIFs tailored to specific application requirements.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, gif_options: aspose.imaging.imageoptions.GifOptions):
        '''Initializes a new instance of the  class.
        
        :param gif_options: The GIF Options.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def do_palette_correction(self) -> bool:
        ...
    
    @do_palette_correction.setter
    def do_palette_correction(self, value : bool):
        ...
    
    @property
    def loops_count(self) -> int:
        ...
    
    @loops_count.setter
    def loops_count(self, value : int):
        ...
    
    @property
    def color_resolution(self) -> int:
        ...
    
    @color_resolution.setter
    def color_resolution(self, value : int):
        ...
    
    @property
    def is_palette_sorted(self) -> bool:
        ...
    
    @is_palette_sorted.setter
    def is_palette_sorted(self, value : bool):
        ...
    
    @property
    def pixel_aspect_ratio(self) -> int:
        ...
    
    @pixel_aspect_ratio.setter
    def pixel_aspect_ratio(self, value : int):
        ...
    
    @property
    def background_color_index(self) -> int:
        ...
    
    @background_color_index.setter
    def background_color_index(self, value : int):
        ...
    
    @property
    def has_trailer(self) -> bool:
        ...
    
    @has_trailer.setter
    def has_trailer(self, value : bool):
        ...
    
    @property
    def interlaced(self) -> bool:
        '''True if image should be interlaced.'''
        ...
    
    @interlaced.setter
    def interlaced(self, value : bool):
        '''True if image should be interlaced.'''
        ...
    
    @property
    def max_diff(self) -> int:
        ...
    
    @max_diff.setter
    def max_diff(self, value : int):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def has_transparent_color(self) -> System.Nullable`1[[System.Boolean]]:
        ...
    
    @has_transparent_color.setter
    def has_transparent_color(self, value : System.Nullable`1[[System.Boolean]]):
        ...
    
    ...

class Html5CanvasOptions(aspose.imaging.ImageOptionsBase):
    '''Create HTML5 Canvas files effortlessly with our API, allowing you to seamlessly
    combine elements like forms, text, images, animations, and links. Benefit from
    robust features including tag identifier and encoding settings support,
    ensuring optimal performance and customization for your web projects.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def canvas_tag_id(self) -> str:
        ...
    
    @canvas_tag_id.setter
    def canvas_tag_id(self, value : str):
        ...
    
    @property
    def full_html_page(self) -> bool:
        ...
    
    @full_html_page.setter
    def full_html_page(self, value : bool):
        ...
    
    @property
    def encoding(self) -> System.Text.Encoding:
        '''Gets the encoding.'''
        ...
    
    @encoding.setter
    def encoding(self, value : System.Text.Encoding):
        '''Sets the encoding.'''
        ...
    
    ...

class IcoOptions(aspose.imaging.ImageOptionsBase):
    '''Create custom ICO image files for application icons effortlessly with our API,
    empowering you to represent your software seamlessly. Our API supports PNG and
    BMP image frames with various bits per pixel values, ensuring versatility and
    compatibility for your icon creation needs.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class with the ICO frame format equals to Png and
        bitsPerPixel equals to 32.'''
        ...
    
    @overload
    def __init__(self, format: aspose.imaging.FileFormat, bits_per_pixel: int):
        '''Initializes a new instance of the  class.
        
        :param format: The ICO frame format.
        Note that ICO image supports only  and  images as entries.
        :param bits_per_pixel: The bits-per-pixel value.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def format(self) -> aspose.imaging.FileFormat:
        '''Gets the ICO frame format.'''
        ...
    
    @format.setter
    def format(self, value : aspose.imaging.FileFormat):
        '''Sets the ICO frame format.'''
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    @bits_per_pixel.setter
    def bits_per_pixel(self, value : int):
        ...
    
    ...

class Jpeg2000Options(aspose.imaging.ImageOptionsBase):
    '''Create JPEG2000 (JP2) image files with our API, utilizing advanced wavelet technology
    for coding lossless content. Benefit from support for various codecs, including
    irreversible and lossless compression, as well as XMP metadata containers, ensuring
    versatility and high-quality image creation tailored to your needs.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, jpeg_2000_options: aspose.imaging.imageoptions.Jpeg2000Options):
        '''Initializes a new instance of the  class.
        
        :param jpeg_2000_options: The Jpeg2000 file format options to copy settings from.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def comments(self) -> List[str]:
        '''Gets the Jpeg comment markers.'''
        ...
    
    @comments.setter
    def comments(self, value : List[str]):
        '''Sets the Jpeg comment markers.'''
        ...
    
    @property
    def codec(self) -> aspose.imaging.fileformats.jpeg2000.Jpeg2000Codec:
        '''Gets the JPEG2000 codec'''
        ...
    
    @codec.setter
    def codec(self, value : aspose.imaging.fileformats.jpeg2000.Jpeg2000Codec):
        '''Sets the JPEG2000 codec'''
        ...
    
    @property
    def compression_ratios(self) -> List[int]:
        ...
    
    @compression_ratios.setter
    def compression_ratios(self, value : List[int]):
        ...
    
    @property
    def irreversible(self) -> bool:
        '''Gets a value indicating whether use the irreversible DWT 9-7 (true) or use lossless DWT 5-3 compression (default).'''
        ...
    
    @irreversible.setter
    def irreversible(self, value : bool):
        '''Sets a value indicating whether use the irreversible DWT 9-7 (true) or use lossless DWT 5-3 compression (default).'''
        ...
    
    ...

class JpegOptions(aspose.imaging.ImageOptionsBase):
    '''Create high-quality JPEG images effortlessly with our API, offering adjustable
    levels of compression to optimize storage size without compromising image quality.
    Benefit from support for various compression types, near lossless coding,
    RGB and CMYK color profiles, as well as EXIF, JFIF image data, and XMP
    containers, ensuring versatile and customizable options for your image creation needs.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, jpeg_options: aspose.imaging.imageoptions.JpegOptions):
        '''Initializes a new instance of the  class.
        
        :param jpeg_options: The JPEG options.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def default_memory_allocation_limit(self) -> int:
        ...
    
    @default_memory_allocation_limit.setter
    def default_memory_allocation_limit(self, value : int):
        ...
    
    @property
    def jfif(self) -> aspose.imaging.fileformats.jpeg.JFIFData:
        '''Gets the jfif.'''
        ...
    
    @jfif.setter
    def jfif(self, value : aspose.imaging.fileformats.jpeg.JFIFData):
        '''Sets the jfif.'''
        ...
    
    @property
    def comment(self) -> str:
        '''Gets the jpeg file comment.'''
        ...
    
    @comment.setter
    def comment(self, value : str):
        '''Sets the jpeg file comment.'''
        ...
    
    @property
    def exif_data(self) -> aspose.imaging.exif.JpegExifData:
        ...
    
    @exif_data.setter
    def exif_data(self, value : aspose.imaging.exif.JpegExifData):
        ...
    
    @property
    def compression_type(self) -> aspose.imaging.fileformats.jpeg.JpegCompressionMode:
        ...
    
    @compression_type.setter
    def compression_type(self, value : aspose.imaging.fileformats.jpeg.JpegCompressionMode):
        ...
    
    @property
    def color_type(self) -> aspose.imaging.fileformats.jpeg.JpegCompressionColorMode:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.imaging.fileformats.jpeg.JpegCompressionColorMode):
        ...
    
    @property
    def bits_per_channel(self) -> int:
        ...
    
    @bits_per_channel.setter
    def bits_per_channel(self, value : int):
        ...
    
    @property
    def quality(self) -> int:
        '''Gets image quality.'''
        ...
    
    @quality.setter
    def quality(self, value : int):
        '''Sets image quality.'''
        ...
    
    @property
    def scaled_quality(self) -> int:
        ...
    
    @property
    def rd_opt_settings(self) -> aspose.imaging.imageoptions.RdOptimizerSettings:
        ...
    
    @rd_opt_settings.setter
    def rd_opt_settings(self, value : aspose.imaging.imageoptions.RdOptimizerSettings):
        ...
    
    @property
    def rgb_color_profile(self) -> aspose.imaging.sources.StreamSource:
        ...
    
    @rgb_color_profile.setter
    def rgb_color_profile(self, value : aspose.imaging.sources.StreamSource):
        ...
    
    @property
    def cmyk_color_profile(self) -> aspose.imaging.sources.StreamSource:
        ...
    
    @cmyk_color_profile.setter
    def cmyk_color_profile(self, value : aspose.imaging.sources.StreamSource):
        ...
    
    @property
    def jpeg_ls_allowed_lossy_error(self) -> int:
        ...
    
    @jpeg_ls_allowed_lossy_error.setter
    def jpeg_ls_allowed_lossy_error(self, value : int):
        ...
    
    @property
    def jpeg_ls_interleave_mode(self) -> aspose.imaging.fileformats.jpeg.JpegLsInterleaveMode:
        ...
    
    @jpeg_ls_interleave_mode.setter
    def jpeg_ls_interleave_mode(self, value : aspose.imaging.fileformats.jpeg.JpegLsInterleaveMode):
        ...
    
    @property
    def jpeg_ls_preset(self) -> aspose.imaging.fileformats.jpeg.JpegLsPresetCodingParameters:
        ...
    
    @jpeg_ls_preset.setter
    def jpeg_ls_preset(self, value : aspose.imaging.fileformats.jpeg.JpegLsPresetCodingParameters):
        ...
    
    @property
    def horizontal_sampling(self) -> bytes:
        ...
    
    @horizontal_sampling.setter
    def horizontal_sampling(self, value : bytes):
        ...
    
    @property
    def vertical_sampling(self) -> bytes:
        ...
    
    @vertical_sampling.setter
    def vertical_sampling(self, value : bytes):
        ...
    
    @property
    def sample_rounding_mode(self) -> aspose.imaging.fileformats.jpeg.SampleRoundingMode:
        ...
    
    @sample_rounding_mode.setter
    def sample_rounding_mode(self, value : aspose.imaging.fileformats.jpeg.SampleRoundingMode):
        ...
    
    @property
    def preblend_alpha_if_present(self) -> bool:
        ...
    
    @preblend_alpha_if_present.setter
    def preblend_alpha_if_present(self, value : bool):
        ...
    
    @property
    def resolution_unit(self) -> aspose.imaging.ResolutionUnit:
        ...
    
    @resolution_unit.setter
    def resolution_unit(self, value : aspose.imaging.ResolutionUnit):
        ...
    
    ...

class MetafileOptions(aspose.imaging.ImageOptionsBase):
    '''The Metafiles base options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def compress(self) -> bool:
        '''Gets a value indicating whether this  is compressed.'''
        ...
    
    @compress.setter
    def compress(self, value : bool):
        '''Sets a value indicating whether this  is compressed.'''
        ...
    
    ...

class MetafileRasterizationOptions(VectorRasterizationOptions):
    '''The metafile rasterization options'''
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies to.
        
        :param vector_rasterization_options: The vector rasterization options.'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    ...

class MultiPageOptions:
    '''Base class for multiple pages supported formats'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, pages: List[int]):
        '''Initializes a new instance of the  class.
        
        :param pages: The pages.'''
        ...
    
    @overload
    def __init__(self, pages: List[int], export_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param pages: The array of pages.
        :param export_area: The export area.'''
        ...
    
    @overload
    def __init__(self, page_titles: List[str]):
        '''Initializes a new instance of the  class.
        
        :param page_titles: The page titles.'''
        ...
    
    @overload
    def __init__(self, page_titles: List[str], export_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param page_titles: The page titles.
        :param export_area: The export area.'''
        ...
    
    @overload
    def __init__(self, ranges: List[aspose.imaging.IntRange]):
        '''Initializes a new instance of the  class.
        
        :param ranges: The .'''
        ...
    
    @overload
    def __init__(self, ranges: List[aspose.imaging.IntRange], export_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param ranges: The .
        :param export_area: The export area.'''
        ...
    
    @overload
    def __init__(self, range: aspose.imaging.IntRange):
        '''Initializes a new instance of the  class.
        
        :param range: The .'''
        ...
    
    @overload
    def __init__(self, range: aspose.imaging.IntRange, export_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param range: The .
        :param export_area: The export area.'''
        ...
    
    @overload
    def __init__(self, page: int):
        '''Initializes a new instance of the  class.
        
        :param page: The page index.'''
        ...
    
    @overload
    def __init__(self, page: int, export_area: aspose.imaging.Rectangle):
        '''Initializes a new instance of the  class.
        
        :param page: The page index.
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_page_numbers(pages: List[int]) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param pages: The pages.'''
        ...
    
    @staticmethod
    def create_with_page_numbers_rect(pages: List[int], export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param pages: The array of pages.
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_page_titles(page_titles: List[str]) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param page_titles: The page titles.'''
        ...
    
    @staticmethod
    def create_with_page_titles_rect(page_titles: List[str], export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param page_titles: The page titles.
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_int_ranges(ranges: List[aspose.imaging.IntRange]) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param ranges: The .'''
        ...
    
    @staticmethod
    def create_with_int_ranges_rect(ranges: List[aspose.imaging.IntRange], export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param ranges: The .
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_int_range(range: aspose.imaging.IntRange) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param range: The .'''
        ...
    
    @staticmethod
    def create_with_int_range_rect(range: aspose.imaging.IntRange, export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param range: The .
        :param export_area: The export area.'''
        ...
    
    @staticmethod
    def create_with_page_number(page: int) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param page: The page index.'''
        ...
    
    @staticmethod
    def create_with_page_number_rect(page: int, export_area: aspose.imaging.Rectangle) -> aspose.imaging.imageoptions.MultiPageOptions:
        '''Initializes a new instance of the  class.
        
        :param page: The page index.
        :param export_area: The export area.'''
        ...
    
    def init_pages(self, ranges: List[aspose.imaging.IntRange]):
        '''Initializes the pages from ranges array
        
        :param ranges: The ranges.'''
        ...
    
    @property
    def pages(self) -> List[int]:
        '''Gets the pages.'''
        ...
    
    @pages.setter
    def pages(self, value : List[int]):
        '''Sets the pages.'''
        ...
    
    @property
    def page_titles(self) -> List[str]:
        ...
    
    @page_titles.setter
    def page_titles(self, value : List[str]):
        ...
    
    @property
    def time_interval(self) -> aspose.imaging.imageoptions.TimeInterval:
        ...
    
    @time_interval.setter
    def time_interval(self, value : aspose.imaging.imageoptions.TimeInterval):
        ...
    
    @property
    def page_rasterization_options(self) -> List[aspose.imaging.imageoptions.VectorRasterizationOptions]:
        ...
    
    @page_rasterization_options.setter
    def page_rasterization_options(self, value : List[aspose.imaging.imageoptions.VectorRasterizationOptions]):
        ...
    
    @property
    def export_area(self) -> aspose.imaging.Rectangle:
        ...
    
    @export_area.setter
    def export_area(self, value : aspose.imaging.Rectangle):
        ...
    
    @property
    def mode(self) -> aspose.imaging.imageoptions.MultiPageMode:
        '''Gets the mode.'''
        ...
    
    @mode.setter
    def mode(self, value : aspose.imaging.imageoptions.MultiPageMode):
        '''Sets the mode.'''
        ...
    
    @property
    def output_layers_names(self) -> List[str]:
        ...
    
    @output_layers_names.setter
    def output_layers_names(self, value : List[str]):
        ...
    
    @property
    def merge_layers(self) -> bool:
        ...
    
    @merge_layers.setter
    def merge_layers(self, value : bool):
        ...
    
    ...

class MultipageCreateOptions:
    '''The multipage create options'''
    
    def __init__(self):
        ...
    
    @property
    def page_count(self) -> int:
        ...
    
    @page_count.setter
    def page_count(self, value : int):
        ...
    
    ...

class OdRasterizationOptions(VectorRasterizationOptions):
    '''The Od rasterization options'''
    
    def __init__(self):
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies to.
        
        :param vector_rasterization_options: The vector rasterization options.'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    ...

class OdgRasterizationOptions(OdRasterizationOptions):
    '''The Odg rasterization options'''
    
    def __init__(self):
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies to.
        
        :param vector_rasterization_options: The vector rasterization options.'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    ...

class OtgRasterizationOptions(OdRasterizationOptions):
    '''The Otg rasterization options'''
    
    def __init__(self):
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies to.
        
        :param vector_rasterization_options: The vector rasterization options.'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    ...

class PdfOptions(aspose.imaging.ImageOptionsBase):
    '''The PDF options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def use_original_image_resolution(self) -> bool:
        ...
    
    @use_original_image_resolution.setter
    def use_original_image_resolution(self, value : bool):
        ...
    
    @property
    def pdf_document_info(self) -> aspose.imaging.fileformats.pdf.PdfDocumentInfo:
        ...
    
    @pdf_document_info.setter
    def pdf_document_info(self, value : aspose.imaging.fileformats.pdf.PdfDocumentInfo):
        ...
    
    @property
    def pdf_core_options(self) -> aspose.imaging.fileformats.pdf.PdfCoreOptions:
        ...
    
    @pdf_core_options.setter
    def pdf_core_options(self, value : aspose.imaging.fileformats.pdf.PdfCoreOptions):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    ...

class PngOptions(aspose.imaging.ImageOptionsBase):
    '''Create high-quality Portable Network Graphics (PNG) raster images effortlessly
    with our API, offering customizable options for compression levels,
    bits per pixel depths, and alpha bits. Seamlessly process XMP metadata containers,
    ensuring comprehensive image metadata management, and empowering you to tailor
    PNG images to your exact specifications with ease.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, png_options: aspose.imaging.imageoptions.PngOptions):
        '''Initializes a new instance of the  class.
        
        :param png_options: The PNG options.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def color_type(self) -> aspose.imaging.fileformats.png.PngColorType:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.imaging.fileformats.png.PngColorType):
        ...
    
    @property
    def progressive(self) -> bool:
        '''Gets a value indicating whether a  is progressive.'''
        ...
    
    @progressive.setter
    def progressive(self, value : bool):
        '''Sets a value indicating whether a  is progressive.'''
        ...
    
    @property
    def filter_type(self) -> aspose.imaging.fileformats.png.PngFilterType:
        ...
    
    @filter_type.setter
    def filter_type(self, value : aspose.imaging.fileformats.png.PngFilterType):
        ...
    
    @property
    def compression_level(self) -> int:
        ...
    
    @compression_level.setter
    def compression_level(self, value : int):
        ...
    
    @property
    def png_compression_level(self) -> aspose.imaging.imageoptions.PngCompressionLevel:
        ...
    
    @png_compression_level.setter
    def png_compression_level(self, value : aspose.imaging.imageoptions.PngCompressionLevel):
        ...
    
    @property
    def bit_depth(self) -> int:
        ...
    
    @bit_depth.setter
    def bit_depth(self, value : int):
        ...
    
    @classmethod
    @property
    def DEFAULT_COMPRESSION_LEVEL(cls) -> aspose.imaging.imageoptions.PngCompressionLevel:
        ...
    
    ...

class PsdOptions(aspose.imaging.ImageOptionsBase):
    '''Create Photoshop Document (PSD) images with our API, offering versatile options
    with different format versions, compression methods, color modes, and
    bits counts per color channel. Seamlessly handle XMP metadata containers,
    ensuring comprehensive image processing with the power of PSD format features
    like image layers, layer masks, and file information for customization
    and creativity in your designs.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, options: aspose.imaging.imageoptions.PsdOptions):
        '''Initializes a new instance of the  class.
        
        :param options: The options.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def version(self) -> int:
        '''Gets the psd file version.'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets the psd file version.'''
        ...
    
    @property
    def compression_method(self) -> aspose.imaging.fileformats.psd.CompressionMethod:
        ...
    
    @compression_method.setter
    def compression_method(self, value : aspose.imaging.fileformats.psd.CompressionMethod):
        ...
    
    @property
    def psd_version(self) -> aspose.imaging.fileformats.psd.PsdVersion:
        ...
    
    @psd_version.setter
    def psd_version(self, value : aspose.imaging.fileformats.psd.PsdVersion):
        ...
    
    @property
    def color_mode(self) -> aspose.imaging.fileformats.psd.ColorModes:
        ...
    
    @color_mode.setter
    def color_mode(self, value : aspose.imaging.fileformats.psd.ColorModes):
        ...
    
    @property
    def channel_bits_count(self) -> int:
        ...
    
    @channel_bits_count.setter
    def channel_bits_count(self, value : int):
        ...
    
    @property
    def channels_count(self) -> int:
        ...
    
    @channels_count.setter
    def channels_count(self, value : int):
        ...
    
    @property
    def remove_global_text_engine_resource(self) -> bool:
        ...
    
    @remove_global_text_engine_resource.setter
    def remove_global_text_engine_resource(self, value : bool):
        ...
    
    @property
    def refresh_image_preview_data(self) -> bool:
        ...
    
    @refresh_image_preview_data.setter
    def refresh_image_preview_data(self, value : bool):
        ...
    
    @property
    def vectorization_options(self) -> aspose.imaging.imageoptions.PsdVectorizationOptions:
        ...
    
    @vectorization_options.setter
    def vectorization_options(self, value : aspose.imaging.imageoptions.PsdVectorizationOptions):
        ...
    
    ...

class PsdVectorizationOptions:
    '''The vectorized PSD rasterization options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def vector_data_composition_mode(self) -> aspose.imaging.fileformats.psd.VectorDataCompositionMode:
        ...
    
    @vector_data_composition_mode.setter
    def vector_data_composition_mode(self, value : aspose.imaging.fileformats.psd.VectorDataCompositionMode):
        ...
    
    ...

class RdOptimizerSettings:
    '''RD optimizer settings class'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @staticmethod
    def create() -> aspose.imaging.imageoptions.RdOptimizerSettings:
        '''Creates this instance.
        
        :returns: returns RDOptimizerSettings class instance'''
        ...
    
    @property
    def bpp_scale(self) -> int:
        ...
    
    @bpp_scale.setter
    def bpp_scale(self, value : int):
        ...
    
    @property
    def bpp_max(self) -> float:
        ...
    
    @bpp_max.setter
    def bpp_max(self, value : float):
        ...
    
    @property
    def max_q(self) -> int:
        ...
    
    @max_q.setter
    def max_q(self, value : int):
        ...
    
    @property
    def min_q(self) -> int:
        ...
    
    @property
    def max_pixel_value(self) -> int:
        ...
    
    @property
    def psnr_max(self) -> int:
        ...
    
    @property
    def discretized_bpp_max(self) -> int:
        ...
    
    ...

class RenderResult:
    '''Represents information with results of rendering'''
    
    def __init__(self):
        ...
    
    @property
    def message(self) -> str:
        '''Gets string message'''
        ...
    
    @message.setter
    def message(self, value : str):
        '''Sets string message'''
        ...
    
    @property
    def render_code(self) -> aspose.imaging.imageoptions.RenderErrorCode:
        ...
    
    @render_code.setter
    def render_code(self, value : aspose.imaging.imageoptions.RenderErrorCode):
        ...
    
    ...

class SvgOptions(aspose.imaging.ImageOptionsBase):
    '''Create Scalar Vector Graphics (SVG) image files with our API, utilizing versatile
    options for color types and compression levels. Seamlessly customize your
    SVG images with precision, ensuring optimal quality and compatibility for your design needs.'''
    
    def __init__(self):
        '''Initializes a new instance of the .'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def color_type(self) -> aspose.imaging.fileformats.svg.SvgColorMode:
        ...
    
    @color_type.setter
    def color_type(self, value : aspose.imaging.fileformats.svg.SvgColorMode):
        ...
    
    @property
    def text_as_shapes(self) -> bool:
        ...
    
    @text_as_shapes.setter
    def text_as_shapes(self, value : bool):
        ...
    
    @property
    def callback(self) -> aspose.imaging.fileformats.svg.ISvgResourceKeeperCallback:
        '''Gets the storing strategy for embedded resousces of  such as fonts, nested rasters.'''
        ...
    
    @callback.setter
    def callback(self, value : aspose.imaging.fileformats.svg.ISvgResourceKeeperCallback):
        '''Sets the storing strategy for embedded resousces of  such as fonts, nested rasters.'''
        ...
    
    @property
    def compress(self) -> bool:
        '''Gets a value indicating whether the output image must to be compressed.'''
        ...
    
    @compress.setter
    def compress(self, value : bool):
        '''Sets a value indicating whether the output image must to be compressed.'''
        ...
    
    ...

class SvgRasterizationOptions(VectorRasterizationOptions):
    '''The SVG rasterization options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies this instance to ``vectorRasterizationOptions``.
        
        :param vector_rasterization_options: The vector rasterization options.'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    @property
    def scale_x(self) -> float:
        ...
    
    @scale_x.setter
    def scale_x(self, value : float):
        ...
    
    @property
    def scale_y(self) -> float:
        ...
    
    @scale_y.setter
    def scale_y(self, value : float):
        ...
    
    ...

class TgaOptions(aspose.imaging.ImageOptionsBase):
    '''The TGA file format create options.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, tga_options: aspose.imaging.imageoptions.TgaOptions):
        '''Initializes a new instance of the  class.
        
        :param tga_options: The TGA options.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    ...

class TiffOptions(aspose.imaging.ImageOptionsBase):
    '''The tiff file format options.
    Note that width and height tags will get overwritten on image creation by width and height parameters so there is no need to specify them directly.
    Note that many options return a default value but that does not mean that this option is set explicitly as a tag value. To verify the tag is present use Tags property or the corresponding IsTagPresent method.'''
    
    @overload
    def __init__(self, expected_format: aspose.imaging.fileformats.tiff.enums.TiffExpectedFormat, byte_order: aspose.imaging.fileformats.tiff.enums.TiffByteOrder):
        '''Initializes a new instance of the  class.
        
        :param expected_format: The expected tiff file format.
        :param byte_order: The tiff file format byte order to use.'''
        ...
    
    @overload
    def __init__(self, expected_format: aspose.imaging.fileformats.tiff.enums.TiffExpectedFormat):
        '''Initializes a new instance of the  class. By default little endian convention is used.
        
        :param expected_format: The expected tiff file format.'''
        ...
    
    @overload
    def __init__(self, options: aspose.imaging.imageoptions.TiffOptions):
        '''Initializes a new instance of the  class.
        
        :param options: The options to copy from.'''
        ...
    
    @overload
    def __init__(self, tags: List[aspose.imaging.fileformats.tiff.TiffDataType]):
        '''Initializes a new instance of the  class.
        
        :param tags: The tags to initialize options with.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Clones this instance.
        
        :returns: Returns a deep clone.'''
        ...
    
    @staticmethod
    def create_with_format(expected_format: aspose.imaging.fileformats.tiff.enums.TiffExpectedFormat) -> aspose.imaging.imageoptions.TiffOptions:
        '''Initializes a new instance of the  class. By default little endian convention is used.
        
        :param expected_format: The expected tiff file format.'''
        ...
    
    @staticmethod
    def create_with_options(options: aspose.imaging.imageoptions.TiffOptions) -> aspose.imaging.imageoptions.TiffOptions:
        '''Initializes a new instance of the  class.
        
        :param options: The options to copy from.'''
        ...
    
    @staticmethod
    def create_with_tags(tags: List[aspose.imaging.fileformats.tiff.TiffDataType]) -> aspose.imaging.imageoptions.TiffOptions:
        '''Initializes a new instance of the  class.
        
        :param tags: The tags to initialize options with.'''
        ...
    
    def is_tag_present(self, tag: aspose.imaging.fileformats.tiff.enums.TiffTags) -> bool:
        '''Determines whether tag is present in the options or not.
        
        :param tag: The tag id to check.
        :returns: ``true`` if tag is present; otherwise, ``false``.'''
        ...
    
    @staticmethod
    def get_valid_tags_count(tags: List[aspose.imaging.fileformats.tiff.TiffDataType]) -> int:
        '''Gets the valid tags count.
        
        :param tags: The tags to validate.
        :returns: The valid tags count.'''
        ...
    
    def remove_tag(self, tag: aspose.imaging.fileformats.tiff.enums.TiffTags) -> bool:
        '''Removes the tag.
        
        :param tag: The tag to remove.
        :returns: true if successfully removed'''
        ...
    
    def remove_tags(self, tags: List[aspose.imaging.fileformats.tiff.enums.TiffTags]) -> bool:
        '''Removes the tags.
        
        :param tags: The tags to remove.
        :returns: if tag collection size changed.'''
        ...
    
    def validate(self):
        '''Validates if options have valid combination of tags'''
        ...
    
    def add_tags(self, tags_to_add: List[aspose.imaging.fileformats.tiff.TiffDataType]):
        '''Adds the tags.
        
        :param tags_to_add: The tags to add.'''
        ...
    
    def add_tag(self, tag_to_add: aspose.imaging.fileformats.tiff.TiffDataType):
        '''Adds a new tag.
        
        :param tag_to_add: The tag to add.'''
        ...
    
    def get_tag_by_type(self, tag_key: aspose.imaging.fileformats.tiff.enums.TiffTags) -> aspose.imaging.fileformats.tiff.TiffDataType:
        '''Gets the instance of the tag by type.
        
        :param tag_key: The tag key.
        :returns: Instance of the tag if exists or null otherwise.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def tag_count(self) -> int:
        ...
    
    @property
    def file_standard(self) -> aspose.imaging.fileformats.tiff.enums.TiffFileStandards:
        ...
    
    @file_standard.setter
    def file_standard(self, value : aspose.imaging.fileformats.tiff.enums.TiffFileStandards):
        ...
    
    @property
    def default_memory_allocation_limit(self) -> int:
        ...
    
    @default_memory_allocation_limit.setter
    def default_memory_allocation_limit(self, value : int):
        ...
    
    @property
    def premultiply_components(self) -> bool:
        ...
    
    @premultiply_components.setter
    def premultiply_components(self, value : bool):
        ...
    
    @property
    def is_valid(self) -> bool:
        ...
    
    @property
    def y_cb_cr_subsampling(self) -> List[int]:
        ...
    
    @y_cb_cr_subsampling.setter
    def y_cb_cr_subsampling(self, value : List[int]):
        ...
    
    @property
    def y_cb_cr_coefficients(self) -> List[aspose.imaging.fileformats.tiff.TiffRational]:
        ...
    
    @y_cb_cr_coefficients.setter
    def y_cb_cr_coefficients(self, value : List[aspose.imaging.fileformats.tiff.TiffRational]):
        ...
    
    @property
    def is_tiled(self) -> bool:
        ...
    
    @property
    def artist(self) -> str:
        '''Gets the artist.'''
        ...
    
    @artist.setter
    def artist(self, value : str):
        '''Sets the artist.'''
        ...
    
    @property
    def byte_order(self) -> aspose.imaging.fileformats.tiff.enums.TiffByteOrder:
        ...
    
    @byte_order.setter
    def byte_order(self, value : aspose.imaging.fileformats.tiff.enums.TiffByteOrder):
        ...
    
    @property
    def disable_icc_export(self) -> bool:
        ...
    
    @disable_icc_export.setter
    def disable_icc_export(self, value : bool):
        ...
    
    @property
    def bits_per_sample(self) -> List[int]:
        ...
    
    @bits_per_sample.setter
    def bits_per_sample(self, value : List[int]):
        ...
    
    @property
    def extra_samples(self) -> List[int]:
        ...
    
    @property
    def compression(self) -> aspose.imaging.fileformats.tiff.enums.TiffCompressions:
        '''Gets the compression.'''
        ...
    
    @compression.setter
    def compression(self, value : aspose.imaging.fileformats.tiff.enums.TiffCompressions):
        '''Sets the compression.'''
        ...
    
    @property
    def compressed_quality(self) -> int:
        ...
    
    @compressed_quality.setter
    def compressed_quality(self, value : int):
        ...
    
    @property
    def copyright(self) -> str:
        '''Gets the copyright.'''
        ...
    
    @copyright.setter
    def copyright(self, value : str):
        '''Sets the copyright.'''
        ...
    
    @property
    def color_map(self) -> List[int]:
        ...
    
    @color_map.setter
    def color_map(self, value : List[int]):
        ...
    
    @property
    def date_time(self) -> str:
        ...
    
    @date_time.setter
    def date_time(self, value : str):
        ...
    
    @property
    def document_name(self) -> str:
        ...
    
    @document_name.setter
    def document_name(self, value : str):
        ...
    
    @property
    def alpha_storage(self) -> aspose.imaging.fileformats.tiff.enums.TiffAlphaStorage:
        ...
    
    @alpha_storage.setter
    def alpha_storage(self, value : aspose.imaging.fileformats.tiff.enums.TiffAlphaStorage):
        ...
    
    @property
    def is_extra_samples_present(self) -> bool:
        ...
    
    @property
    def fill_order(self) -> aspose.imaging.fileformats.tiff.enums.TiffFillOrders:
        ...
    
    @fill_order.setter
    def fill_order(self, value : aspose.imaging.fileformats.tiff.enums.TiffFillOrders):
        ...
    
    @property
    def half_tone_hints(self) -> List[int]:
        ...
    
    @half_tone_hints.setter
    def half_tone_hints(self, value : List[int]):
        ...
    
    @property
    def image_description(self) -> str:
        ...
    
    @image_description.setter
    def image_description(self, value : str):
        ...
    
    @property
    def ink_names(self) -> str:
        ...
    
    @ink_names.setter
    def ink_names(self, value : str):
        ...
    
    @property
    def scanner_manufacturer(self) -> str:
        ...
    
    @scanner_manufacturer.setter
    def scanner_manufacturer(self, value : str):
        ...
    
    @property
    def max_sample_value(self) -> List[int]:
        ...
    
    @max_sample_value.setter
    def max_sample_value(self, value : List[int]):
        ...
    
    @property
    def min_sample_value(self) -> List[int]:
        ...
    
    @min_sample_value.setter
    def min_sample_value(self, value : List[int]):
        ...
    
    @property
    def scanner_model(self) -> str:
        ...
    
    @scanner_model.setter
    def scanner_model(self, value : str):
        ...
    
    @property
    def orientation(self) -> aspose.imaging.fileformats.tiff.enums.TiffOrientations:
        '''Gets the orientation.'''
        ...
    
    @orientation.setter
    def orientation(self, value : aspose.imaging.fileformats.tiff.enums.TiffOrientations):
        '''Sets the orientation.'''
        ...
    
    @property
    def page_name(self) -> str:
        ...
    
    @page_name.setter
    def page_name(self, value : str):
        ...
    
    @property
    def page_number(self) -> List[int]:
        ...
    
    @page_number.setter
    def page_number(self, value : List[int]):
        ...
    
    @property
    def photometric(self) -> aspose.imaging.fileformats.tiff.enums.TiffPhotometrics:
        '''Gets the photometric.'''
        ...
    
    @photometric.setter
    def photometric(self, value : aspose.imaging.fileformats.tiff.enums.TiffPhotometrics):
        '''Sets the photometric.'''
        ...
    
    @property
    def planar_configuration(self) -> aspose.imaging.fileformats.tiff.enums.TiffPlanarConfigs:
        ...
    
    @planar_configuration.setter
    def planar_configuration(self, value : aspose.imaging.fileformats.tiff.enums.TiffPlanarConfigs):
        ...
    
    @property
    def resolution_unit(self) -> aspose.imaging.fileformats.tiff.enums.TiffResolutionUnits:
        ...
    
    @resolution_unit.setter
    def resolution_unit(self, value : aspose.imaging.fileformats.tiff.enums.TiffResolutionUnits):
        ...
    
    @property
    def rows_per_strip(self) -> int:
        ...
    
    @rows_per_strip.setter
    def rows_per_strip(self, value : int):
        ...
    
    @property
    def tile_width(self) -> int:
        ...
    
    @tile_width.setter
    def tile_width(self, value : int):
        ...
    
    @property
    def tile_length(self) -> int:
        ...
    
    @tile_length.setter
    def tile_length(self, value : int):
        ...
    
    @property
    def sample_format(self) -> List[aspose.imaging.fileformats.tiff.enums.TiffSampleFormats]:
        ...
    
    @sample_format.setter
    def sample_format(self, value : List[aspose.imaging.fileformats.tiff.enums.TiffSampleFormats]):
        ...
    
    @property
    def samples_per_pixel(self) -> int:
        ...
    
    @property
    def smax_sample_value(self) -> List[int]:
        ...
    
    @smax_sample_value.setter
    def smax_sample_value(self, value : List[int]):
        ...
    
    @property
    def smin_sample_value(self) -> List[int]:
        ...
    
    @smin_sample_value.setter
    def smin_sample_value(self, value : List[int]):
        ...
    
    @property
    def software_type(self) -> str:
        ...
    
    @software_type.setter
    def software_type(self, value : str):
        ...
    
    @property
    def strip_byte_counts(self) -> List[int]:
        ...
    
    @strip_byte_counts.setter
    def strip_byte_counts(self, value : List[int]):
        ...
    
    @property
    def strip_offsets(self) -> List[int]:
        ...
    
    @strip_offsets.setter
    def strip_offsets(self, value : List[int]):
        ...
    
    @property
    def tile_byte_counts(self) -> List[int]:
        ...
    
    @tile_byte_counts.setter
    def tile_byte_counts(self, value : List[int]):
        ...
    
    @property
    def tile_offsets(self) -> List[int]:
        ...
    
    @tile_offsets.setter
    def tile_offsets(self, value : List[int]):
        ...
    
    @property
    def sub_file_type(self) -> aspose.imaging.fileformats.tiff.enums.TiffNewSubFileTypes:
        ...
    
    @sub_file_type.setter
    def sub_file_type(self, value : aspose.imaging.fileformats.tiff.enums.TiffNewSubFileTypes):
        ...
    
    @property
    def target_printer(self) -> str:
        ...
    
    @target_printer.setter
    def target_printer(self, value : str):
        ...
    
    @property
    def threshholding(self) -> aspose.imaging.fileformats.tiff.enums.TiffThresholds:
        '''Gets the threshholding.'''
        ...
    
    @threshholding.setter
    def threshholding(self, value : aspose.imaging.fileformats.tiff.enums.TiffThresholds):
        '''Sets the threshholding.'''
        ...
    
    @property
    def total_pages(self) -> int:
        ...
    
    @property
    def xposition(self) -> aspose.imaging.fileformats.tiff.TiffRational:
        '''Gets the x position.'''
        ...
    
    @xposition.setter
    def xposition(self, value : aspose.imaging.fileformats.tiff.TiffRational):
        '''Sets the x position.'''
        ...
    
    @property
    def xresolution(self) -> aspose.imaging.fileformats.tiff.TiffRational:
        '''Gets the x resolution.'''
        ...
    
    @xresolution.setter
    def xresolution(self, value : aspose.imaging.fileformats.tiff.TiffRational):
        '''Sets the x resolution.'''
        ...
    
    @property
    def yposition(self) -> aspose.imaging.fileformats.tiff.TiffRational:
        '''Gets the y position.'''
        ...
    
    @yposition.setter
    def yposition(self, value : aspose.imaging.fileformats.tiff.TiffRational):
        '''Sets the y position.'''
        ...
    
    @property
    def yresolution(self) -> aspose.imaging.fileformats.tiff.TiffRational:
        '''Gets the y resolution.'''
        ...
    
    @yresolution.setter
    def yresolution(self, value : aspose.imaging.fileformats.tiff.TiffRational):
        '''Sets the y resolution.'''
        ...
    
    @property
    def fax_t4_options(self) -> aspose.imaging.fileformats.tiff.enums.Group3Options:
        ...
    
    @fax_t4_options.setter
    def fax_t4_options(self, value : aspose.imaging.fileformats.tiff.enums.Group3Options):
        ...
    
    @property
    def predictor(self) -> aspose.imaging.fileformats.tiff.enums.TiffPredictor:
        '''Gets the predictor for LZW compression.'''
        ...
    
    @predictor.setter
    def predictor(self, value : aspose.imaging.fileformats.tiff.enums.TiffPredictor):
        '''Sets the predictor for LZW compression.'''
        ...
    
    @property
    def image_length(self) -> int:
        ...
    
    @image_length.setter
    def image_length(self, value : int):
        ...
    
    @property
    def image_width(self) -> int:
        ...
    
    @image_width.setter
    def image_width(self, value : int):
        ...
    
    @property
    def exif_ifd(self) -> aspose.imaging.fileformats.tiff.TiffExifIfd:
        ...
    
    @property
    def tags(self) -> List[aspose.imaging.fileformats.tiff.TiffDataType]:
        '''Gets the tags.'''
        ...
    
    @tags.setter
    def tags(self, value : List[aspose.imaging.fileformats.tiff.TiffDataType]):
        '''Sets the tags.'''
        ...
    
    @property
    def valid_tag_count(self) -> int:
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    @property
    def xp_title(self) -> str:
        ...
    
    @xp_title.setter
    def xp_title(self, value : str):
        ...
    
    @property
    def xp_comment(self) -> str:
        ...
    
    @xp_comment.setter
    def xp_comment(self, value : str):
        ...
    
    @property
    def xp_author(self) -> str:
        ...
    
    @xp_author.setter
    def xp_author(self, value : str):
        ...
    
    @property
    def xp_keywords(self) -> str:
        ...
    
    @xp_keywords.setter
    def xp_keywords(self, value : str):
        ...
    
    @property
    def xp_subject(self) -> str:
        ...
    
    @xp_subject.setter
    def xp_subject(self, value : str):
        ...
    
    @property
    def exif_data(self) -> aspose.imaging.exif.ExifData:
        ...
    
    @exif_data.setter
    def exif_data(self, value : aspose.imaging.exif.ExifData):
        ...
    
    ...

class TimeInterval:
    '''Represents the time interval in milliseconds'''
    
    def __init__(self, from_address: int, to: int):
        '''Initializes a new instance of the  class.
        
        :param from_address: From milliseconds.
        :param to: To milliseconds.'''
        ...
    
    @property
    def from_address(self) -> int:
        ...
    
    @from_address.setter
    def from_address(self, value : int):
        ...
    
    @property
    def to(self) -> int:
        '''Gets To milliseconds.'''
        ...
    
    @to.setter
    def to(self, value : int):
        '''Sets To milliseconds.'''
        ...
    
    ...

class VectorRasterizationOptions:
    '''The vector rasterization options.
    Please note that  will no longer derive from
    since Aspose.Imaging 24.12 version.'''
    
    def __init__(self):
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies to.
        
        :param vector_rasterization_options: The vector rasterization options.'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    ...

class WebPOptions(aspose.imaging.ImageOptionsBase):
    '''Create modern WebP raster web images using our API, featuring robust support for
    lossless and lossy compression, as well as alpha channels and animation loops.
    Enhance your web content with dynamic visuals while optimizing file sizes
    for improved loading speeds and user experience.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def lossless(self) -> bool:
        '''Gets a value indicating whether this  is lossless.'''
        ...
    
    @lossless.setter
    def lossless(self, value : bool):
        '''Sets a value indicating whether this  is lossless.'''
        ...
    
    @property
    def quality(self) -> float:
        '''Gets the quality.'''
        ...
    
    @quality.setter
    def quality(self, value : float):
        '''Sets the quality.'''
        ...
    
    @property
    def anim_loop_count(self) -> int:
        ...
    
    @anim_loop_count.setter
    def anim_loop_count(self, value : int):
        ...
    
    @property
    def anim_background_color(self) -> int:
        ...
    
    @anim_background_color.setter
    def anim_background_color(self, value : int):
        ...
    
    ...

class WmfOptions(MetafileOptions):
    '''The wmf options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> aspose.imaging.ImageOptionsBase:
        '''Creates a memberwise clone of this instance.
        
        :returns: A memberwise clone of this instance.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def keep_metadata(self) -> bool:
        ...
    
    @keep_metadata.setter
    def keep_metadata(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def source(self) -> aspose.imaging.Source:
        '''Gets the source to create image in.'''
        ...
    
    @source.setter
    def source(self, value : aspose.imaging.Source):
        '''Sets the source to create image in.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette.'''
        ...
    
    @property
    def resolution_settings(self) -> aspose.imaging.ResolutionSetting:
        ...
    
    @resolution_settings.setter
    def resolution_settings(self, value : aspose.imaging.ResolutionSetting):
        ...
    
    @property
    def vector_rasterization_options(self) -> aspose.imaging.imageoptions.VectorRasterizationOptions:
        ...
    
    @vector_rasterization_options.setter
    def vector_rasterization_options(self, value : aspose.imaging.imageoptions.VectorRasterizationOptions):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def multi_page_options(self) -> aspose.imaging.imageoptions.MultiPageOptions:
        ...
    
    @multi_page_options.setter
    def multi_page_options(self, value : aspose.imaging.imageoptions.MultiPageOptions):
        ...
    
    @property
    def full_frame(self) -> bool:
        ...
    
    @full_frame.setter
    def full_frame(self, value : bool):
        ...
    
    @property
    def compress(self) -> bool:
        '''Gets a value indicating whether this  is compressed.'''
        ...
    
    @compress.setter
    def compress(self, value : bool):
        '''Sets a value indicating whether this  is compressed.'''
        ...
    
    ...

class WmfRasterizationOptions(MetafileRasterizationOptions):
    '''The Wmf rasterization options.'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def clone(self) -> any:
        '''Creates a new object that is a shallow copy of the current instance.
        
        :returns: A new object that is a shallow copy of this instance.'''
        ...
    
    def copy_to(self, vector_rasterization_options: aspose.imaging.imageoptions.VectorRasterizationOptions):
        '''Copies this to ``vectorRasterizationOptions``.
        
        :param vector_rasterization_options: vectorRasterizationOptions'''
        ...
    
    @property
    def border_x(self) -> float:
        ...
    
    @border_x.setter
    def border_x(self, value : float):
        ...
    
    @property
    def border_y(self) -> float:
        ...
    
    @border_y.setter
    def border_y(self, value : float):
        ...
    
    @property
    def center_drawing(self) -> bool:
        ...
    
    @center_drawing.setter
    def center_drawing(self, value : bool):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def page_size(self) -> aspose.imaging.SizeF:
        ...
    
    @page_size.setter
    def page_size(self, value : aspose.imaging.SizeF):
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def draw_color(self) -> aspose.imaging.Color:
        ...
    
    @draw_color.setter
    def draw_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def smoothing_mode(self) -> aspose.imaging.SmoothingMode:
        ...
    
    @smoothing_mode.setter
    def smoothing_mode(self, value : aspose.imaging.SmoothingMode):
        ...
    
    @property
    def text_rendering_hint(self) -> aspose.imaging.TextRenderingHint:
        ...
    
    @text_rendering_hint.setter
    def text_rendering_hint(self, value : aspose.imaging.TextRenderingHint):
        ...
    
    @property
    def positioning(self) -> aspose.imaging.imageoptions.PositioningTypes:
        '''Gets the positioning.'''
        ...
    
    @positioning.setter
    def positioning(self, value : aspose.imaging.imageoptions.PositioningTypes):
        '''Sets the positioning.'''
        ...
    
    @property
    def render_mode(self) -> aspose.imaging.fileformats.wmf.WmfRenderMode:
        ...
    
    @render_mode.setter
    def render_mode(self, value : aspose.imaging.fileformats.wmf.WmfRenderMode):
        ...
    
    ...

class MultiPageMode(enum.Enum):
    PAGES = enum.auto()
    '''Used page indicies'''
    TITLES = enum.auto()
    '''Used page titles'''
    RANGE = enum.auto()
    '''Used range of pages'''
    TIME_INTERVAL = enum.auto()
    '''Used pages in time interval'''
    ALL_PAGES = enum.auto()
    '''Used all pages'''

class PdfImageCompressionOptions(enum.Enum):
    AUTO = enum.auto()
    '''Automatically selects the most appropriate compression for each image.'''
    NONE = enum.auto()
    '''Saves raw image bytes resulting in bigger pdf file sizes.'''
    RLE = enum.auto()
    '''Run Length compression.'''
    FLATE = enum.auto()
    '''Flate compression.'''
    LZW_BASELINE_PREDICTOR = enum.auto()
    '''Predictor selection is restricted to PNG Paeth predictor to speed-up the process. In practice
    performs surprisingly good. Better than .'''
    LZW_OPTIMIZED_PREDICTOR = enum.auto()
    '''Predictor selection is more complicated and should result in smaller image sizes but
    taking more time. RFC 2083 says it is the best way to go. But on the test data baseline predictor
    kicks ass leaving optimized predictor behing
    by 25-40% compression rate gains.'''
    JPEG = enum.auto()
    '''Jpeg compression.
    Does not support transparency.'''
    CCITT3 = enum.auto()
    '''/CCITTFaxDecode/DecodeParms/K 0/Columns 173
    Does not support transparency.'''
    CCITT4 = enum.auto()
    '''/CCITTFaxDecode/DecodeParms/K -1/Columns 173
    Does not support transparency.'''

class PngCompressionLevel(enum.Enum):
    ZIP_LEVEL0 = enum.auto()
    '''The data will be simply stored, with no change at all.
    Uses a slower deflate implementation with a compression scale.'''
    ZIP_LEVEL1 = enum.auto()
    '''The fastest but least effective compression.
    Uses a slower deflate implementation with a compression scale.'''
    ZIP_LEVEL2 = enum.auto()
    '''A little slower, but better, than level 1.
    Uses a slower deflate implementation with a compression scale.'''
    ZIP_LEVEL3 = enum.auto()
    '''A little slower, but better, than level 2.
    Uses a slower deflate implementation with a compression scale.'''
    ZIP_LEVEL4 = enum.auto()
    '''A little slower, but better, than level 3.
    Uses a slower deflate implementation with a compression scale.'''
    ZIP_LEVEL5 = enum.auto()
    '''A little slower than level 4, but with better compression.
    Uses a slower deflate implementation with a compression scale.'''
    ZIP_LEVEL6 = enum.auto()
    '''A little slower than level 5, but with better compression.
    Uses a slower deflate implementation with a compression scale.'''
    ZIP_LEVEL7 = enum.auto()
    '''Better compression than level 6, but even slower.
    Uses a slower deflate implementation with a compression scale.'''
    ZIP_LEVEL8 = enum.auto()
    '''Better compression than level 7, but even slower.
    Uses a slower deflate implementation with a compression scale.'''
    ZIP_LEVEL9 = enum.auto()
    '''The "best" compression, where best means greatest reduction in size of the input data stream.
    This is also the slowest compression.
    Uses a slower deflate implementation with a compression scale.'''
    DEFLATE_RECOMENDED = enum.auto()
    '''The most optimised compression, with a good balance of speed and compression efficiency.
    Uses a faster deflate implementation with no compression scale.'''

class PositioningTypes(enum.Enum):
    DEFINED_BY_DOCUMENT = enum.auto()
    '''The absolute positioning on the page that is defined by document page settings.'''
    DEFINED_BY_OPTIONS = enum.auto()
    '''The absolute positioning on the page that is defined by options page settings.'''
    RELATIVE = enum.auto()
    '''The relative positioning and size. Determined by the boundary of all graphics objects.'''

class RenderErrorCode(enum.Enum):
    MISSING_HEADER = enum.auto()
    '''Header is missing'''
    MISSING_LAYOUTS = enum.auto()
    '''Layouts information is missing'''
    MISSING_BLOCKS = enum.auto()
    '''Block information is missing'''
    MISSING_DIMENSION_STYLES = enum.auto()
    '''Dimension styles information is missing'''
    MISSING_STYLES = enum.auto()
    '''Styles information is missing'''

class TiffOptionsError(enum.Enum):
    NO_ERROR = enum.auto()
    '''No error code.'''
    NO_COLOR_MAP = enum.auto()
    '''The color map is not defined.'''
    COLOR_MAP_LENGTH_INVALID = enum.auto()
    '''The color map length is invalid.'''
    COMPRESSION_SPP_MISMATCH = enum.auto()
    '''The compression does not match the samples per pixel count.'''
    PHOTOMETRIC_COMPRESSION_MISMATCH = enum.auto()
    '''The compression does not match the photometric settings.'''
    PHOTOMETRIC_SPP_MISMATCH = enum.auto()
    '''The photometric does not match the samples per pixel count.'''
    NOT_SUPPORTED_ALPHA_STORAGE = enum.auto()
    '''The alpha storage is not supported.'''
    PHOTOMETRIC_BITS_PER_SAMPLE_MISMATCH = enum.auto()
    '''The photometric bits per sample is invalid'''
    BASELINE_6_OPTIONS_MISMATCH = enum.auto()
    '''The specified TIFF options parameters don't conform to TIFF Baseline 6.0 standard'''

class TypeOfEntities(enum.Enum):
    ENTITIES_2D = enum.auto()
    '''Render 2D entities'''
    ENTITIES_3D = enum.auto()
    '''Render 3D entities'''

