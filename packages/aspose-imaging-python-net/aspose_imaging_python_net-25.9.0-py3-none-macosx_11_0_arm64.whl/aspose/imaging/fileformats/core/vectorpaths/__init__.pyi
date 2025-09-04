"""The namespace contains PSD Vector Paths."""
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

class BezierKnotRecord(VectorPathRecord):
    '''Bezier Knot Record Class'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, data: bytes):
        '''Initializes a new instance of the  class.
        
        :param data: The record data.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.core.vectorpaths.VectorPathType:
        '''Gets the type.'''
        ...
    
    @property
    def path_points(self) -> List[aspose.imaging.PointF]:
        ...
    
    @path_points.setter
    def path_points(self, value : List[aspose.imaging.PointF]):
        ...
    
    @property
    def points(self) -> List[aspose.imaging.Point]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.Point]):
        '''Sets the points.'''
        ...
    
    @property
    def is_closed(self) -> bool:
        ...
    
    @is_closed.setter
    def is_closed(self, value : bool):
        ...
    
    @property
    def is_linked(self) -> bool:
        ...
    
    @is_linked.setter
    def is_linked(self, value : bool):
        ...
    
    @property
    def is_open(self) -> bool:
        ...
    
    @is_open.setter
    def is_open(self, value : bool):
        ...
    
    ...

