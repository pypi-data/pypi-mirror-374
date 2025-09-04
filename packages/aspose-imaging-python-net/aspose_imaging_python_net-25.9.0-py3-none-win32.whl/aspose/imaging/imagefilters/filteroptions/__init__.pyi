"""The namespace handles Filter options."""
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

class AdaptiveWhiteStretchFilterOptions(FilterOptionsBase):
    '''Provides options for configuring the Adaptive White Stretch filter.
    Allows customization of histogram stretch parameters to enhance the white level
    and improve the readability of faint-text or low-contrast document images.'''
    
    def __init__(self, is_grayscale: bool, low_percentile: int, high_percentile: int, target_white: int, max_scale: float):
        '''Initializes a new instance of the  class.
        
        :param is_grayscale: Indicates whether the filter should operate in grayscale mode.
        :param low_percentile: Lower percentile for black point (e.g. 10).
        :param high_percentile: Upper percentile for white point (e.g. 90).
        :param target_white: Target white value (e.g. 240).
        :param max_scale: Maximum allowed brightness scale (e.g. 1.7).'''
        ...
    
    @property
    def is_grayscale(self) -> bool:
        ...
    
    @property
    def low_percentile(self) -> int:
        ...
    
    @property
    def high_percentile(self) -> int:
        ...
    
    @property
    def target_white(self) -> int:
        ...
    
    @property
    def max_scale(self) -> float:
        ...
    
    ...

class AutoWhiteBalanceFilterOptions(FilterOptionsBase):
    '''Provides configuration options for the Auto White Balance filter.
    Allows tuning of contrast stretching parameters and channel scaling
    to improve the appearance of digital images.'''
    
    def __init__(self, low_percentile: int, target_high_percentile: int, target_value: int, max_scale: float, protected_dark_offset: int):
        '''Initializes a new instance of the  class.
        
        :param low_percentile: The low percentile for black point, used for darks protection (default: 3).
        :param target_high_percentile: The target high percentile for contrast stretching (default 97).
        :param target_value: The target value for the high percentile (default 255).
        :param max_scale: The maximum scaling factor for each channel (default 1.4f).
        :param protected_dark_offset: Offset from low percentile below which dark pixels are not stretched (protection).'''
        ...
    
    @property
    def target_high_percentile(self) -> int:
        ...
    
    @property
    def target_value(self) -> int:
        ...
    
    @property
    def max_scale(self) -> float:
        ...
    
    @property
    def low_percentile(self) -> int:
        ...
    
    @property
    def protected_dark_offset(self) -> int:
        ...
    
    ...

class BigRectangularFilterOptions(FilterOptionsBase):
    '''Big Rectangular Filter Options'''
    
    def __init__(self):
        ...
    
    ...

class BilateralSmoothingFilterOptions(FilterOptionsBase):
    '''The Bilateral Smoothing Filter Options.'''
    
    @overload
    def __init__(self, size: int):
        '''Initializes a new instance of the  class.
        
        :param size: Size of the kernal.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets the size of the kernel.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets the size of the kernel.'''
        ...
    
    @property
    def spatial_factor(self) -> float:
        ...
    
    @spatial_factor.setter
    def spatial_factor(self, value : float):
        ...
    
    @property
    def spatial_power(self) -> float:
        ...
    
    @spatial_power.setter
    def spatial_power(self, value : float):
        ...
    
    @property
    def color_factor(self) -> float:
        ...
    
    @color_factor.setter
    def color_factor(self, value : float):
        ...
    
    @property
    def color_power(self) -> float:
        ...
    
    @color_power.setter
    def color_power(self, value : float):
        ...
    
    ...

class ClaheFilterOptions(FilterOptionsBase):
    '''Provides options for configuring the Contrast-Limited Adaptive Histogram Equalization (CLAHE) filter.'''
    
    def __init__(self, is_grayscale: bool, tiles_number_horizontal: int, tiles_number_vertical: int, clip_limit: float):
        '''Initializes a new instance of the  class
        with the specified parameters.
        
        :param is_grayscale: Indicates whether the filter should operate in grayscale mode.
        :param tiles_number_horizontal: Number of tiles horizontally. Default is 8.
        :param tiles_number_vertical: Number of tiles vertically. Default is 8.
        :param clip_limit: Contrast limiting threshold. Default is 4.0.'''
        ...
    
    @property
    def is_grayscale(self) -> bool:
        ...
    
    @property
    def tiles_number_horizontal(self) -> int:
        ...
    
    @property
    def tiles_number_vertical(self) -> int:
        ...
    
    @property
    def clip_limit(self) -> float:
        ...
    
    ...

