"""The namespace contains different shapes combined from shape segments."""
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

class ArcShape(PieShape):
    '''Represents an arc shape.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, rectangle: aspose.imaging.RectangleF, start_angle: float, sweep_angle: float):
        '''Initializes a new instance of the  class.
        
        :param rectangle: The rectangle.
        :param start_angle: The start angle.
        :param sweep_angle: The sweep angle.'''
        ...
    
    @overload
    def __init__(self, rectangle: aspose.imaging.RectangleF, start_angle: float, sweep_angle: float, is_closed: bool):
        '''Initializes a new instance of the  class.
        
        :param rectangle: The rectangle.
        :param start_angle: The start angle.
        :param sweep_angle: The sweep angle.
        :param is_closed: If set to ``true`` the arc is closed. The closed arc is actually degenereates to an ellipse.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :returns: The estimated object's bounds.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix, pen: aspose.imaging.Pen) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :param pen: The pen to use for object. This can influence the object's bounds size.
        :returns: The estimated object's bounds.'''
        ...
    
    def transform(self, transform: aspose.imaging.Matrix):
        '''Applies the specified transformation to the shape.
        
        :param transform: The transformation to apply.'''
        ...
    
    def reverse(self):
        '''Reverses the order of points for this shape.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.'''
        ...
    
    @property
    def center(self) -> aspose.imaging.PointF:
        '''Gets the shape's center.'''
        ...
    
    @property
    def segments(self) -> List[aspose.imaging.ShapeSegment]:
        '''Gets the shape segments.'''
        ...
    
    @property
    def has_segments(self) -> bool:
        ...
    
    @property
    def left_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def left_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def rectangle_width(self) -> float:
        ...
    
    @property
    def rectangle_height(self) -> float:
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @start_angle.setter
    def start_angle(self, value : float):
        ...
    
    @property
    def sweep_angle(self) -> float:
        ...
    
    @sweep_angle.setter
    def sweep_angle(self, value : float):
        ...
    
    @property
    def start_point(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def end_point(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def is_closed(self) -> bool:
        ...
    
    @is_closed.setter
    def is_closed(self, value : bool):
        ...
    
    ...

class BezierShape(PolygonShape):
    '''Represents a bezier spline.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, points: List[aspose.imaging.PointF]):
        '''Initializes a new instance of the  class.
        
        :param points: The points array.'''
        ...
    
    @overload
    def __init__(self, points: List[aspose.imaging.PointF], is_closed: bool):
        '''Initializes a new instance of the  class.
        
        :param points: The points array.
        :param is_closed: If set to ``true`` the bezier spline is closed.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :returns: The estimated object's bounds.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix, pen: aspose.imaging.Pen) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :param pen: The pen to use for object. This can influence the object's bounds size.
        :returns: The estimated object's bounds.'''
        ...
    
    def transform(self, transform: aspose.imaging.Matrix):
        '''Applies the specified transformation to the shape.
        
        :param transform: The transformation to apply.'''
        ...
    
    def reverse(self):
        '''Reverses the order of points for this shape.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.'''
        ...
    
    @property
    def center(self) -> aspose.imaging.PointF:
        '''Gets the shape's center.'''
        ...
    
    @property
    def segments(self) -> List[aspose.imaging.ShapeSegment]:
        '''Gets the shape segments.'''
        ...
    
    @property
    def has_segments(self) -> bool:
        ...
    
    @property
    def points(self) -> List[aspose.imaging.PointF]:
        '''Gets the curve points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.PointF]):
        '''Sets the curve points.'''
        ...
    
    @property
    def is_closed(self) -> bool:
        ...
    
    @is_closed.setter
    def is_closed(self, value : bool):
        ...
    
    @property
    def start_point(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def end_point(self) -> aspose.imaging.PointF:
        ...
    
    ...

class CurveShape(PolygonShape):
    '''Represents a curved spline shape.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, points: List[aspose.imaging.PointF]):
        '''Initializes a new instance of the  class. The default tension of 0.5 is used.
        
        :param points: The points array.'''
        ...
    
    @overload
    def __init__(self, points: List[aspose.imaging.PointF], is_closed: bool):
        '''Initializes a new instance of the  class. The default tension of 0.5 is used.
        
        :param points: The points array.
        :param is_closed: if set to ``true`` the curve is closed.'''
        ...
    
    @overload
    def __init__(self, points: List[aspose.imaging.PointF], tension: float):
        '''Initializes a new instance of the  class.
        
        :param points: The points array.
        :param tension: The curve tension.'''
        ...
    
    @overload
    def __init__(self, points: List[aspose.imaging.PointF], tension: float, is_closed: bool):
        '''Initializes a new instance of the  class.
        
        :param points: The points array.
        :param tension: The curve tension.
        :param is_closed: if set to ``true`` the curve is closed.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :returns: The estimated object's bounds.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix, pen: aspose.imaging.Pen) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :param pen: The pen to use for object. This can influence the object's bounds size.
        :returns: The estimated object's bounds.'''
        ...
    
    def transform(self, transform: aspose.imaging.Matrix):
        '''Applies the specified transformation to the shape.
        
        :param transform: The transformation to apply.'''
        ...
    
    def reverse(self):
        '''Reverses the order of points for this shape.'''
        ...
    
    @staticmethod
    def create_with_point_fs_closed(points: List[aspose.imaging.PointF], is_closed: bool) -> aspose.imaging.shapes.CurveShape:
        '''Initializes a new instance of the  class. The default tension of 0.5 is used.
        
        :param points: The points array.
        :param is_closed: if set to ``true`` the curve is closed.'''
        ...
    
    @staticmethod
    def create_with_point_fs_tension(points: List[aspose.imaging.PointF], tension: float) -> aspose.imaging.shapes.CurveShape:
        '''Initializes a new instance of the  class.
        
        :param points: The points array.
        :param tension: The curve tension.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.'''
        ...
    
    @property
    def center(self) -> aspose.imaging.PointF:
        '''Gets the shape's center.'''
        ...
    
    @property
    def segments(self) -> List[aspose.imaging.ShapeSegment]:
        '''Gets the shape segments.'''
        ...
    
    @property
    def has_segments(self) -> bool:
        ...
    
    @property
    def points(self) -> List[aspose.imaging.PointF]:
        '''Gets the curve points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.PointF]):
        '''Sets the curve points.'''
        ...
    
    @property
    def is_closed(self) -> bool:
        ...
    
    @is_closed.setter
    def is_closed(self, value : bool):
        ...
    
    @property
    def start_point(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def end_point(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def tension(self) -> float:
        '''Gets the curve tension.'''
        ...
    
    @tension.setter
    def tension(self, value : float):
        '''Sets the curve tension.'''
        ...
    
    ...

class EllipseShape(RectangleShape):
    '''Represents an ellipse shape.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, rectangle: aspose.imaging.RectangleF):
        '''Initializes a new instance of the  class.
        
        :param rectangle: The rectangle.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :returns: The estimated object's bounds.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix, pen: aspose.imaging.Pen) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :param pen: The pen to use for object. This can influence the object's bounds size.
        :returns: The estimated object's bounds.'''
        ...
    
    def transform(self, transform: aspose.imaging.Matrix):
        '''Applies the specified transformation to the shape.
        
        :param transform: The transformation to apply.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.'''
        ...
    
    @property
    def center(self) -> aspose.imaging.PointF:
        '''Gets the shape's center.'''
        ...
    
    @property
    def segments(self) -> List[aspose.imaging.ShapeSegment]:
        '''Gets the shape segments.'''
        ...
    
    @property
    def has_segments(self) -> bool:
        ...
    
    @property
    def left_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def left_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def rectangle_width(self) -> float:
        ...
    
    @property
    def rectangle_height(self) -> float:
        ...
    
    ...