class ClipboardRecord(VectorPathRecord):
    '''Clipboard Record Class'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, data: bytes):
        '''Initializes a new instance of the  class.
        
        :param data: The record data.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.core.vectorpaths.VectorPathType:
        '''Gets the type.'''
        ...
    
    @property
    def bounding_rect(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounding_rect.setter
    def bounding_rect(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def resolution(self) -> float:
        '''Gets the resolution.'''
        ...
    
    @resolution.setter
    def resolution(self, value : float):
        '''Sets the resolution.'''
        ...
    
    ...

class IVectorPathData:
    '''The interface for access to the vector path data.'''
    
    @property
    def paths(self) -> List[aspose.imaging.fileformats.core.vectorpaths.VectorPathRecord]:
        '''Gets the path records.'''
        ...
    
    @paths.setter
    def paths(self, value : List[aspose.imaging.fileformats.core.vectorpaths.VectorPathRecord]):
        '''Sets the path records.'''
        ...
    
    @property
    def version(self) -> int:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets the version.'''
        ...
    
    @property
    def is_disabled(self) -> bool:
        ...
    
    @is_disabled.setter
    def is_disabled(self, value : bool):
        ...
    
    @property
    def is_not_linked(self) -> bool:
        ...
    
    @is_not_linked.setter
    def is_not_linked(self, value : bool):
        ...
    
    @property
    def is_inverted(self) -> bool:
        ...
    
    @is_inverted.setter
    def is_inverted(self, value : bool):
        ...
    
    ...

class InitialFillRuleRecord(VectorPathRecord):
    '''Initial Fill Rule Record Class'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, is_fill_starts_with_all_pixels: bool):
        '''Initializes a new instance of the  class.
        
        :param is_fill_starts_with_all_pixels: The is fill starts with all pixels.'''
        ...
    
    @overload
    def __init__(self, data: bytes):
        '''Initializes a new instance of the  class.
        
        :param data: The record data.'''
        ...
    
    @staticmethod
    def create_filled_with_pixels(is_fill_starts_with_all_pixels: bool) -> aspose.imaging.fileformats.core.vectorpaths.InitialFillRuleRecord:
        '''Initializes a new instance of the  class.
        
        :param is_fill_starts_with_all_pixels: The is fill starts with all pixels.'''
        ...
    
    @staticmethod
    def create_from_bytes(data: bytes) -> aspose.imaging.fileformats.core.vectorpaths.InitialFillRuleRecord:
        '''Initializes a new instance of the  class.
        
        :param data: The record data.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.core.vectorpaths.VectorPathType:
        '''Gets the type.'''
        ...
    
    @property
    def is_fill_starts_with_all_pixels(self) -> bool:
        ...
    
    @is_fill_starts_with_all_pixels.setter
    def is_fill_starts_with_all_pixels(self, value : bool):
        ...
    
    ...

class LengthRecord(VectorPathRecord):
    '''Subpath Length Record Class'''
    
    @overload
    def __init__(self, data: bytes):
        '''Initializes a new instance of the  class.
        
        :param data: The record data.'''
        ...
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.core.vectorpaths.VectorPathType:
        '''Gets the type.'''
        ...
    
    @property
    def is_closed(self) -> bool:
        ...
    
    @is_closed.setter
    def is_closed(self, value : bool):
        ...
    
    @property
    def is_open(self) -> bool:
        ...
    
    @is_open.setter
    def is_open(self, value : bool):
        ...
    
    @property
    def record_count(self) -> int:
        ...
    
    @record_count.setter
    def record_count(self, value : int):
        ...
    
    @property
    def bezier_knot_records_count(self) -> int:
        ...
    
    @bezier_knot_records_count.setter
    def bezier_knot_records_count(self, value : int):
        ...
    
    @property
    def path_operations(self) -> aspose.imaging.fileformats.core.vectorpaths.PathOperations:
        ...
    
    @path_operations.setter
    def path_operations(self, value : aspose.imaging.fileformats.core.vectorpaths.PathOperations):
        ...
    
    @property
    def shape_index(self) -> int:
        ...
    
    @shape_index.setter
    def shape_index(self, value : int):
        ...
    
    ...

class PathFillRuleRecord(VectorPathRecord):
    '''Path Fill Rule Record Class'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, data: bytes):
        '''Initializes a new instance of the  class.
        
        :param data: The record data.'''
        ...
    
    @property
    def type(self) -> aspose.imaging.fileformats.core.vectorpaths.VectorPathType:
        '''Gets the type.'''
        ...
    
    ...

class VectorPathRecord:
    '''Vector Path Record Class'''
    
    @property
    def type(self) -> aspose.imaging.fileformats.core.vectorpaths.VectorPathType:
        '''Gets the type.'''
        ...
    
    ...

class VectorPathRecordFactory:
    '''Vector Path Record Factory Class'''
    
    def __init__(self):
        ...
    
    def produce_path_record(self, data: bytes) -> aspose.imaging.fileformats.core.vectorpaths.VectorPathRecord:
        '''Produces the path record.
        
        :param data: The record data.
        :returns: Created'''
        ...
    
    ...

class PathOperations(enum.Enum):
    EXCLUDE_OVERLAPPING_SHAPES = enum.auto()
    '''Exclude Overlapping Shapes (XOR operation).'''
    COMBINE_SHAPES = enum.auto()
    '''Combine Shapes (OR operation). This is default value in Photoshop.'''
    SUBTRACT_FRONT_SHAPE = enum.auto()
    '''Subtract Front Shape (NOT operation).'''
    INTERSECT_SHAPE_AREAS = enum.auto()
    '''Intersect Shape Areas (AND operation).'''

class VectorPathType(enum.Enum):
    CLOSED_SUBPATH_LENGTH_RECORD = enum.auto()
    '''The closed subpath length record'''
    CLOSED_SUBPATH_BEZIER_KNOT_LINKED = enum.auto()
    '''The closed subpath bezier knot linked'''
    CLOSED_SUBPATH_BEZIER_KNOT_UNLINKED = enum.auto()
    '''The closed subpath bezier knot unlinked'''
    OPEN_SUBPATH_LENGTH_RECORD = enum.auto()
    '''The open subpath length record'''
    OPEN_SUBPATH_BEZIER_KNOT_LINKED = enum.auto()
    '''The open subpath bezier knot linked'''
    OPEN_SUBPATH_BEZIER_KNOT_UNLINKED = enum.auto()
    '''The open subpath bezier knot unlinked'''
    PATH_FILL_RULE_RECORD = enum.auto()
    '''The path fill rule record'''
    CLIPBOARD_RECORD = enum.auto()
    '''The clipboard record'''
    INITIAL_FILL_RULE_RECORD = enum.auto()
    '''The initial fill rule record'''