class ConvolutionFilterOptions(FilterOptionsBase):
    '''The convolution filter options.'''
    
    @overload
    def __init__(self, kernel: List[float]):
        '''Initializes a new instance of the  class with factor = 1, and bias = 0.
        
        :param kernel: The convolution kernel for X-axis direction.'''
        ...
    
    @overload
    def __init__(self, kernel: List[float], factor: float):
        '''Initializes a new instance of the  class with bias = 0.
        
        :param kernel: The convolution kernel for X-axis direction.
        :param factor: The factor.'''
        ...
    
    @overload
    def __init__(self, kernel: List[float], factor: float, bias: int):
        '''Initializes a new instance of the  class.
        
        :param kernel: The convolution kernel for X-axis direction.
        :param factor: The factor.
        :param bias: The bias value.'''
        ...
    
    @property
    def kernel_data(self) -> List[float]:
        ...
    
    @property
    def factor(self) -> float:
        '''Gets the factor.'''
        ...
    
    @factor.setter
    def factor(self, value : float):
        '''Sets the factor.'''
        ...
    
    @property
    def bias(self) -> int:
        '''Gets the bias.'''
        ...
    
    @bias.setter
    def bias(self, value : int):
        '''Sets the bias.'''
        ...
    
    ...

class DeconvolutionFilterOptions(FilterOptionsBase):
    '''Deconvolution Filter Options, abstract class'''
    
    @overload
    def __init__(self, kernel: List[float]):
        '''Initializes a new instance of the  class.
        
        :param kernel: The kernel.'''
        ...
    
    @overload
    def __init__(self, kernel: List[aspose.imaging.imagefilters.complexutils.Complex]):
        '''Initializes a new instance of the  class.
        
        :param kernel: The kernel.'''
        ...
    
    @staticmethod
    def create_with_double(kernel: List[float]) -> aspose.imaging.imagefilters.filteroptions.DeconvolutionFilterOptions:
        '''Initializes a new instance of the  class.
        
        :param kernel: The double[] kernel.'''
        ...
    
    @staticmethod
    def create_with_complex(kernel: List[aspose.imaging.imagefilters.complexutils.Complex]) -> aspose.imaging.imagefilters.filteroptions.DeconvolutionFilterOptions:
        '''Initializes a new instance of the  class.
        
        :param kernel: The Complex[] kernel.'''
        ...
    
    @property
    def kernel_data(self) -> List[aspose.imaging.imagefilters.complexutils.Complex]:
        ...
    
    @property
    def snr(self) -> float:
        '''Gets the SNR(signal-to-noise ratio)
        recommended range 0.002 - 0.009, default value = 0.007'''
        ...
    
    @snr.setter
    def snr(self, value : float):
        '''Sets the SNR(signal-to-noise ratio)
        recommended range 0.002 - 0.009, default value = 0.007'''
        ...
    
    @property
    def brightness(self) -> float:
        '''Gets the brightness.
        recommended range 1 - 1.5
        default value = 1.15'''
        ...
    
    @brightness.setter
    def brightness(self, value : float):
        '''Sets the brightness.
        recommended range 1 - 1.5
        default value = 1.15'''
        ...
    
    @property
    def grayscale(self) -> bool:
        '''Gets a value indicating whether this  is grayscale.
        Return grayscale mode or RGB mode.'''
        ...
    
    @grayscale.setter
    def grayscale(self, value : bool):
        '''Sets a value indicating whether this  is grayscale.
        Return grayscale mode or RGB mode.'''
        ...
    
    @property
    def is_partial_loaded(self) -> bool:
        ...
    
    ...

class FilterOptionsBase:
    '''Base filter options class.'''
    
    ...