class PieShape(EllipseShape):
    '''Represents a pie shape.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, rectangle: aspose.imaging.RectangleF, start_angle: float, sweep_angle: float):
        '''Initializes a new instance of the  class.
        
        :param rectangle: The rectangle.
        :param start_angle: The start angle.
        :param sweep_angle: The sweep angle.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :returns: The estimated object's bounds.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix, pen: aspose.imaging.Pen) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :param pen: The pen to use for object. This can influence the object's bounds size.
        :returns: The estimated object's bounds.'''
        ...
    
    def transform(self, transform: aspose.imaging.Matrix):
        '''Applies the specified transformation to the shape.
        
        :param transform: The transformation to apply.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.'''
        ...
    
    @property
    def center(self) -> aspose.imaging.PointF:
        '''Gets the shape's center.'''
        ...
    
    @property
    def segments(self) -> List[aspose.imaging.ShapeSegment]:
        '''Gets the shape segments.'''
        ...
    
    @property
    def has_segments(self) -> bool:
        ...
    
    @property
    def left_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def left_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def rectangle_width(self) -> float:
        ...
    
    @property
    def rectangle_height(self) -> float:
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @start_angle.setter
    def start_angle(self, value : float):
        ...
    
    @property
    def sweep_angle(self) -> float:
        ...
    
    @sweep_angle.setter
    def sweep_angle(self, value : float):
        ...
    
    ...

