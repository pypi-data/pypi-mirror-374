"""The namespace handles WebP file format processing."""
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

class IFrame:
    '''Webp frame'''
    
    @property
    def left(self) -> int:
        '''Gets the frame position left.'''
        ...
    
    @left.setter
    def left(self, value : int):
        '''Sets the frame position left.'''
        ...
    
    @property
    def top(self) -> int:
        '''Gets the frame position top.'''
        ...
    
    @top.setter
    def top(self, value : int):
        '''Sets the frame position top.'''
        ...
    
    @property
    def duration(self) -> int:
        '''Gets the frame duration.'''
        ...
    
    @duration.setter
    def duration(self, value : int):
        '''Sets the frame duration.'''
        ...
    
    ...

class WebPFrameBlock(aspose.imaging.RasterCachedImage):
    '''Represents the webp blocks openers registry.'''
    
    @overload
    def __init__(self, raster_image: aspose.imaging.RasterImage):
        '''Initializes a new instance of the
        
        class.
        
        :param raster_image: The raster image.'''
        ...
    
    @overload
    def __init__(self, width: int, height: int):
        '''Initializes a new instance of the  class.
        
        :param width: The width.
        :param height: The height.'''
        ...
    
    @overload
    def save(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use source bounds.'''
        ...
    
    @overload
    def save(self):
        '''Saves the image data to the underlying stream.'''
        ...
    
    @overload
    def save(self, file_path: str):
        '''Saves the image to the specified file location.
        
        :param file_path: The file path to save the image to.'''
        ...
    
    @overload
    def save(self, file_path: str, options: aspose.imaging.ImageOptionsBase):
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.'''
        ...
    
    @overload
    def save(self, file_path: str, options: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use sourse bounds.'''
        ...
    
    @overload
    def save(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.'''
        ...
    
    @overload
    def save(self, stream: io.RawIOBase):
        '''Saves the object's data to the specified stream.
        
        :param stream: The stream to save the object's data to.'''
        ...
    
    @overload
    def save(self, file_path: str, over_write: bool):
        '''Saves the object's data to the specified file location.
        
        :param file_path: The file path to save the object's data to.
        :param over_write: if set to ``true`` over write the file contents, otherwise append will occur.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path: str) -> bool:
        '''Determines whether image can be loaded from the specified file path.
        
        :param file_path: The file path.
        :returns: ``true`` if image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path: str, load_options: aspose.imaging.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified file path and optionally using the specified open options.
        
        :param file_path: The file path.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream: io.RawIOBase) -> bool:
        '''Determines whether image can be loaded from the specified stream.
        
        :param stream: The stream to load from.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified stream and optionally using the specified ``loadOptions``.
        
        :param stream: The stream to load from.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def create(image_options: aspose.imaging.ImageOptionsBase, width: int, height: int) -> aspose.imaging.Image:
        '''Creates a new image using the specified create options.
        
        :param image_options: The image options.
        :param width: The width.
        :param height: The height.
        :returns: The newly created image.'''
        ...
    
    @overload
    @staticmethod
    def create(images: List[aspose.imaging.Image]) -> aspose.imaging.Image:
        '''Creates a new image using the specified images as pages
        
        :param images: The images.
        :returns: The Image as IMultipageImage'''
        ...
    
    @overload
    @staticmethod
    def create(multipage_create_options: aspose.imaging.imageoptions.MultipageCreateOptions) -> aspose.imaging.Image:
        '''Creates the specified multipage create options.
        
        :param multipage_create_options: The multipage create options.
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def create(files: List[str], throw_exception_on_load_error: bool) -> aspose.imaging.Image:
        '''Creates the multipage image containing the specified files.
        
        :param files: The files.
        :param throw_exception_on_load_error: if set to ``true`` [throw exception on load error].
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def create(files: List[str]) -> aspose.imaging.Image:
        '''Creates the multipage image containing the specified files.
        
        :param files: The files.
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def create(images: List[aspose.imaging.Image], dispose_images: bool) -> aspose.imaging.Image:
        '''Creates a new image the specified images as pages.
        
        :param images: The images.
        :param dispose_images: if set to ``true`` [dispose images].
        :returns: The Image as IMultipageImage'''
        ...
    
    @overload
    @staticmethod
    def create_from_images(images: List[aspose.imaging.Image]) -> aspose.imaging.Image:
        '''Creates a new image using the specified images as pages
        
        :param images: The images.
        :returns: The Image as IMultipageImage'''
        ...
    
    @overload
    @staticmethod
    def create_from_images(images: List[aspose.imaging.Image], dispose_images: bool) -> aspose.imaging.Image:
        '''Creates a new image the specified images as pages.
        
        :param images: The images.
        :param dispose_images: if set to ``true`` [dispose images].
        :returns: The Image as IMultipageImage'''
        ...
    
    @overload
    @staticmethod
    def create_from_files(files: List[str], throw_exception_on_load_error: bool) -> aspose.imaging.Image:
        '''Creates the multipage image containing the specified files as lazy loading pages.
        
        :param files: The files.
        :param throw_exception_on_load_error: if set to ``true`` throw exception on load error.
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def create_from_files(files: List[str]) -> aspose.imaging.Image:
        '''Creates the multipage image containing the specified files as lazy loading pages.
        
        :param files: The files.
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(file_path: str) -> aspose.imaging.FileFormat:
        '''Gets the file format.
        
        :param file_path: The file path.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(stream: io.RawIOBase) -> aspose.imaging.FileFormat:
        '''Gets the file format.
        
        :param stream: The stream.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def get_fitting_rectangle(rectangle: aspose.imaging.Rectangle, width: int, height: int) -> aspose.imaging.Rectangle:
        '''Gets rectangle which fits the current image.
        
        :param rectangle: The rectangle to get fitting rectangle for.
        :param width: The object width.
        :param height: The object height.
        :returns: The fitting rectangle or exception if no fitting rectangle can be found.'''
        ...
    
    @overload
    @staticmethod
    def get_fitting_rectangle(rectangle: aspose.imaging.Rectangle, pixels: List[int], width: int, height: int) -> aspose.imaging.Rectangle:
        '''Gets rectangle which fits the current image.
        
        :param rectangle: The rectangle to get fitting rectangle for.
        :param pixels: The 32-bit ARGB pixels.
        :param width: The object width.
        :param height: The object height.
        :returns: The fitting rectangle or exception if no fitting rectangle can be found.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path: str, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.Image:
        '''Loads a new image from the specified file path or URL.
        If ``filePath`` is a file path the method just opens the file.
        If ``filePath`` is an URL, the method downloads the file, stores it as a temporary one, and opens it.
        
        :param file_path: The file path or URL to load image from.
        :param load_options: The load options.
        :returns: The loaded image.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path: str) -> aspose.imaging.Image:
        '''Loads a new image from the specified file path or URL.
        If ``filePath`` is a file path the method just opens the file.
        If ``filePath`` is an URL, the method downloads the file, stores it as a temporary one, and opens it.
        
        :param file_path: The file path or URL to load image from.
        :returns: The loaded image.'''
        ...
    
    @overload
    @staticmethod
    def load(stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param load_options: The load options.
        :returns: The loaded image.'''
        ...
    
    @overload
    @staticmethod
    def load(stream: io.RawIOBase) -> aspose.imaging.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :returns: The loaded image.'''
        ...
    
    @overload
    def resize(self, new_width: int, new_height: int, resize_type: aspose.imaging.ResizeType):
        '''Resizes the image.
        
        :param new_width: The new width.
        :param new_height: The new height.
        :param resize_type: The resize type.'''
        ...
    
    @overload
    def resize(self, new_width: int, new_height: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the image.
        
        :param new_width: The new width.
        :param new_height: The new height.
        :param settings: The resize settings.'''
        ...
    
    @overload
    def resize(self, new_width: int, new_height: int):
        '''Resizes the image. The default  is used.
        
        :param new_width: The new width.
        :param new_height: The new height.'''
        ...
    
    @overload
    def resize_width_proportionally(self, new_width: int):
        '''Resizes the width proportionally. The default  is used.
        
        :param new_width: The new width.'''
        ...
    
    @overload
    def resize_width_proportionally(self, new_width: int, resize_type: aspose.imaging.ResizeType):
        '''Resizes the width proportionally.
        
        :param new_width: The new width.
        :param resize_type: Type of the resize.'''
        ...
    
    @overload
    def resize_width_proportionally(self, new_width: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the width proportionally.
        
        :param new_width: The new width.
        :param settings: The image resize settings.'''
        ...
    
    @overload
    def resize_height_proportionally(self, new_height: int):
        '''Resizes the height proportionally. The default  is used.
        
        :param new_height: The new height.'''
        ...
    
    @overload
    def resize_height_proportionally(self, new_height: int, resize_type: aspose.imaging.ResizeType):
        '''Resizes the height proportionally.
        
        :param new_height: The new height.
        :param resize_type: Type of the resize.'''
        ...
    
    @overload
    def resize_height_proportionally(self, new_height: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the height proportionally.
        
        :param new_height: The new height.
        :param settings: The image resize settings.'''
        ...
    
    @overload
    def rotate(self, angle: float, resize_proportionally: bool, background_color: aspose.imaging.Color):
        '''Rotate image around the center.
        
        :param angle: The rotate angle in degrees. Positive values will rotate clockwise.
        :param resize_proportionally: if set to ``true`` you will have your image size changed according to rotated rectangle (corner points) projections in other case that leaves dimensions untouched and only internal image contents are rotated.
        :param background_color: Color of the background.'''
        ...
    
    @overload
    def rotate(self, angle: float):
        '''Rotate image around the center.
        
        :param angle: The rotate angle in degrees. Positive values will rotate clockwise.'''
        ...
    
    @overload
    def crop(self, rectangle: aspose.imaging.Rectangle):
        '''Cropping the image.
        
        :param rectangle: The rectangle.'''
        ...
    
    @overload
    def crop(self, left_shift: int, right_shift: int, top_shift: int, bottom_shift: int):
        '''Crop image with shifts.
        
        :param left_shift: The left shift.
        :param right_shift: The right shift.
        :param top_shift: The top shift.
        :param bottom_shift: The bottom shift.'''
        ...
    
    @overload
    def dither(self, dithering_method: aspose.imaging.DitheringMethod, bits_count: int, custom_palette: aspose.imaging.IColorPalette):
        '''Performs dithering on the current image.
        
        :param dithering_method: The dithering method.
        :param bits_count: The final bits count for dithering.
        :param custom_palette: The custom palette for dithering.'''
        ...
    
    @overload
    def dither(self, dithering_method: aspose.imaging.DitheringMethod, bits_count: int):
        '''Performs dithering on the current image.
        
        :param dithering_method: The dithering method.
        :param bits_count: The final bits count for dithering.'''
        ...
    
    @overload
    def get_default_raw_data(self, rectangle: aspose.imaging.Rectangle, partial_raw_data_loader: aspose.imaging.IPartialRawDataLoader, raw_data_settings: aspose.imaging.RawDataSettings):
        '''Gets the default raw data array using partial pixel loader.
        
        :param rectangle: The rectangle to get pixels for.
        :param partial_raw_data_loader: The partial raw data loader.
        :param raw_data_settings: The raw data settings.'''
        ...
    
    @overload
    def get_default_raw_data(self, rectangle: aspose.imaging.Rectangle, raw_data_settings: aspose.imaging.RawDataSettings) -> bytes:
        '''Gets the default raw data array.
        
        :param rectangle: The rectangle to get raw data for.
        :param raw_data_settings: The raw data settings.
        :returns: The default raw data array.'''
        ...
    
    @overload
    def load_raw_data(self, rectangle: aspose.imaging.Rectangle, raw_data_settings: aspose.imaging.RawDataSettings, raw_data_loader: aspose.imaging.IPartialRawDataLoader):
        '''Loads raw data.
        
        :param rectangle: The rectangle to load raw data from.
        :param raw_data_settings: The raw data settings to use for loaded data. Note if data is not in the format specified then data conversion will be performed.
        :param raw_data_loader: The raw data loader.'''
        ...
    
    @overload
    def load_raw_data(self, rectangle: aspose.imaging.Rectangle, dest_image_bounds: aspose.imaging.Rectangle, raw_data_settings: aspose.imaging.RawDataSettings, raw_data_loader: aspose.imaging.IPartialRawDataLoader):
        '''Loads raw data.
        
        :param rectangle: The rectangle to load raw data from.
        :param dest_image_bounds: The dest image bounds.
        :param raw_data_settings: The raw data settings to use for loaded data. Note if data is not in the format specified then data conversion will be performed.
        :param raw_data_loader: The raw data loader.'''
        ...
    
    @overload
    def binarize_bradley(self, brightness_difference: float, window_size: int):
        '''Binarization of an image using Bradley's adaptive thresholding algorithm using the integral image thresholding
        
        :param brightness_difference: The brightness difference between pixel and the average of an s x s window of pixels centered around this pixel.
        :param window_size: The size of s x s window of pixels centered around this pixel'''
        ...
    
    @overload
    def binarize_bradley(self, brightness_difference: float):
        '''Binarization of an image using Bradley's adaptive thresholding algorithm using the integral image thresholding
        
        :param brightness_difference: The brightness difference between pixel and the average of an s x s window of pixels centered around this pixel.'''
        ...
    
    @overload
    def blend(self, origin: aspose.imaging.Point, overlay: aspose.imaging.RasterImage, overlay_area: aspose.imaging.Rectangle, overlay_alpha: int):
        '''Blends this image instance with the ``overlay`` image.
        
        :param origin: The background image blending origin.
        :param overlay: The overlay image.
        :param overlay_area: The overlay area.
        :param overlay_alpha: The overlay alpha.'''
        ...
    
    @overload
    def blend(self, origin: aspose.imaging.Point, overlay: aspose.imaging.RasterImage, overlay_alpha: int):
        '''Blends this image instance with the ``overlay`` image.
        
        :param origin: The background image blending origin.
        :param overlay: The overlay image.
        :param overlay_alpha: The overlay alpha.'''
        ...
    
    @overload
    def adjust_gamma(self, gamma_red: float, gamma_green: float, gamma_blue: float):
        '''Gamma-correction of an image.
        
        :param gamma_red: Gamma for red channel coefficient
        :param gamma_green: Gamma for green channel coefficient
        :param gamma_blue: Gamma for blue channel coefficient'''
        ...
    
    @overload
    def adjust_gamma(self, gamma: float):
        '''Gamma-correction of an image.
        
        :param gamma: Gamma for red, green and blue channels coefficient'''
        ...
    
    @overload
    def normalize_angle(self):
        '''Normalizes the angle.
        This method is applicable to scanned text documents to get rid of the skewed scan.
        This method uses  and  methods.'''
        ...
    
    @overload
    def normalize_angle(self, resize_proportionally: bool, background_color: aspose.imaging.Color):
        '''Normalizes the angle.
        This method is applicable to scanned text documents to get rid of the skewed scan.
        This method uses  and  methods.
        
        :param resize_proportionally: if set to ``true`` you will have your image size changed according to rotated rectangle (corner points) projections in other case that leaves dimensions untouched and only internal image contents are rotated.
        :param background_color: Color of the background.'''
        ...
    
    @overload
    def replace_color(self, old_color: aspose.imaging.Color, old_color_diff: int, new_color: aspose.imaging.Color):
        '''Replaces one color to another with allowed difference and preserves original alpha value to save smooth edges.
        
        :param old_color: Old color to be replaced.
        :param old_color_diff: Allowed difference in old color to be able to widen replaced color tone.
        :param new_color: New color to replace old color with.'''
        ...
    
    @overload
    def replace_color(self, old_color_argb: int, old_color_diff: int, new_color_argb: int):
        '''Replaces one color to another with allowed difference and preserves original alpha value to save smooth edges.
        
        :param old_color_argb: Old color ARGB value to be replaced.
        :param old_color_diff: Allowed difference in old color to be able to widen replaced color tone.
        :param new_color_argb: New color ARGB value to replace old color with.'''
        ...
    
    @overload
    def replace_non_transparent_colors(self, new_color: aspose.imaging.Color):
        '''Replaces all non-transparent colors with new color and preserves original alpha value to save smooth edges.
        Note: if you use it on images without transparency, all colors will be replaced with a single one.
        
        :param new_color: New color to replace non transparent colors with.'''
        ...
    
    @overload
    def replace_non_transparent_colors(self, new_color_argb: int):
        '''Replaces all non-transparent colors with new color and preserves original alpha value to save smooth edges.
        Note: if you use it on images without transparency, all colors will be replaced with a single one.
        
        :param new_color_argb: New color ARGB value to replace non transparent colors with.'''
        ...
    
    def cache_data(self):
        '''Caches the data and ensures no additional data loading will be performed from the underlying .'''
        ...
    
    def save_to_stream(self, stream: io.RawIOBase):
        '''Saves the object's data to the specified stream.
        
        :param stream: The stream to save the object's data to.'''
        ...
    
    @staticmethod
    def can_load_with_options(file_path: str, load_options: aspose.imaging.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified file path and optionally using the specified open options.
        
        :param file_path: The file path.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @staticmethod
    def can_load_stream(stream: io.RawIOBase) -> bool:
        '''Determines whether image can be loaded from the specified stream.
        
        :param stream: The stream to load from.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @staticmethod
    def can_load_stream_with_options(stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified stream and optionally using the specified ``loadOptions``.
        
        :param stream: The stream to load from.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @staticmethod
    def get_file_format_of_stream(stream: io.RawIOBase) -> aspose.imaging.FileFormat:
        '''Gets the file format.
        
        :param stream: The stream.
        :returns: The determined file format.'''
        ...
    
    @staticmethod
    def load_with_options(file_path: str, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.Image:
        '''Loads a new image from the specified file path or URL.
        If ``filePath`` is a file path the method just opens the file.
        If ``filePath`` is an URL, the method downloads the file, stores it as a temporary one, and opens it.
        
        :param file_path: The file path or URL to load image from.
        :param load_options: The load options.
        :returns: The loaded image.'''
        ...
    
    @staticmethod
    def load_stream_with_options(stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param load_options: The load options.
        :returns: The loaded image.'''
        ...
    
    @staticmethod
    def load_stream(stream: io.RawIOBase) -> aspose.imaging.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :returns: The loaded image.'''
        ...
    
    @staticmethod
    def get_proportional_width(width: int, height: int, new_height: int) -> int:
        '''Gets a proportional width.
        
        :param width: The width.
        :param height: The height.
        :param new_height: The new height.
        :returns: The proportional width.'''
        ...
    
    @staticmethod
    def get_proportional_height(width: int, height: int, new_width: int) -> int:
        '''Gets a proportional height.
        
        :param width: The width.
        :param height: The height.
        :param new_width: The new width.
        :returns: The proportional height.'''
        ...
    
    def remove_metadata(self):
        '''Removes this image instance metadata by setting this  value to .'''
        ...
    
    def can_save(self, options: aspose.imaging.ImageOptionsBase) -> bool:
        '''Determines whether image can be saved to the specified file format represented by the passed save options.
        
        :param options: The save options to use.
        :returns: ``true`` if image can be saved to the specified file format represented by the passed save options; otherwise, ``false``.'''
        ...
    
    def resize_by_type(self, new_width: int, new_height: int, resize_type: aspose.imaging.ResizeType):
        '''Resizes the image.
        
        :param new_width: The new width.
        :param new_height: The new height.
        :param resize_type: The resize type.'''
        ...
    
    def resize_by_settings(self, new_width: int, new_height: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the image.
        
        :param new_width: The new width.
        :param new_height: The new height.
        :param settings: The resize settings.'''
        ...
    
    def get_default_options(self, args: List[any]) -> aspose.imaging.ImageOptionsBase:
        '''Gets the default options.
        
        :param args: The arguments.
        :returns: Default options'''
        ...
    
    def get_original_options(self) -> aspose.imaging.ImageOptionsBase:
        '''Gets the options based on the original file settings.
        This can be helpful to keep bit-depth and other parameters of the original image unchanged.
        For example, if we load a black-white PNG image with 1 bit per pixel and then save it using the
        method, the output PNG image with 8-bit per pixel will be produced.
        To avoid it and save PNG image with 1-bit per pixel, use this method to get corresponding saving options and pass them
        to the  method as the second parameter.
        
        :returns: The options based on the original file settings.'''
        ...
    
    def resize_width_proportionally_settings(self, new_width: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the width proportionally.
        
        :param new_width: The new width.
        :param settings: The image resize settings.'''
        ...
    
    def resize_height_proportionally_settings(self, new_height: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the height proportionally.
        
        :param new_height: The new height.
        :param settings: The image resize settings.'''
        ...
    
    def rotate_flip(self, rotate_flip_type: aspose.imaging.RotateFlipType):
        '''Rotates, flips, or rotates and flips the image.
        
        :param rotate_flip_type: The rotate flip type.'''
        ...
    
    def save_with_options(self, file_path: str, options: aspose.imaging.ImageOptionsBase):
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.'''
        ...
    
    def save_with_options_rect(self, file_path: str, options: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use sourse bounds.'''
        ...
    
    def save_to_stream_with_options(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.'''
        ...
    
    def save_to_stream_with_options_rect(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use source bounds.'''
        ...
    
    def get_serialized_stream(self, image_options: aspose.imaging.ImageOptionsBase, clipping_rectangle: aspose.imaging.Rectangle, page_number: Any) -> io.RawIOBase:
        '''Converts to aps.
        
        :param image_options: The image options.
        :param clipping_rectangle: The clipping rectangle.
        :param page_number: The page number.
        :returns: The serialized stream'''
        ...
    
    def set_palette(self, palette: aspose.imaging.IColorPalette, update_colors: bool):
        '''Sets the image palette.
        
        :param palette: The palette to set.
        :param update_colors: if set to ``true`` colors will be updated according to the new palette; otherwise color indexes remain unchanged. Note that unchanged indexes may crash the image on loading if some indexes have no corresponding palette entries.'''
        ...
    
    def get_modify_date(self, use_default: bool) -> System.DateTime:
        '''Gets the date and time the resource image was last modified.
        
        :param use_default: if set to ``true`` uses the information from FileInfo as default value.
        :returns: The date and time the resource image was last modified.'''
        ...
    
    def get_default_pixels(self, rectangle: aspose.imaging.Rectangle, partial_pixel_loader: aspose.imaging.IPartialArgb32PixelLoader):
        '''Gets the default pixels array using partial pixel loader.
        
        :param rectangle: The rectangle to get pixels for.
        :param partial_pixel_loader: The partial pixel loader.'''
        ...
    
    def get_default_argb_32_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[int]:
        '''Gets the default 32-bit ARGB pixels array.
        
        :param rectangle: The rectangle to get pixels for.
        :returns: The default pixels array.'''
        ...
    
    def get_argb_32_pixel(self, x: int, y: int) -> int:
        '''Gets an image 32-bit ARGB pixel.
        
        :param x: The pixel x location.
        :param y: The pixel y location.
        :returns: The 32-bit ARGB pixel for the specified location.'''
        ...
    
    def get_pixel(self, x: int, y: int) -> aspose.imaging.Color:
        '''Gets an image pixel.
        
        :param x: The pixel x location.
        :param y: The pixel y location.
        :returns: The pixel color for the specified location.'''
        ...
    
    def set_argb_32_pixel(self, x: int, y: int, argb_32_color: int):
        '''Sets an image 32-bit ARGB pixel for the specified position.
        
        :param x: The pixel x location.
        :param y: The pixel y location.
        :param argb_32_color: The 32-bit ARGB pixel for the specified position.'''
        ...
    
    def set_pixel(self, x: int, y: int, color: aspose.imaging.Color):
        '''Sets an image pixel for the specified position.
        
        :param x: The pixel x location.
        :param y: The pixel y location.
        :param color: The pixel color for the specified position.'''
        ...
    
    def read_scan_line(self, scan_line_index: int) -> List[aspose.imaging.Color]:
        '''Reads the whole scan line by the specified scan line index.
        
        :param scan_line_index: Zero based index of the scan line.
        :returns: The scan line pixel color values array.'''
        ...
    
    def read_argb_32_scan_line(self, scan_line_index: int) -> List[int]:
        '''Reads the whole scan line by the specified scan line index.
        
        :param scan_line_index: Zero based index of the scan line.
        :returns: The scan line 32-bit ARGB color values array.'''
        ...
    
    def write_scan_line(self, scan_line_index: int, pixels: List[aspose.imaging.Color]):
        '''Writes the whole scan line to the specified scan line index.
        
        :param scan_line_index: Zero based index of the scan line.
        :param pixels: The pixel colors array to write.'''
        ...
    
    def write_argb_32_scan_line(self, scan_line_index: int, argb_32_pixels: List[int]):
        '''Writes the whole scan line to the specified scan line index.
        
        :param scan_line_index: Zero based index of the scan line.
        :param argb_32_pixels: The 32-bit ARGB colors array to write.'''
        ...
    
    def load_partial_argb_32_pixels(self, rectangle: aspose.imaging.Rectangle, partial_pixel_loader: aspose.imaging.IPartialArgb32PixelLoader):
        '''Loads 32-bit ARGB pixels partially by packs.
        
        :param rectangle: The desired rectangle.
        :param partial_pixel_loader: The 32-bit ARGB pixel loader.'''
        ...
    
    def load_partial_pixels(self, desired_rectangle: aspose.imaging.Rectangle, pixel_loader: aspose.imaging.IPartialPixelLoader):
        '''Loads pixels partially by packs.
        
        :param desired_rectangle: The desired rectangle.
        :param pixel_loader: The pixel loader.'''
        ...
    
    def load_argb_32_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[int]:
        '''Loads 32-bit ARGB pixels.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded 32-bit ARGB pixels array.'''
        ...
    
    def load_argb_64_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[int]:
        '''Loads 64-bit ARGB pixels.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded 64-bit ARGB pixels array.'''
        ...
    
    def load_partial_argb_64_pixels(self, rectangle: aspose.imaging.Rectangle, partial_pixel_loader: aspose.imaging.IPartialArgb64PixelLoader):
        '''Loads 64-bit ARGB pixels partially by packs.
        
        :param rectangle: The desired rectangle.
        :param partial_pixel_loader: The 64-bit ARGB pixel loader.'''
        ...
    
    def load_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[aspose.imaging.Color]:
        '''Loads pixels.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded pixels array.'''
        ...
    
    def load_cmyk_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[aspose.imaging.CmykColor]:
        '''Loads pixels in CMYK format.
        This method is deprecated. Please use more effective the  method.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded CMYK pixels array.'''
        ...
    
    def load_cmyk_32_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[int]:
        '''Loads pixels in CMYK format.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded CMYK pixels presentes as 32-bit inateger values.'''
        ...
    
    def save_raw_data(self, data: bytes, data_offset: int, rectangle: aspose.imaging.Rectangle, raw_data_settings: aspose.imaging.RawDataSettings):
        '''Saves the raw data.
        
        :param data: The raw data.
        :param data_offset: The starting raw data offset.
        :param rectangle: The raw data rectangle.
        :param raw_data_settings: The raw data settings the data is in.'''
        ...
    
    def save_argb_32_pixels(self, rectangle: aspose.imaging.Rectangle, pixels: List[int]):
        '''Saves the 32-bit ARGB pixels.
        
        :param rectangle: The rectangle to save pixels to.
        :param pixels: The 32-bit ARGB pixels array.'''
        ...
    
    def save_pixels(self, rectangle: aspose.imaging.Rectangle, pixels: List[aspose.imaging.Color]):
        '''Saves the pixels.
        
        :param rectangle: The rectangle to save pixels to.
        :param pixels: The pixels array.'''
        ...
    
    def save_cmyk_pixels(self, rectangle: aspose.imaging.Rectangle, pixels: List[aspose.imaging.CmykColor]):
        '''Saves the pixels.
        This method is deprecated. Please use more effective the  method.
        
        :param rectangle: The rectangle to save pixels to.
        :param pixels: The CMYK pixels array.'''
        ...
    
    def save_cmyk_32_pixels(self, rectangle: aspose.imaging.Rectangle, pixels: List[int]):
        '''Saves the pixels.
        
        :param rectangle: The rectangle to save pixels to.
        :param pixels: The CMYK pixels presented as the 32-bit integer values.'''
        ...
    
    def set_resolution(self, dpi_x: float, dpi_y: float):
        '''Sets the resolution for this .
        
        :param dpi_x: The horizontal resolution, in dots per inch, of the .
        :param dpi_y: The vertical resolution, in dots per inch, of the .'''
        ...
    
    def binarize_fixed(self, threshold: int):
        '''Binarization of an image with predefined threshold
        
        :param threshold: Threshold value. If corresponding gray value of a pixel is greater than threshold, a value of 255 will be assigned to it, 0 otherwise.'''
        ...
    
    def binarize_otsu(self):
        '''Binarization of an image with Otsu thresholding'''
        ...
    
    def grayscale(self):
        '''Transformation of an image to its grayscale representation'''
        ...
    
    def normalize_histogram(self):
        '''Normalizes the image histogram — adjust pixel values to use all available range.'''
        ...
    
    def auto_brightness_contrast(self):
        '''Performs automatic adaptive brightness and contrast normalization for the entire image.'''
        ...
    
    def adjust_brightness(self, brightness: int):
        '''Adjust of a brightness for image.
        
        :param brightness: Brightness value.'''
        ...
    
    def adjust_contrast(self, contrast: float):
        '''Image contrasting
        
        :param contrast: Contrast value (in range [-100; 100])'''
        ...
    
    def embed_digital_signature(self, password: str):
        '''Embed digital sign based on provided password into the image using steganography.
        
        :param password: The password used for generate digital sign data'''
        ...
    
    def analyze_percentage_digital_signature(self, password: str) -> int:
        '''Calculates the percentage similarity between the extracted data and the original password.
        
        :param password: The password used to extract the embedded data.
        :returns: The percentage similarity value.'''
        ...
    
    def is_digital_signed(self, password: str, percentage_threshold: int) -> bool:
        '''Performs a fast check to determine if the image is digitally signed, using the provided password and threshold.
        
        :param password: The password to check the signing.
        :param percentage_threshold: The threshold (in percentage)[0-100] that determines if the image is considered signed.
        If not specified, a default threshold (``75``) will be applied.
        :returns: True if the image is signed, otherwise false.'''
        ...
    
    def get_skew_angle(self) -> float:
        '''Gets the skew angle.
        This method is applicable to scanned text documents, to determine the skew angle when scanning.
        
        :returns: The skew angle, in degrees.'''
        ...
    
    def filter(self, rectangle: aspose.imaging.Rectangle, options: aspose.imaging.imagefilters.filteroptions.FilterOptionsBase):
        '''Filters the specified rectangle.
        
        :param rectangle: The rectangle.
        :param options: The options.'''
        ...
    
    def replace_argb(self, old_color_argb: int, old_color_diff: int, new_color_argb: int):
        '''Replaces one color to another with allowed difference and preserves original alpha value to save smooth edges.
        
        :param old_color_argb: Old color ARGB value to be replaced.
        :param old_color_diff: Allowed difference in old color to be able to widen replaced color tone.
        :param new_color_argb: New color ARGB value to replace old color with.'''
        ...
    
    def get_full_frame(self) -> aspose.imaging.RasterImage:
        '''Gets the full frame.
        
        :returns: The full frame image.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def data_stream_container(self) -> aspose.imaging.StreamContainer:
        ...
    
    @property
    def is_cached(self) -> bool:
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets the image bounds.'''
        ...
    
    @property
    def container(self) -> aspose.imaging.Image:
        '''Gets the  container.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the image height.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette. The color palette is not used when pixels are represented directly.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette. The color palette is not used when pixels are represented directly.'''
        ...
    
    @property
    def use_palette(self) -> bool:
        ...
    
    @property
    def size(self) -> aspose.imaging.Size:
        '''Gets the image size.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the image width.'''
        ...
    
    @property
    def interrupt_monitor(self) -> aspose.imaging.multithreading.InterruptMonitor:
        ...
    
    @interrupt_monitor.setter
    def interrupt_monitor(self, value : aspose.imaging.multithreading.InterruptMonitor):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def auto_adjust_palette(self) -> bool:
        ...
    
    @auto_adjust_palette.setter
    def auto_adjust_palette(self, value : bool):
        ...
    
    @property
    def has_background_color(self) -> bool:
        ...
    
    @has_background_color.setter
    def has_background_color(self, value : bool):
        ...
    
    @property
    def file_format(self) -> aspose.imaging.FileFormat:
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def premultiply_components(self) -> bool:
        ...
    
    @premultiply_components.setter
    def premultiply_components(self, value : bool):
        ...
    
    @property
    def use_raw_data(self) -> bool:
        ...
    
    @use_raw_data.setter
    def use_raw_data(self, value : bool):
        ...
    
    @property
    def update_xmp_data(self) -> bool:
        ...
    
    @update_xmp_data.setter
    def update_xmp_data(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def raw_indexed_color_converter(self) -> aspose.imaging.IIndexedColorConverter:
        ...
    
    @raw_indexed_color_converter.setter
    def raw_indexed_color_converter(self, value : aspose.imaging.IIndexedColorConverter):
        ...
    
    @property
    def raw_custom_color_converter(self) -> aspose.imaging.IColorConverter:
        ...
    
    @raw_custom_color_converter.setter
    def raw_custom_color_converter(self, value : aspose.imaging.IColorConverter):
        ...
    
    @property
    def raw_fallback_index(self) -> int:
        ...
    
    @raw_fallback_index.setter
    def raw_fallback_index(self, value : int):
        ...
    
    @property
    def raw_data_settings(self) -> aspose.imaging.RawDataSettings:
        ...
    
    @property
    def raw_data_format(self) -> aspose.imaging.PixelDataFormat:
        ...
    
    @property
    def raw_line_size(self) -> int:
        ...
    
    @property
    def is_raw_data_available(self) -> bool:
        ...
    
    @property
    def horizontal_resolution(self) -> float:
        ...
    
    @horizontal_resolution.setter
    def horizontal_resolution(self, value : float):
        ...
    
    @property
    def vertical_resolution(self) -> float:
        ...
    
    @vertical_resolution.setter
    def vertical_resolution(self, value : float):
        ...
    
    @property
    def has_transparent_color(self) -> bool:
        ...
    
    @has_transparent_color.setter
    def has_transparent_color(self, value : bool):
        ...
    
    @property
    def has_alpha(self) -> bool:
        ...
    
    @property
    def transparent_color(self) -> aspose.imaging.Color:
        ...
    
    @transparent_color.setter
    def transparent_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def image_opacity(self) -> float:
        ...
    
    @property
    def duration(self) -> int:
        '''Gets the frame duration.'''
        ...
    
    @duration.setter
    def duration(self, value : int):
        '''Sets the frame duration.'''
        ...
    
    @property
    def left(self) -> int:
        '''Gets the frame position left.'''
        ...
    
    @left.setter
    def left(self, value : int):
        '''Sets the frame position left.'''
        ...
    
    @property
    def top(self) -> int:
        '''Gets the frame position top.'''
        ...
    
    @top.setter
    def top(self, value : int):
        '''Sets the frame position top.'''
        ...
    
    @property
    def frame_time(self) -> int:
        ...
    
    @property
    def frame_top(self) -> int:
        ...
    
    @property
    def frame_left(self) -> int:
        ...
    
    @property
    def disposal_method(self) -> aspose.imaging.AnimationDisposalMethods:
        ...
    
    @disposal_method.setter
    def disposal_method(self, value : aspose.imaging.AnimationDisposalMethods):
        ...
    
    @property
    def use_alpha_blending(self) -> bool:
        ...
    
    @use_alpha_blending.setter
    def use_alpha_blending(self, value : bool):
        ...
    
    ...

class WebPImage(aspose.imaging.RasterCachedMultipageImage):
    '''Manipulate WebP raster images with our API, using its modern features for both
    lossless and lossy compression, ensuring optimal image quality with reduced file sizes.
    Seamlessly handle extended file formats, animations, and alpha channels, while easily
    updating dimensions, resizing proportionally, cropping, rotating, applying filters,
    adjusting image parameters, and converting to other image formats for versatile
    web image optimization.'''
    
    @overload
    def __init__(self, stream: io.RawIOBase):
        '''Instantiate a new instance of the  class, initialized
        from a provided stream source. Utilize this constructor to seamlessly create WebP
        image objects directly from streams, enabling efficient handling and manipulation
        of WebP image data within your application.
        
        :param stream: The stream WebP image.'''
        ...
    
    @overload
    def __init__(self, stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions):
        '''Create a new instance of the  class using a stream and
        specified load options, facilitating versatile handling of WebP image data.
        Incorporate this constructor to seamlessly initialize WebP image objects from
        streams while customizing loading parameters as needed within your application.
        
        :param stream: The stream WebP image.
        :param load_options: The load options.'''
        ...
    
    @overload
    def __init__(self, path: str):
        '''Instantiate a fresh instance of the  class, initialized
        from a provided file source. Utilize this constructor to seamlessly create WebP
        image objects directly from files, streamlining the process of loading and
        manipulating WebP image data within your application.
        
        :param path: The path to file WebP Image'''
        ...
    
    @overload
    def __init__(self, path: str, load_options: aspose.imaging.LoadOptions):
        '''Create a new instance of the  class using a file and
        specified load options, facilitating flexible handling of WebP image data. Utilize
        this constructor to seamlessly initialize WebP image objects from files while
        customizing loading parameters according to your application's requirements.
        
        :param path: The path to file WebP Image
        :param load_options: The load options.'''
        ...
    
    @overload
    def __init__(self, raster_image: aspose.imaging.RasterImage):
        '''Instantiate a new instance of the  class, initialized
        from a provided rasterImage object. This constructor allows for seamless
        conversion of raster images to WebP format, enabling efficient handling and
        manipulation of image data within your application.
        
        :param raster_image: The raster image.'''
        ...
    
    @overload
    def __init__(self, raster_image: aspose.imaging.RasterImage, load_options: aspose.imaging.LoadOptions):
        '''Create a new instance of the  class using a rasterImage object and
        specified load options, enabling flexible handling of image data. Utilize this
        constructor to seamlessly initialize WebP image objects from raster images while
        customizing loading parameters according to your application's requirements.
        
        :param raster_image: The raster image.
        :param load_options: The load options.'''
        ...
    
    @overload
    def __init__(self, width: int, height: int, options: aspose.imaging.imageoptions.WebPOptions):
        '''Instantiate a new instance of the  class with an empty
        image of specified width and height dimensions. This constructor allows for the
        creation of blank WebP images, providing a foundation for subsequent image
        manipulation and content generation within your application.
        
        :param width: The image width
        :param height: The image height.
        :param options: The options.'''
        ...
    
    @overload
    def __init__(self, width: int, height: int, options: aspose.imaging.imageoptions.WebPOptions, load_options: aspose.imaging.LoadOptions):
        '''Create a new instance of the  class with an empty image and specified
        load options. This constructor allows for the initialization of WebP images with
        customizable loading parameters, providing flexibility in image creation and
        manipulation within your application.
        
        :param width: The image width
        :param height: The image height.
        :param options: The options.
        :param load_options: The load options.'''
        ...
    
    @overload
    def save(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use source bounds.'''
        ...
    
    @overload
    def save(self):
        '''Saves the image data to the underlying stream.'''
        ...
    
    @overload
    def save(self, file_path: str):
        '''Saves the image to the specified file location.
        
        :param file_path: The file path to save the image to.'''
        ...
    
    @overload
    def save(self, file_path: str, options: aspose.imaging.ImageOptionsBase):
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.'''
        ...
    
    @overload
    def save(self, file_path: str, options: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use sourse bounds.'''
        ...
    
    @overload
    def save(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.'''
        ...
    
    @overload
    def save(self, stream: io.RawIOBase):
        '''Saves the object's data to the specified stream.
        
        :param stream: The stream to save the object's data to.'''
        ...
    
    @overload
    def save(self, file_path: str, over_write: bool):
        '''Saves the object's data to the specified file location.
        
        :param file_path: The file path to save the object's data to.
        :param over_write: if set to ``true`` over write the file contents, otherwise append will occur.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path: str) -> bool:
        '''Determines whether image can be loaded from the specified file path.
        
        :param file_path: The file path.
        :returns: ``true`` if image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(file_path: str, load_options: aspose.imaging.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified file path and optionally using the specified open options.
        
        :param file_path: The file path.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream: io.RawIOBase) -> bool:
        '''Determines whether image can be loaded from the specified stream.
        
        :param stream: The stream to load from.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def can_load(stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified stream and optionally using the specified ``loadOptions``.
        
        :param stream: The stream to load from.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @overload
    @staticmethod
    def create(image_options: aspose.imaging.ImageOptionsBase, width: int, height: int) -> aspose.imaging.Image:
        '''Creates a new image using the specified create options.
        
        :param image_options: The image options.
        :param width: The width.
        :param height: The height.
        :returns: The newly created image.'''
        ...
    
    @overload
    @staticmethod
    def create(images: List[aspose.imaging.Image]) -> aspose.imaging.Image:
        '''Creates a new image using the specified images as pages
        
        :param images: The images.
        :returns: The Image as IMultipageImage'''
        ...
    
    @overload
    @staticmethod
    def create(multipage_create_options: aspose.imaging.imageoptions.MultipageCreateOptions) -> aspose.imaging.Image:
        '''Creates the specified multipage create options.
        
        :param multipage_create_options: The multipage create options.
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def create(files: List[str], throw_exception_on_load_error: bool) -> aspose.imaging.Image:
        '''Creates the multipage image containing the specified files.
        
        :param files: The files.
        :param throw_exception_on_load_error: if set to ``true`` [throw exception on load error].
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def create(files: List[str]) -> aspose.imaging.Image:
        '''Creates the multipage image containing the specified files.
        
        :param files: The files.
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def create(images: List[aspose.imaging.Image], dispose_images: bool) -> aspose.imaging.Image:
        '''Creates a new image the specified images as pages.
        
        :param images: The images.
        :param dispose_images: if set to ``true`` [dispose images].
        :returns: The Image as IMultipageImage'''
        ...
    
    @overload
    @staticmethod
    def create_from_images(images: List[aspose.imaging.Image]) -> aspose.imaging.Image:
        '''Creates a new image using the specified images as pages
        
        :param images: The images.
        :returns: The Image as IMultipageImage'''
        ...
    
    @overload
    @staticmethod
    def create_from_images(images: List[aspose.imaging.Image], dispose_images: bool) -> aspose.imaging.Image:
        '''Creates a new image the specified images as pages.
        
        :param images: The images.
        :param dispose_images: if set to ``true`` [dispose images].
        :returns: The Image as IMultipageImage'''
        ...
    
    @overload
    @staticmethod
    def create_from_files(files: List[str], throw_exception_on_load_error: bool) -> aspose.imaging.Image:
        '''Creates the multipage image containing the specified files as lazy loading pages.
        
        :param files: The files.
        :param throw_exception_on_load_error: if set to ``true`` throw exception on load error.
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def create_from_files(files: List[str]) -> aspose.imaging.Image:
        '''Creates the multipage image containing the specified files as lazy loading pages.
        
        :param files: The files.
        :returns: The multipage image'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(file_path: str) -> aspose.imaging.FileFormat:
        '''Gets the file format.
        
        :param file_path: The file path.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def get_file_format(stream: io.RawIOBase) -> aspose.imaging.FileFormat:
        '''Gets the file format.
        
        :param stream: The stream.
        :returns: The determined file format.'''
        ...
    
    @overload
    @staticmethod
    def get_fitting_rectangle(rectangle: aspose.imaging.Rectangle, width: int, height: int) -> aspose.imaging.Rectangle:
        '''Gets rectangle which fits the current image.
        
        :param rectangle: The rectangle to get fitting rectangle for.
        :param width: The object width.
        :param height: The object height.
        :returns: The fitting rectangle or exception if no fitting rectangle can be found.'''
        ...
    
    @overload
    @staticmethod
    def get_fitting_rectangle(rectangle: aspose.imaging.Rectangle, pixels: List[int], width: int, height: int) -> aspose.imaging.Rectangle:
        '''Gets rectangle which fits the current image.
        
        :param rectangle: The rectangle to get fitting rectangle for.
        :param pixels: The 32-bit ARGB pixels.
        :param width: The object width.
        :param height: The object height.
        :returns: The fitting rectangle or exception if no fitting rectangle can be found.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path: str, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.Image:
        '''Loads a new image from the specified file path or URL.
        If ``filePath`` is a file path the method just opens the file.
        If ``filePath`` is an URL, the method downloads the file, stores it as a temporary one, and opens it.
        
        :param file_path: The file path or URL to load image from.
        :param load_options: The load options.
        :returns: The loaded image.'''
        ...
    
    @overload
    @staticmethod
    def load(file_path: str) -> aspose.imaging.Image:
        '''Loads a new image from the specified file path or URL.
        If ``filePath`` is a file path the method just opens the file.
        If ``filePath`` is an URL, the method downloads the file, stores it as a temporary one, and opens it.
        
        :param file_path: The file path or URL to load image from.
        :returns: The loaded image.'''
        ...
    
    @overload
    @staticmethod
    def load(stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param load_options: The load options.
        :returns: The loaded image.'''
        ...
    
    @overload
    @staticmethod
    def load(stream: io.RawIOBase) -> aspose.imaging.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :returns: The loaded image.'''
        ...
    
    @overload
    def resize(self, new_width: int, new_height: int, resize_type: aspose.imaging.ResizeType):
        '''Resize the image, adjusting its dimensions while preserving the aspect ratio.
        Integrate this method into your image processing workflow to dynamically scale
        images to fit various display or storage requirements within your application.
        
        :param new_width: The new width.
        :param new_height: The new height.
        :param resize_type: The resize type.'''
        ...
    
    @overload
    def resize(self, new_width: int, new_height: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resize the image according to specified settings, enabling precise control over
        dimensions, aspect ratio, and scaling behavior. Integrate this method into your
        image processing workflow to achieve customized resizing operations tailored to
        the specific requirements of your application.
        
        :param new_width: The new width.
        :param new_height: The new height.
        :param settings: The resize settings.'''
        ...
    
    @overload
    def resize(self, new_width: int, new_height: int):
        '''Resizes the image. The default  is used.
        
        :param new_width: The new width.
        :param new_height: The new height.'''
        ...
    
    @overload
    def resize_width_proportionally(self, new_width: int, resize_type: aspose.imaging.ResizeType):
        '''Proportionally adjust the width of the image while maintaining its aspect ratio.
        Integrate this method into your image processing workflow to dynamically resize
        images with consistent proportions, ensuring optimal display or storage within
        your application.
        
        :param new_width: The new width.
        :param resize_type: Type of the resize.'''
        ...
    
    @overload
    def resize_width_proportionally(self, new_width: int):
        '''Resizes the width proportionally. The default  is used.
        
        :param new_width: The new width.'''
        ...
    
    @overload
    def resize_width_proportionally(self, new_width: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the width proportionally.
        
        :param new_width: The new width.
        :param settings: The image resize settings.'''
        ...
    
    @overload
    def resize_height_proportionally(self, new_height: int, resize_type: aspose.imaging.ResizeType):
        '''Adjust the height of the image proportionally, while preserving its aspect ratio
        for consistent resizing. Integrate this method into your image processing workflow
        to dynamically resize images with uniform proportions, ensuring optimal display or
        storage within your application.
        
        :param new_height: The new height.
        :param resize_type: Type of the resize.'''
        ...
    
    @overload
    def resize_height_proportionally(self, new_height: int):
        '''Resizes the height proportionally. The default  is used.
        
        :param new_height: The new height.'''
        ...
    
    @overload
    def resize_height_proportionally(self, new_height: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the height proportionally.
        
        :param new_height: The new height.
        :param settings: The image resize settings.'''
        ...
    
    @overload
    def rotate(self, angle: float, resize_proportionally: bool, background_color: aspose.imaging.Color):
        '''Rotate the image around its center by a specified angle, while proportionally
        resizing it and applying specified background color parameters. Incorporate this
        method into your image processing workflow to achieve precise transformations with
        customizable background colors, ensuring optimal visual presentation within your
        application.
        
        :param angle: The rotate angle in degrees. Positive values will rotate clockwise.
        :param resize_proportionally: if set to ``true`` you will have your image size changed
        according to rotated rectangle (corner points) projections in other
        case that leaves dimensions untouched and only
        image contents are rotated.
        :param background_color: Color of the background.'''
        ...
    
    @overload
    def rotate(self, angle: float):
        '''Rotate image around the center.
        
        :param angle: The rotate angle in degrees. Positive values will rotate clockwise.'''
        ...
    
    @overload
    def crop(self, rectangle: aspose.imaging.Rectangle):
        '''Crop the image using a specified rectangle region, removing unwanted portions
        while retaining the desired content. Integrate this method into your image
        processing workflow to precisely extract and focus on specific areas of interest
        within the image, enhancing clarity and composition for various applications.
        
        :param rectangle: The rectangle.'''
        ...
    
    @overload
    def crop(self, left_shift: int, right_shift: int, top_shift: int, bottom_shift: int):
        '''Crop the image by applying left, right, top, and bottom shifts, effectively
        selecting a region of interest within the image. Utilize this method to
        dynamically extract desired portions of the image while adjusting its composition
        and focus according to your application's requirements.
        
        :param left_shift: The left shift.
        :param right_shift: The right shift.
        :param top_shift: The top shift.
        :param bottom_shift: The bottom shift.'''
        ...
    
    @overload
    def dither(self, dithering_method: aspose.imaging.DitheringMethod, bits_count: int, custom_palette: aspose.imaging.IColorPalette):
        '''Perform dithering on the current image to reduce color banding and enhance visual
        quality. Integrate this method into your image processing workflow to achieve
        smoother transitions between colors and improve the overall appearance of the
        image within your application.
        
        :param dithering_method: The dithering method.
        :param bits_count: The final bits count for dithering.
        :param custom_palette: The custom palette for dithering.'''
        ...
    
    @overload
    def dither(self, dithering_method: aspose.imaging.DitheringMethod, bits_count: int):
        '''Performs dithering on the current image.
        
        :param dithering_method: The dithering method.
        :param bits_count: The final bits count for dithering.'''
        ...
    
    @overload
    def get_default_raw_data(self, rectangle: aspose.imaging.Rectangle, partial_raw_data_loader: aspose.imaging.IPartialRawDataLoader, raw_data_settings: aspose.imaging.RawDataSettings):
        '''Gets the default raw data array using partial pixel loader.
        
        :param rectangle: The rectangle to get pixels for.
        :param partial_raw_data_loader: The partial raw data loader.
        :param raw_data_settings: The raw data settings.'''
        ...
    
    @overload
    def get_default_raw_data(self, rectangle: aspose.imaging.Rectangle, raw_data_settings: aspose.imaging.RawDataSettings) -> bytes:
        '''Gets the default raw data array.
        
        :param rectangle: The rectangle to get raw data for.
        :param raw_data_settings: The raw data settings.
        :returns: The default raw data array.'''
        ...
    
    @overload
    def load_raw_data(self, rectangle: aspose.imaging.Rectangle, raw_data_settings: aspose.imaging.RawDataSettings, raw_data_loader: aspose.imaging.IPartialRawDataLoader):
        '''Loads raw data.
        
        :param rectangle: The rectangle to load raw data from.
        :param raw_data_settings: The raw data settings to use for loaded data. Note if data is not in the format specified then data conversion will be performed.
        :param raw_data_loader: The raw data loader.'''
        ...
    
    @overload
    def load_raw_data(self, rectangle: aspose.imaging.Rectangle, dest_image_bounds: aspose.imaging.Rectangle, raw_data_settings: aspose.imaging.RawDataSettings, raw_data_loader: aspose.imaging.IPartialRawDataLoader):
        '''Loads raw data.
        
        :param rectangle: The rectangle to load raw data from.
        :param dest_image_bounds: The dest image bounds.
        :param raw_data_settings: The raw data settings to use for loaded data. Note if data is not in the format specified then data conversion will be performed.
        :param raw_data_loader: The raw data loader.'''
        ...
    
    @overload
    def binarize_bradley(self, brightness_difference: float, window_size: int):
        '''Apply binarization to the image using Bradley's adaptive thresholding algorithm
        with integral image thresholding. This method dynamically computes local
        thresholds based on the image's neighborhood, enhancing adaptability to varying
        lighting conditions and ensuring robust segmentation for subsequent processing
        tasks within your application.
        
        :param brightness_difference: The brightness difference between pixel and the average of an s x s window of pixels
        centered around this pixel.
        :param window_size: The size of s x s window of pixels centered around this pixel'''
        ...
    
    @overload
    def binarize_bradley(self, brightness_difference: float):
        '''Binarization of an image using Bradley's adaptive thresholding algorithm using the integral image thresholding
        
        :param brightness_difference: The brightness difference between pixel and the average of an s x s window of pixels
        centered around this pixel.'''
        ...
    
    @overload
    def blend(self, origin: aspose.imaging.Point, overlay: aspose.imaging.RasterImage, overlay_area: aspose.imaging.Rectangle, overlay_alpha: int):
        '''Blends this image instance with the ``overlay`` image.
        
        :param origin: The background image blending origin.
        :param overlay: The overlay image.
        :param overlay_area: The overlay area.
        :param overlay_alpha: The overlay alpha.'''
        ...
    
    @overload
    def blend(self, origin: aspose.imaging.Point, overlay: aspose.imaging.RasterImage, overlay_alpha: int):
        '''Blends this image instance with the ``overlay`` image.
        
        :param origin: The background image blending origin.
        :param overlay: The overlay image.
        :param overlay_alpha: The overlay alpha.'''
        ...
    
    @overload
    def adjust_gamma(self, gamma: float):
        '''Apply gamma correction to the image, adjusting pixel intensities to achieve
        desired brightness and color balance. Incorporate this method into your image
        processing workflow to enhance visual quality and improve the accuracy of
        subsequent analysis or display tasks within your application.
        
        :param gamma: Gamma for red, green and blue channels coefficient'''
        ...
    
    @overload
    def adjust_gamma(self, gamma_red: float, gamma_green: float, gamma_blue: float):
        '''Perform gamma correction on the image using individual coefficients for the red,
        green, and blue channels, allowing for fine-tuned adjustments of color balance and
        contrast. Integrate this method into your image processing pipeline to achieve
        precise control over color rendering and enhance visual fidelity within your
        application.
        
        :param gamma_red: Gamma for red channel coefficient
        :param gamma_green: Gamma for green channel coefficient
        :param gamma_blue: Gamma for blue channel coefficient'''
        ...
    
    @overload
    def normalize_angle(self, resize_proportionally: bool, background_color: aspose.imaging.Color):
        '''Normalizes the angle.
        This method is applicable to scanned text documents to get rid of the skewed scan.
        This method uses  and  methods.
        
        :param resize_proportionally: if set to ``true`` you will have your image size changed according to rotated rectangle (corner points) projections in other case that leaves dimensions untouched and only internal image contents are rotated.
        :param background_color: Color of the background.'''
        ...
    
    @overload
    def normalize_angle(self):
        '''Normalizes the angle.
        This method is applicable to scanned text documents to get rid of the skewed scan.
        This method uses  and  methods.'''
        ...
    
    @overload
    def replace_color(self, old_color_argb: int, old_color_diff: int, new_color_argb: int):
        '''Replaces one color to another with allowed difference and preserves original alpha value to save smooth edges.
        
        :param old_color_argb: Old color ARGB value to be replaced.
        :param old_color_diff: Allowed difference in old color to be able to widen replaced color tone.
        :param new_color_argb: New color ARGB value to replace old color with.'''
        ...
    
    @overload
    def replace_color(self, old_color: aspose.imaging.Color, old_color_diff: int, new_color: aspose.imaging.Color):
        '''Replaces one color to another with allowed difference and preserves original alpha value to save smooth edges.
        
        :param old_color: Old color to be replaced.
        :param old_color_diff: Allowed difference in old color to be able to widen replaced color tone.
        :param new_color: New color to replace old color with.'''
        ...
    
    @overload
    def replace_non_transparent_colors(self, new_color_argb: int):
        '''Replaces all non-transparent colors with new color and preserves original alpha value to save smooth edges.
        Note: if you use it on images without transparency, all colors will be replaced with a single one.
        
        :param new_color_argb: New color ARGB value to replace non transparent colors with.'''
        ...
    
    @overload
    def replace_non_transparent_colors(self, new_color: aspose.imaging.Color):
        '''Replaces all non-transparent colors with new color and preserves original alpha value to save smooth edges.
        Note: if you use it on images without transparency, all colors will be replaced with a single one.
        
        :param new_color: New color to replace non transparent colors with.'''
        ...
    
    def cache_data(self):
        '''Caches the data private.'''
        ...
    
    def save_to_stream(self, stream: io.RawIOBase):
        '''Saves the object's data to the specified stream.
        
        :param stream: The stream to save the object's data to.'''
        ...
    
    @staticmethod
    def can_load_with_options(file_path: str, load_options: aspose.imaging.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified file path and optionally using the specified open options.
        
        :param file_path: The file path.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified file; otherwise, ``false``.'''
        ...
    
    @staticmethod
    def can_load_stream(stream: io.RawIOBase) -> bool:
        '''Determines whether image can be loaded from the specified stream.
        
        :param stream: The stream to load from.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @staticmethod
    def can_load_stream_with_options(stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions) -> bool:
        '''Determines whether image can be loaded from the specified stream and optionally using the specified ``loadOptions``.
        
        :param stream: The stream to load from.
        :param load_options: The load options.
        :returns: ``true`` if image can be loaded from the specified stream; otherwise, ``false``.'''
        ...
    
    @staticmethod
    def get_file_format_of_stream(stream: io.RawIOBase) -> aspose.imaging.FileFormat:
        '''Gets the file format.
        
        :param stream: The stream.
        :returns: The determined file format.'''
        ...
    
    @staticmethod
    def load_with_options(file_path: str, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.Image:
        '''Loads a new image from the specified file path or URL.
        If ``filePath`` is a file path the method just opens the file.
        If ``filePath`` is an URL, the method downloads the file, stores it as a temporary one, and opens it.
        
        :param file_path: The file path or URL to load image from.
        :param load_options: The load options.
        :returns: The loaded image.'''
        ...
    
    @staticmethod
    def load_stream_with_options(stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :param load_options: The load options.
        :returns: The loaded image.'''
        ...
    
    @staticmethod
    def load_stream(stream: io.RawIOBase) -> aspose.imaging.Image:
        '''Loads a new image from the specified stream.
        
        :param stream: The stream to load image from.
        :returns: The loaded image.'''
        ...
    
    @staticmethod
    def get_proportional_width(width: int, height: int, new_height: int) -> int:
        '''Gets a proportional width.
        
        :param width: The width.
        :param height: The height.
        :param new_height: The new height.
        :returns: The proportional width.'''
        ...
    
    @staticmethod
    def get_proportional_height(width: int, height: int, new_width: int) -> int:
        '''Gets a proportional height.
        
        :param width: The width.
        :param height: The height.
        :param new_width: The new width.
        :returns: The proportional height.'''
        ...
    
    def remove_metadata(self):
        '''Removes this image instance metadata by setting this  value to .'''
        ...
    
    def can_save(self, options: aspose.imaging.ImageOptionsBase) -> bool:
        '''Determines whether image can be saved to the specified file format represented by the passed save options.
        
        :param options: The save options to use.
        :returns: ``true`` if image can be saved to the specified file format represented by the passed save options; otherwise, ``false``.'''
        ...
    
    def resize_by_type(self, new_width: int, new_height: int, resize_type: aspose.imaging.ResizeType):
        '''Resizes the image.
        
        :param new_width: The new width.
        :param new_height: The new height.
        :param resize_type: The resize type.'''
        ...
    
    def resize_by_settings(self, new_width: int, new_height: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the image.
        
        :param new_width: The new width.
        :param new_height: The new height.
        :param settings: The resize settings.'''
        ...
    
    def get_default_options(self, args: List[any]) -> aspose.imaging.ImageOptionsBase:
        '''Gets the default options.
        
        :param args: The arguments.
        :returns: Default options'''
        ...
    
    def get_original_options(self) -> aspose.imaging.ImageOptionsBase:
        '''Gets the options based on the original file settings.
        This can be helpful to keep bit-depth and other parameters of the original image unchanged.
        For example, if we load a black-white PNG image with 1 bit per pixel and then save it using the
        method, the output PNG image with 8-bit per pixel will be produced.
        To avoid it and save PNG image with 1-bit per pixel, use this method to get corresponding saving options and pass them
        to the  method as the second parameter.
        
        :returns: The options based on the original file settings.'''
        ...
    
    def resize_width_proportionally_settings(self, new_width: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the width proportionally.
        
        :param new_width: The new width.
        :param settings: The image resize settings.'''
        ...
    
    def resize_height_proportionally_settings(self, new_height: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the height proportionally.
        
        :param new_height: The new height.
        :param settings: The image resize settings.'''
        ...
    
    def rotate_flip(self, rotate_flip_type: aspose.imaging.RotateFlipType):
        '''Apply rotation, flipping, or both operations exclusively to the active frame
        within the image. Integrate this method into your image processing workflow to
        achieve precise manipulation of individual frames, enhancing flexibility and
        control over frame transformations within your application.
        
        :param rotate_flip_type: The rotate flip type.'''
        ...
    
    def save_with_options(self, file_path: str, options: aspose.imaging.ImageOptionsBase):
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.'''
        ...
    
    def save_with_options_rect(self, file_path: str, options: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the object's data to the specified file location in the specified file format according to save options.
        
        :param file_path: The file path.
        :param options: The options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use sourse bounds.'''
        ...
    
    def save_to_stream_with_options(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.'''
        ...
    
    def save_to_stream_with_options_rect(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use source bounds.'''
        ...
    
    def get_serialized_stream(self, image_options: aspose.imaging.ImageOptionsBase, clipping_rectangle: aspose.imaging.Rectangle, page_number: Any) -> io.RawIOBase:
        '''Converts to aps.
        
        :param image_options: The image options.
        :param clipping_rectangle: The clipping rectangle.
        :param page_number: The page number.
        :returns: The serialized stream'''
        ...
    
    def set_palette(self, palette: aspose.imaging.IColorPalette, update_colors: bool):
        '''Sets the image palette.
        
        :param palette: The palette to set.
        :param update_colors: if set to ``true`` colors will be updated according to the new palette; otherwise color indexes remain unchanged. Note that unchanged indexes may crash the image on loading if some indexes have no corresponding palette entries.'''
        ...
    
    def get_modify_date(self, use_default: bool) -> System.DateTime:
        '''Gets the date and time the resource image was last modified.
        
        :param use_default: if set to ``true`` uses the information from FileInfo as default value.
        :returns: The date and time the resource image was last modified.'''
        ...
    
    def get_default_pixels(self, rectangle: aspose.imaging.Rectangle, partial_pixel_loader: aspose.imaging.IPartialArgb32PixelLoader):
        '''Gets the default pixels array using partial pixel loader.
        
        :param rectangle: The rectangle to get pixels for.
        :param partial_pixel_loader: The partial pixel loader.'''
        ...
    
    def get_default_argb_32_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[int]:
        '''Gets the default 32-bit ARGB pixels array.
        
        :param rectangle: The rectangle to get pixels for.
        :returns: The default pixels array.'''
        ...
    
    def get_argb_32_pixel(self, x: int, y: int) -> int:
        '''Gets an image 32-bit ARGB pixel.
        
        :param x: The pixel x location.
        :param y: The pixel y location.
        :returns: The 32-bit ARGB pixel for the specified location.'''
        ...
    
    def get_pixel(self, x: int, y: int) -> aspose.imaging.Color:
        '''Gets an image pixel.
        
        :param x: The pixel x location.
        :param y: The pixel y location.
        :returns: The pixel color for the specified location.'''
        ...
    
    def set_argb_32_pixel(self, x: int, y: int, argb_32_color: int):
        '''Sets an image 32-bit ARGB pixel for the specified position.
        
        :param x: The pixel x location.
        :param y: The pixel y location.
        :param argb_32_color: The 32-bit ARGB pixel for the specified position.'''
        ...
    
    def set_pixel(self, x: int, y: int, color: aspose.imaging.Color):
        '''Sets an image pixel for the specified position.
        
        :param x: The pixel x location.
        :param y: The pixel y location.
        :param color: The pixel color for the specified position.'''
        ...
    
    def read_scan_line(self, scan_line_index: int) -> List[aspose.imaging.Color]:
        '''Reads the whole scan line by the specified scan line index.
        
        :param scan_line_index: Zero based index of the scan line.
        :returns: The scan line pixel color values array.'''
        ...
    
    def read_argb_32_scan_line(self, scan_line_index: int) -> List[int]:
        '''Reads the whole scan line by the specified scan line index.
        
        :param scan_line_index: Zero based index of the scan line.
        :returns: The scan line 32-bit ARGB color values array.'''
        ...
    
    def write_scan_line(self, scan_line_index: int, pixels: List[aspose.imaging.Color]):
        '''Writes the whole scan line to the specified scan line index.
        
        :param scan_line_index: Zero based index of the scan line.
        :param pixels: The pixel colors array to write.'''
        ...
    
    def write_argb_32_scan_line(self, scan_line_index: int, argb_32_pixels: List[int]):
        '''Writes the whole scan line to the specified scan line index.
        
        :param scan_line_index: Zero based index of the scan line.
        :param argb_32_pixels: The 32-bit ARGB colors array to write.'''
        ...
    
    def load_partial_argb_32_pixels(self, rectangle: aspose.imaging.Rectangle, partial_pixel_loader: aspose.imaging.IPartialArgb32PixelLoader):
        '''Loads 32-bit ARGB pixels partially by packs.
        
        :param rectangle: The desired rectangle.
        :param partial_pixel_loader: The 32-bit ARGB pixel loader.'''
        ...
    
    def load_partial_pixels(self, desired_rectangle: aspose.imaging.Rectangle, pixel_loader: aspose.imaging.IPartialPixelLoader):
        '''Loads pixels partially by packs.
        
        :param desired_rectangle: The desired rectangle.
        :param pixel_loader: The pixel loader.'''
        ...
    
    def load_argb_32_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[int]:
        '''Loads 32-bit ARGB pixels.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded 32-bit ARGB pixels array.'''
        ...
    
    def load_argb_64_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[int]:
        '''Loads 64-bit ARGB pixels.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded 64-bit ARGB pixels array.'''
        ...
    
    def load_partial_argb_64_pixels(self, rectangle: aspose.imaging.Rectangle, partial_pixel_loader: aspose.imaging.IPartialArgb64PixelLoader):
        '''Loads 64-bit ARGB pixels partially by packs.
        
        :param rectangle: The desired rectangle.
        :param partial_pixel_loader: The 64-bit ARGB pixel loader.'''
        ...
    
    def load_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[aspose.imaging.Color]:
        '''Loads pixels.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded pixels array.'''
        ...
    
    def load_cmyk_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[aspose.imaging.CmykColor]:
        '''Loads pixels in CMYK format.
        This method is deprecated. Please use more effective the  method.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded CMYK pixels array.'''
        ...
    
    def load_cmyk_32_pixels(self, rectangle: aspose.imaging.Rectangle) -> List[int]:
        '''Loads pixels in CMYK format.
        
        :param rectangle: The rectangle to load pixels from.
        :returns: The loaded CMYK pixels presentes as 32-bit inateger values.'''
        ...
    
    def save_raw_data(self, data: bytes, data_offset: int, rectangle: aspose.imaging.Rectangle, raw_data_settings: aspose.imaging.RawDataSettings):
        '''Saves the raw data.
        
        :param data: The raw data.
        :param data_offset: The starting raw data offset.
        :param rectangle: The raw data rectangle.
        :param raw_data_settings: The raw data settings the data is in.'''
        ...
    
    def save_argb_32_pixels(self, rectangle: aspose.imaging.Rectangle, pixels: List[int]):
        '''Saves the 32-bit ARGB pixels.
        
        :param rectangle: The rectangle to save pixels to.
        :param pixels: The 32-bit ARGB pixels array.'''
        ...
    
    def save_pixels(self, rectangle: aspose.imaging.Rectangle, pixels: List[aspose.imaging.Color]):
        '''Saves the pixels.
        
        :param rectangle: The rectangle to save pixels to.
        :param pixels: The pixels array.'''
        ...
    
    def save_cmyk_pixels(self, rectangle: aspose.imaging.Rectangle, pixels: List[aspose.imaging.CmykColor]):
        '''Saves the pixels.
        This method is deprecated. Please use more effective the  method.
        
        :param rectangle: The rectangle to save pixels to.
        :param pixels: The CMYK pixels array.'''
        ...
    
    def save_cmyk_32_pixels(self, rectangle: aspose.imaging.Rectangle, pixels: List[int]):
        '''Saves the pixels.
        
        :param rectangle: The rectangle to save pixels to.
        :param pixels: The CMYK pixels presented as the 32-bit integer values.'''
        ...
    
    def set_resolution(self, dpi_x: float, dpi_y: float):
        '''Sets the resolution for this .
        
        :param dpi_x: The horizontal resolution, in dots per inch, of the .
        :param dpi_y: The vertical resolution, in dots per inch, of the .'''
        ...
    
    def binarize_fixed(self, threshold: int):
        '''Perform binarization on the image using a predefined threshold value, converting
        it into a binary image where pixels are classified as foreground or background
        based on their intensity relative to the threshold. Integrate this method into
        your image processing workflow to facilitate segmentation and feature extraction
        tasks, enhancing the accuracy and efficiency of subsequent analysis within your
        application.
        
        :param threshold: Threshold value. If corresponding gray value of a pixel is greater than threshold, a value of
        255 will be assigned to it, 0 otherwise.'''
        ...
    
    def binarize_otsu(self):
        '''Perform binarization on the image using Otsu's thresholding method, automatically
        determining the optimal threshold value based on the image's histogram. Integrate
        this method into your image processing workflow to achieve effective segmentation
        and feature extraction, enhancing the accuracy and reliability of image analysis
        tasks within your application.'''
        ...
    
    def grayscale(self):
        '''Convert the image to its grayscale representation, transforming it into a
        single-channel image where each pixel represents intensity or luminance. Integrate
        this method into your image processing pipeline to simplify analysis and enhance
        compatibility with grayscale-based algorithms, facilitating various computer
        vision and image analysis tasks within your application.'''
        ...
    
    def normalize_histogram(self):
        '''Normalizes the image histogram — adjust pixel values to use all available range.'''
        ...
    
    def auto_brightness_contrast(self):
        '''Performs automatic adaptive brightness and contrast normalization for the entire image.'''
        ...
    
    def adjust_brightness(self, brightness: int):
        '''Implement ``brightness`` adjustment for the image, allowing the
        modification of overall luminance levels. Incorporate this method into your image
        processing workflow to enhance visibility and improve the visual quality of images
        within your application.
        
        :param brightness: Brightness value.'''
        ...
    
    def adjust_contrast(self, contrast: float):
        '''Enhance the contrast of the , amplifying the
        differences between light and dark areas. Integrate this method into your image
        processing workflow to improve visual clarity and overall image quality within
        your application.
        
        :param contrast: Contrast value (in range [-100; 100])'''
        ...
    
    def embed_digital_signature(self, password: str):
        '''Embed digital sign based on provided password into each page of the image.
        
        :param password: The password used for generate digital sign data'''
        ...
    
    def analyze_percentage_digital_signature(self, password: str) -> int:
        '''Calculates the percentage similarity between the extracted data and the original password.
        
        :param password: The password used to extract the embedded data.
        :returns: The percentage similarity value.'''
        ...
    
    def is_digital_signed(self, password: str, percentage_threshold: int) -> bool:
        '''Performs a fast check to determine if the image is digitally signed, using the provided password and threshold.
        
        :param password: The password to check the signing.
        :param percentage_threshold: The threshold (in percentage)[0-100] that determines if the image is considered signed.
        If not specified, a default threshold (``75``) will be applied.
        :returns: True if the image is signed, otherwise false.'''
        ...
    
    def get_skew_angle(self) -> float:
        '''Gets the skew angle.
        This method is applicable to scanned text documents, to determine the skew angle when scanning.
        
        :returns: The skew angle, in degrees.'''
        ...
    
    def filter(self, rectangle: aspose.imaging.Rectangle, options: aspose.imaging.imagefilters.filteroptions.FilterOptionsBase):
        '''Filter the content within the specified rectangle, applying a designated image
        processing filter to enhance or modify the selected region. Integrate this method
        into your image manipulation workflow to achieve targeted enhancements or
        transformations within your application.
        
        :param rectangle: The rectangle.
        :param options: The options.'''
        ...
    
    def replace_argb(self, old_color_argb: int, old_color_diff: int, new_color_argb: int):
        '''Replaces one color to another with allowed difference and preserves original alpha value to save smooth edges.
        
        :param old_color_argb: Old color ARGB value to be replaced.
        :param old_color_diff: Allowed difference in old color to be able to widen replaced color tone.
        :param new_color_argb: New color ARGB value to replace old color with.'''
        ...
    
    def rotate_flip_all(self, rotate_flip: aspose.imaging.RotateFlipType):
        '''Rotates the flip all.
        
        :param rotate_flip: The rotate flip.'''
        ...
    
    @staticmethod
    def create_from_stream(stream: io.RawIOBase) -> aspose.imaging.fileformats.webp.WebPImage:
        '''Initializes a new instance of the  class
        from stream.
        
        :param stream: The stream WebP image.'''
        ...
    
    @staticmethod
    def create_from_stream_with_options(stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.fileformats.webp.WebPImage:
        '''Initializes a new instance of the  class from stream.
        
        :param stream: The stream WebP image.
        :param load_options: The load options.'''
        ...
    
    @staticmethod
    def create_from_file_with_options(path: str, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.fileformats.webp.WebPImage:
        '''Initializes a new instance of the  class from file.
        
        :param path: The path to file WebP Image
        :param load_options: The load options.'''
        ...
    
    @staticmethod
    def create_from_image(raster_image: aspose.imaging.RasterImage) -> aspose.imaging.fileformats.webp.WebPImage:
        '''Initializes a new instance of the  class from rasterImage.
        
        :param raster_image: The raster image.'''
        ...
    
    @staticmethod
    def create_from_image_with_options(raster_image: aspose.imaging.RasterImage, load_options: aspose.imaging.LoadOptions) -> aspose.imaging.fileformats.webp.WebPImage:
        '''Initializes a new instance of the  class from rasterImage.
        
        :param raster_image: The raster image.
        :param load_options: The load options.'''
        ...
    
    def add_page(self, page: aspose.imaging.RasterImage):
        '''Append a new page to the image, expanding its content and accommodating additional
        visual elements. Integrate this method to facilitate dynamic page management
        within your application, enabling seamless creation and augmentation of multi-page
        documents or images.
        
        :param page: The page to add.'''
        ...
    
    def add_block(self, block: aspose.imaging.fileformats.webp.IFrame):
        '''Incorporate a new WebP block into the image, enriching its content and
        facilitating advanced image manipulation. Integrate this method to dynamically
        enhance the structure and complexity of the WebP image data within your
        application, enabling precise control and optimization of image rendering.
        
        :param block: The Webp block to add.'''
        ...
    
    def clear_blocks(self):
        '''Clear all existing WebP blocks from the image, facilitating a clean slate for
        subsequent modifications or additions. Utilize this method to effectively reset
        the block structure within the WebP image data, ensuring optimal management and
        organization of image content within your application.'''
        ...
    
    def insert_block(self, index: int, block: aspose.imaging.fileformats.webp.IFrame):
        '''Insert a new WebP block at the specified index within the image, enabling precise
        control over the block sequence. Integrate this method to seamlessly incorporate
        additional WebP blocks into the image data structure, facilitating advanced image
        processing and optimization within your application.
        
        :param index: The zero-based element, at which ``block`` will be
        inserted.
        :param block: The Webp block to add.'''
        ...
    
    def remove_block(self, block: aspose.imaging.fileformats.webp.IFrame):
        '''Remove the specified WebP block from the image, facilitating efficient management
        of image data structure. Utilize this method to streamline image processing
        workflows by eliminating unnecessary blocks or components within your application.
        
        :param block: The block to remove.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def data_stream_container(self) -> aspose.imaging.StreamContainer:
        ...
    
    @property
    def is_cached(self) -> bool:
        ...
    
    @property
    def bits_per_pixel(self) -> int:
        ...
    
    @property
    def bounds(self) -> aspose.imaging.Rectangle:
        '''Gets the image bounds.'''
        ...
    
    @property
    def container(self) -> aspose.imaging.Image:
        '''Gets the  container.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the image height.'''
        ...
    
    @property
    def palette(self) -> aspose.imaging.IColorPalette:
        '''Gets the color palette. The color palette is not used when pixels are represented directly.'''
        ...
    
    @palette.setter
    def palette(self, value : aspose.imaging.IColorPalette):
        '''Sets the color palette. The color palette is not used when pixels are represented directly.'''
        ...
    
    @property
    def use_palette(self) -> bool:
        ...
    
    @property
    def size(self) -> aspose.imaging.Size:
        '''Gets the image size.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the image width.'''
        ...
    
    @property
    def interrupt_monitor(self) -> aspose.imaging.multithreading.InterruptMonitor:
        ...
    
    @interrupt_monitor.setter
    def interrupt_monitor(self, value : aspose.imaging.multithreading.InterruptMonitor):
        ...
    
    @property
    def buffer_size_hint(self) -> int:
        ...
    
    @buffer_size_hint.setter
    def buffer_size_hint(self, value : int):
        ...
    
    @property
    def auto_adjust_palette(self) -> bool:
        ...
    
    @auto_adjust_palette.setter
    def auto_adjust_palette(self, value : bool):
        ...
    
    @property
    def has_background_color(self) -> bool:
        ...
    
    @has_background_color.setter
    def has_background_color(self, value : bool):
        ...
    
    @property
    def file_format(self) -> aspose.imaging.FileFormat:
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def premultiply_components(self) -> bool:
        ...
    
    @premultiply_components.setter
    def premultiply_components(self, value : bool):
        ...
    
    @property
    def use_raw_data(self) -> bool:
        ...
    
    @use_raw_data.setter
    def use_raw_data(self, value : bool):
        ...
    
    @property
    def update_xmp_data(self) -> bool:
        ...
    
    @update_xmp_data.setter
    def update_xmp_data(self, value : bool):
        ...
    
    @property
    def xmp_data(self) -> aspose.imaging.xmp.XmpPacketWrapper:
        ...
    
    @xmp_data.setter
    def xmp_data(self, value : aspose.imaging.xmp.XmpPacketWrapper):
        ...
    
    @property
    def raw_indexed_color_converter(self) -> aspose.imaging.IIndexedColorConverter:
        ...
    
    @raw_indexed_color_converter.setter
    def raw_indexed_color_converter(self, value : aspose.imaging.IIndexedColorConverter):
        ...
    
    @property
    def raw_custom_color_converter(self) -> aspose.imaging.IColorConverter:
        ...
    
    @raw_custom_color_converter.setter
    def raw_custom_color_converter(self, value : aspose.imaging.IColorConverter):
        ...
    
    @property
    def raw_fallback_index(self) -> int:
        ...
    
    @raw_fallback_index.setter
    def raw_fallback_index(self, value : int):
        ...
    
    @property
    def raw_data_settings(self) -> aspose.imaging.RawDataSettings:
        ...
    
    @property
    def raw_data_format(self) -> aspose.imaging.PixelDataFormat:
        ...
    
    @property
    def raw_line_size(self) -> int:
        ...
    
    @property
    def is_raw_data_available(self) -> bool:
        ...
    
    @property
    def horizontal_resolution(self) -> float:
        ...
    
    @horizontal_resolution.setter
    def horizontal_resolution(self, value : float):
        ...
    
    @property
    def vertical_resolution(self) -> float:
        ...
    
    @vertical_resolution.setter
    def vertical_resolution(self, value : float):
        ...
    
    @property
    def has_transparent_color(self) -> bool:
        ...
    
    @has_transparent_color.setter
    def has_transparent_color(self, value : bool):
        ...
    
    @property
    def has_alpha(self) -> bool:
        ...
    
    @property
    def transparent_color(self) -> aspose.imaging.Color:
        ...
    
    @transparent_color.setter
    def transparent_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def image_opacity(self) -> float:
        ...
    
    @property
    def page_count(self) -> int:
        ...
    
    @property
    def pages(self) -> List[aspose.imaging.Image]:
        '''Access the WebP blocks within the image, allowing detailed examination or
        manipulation of the underlying block structure. Utilize this property to analyze
        or modify individual blocks within the WebP image data, facilitating advanced
        image processing techniques within your application.'''
        ...
    
    @property
    def options(self) -> aspose.imaging.imageoptions.WebPOptions:
        '''Retrieve or modify the options associated with the specified property, enabling
        fine-tuned customization of behavior and settings. Utilize this property to
        seamlessly access and manipulate configurable parameters, facilitating versatile
        control and optimization within your application's functionality.'''
        ...
    
    ...

