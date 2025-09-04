"""The namespace handles Cdr file format processing."""
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

class CdrImage(aspose.imaging.VectorMultipageImage):
    '''The API for CorelDRAW CDR vector image format support is an essential toolkit
    for developers working with vector graphics. This API enables the
    seamless processing of CDR files, allowing for the storage and
    manipulation of diverse elements such as text, lines, shapes, images,
    colors, and effects. With its comprehensive capabilities, developers can
    efficiently work with vector representations of image contents, ensuring
    precision and flexibility in creating and editing CorelDRAW vector
    graphics programmatically.'''
    
    def __init__(self, stream: io.RawIOBase, load_options: aspose.imaging.LoadOptions):
        '''Start working with the  class effortlessly by
        initializing a new instance with a stream and loadOptions parameters.
        Ideal for developers seeking a convenient way to load CDR images from
        various data sources while customizing the loading process as needed.
        
        :param stream: The stream.
        :param load_options: The load options.'''
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
    def save(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use source bounds.'''
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
    def crop(self, rectangle: aspose.imaging.Rectangle):
        '''Crops the specified rectangle.
        
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
    def remove_background(self, settings: aspose.imaging.RemoveBackgroundSettings):
        '''Removes the background.
        
        :param settings: The settings.'''
        ...
    
    @overload
    def remove_background(self):
        '''Removes the background.'''
        ...
    
    def cache_data(self):
        '''Effortlessly cache the data to prevent additional loading from the underlying source
        with this user-friendly method. Ideal for developers seeking to optimize performance
        by preloading data, ensuring faster access and smoother operation in their applications.
        .'''
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
        '''Removes metadata.'''
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
        '''Gets the default image options.
        
        :param args: The arguments.
        :returns: The default image options.'''
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
        
        :param rotate_flip_type: Type of the rotate flip.'''
        ...
    
    def rotate(self, angle: float):
        '''Rotate image around the center.
        
        :param angle: The rotate angle in degrees. Positive values will rotate clockwise.'''
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
        '''Customize the color palette of the image with this intuitive method. Ideal for
        developers seeking to apply specific color schemes or adjustments dynamically,
        ensuring precise control over the visual appearance of their images.
        
        :param palette: The palette to set.
        :param update_colors: if set to ``true`` colors will be updated according to the new palette; otherwise color
        indexes remain unchanged. Note that unchanged indexes may crash the image on loading if some indexes have no
        corresponding palette entries.'''
        ...
    
    def get_embedded_images(self) -> List[aspose.imaging.EmbeddedImage]:
        '''Gets the embedded images.
        
        :returns: Array of images'''
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
    def size_f(self) -> aspose.imaging.SizeF:
        ...
    
    @property
    def width_f(self) -> float:
        ...
    
    @property
    def height_f(self) -> float:
        ...
    
    @property
    def page_count(self) -> int:
        ...
    
    @property
    def pages(self) -> List[aspose.imaging.Image]:
        '''Retrieve the pages of the image seamlessly with this intuitive property.
        Ideal for developers seeking to access and manipulate individual pages within
        multi-page images, ensuring efficient navigation and processing.'''
        ...
    
    @property
    def default_page(self) -> aspose.imaging.Image:
        ...
    
    @property
    def cdr_document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        ...
    
    ...

class CdrImagePage(aspose.imaging.VectorImage):
    '''The Cdr image page'''
    
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
    def save(self, stream: io.RawIOBase, options_base: aspose.imaging.ImageOptionsBase, bounds_rectangle: aspose.imaging.Rectangle):
        '''Saves the image's data to the specified stream in the specified file format according to save options.
        
        :param stream: The stream to save the image's data to.
        :param options_base: The save options.
        :param bounds_rectangle: The destination image bounds rectangle. Set the empty rectangle for use source bounds.'''
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
        '''Resizes the specified new width.
        
        :param new_width: The new width.
        :param new_height: The new height.
        :param resize_type: Type of the resize.'''
        ...
    
    @overload
    def resize(self, new_width: int, new_height: int, settings: aspose.imaging.ImageResizeSettings):
        '''Resizes the image with extended options.
        
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
    def crop(self, rectangle: aspose.imaging.Rectangle):
        '''Crops the specified rectangle.
        
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
    def remove_background(self):
        '''Removes the background.'''
        ...
    
    @overload
    def remove_background(self, settings: aspose.imaging.RemoveBackgroundSettings):
        '''Removes the background.
        
        :param settings: The settings.'''
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
        '''Removes metadata.'''
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
        
        :param rotate_flip_type: Type of the rotate flip.'''
        ...
    
    def rotate(self, angle: float):
        '''Rotate image around the center.
        
        :param angle: The rotate angle in degrees. Positive values will rotate clockwise.'''
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
    
    def get_embedded_images(self) -> List[aspose.imaging.EmbeddedImage]:
        '''Gets the embedded images.
        
        :returns: Array of images'''
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
    def size_f(self) -> aspose.imaging.SizeF:
        ...
    
    @property
    def width_f(self) -> float:
        ...
    
    @property
    def height_f(self) -> float:
        ...
    
    @property
    def parent_image(self) -> aspose.imaging.fileformats.cdr.CdrImage:
        ...
    
    @property
    def page_number(self) -> int:
        ...
    
    @property
    def cdr_document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        ...
    
    ...

class ICdrImage:
    '''The Cdr image interface'''
    
    @property
    def cdr_document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        ...
    
    ...