class PolygonShape(aspose.imaging.Shape):
    '''Represents a polygon shape.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, points: List[aspose.imaging.PointF]):
        '''Initializes a new instance of the  class.
        
        :param points: The points array.'''
        ...
    
    @overload
    def __init__(self, points: List[aspose.imaging.PointF], is_closed: bool):
        '''Initializes a new instance of the  class.
        
        :param points: The points array.
        :param is_closed: If set to ``true`` the polygon is closed.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :returns: The estimated object's bounds.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix, pen: aspose.imaging.Pen) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :param pen: The pen to use for object. This can influence the object's bounds size.
        :returns: The estimated object's bounds.'''
        ...
    
    def transform(self, transform: aspose.imaging.Matrix):
        '''Applies the specified transformation to the shape.
        
        :param transform: The transformation to apply.'''
        ...
    
    def reverse(self):
        '''Reverses the order of points for this shape.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.'''
        ...
    
    @property
    def center(self) -> aspose.imaging.PointF:
        '''Gets the shape's center.'''
        ...
    
    @property
    def segments(self) -> List[aspose.imaging.ShapeSegment]:
        '''Gets the shape segments.'''
        ...
    
    @property
    def has_segments(self) -> bool:
        ...
    
    @property
    def points(self) -> List[aspose.imaging.PointF]:
        '''Gets the curve points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.PointF]):
        '''Sets the curve points.'''
        ...
    
    @property
    def is_closed(self) -> bool:
        ...
    
    @is_closed.setter
    def is_closed(self, value : bool):
        ...
    
    @property
    def start_point(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def end_point(self) -> aspose.imaging.PointF:
        ...
    
    ...

class RectangleProjectedShape(aspose.imaging.Shape):
    '''Represents a shape which is projected over rectangle turned to a particular orientation.
    Specified by four points which can be rotated in space maintaining the same edges length and 90 degrees between adjacent edges.'''
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :returns: The estimated object's bounds.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix, pen: aspose.imaging.Pen) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :param pen: The pen to use for object. This can influence the object's bounds size.
        :returns: The estimated object's bounds.'''
        ...
    
    def transform(self, transform: aspose.imaging.Matrix):
        '''Applies the specified transformation to the shape.
        
        :param transform: The transformation to apply.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.'''
        ...
    
    @property
    def center(self) -> aspose.imaging.PointF:
        '''Gets the shape's center.'''
        ...
    
    @property
    def segments(self) -> List[aspose.imaging.ShapeSegment]:
        '''Gets the shape segments.'''
        ...
    
    @property
    def has_segments(self) -> bool:
        ...
    
    @property
    def left_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def left_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def rectangle_width(self) -> float:
        ...
    
    @property
    def rectangle_height(self) -> float:
        ...
    
    ...

class RectangleShape(RectangleProjectedShape):
    '''Represents a rectangular shape.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, rectangle: aspose.imaging.RectangleF):
        '''Initializes a new instance of the  class.
        
        :param rectangle: The rectangle.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :returns: The estimated object's bounds.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix, pen: aspose.imaging.Pen) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :param pen: The pen to use for object. This can influence the object's bounds size.
        :returns: The estimated object's bounds.'''
        ...
    
    def transform(self, transform: aspose.imaging.Matrix):
        '''Applies the specified transformation to the shape.
        
        :param transform: The transformation to apply.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.'''
        ...
    
    @property
    def center(self) -> aspose.imaging.PointF:
        '''Gets the shape's center.'''
        ...
    
    @property
    def segments(self) -> List[aspose.imaging.ShapeSegment]:
        '''Gets the shape segments.'''
        ...
    
    @property
    def has_segments(self) -> bool:
        ...
    
    @property
    def left_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def left_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def rectangle_width(self) -> float:
        ...
    
    @property
    def rectangle_height(self) -> float:
        ...
    
    ...

class TextShape(RectangleProjectedShape):
    '''Represents a text shape.'''
    
    @overload
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @overload
    def __init__(self, text: str, rectangle: aspose.imaging.RectangleF, font: aspose.imaging.Font, string_format: aspose.imaging.StringFormat):
        '''Initializes a new instance of the  class.
        
        :param text: The text to draw.
        :param rectangle: The text rectangle.
        :param font: The font to use.
        :param string_format: The string format.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :returns: The estimated object's bounds.'''
        ...
    
    @overload
    def get_bounds(self, matrix: aspose.imaging.Matrix, pen: aspose.imaging.Pen) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.
        
        :param matrix: The matrix to apply before bounds will be calculated.
        :param pen: The pen to use for object. This can influence the object's bounds size.
        :returns: The estimated object's bounds.'''
        ...
    
    def transform(self, transform: aspose.imaging.Matrix):
        '''Applies the specified transformation to the shape.
        
        :param transform: The transformation to apply.'''
        ...
    
    @property
    def bounds(self) -> aspose.imaging.RectangleF:
        '''Gets the object's bounds.'''
        ...
    
    @property
    def center(self) -> aspose.imaging.PointF:
        '''Gets the shape's center.'''
        ...
    
    @property
    def segments(self) -> List[aspose.imaging.ShapeSegment]:
        '''Gets the shape segments.'''
        ...
    
    @property
    def has_segments(self) -> bool:
        ...
    
    @property
    def left_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_top(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def left_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def right_bottom(self) -> aspose.imaging.PointF:
        ...
    
    @property
    def rectangle_width(self) -> float:
        ...
    
    @property
    def rectangle_height(self) -> float:
        ...
    
    @property
    def text(self) -> str:
        '''Gets the drawn text.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the drawn text.'''
        ...
    
    @property
    def font(self) -> aspose.imaging.Font:
        '''Gets the font used to draw the text.'''
        ...
    
    @font.setter
    def font(self, value : aspose.imaging.Font):
        '''Sets the font used to draw the text.'''
        ...
    
    @property
    def text_format(self) -> aspose.imaging.StringFormat:
        ...
    
    @text_format.setter
    def text_format(self, value : aspose.imaging.StringFormat):
        ...
    
    ...