class GaussWienerFilterOptions(GaussianDeconvolutionFilterOptions):
    '''Gauss Wiener filter options for image debluring.'''
    
    @overload
    def __init__(self, size: int, sigma: float):
        '''Initializes a new instance of the  class.
        
        :param size: The Gaussian kernel size.
        :param sigma: The Gaussian kernel sigma.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @staticmethod
    def create_with_double(kernel: List[float]) -> aspose.imaging.imagefilters.filteroptions.DeconvolutionFilterOptions:
        '''Initializes a new instance of the  class.
        
        :param kernel: The double[] kernel.'''
        ...
    
    @staticmethod
    def create_with_complex(kernel: List[aspose.imaging.imagefilters.complexutils.Complex]) -> aspose.imaging.imagefilters.filteroptions.DeconvolutionFilterOptions:
        '''Initializes a new instance of the  class.
        
        :param kernel: The Complex[] kernel.'''
        ...
    
    @property
    def kernel_data(self) -> List[aspose.imaging.imagefilters.complexutils.Complex]:
        ...
    
    @property
    def snr(self) -> float:
        '''Gets the SNR(signal-to-noise ratio)
        recommended range 0.002 - 0.009, default value = 0.007'''
        ...
    
    @snr.setter
    def snr(self, value : float):
        '''Sets the SNR(signal-to-noise ratio)
        recommended range 0.002 - 0.009, default value = 0.007'''
        ...
    
    @property
    def brightness(self) -> float:
        '''Gets the brightness.
        recommended range 1 - 1.5
        default value = 1.15'''
        ...
    
    @brightness.setter
    def brightness(self, value : float):
        '''Sets the brightness.
        recommended range 1 - 1.5
        default value = 1.15'''
        ...
    
    @property
    def grayscale(self) -> bool:
        '''Gets a value indicating whether this  is grayscale.
        Return grayscale mode or RGB mode.'''
        ...
    
    @grayscale.setter
    def grayscale(self, value : bool):
        '''Sets a value indicating whether this  is grayscale.
        Return grayscale mode or RGB mode.'''
        ...
    
    @property
    def is_partial_loaded(self) -> bool:
        ...
    
    @property
    def size(self) -> int:
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @property
    def sigma(self) -> float:
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @sigma.setter
    def sigma(self, value : float):
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @property
    def radius(self) -> int:
        '''Gets the radius of Gausseian .'''
        ...
    
    @radius.setter
    def radius(self, value : int):
        '''Gets the radius of Gausseian .'''
        ...
    
    ...

class GaussianBlurFilterOptions(ConvolutionFilterOptions):
    '''The Gaussian blur filter options.'''
    
    @overload
    def __init__(self, size: int, sigma: float):
        '''Initializes a new instance of the  class.
        
        :param size: The Gaussian kernel size..
        :param sigma: The Gaussian kernel sigma.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def kernel_data(self) -> List[float]:
        ...
    
    @property
    def factor(self) -> float:
        '''Gets the factor.'''
        ...
    
    @factor.setter
    def factor(self, value : float):
        '''Sets the factor.'''
        ...
    
    @property
    def bias(self) -> int:
        '''Gets the bias.'''
        ...
    
    @bias.setter
    def bias(self, value : int):
        '''Sets the bias.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @property
    def sigma(self) -> float:
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @sigma.setter
    def sigma(self, value : float):
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @property
    def radius(self) -> int:
        '''Gets the radius of Gausseian .'''
        ...
    
    @radius.setter
    def radius(self, value : int):
        '''Gets the radius of Gausseian .'''
        ...
    
    ...

class GaussianDeconvolutionFilterOptions(DeconvolutionFilterOptions):
    '''The deconvolution filter options using Gaussian bluring.'''
    
    @staticmethod
    def create_with_double(kernel: List[float]) -> aspose.imaging.imagefilters.filteroptions.DeconvolutionFilterOptions:
        '''Initializes a new instance of the  class.
        
        :param kernel: The double[] kernel.'''
        ...
    
    @staticmethod
    def create_with_complex(kernel: List[aspose.imaging.imagefilters.complexutils.Complex]) -> aspose.imaging.imagefilters.filteroptions.DeconvolutionFilterOptions:
        '''Initializes a new instance of the  class.
        
        :param kernel: The Complex[] kernel.'''
        ...
    
    @property
    def kernel_data(self) -> List[aspose.imaging.imagefilters.complexutils.Complex]:
        ...
    
    @property
    def snr(self) -> float:
        '''Gets the SNR(signal-to-noise ratio)
        recommended range 0.002 - 0.009, default value = 0.007'''
        ...
    
    @snr.setter
    def snr(self, value : float):
        '''Sets the SNR(signal-to-noise ratio)
        recommended range 0.002 - 0.009, default value = 0.007'''
        ...
    
    @property
    def brightness(self) -> float:
        '''Gets the brightness.
        recommended range 1 - 1.5
        default value = 1.15'''
        ...
    
    @brightness.setter
    def brightness(self, value : float):
        '''Sets the brightness.
        recommended range 1 - 1.5
        default value = 1.15'''
        ...
    
    @property
    def grayscale(self) -> bool:
        '''Gets a value indicating whether this  is grayscale.
        Return grayscale mode or RGB mode.'''
        ...
    
    @grayscale.setter
    def grayscale(self, value : bool):
        '''Sets a value indicating whether this  is grayscale.
        Return grayscale mode or RGB mode.'''
        ...
    
    @property
    def is_partial_loaded(self) -> bool:
        ...
    
    @property
    def size(self) -> int:
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @property
    def sigma(self) -> float:
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @sigma.setter
    def sigma(self, value : float):
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @property
    def radius(self) -> int:
        '''Gets the radius of Gausseian .'''
        ...
    
    @radius.setter
    def radius(self, value : int):
        '''Gets the radius of Gausseian .'''
        ...
    
    ...

class MedianFilterOptions(FilterOptionsBase):
    '''Median filter'''
    
    def __init__(self, size: int):
        '''Initializes a new instance of the  class.
        
        :param size: The size of filter rectangle.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets the size.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Sets the size.'''
        ...
    
    ...

class MotionWienerFilterOptions(GaussianDeconvolutionFilterOptions):
    '''The motion debluring filter options.'''
    
    def __init__(self, size: int, sigma: float, angle: float):
        '''Initializes a new instance of the  class.
        
        :param size: The Gaussian kernel size.
        :param sigma: The Gaussian kernel sigma.
        :param angle: The angle in degrees.'''
        ...
    
    @staticmethod
    def create_with_double(kernel: List[float]) -> aspose.imaging.imagefilters.filteroptions.DeconvolutionFilterOptions:
        '''Initializes a new instance of the  class.
        
        :param kernel: The double[] kernel.'''
        ...
    
    @staticmethod
    def create_with_complex(kernel: List[aspose.imaging.imagefilters.complexutils.Complex]) -> aspose.imaging.imagefilters.filteroptions.DeconvolutionFilterOptions:
        '''Initializes a new instance of the  class.
        
        :param kernel: The Complex[] kernel.'''
        ...
    
    @property
    def kernel_data(self) -> List[aspose.imaging.imagefilters.complexutils.Complex]:
        ...
    
    @property
    def snr(self) -> float:
        '''Gets the SNR(signal-to-noise ratio)
        recommended range 0.002 - 0.009, default value = 0.007'''
        ...
    
    @snr.setter
    def snr(self, value : float):
        '''Sets the SNR(signal-to-noise ratio)
        recommended range 0.002 - 0.009, default value = 0.007'''
        ...
    
    @property
    def brightness(self) -> float:
        '''Gets the brightness.
        recommended range 1 - 1.5
        default value = 1.15'''
        ...
    
    @brightness.setter
    def brightness(self, value : float):
        '''Sets the brightness.
        recommended range 1 - 1.5
        default value = 1.15'''
        ...
    
    @property
    def grayscale(self) -> bool:
        '''Gets a value indicating whether this  is grayscale.
        Return grayscale mode or RGB mode.'''
        ...
    
    @grayscale.setter
    def grayscale(self, value : bool):
        '''Sets a value indicating whether this  is grayscale.
        Return grayscale mode or RGB mode.'''
        ...
    
    @property
    def is_partial_loaded(self) -> bool:
        ...
    
    @property
    def size(self) -> int:
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @property
    def sigma(self) -> float:
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @sigma.setter
    def sigma(self, value : float):
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @property
    def radius(self) -> int:
        '''Gets the radius of Gausseian .'''
        ...
    
    @radius.setter
    def radius(self, value : int):
        '''Gets the radius of Gausseian .'''
        ...
    
    @property
    def angle(self) -> float:
        '''Gets the angle in degrees.'''
        ...
    
    @angle.setter
    def angle(self, value : float):
        '''Sets the angle in degrees.'''
        ...
    
    ...

class SharpenFilterOptions(GaussianBlurFilterOptions):
    '''The sharpen filter options.'''
    
    @overload
    def __init__(self, size: int, sigma: float):
        '''Initializes a new instance of the  class.
        
        :param size: The size of the kernel.
        :param sigma: The sigma.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def kernel_data(self) -> List[float]:
        ...
    
    @property
    def factor(self) -> float:
        '''Gets the factor.'''
        ...
    
    @factor.setter
    def factor(self, value : float):
        '''Sets the factor.'''
        ...
    
    @property
    def bias(self) -> int:
        '''Gets the bias.'''
        ...
    
    @bias.setter
    def bias(self, value : int):
        '''Sets the bias.'''
        ...
    
    @property
    def size(self) -> int:
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @size.setter
    def size(self, value : int):
        '''Gets the Gaussian kernel size. Must be a positive non-zero odd value.'''
        ...
    
    @property
    def sigma(self) -> float:
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @sigma.setter
    def sigma(self, value : float):
        '''Gets the Gaussian kernel sigma (smoothing). Must be a positive non-zero value.'''
        ...
    
    @property
    def radius(self) -> int:
        '''Gets the radius of Gausseian .'''
        ...
    
    @radius.setter
    def radius(self, value : int):
        '''Gets the radius of Gausseian .'''
        ...
    
    ...

class SmallRectangularFilterOptions(FilterOptionsBase):
    '''Small rectangular filter options'''
    
    def __init__(self):
        ...
    
    ...

