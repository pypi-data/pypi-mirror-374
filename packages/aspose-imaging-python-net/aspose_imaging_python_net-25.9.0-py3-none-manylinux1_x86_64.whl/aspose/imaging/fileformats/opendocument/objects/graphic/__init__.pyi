"""The Open document graphic objects"""
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

class OdAngleEllipse(OdStyledObject):
    '''The Enhanced angle ellipse'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @start_angle.setter
    def start_angle(self, value : float):
        ...
    
    @property
    def end_angle(self) -> float:
        ...
    
    @end_angle.setter
    def end_angle(self, value : float):
        ...
    
    @property
    def closed(self) -> bool:
        '''Gets a value indicating whether this  is closed.'''
        ...
    
    @closed.setter
    def closed(self, value : bool):
        '''Sets a value indicating whether this  is closed.'''
        ...
    
    @property
    def kind(self) -> aspose.imaging.fileformats.opendocument.enums.OdObjectKind:
        '''Gets the kind.'''
        ...
    
    @kind.setter
    def kind(self, value : aspose.imaging.fileformats.opendocument.enums.OdObjectKind):
        '''Sets the kind.'''
        ...
    
    ...

class OdArc(OdGraphicObject):
    '''The Enhanced Arc'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def is_arc_to(self) -> bool:
        ...
    
    @is_arc_to.setter
    def is_arc_to(self, value : bool):
        ...
    
    @property
    def is_elliptical_qundrant_x(self) -> bool:
        ...
    
    @is_elliptical_qundrant_x.setter
    def is_elliptical_qundrant_x(self, value : bool):
        ...
    
    @property
    def is_elliptical_qundrant_y(self) -> bool:
        ...
    
    @is_elliptical_qundrant_y.setter
    def is_elliptical_qundrant_y(self, value : bool):
        ...
    
    @property
    def clock_wise(self) -> bool:
        ...
    
    @clock_wise.setter
    def clock_wise(self, value : bool):
        ...
    
    @property
    def point1(self) -> aspose.imaging.PointF:
        '''Gets the point1.'''
        ...
    
    @point1.setter
    def point1(self, value : aspose.imaging.PointF):
        '''Sets the point1.'''
        ...
    
    @property
    def point2(self) -> aspose.imaging.PointF:
        '''Gets the point2.'''
        ...
    
    @point2.setter
    def point2(self, value : aspose.imaging.PointF):
        '''Sets the point2.'''
        ...
    
    @property
    def point3(self) -> aspose.imaging.PointF:
        '''Gets the point3.'''
        ...
    
    @point3.setter
    def point3(self, value : aspose.imaging.PointF):
        '''Sets the point3.'''
        ...
    
    @property
    def point4(self) -> aspose.imaging.PointF:
        '''Gets the point4.'''
        ...
    
    @point4.setter
    def point4(self, value : aspose.imaging.PointF):
        '''Sets the point4.'''
        ...
    
    ...

class OdCircle(OdAngleEllipse):
    '''The circle object'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def start_angle(self) -> float:
        ...
    
    @start_angle.setter
    def start_angle(self, value : float):
        ...
    
    @property
    def end_angle(self) -> float:
        ...
    
    @end_angle.setter
    def end_angle(self, value : float):
        ...
    
    @property
    def closed(self) -> bool:
        '''Gets a value indicating whether this  is closed.'''
        ...
    
    @closed.setter
    def closed(self, value : bool):
        '''Sets a value indicating whether this  is closed.'''
        ...
    
    @property
    def kind(self) -> aspose.imaging.fileformats.opendocument.enums.OdObjectKind:
        '''Gets the kind.'''
        ...
    
    @kind.setter
    def kind(self, value : aspose.imaging.fileformats.opendocument.enums.OdObjectKind):
        '''Sets the kind.'''
        ...
    
    ...

class OdClosePath(OdGraphicObject):
    '''The close path'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    ...

class OdConnector(OdStyledObject):
    '''The  connector'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def path_commands(self) -> List[aspose.imaging.fileformats.opendocument.objects.graphic.OdGraphicObject]:
        ...
    
    @path_commands.setter
    def path_commands(self, value : List[aspose.imaging.fileformats.opendocument.objects.graphic.OdGraphicObject]):
        ...
    
    @property
    def point1(self) -> aspose.imaging.PointF:
        '''Gets the point1.'''
        ...
    
    @point1.setter
    def point1(self, value : aspose.imaging.PointF):
        '''Sets the point1.'''
        ...
    
    @property
    def point2(self) -> aspose.imaging.PointF:
        '''Gets the point2.'''
        ...
    
    @point2.setter
    def point2(self, value : aspose.imaging.PointF):
        '''Sets the point2.'''
        ...
    
    ...

class OdContainer(OdStyledObject):
    '''The Container'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    ...

class OdCurveTo(OdGraphicObject):
    '''The Enhanced CurveTo'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def points(self) -> List[aspose.imaging.PointF]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.PointF]):
        '''Sets the points.'''
        ...
    
    ...

class OdCustomShape(OdStyledObject):
    '''The open document custom-shape.'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def style_name(self) -> str:
        ...
    
    @style_name.setter
    def style_name(self, value : str):
        ...
    
    @property
    def text_style_name(self) -> str:
        ...
    
    @text_style_name.setter
    def text_style_name(self, value : str):
        ...
    
    @property
    def layer(self) -> str:
        '''Gets the layer.'''
        ...
    
    @layer.setter
    def layer(self, value : str):
        '''Sets the layer.'''
        ...
    
    ...

class OdEllipticalQundrant(OdGraphicObject):
    '''The elliptical quadrant'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def point(self) -> aspose.imaging.PointF:
        '''Gets the point.'''
        ...
    
    @point.setter
    def point(self, value : aspose.imaging.PointF):
        '''Sets the point.'''
        ...
    
    @property
    def axis_x(self) -> bool:
        ...
    
    @axis_x.setter
    def axis_x(self, value : bool):
        ...
    
    ...

class OdEndPath(OdGraphicObject):
    '''The enhanced end path'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def fill(self) -> bool:
        '''Gets a value indicating whether this  is fill.'''
        ...
    
    @fill.setter
    def fill(self, value : bool):
        '''Sets a value indicating whether this  is fill.'''
        ...
    
    ...

class OdEnhancedGeometry(OdGraphicObject):
    '''The Enhanced geometry object.'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def enhanced_path(self) -> List[aspose.imaging.fileformats.opendocument.objects.graphic.OdGraphicObject]:
        ...
    
    @enhanced_path.setter
    def enhanced_path(self, value : List[aspose.imaging.fileformats.opendocument.objects.graphic.OdGraphicObject]):
        ...
    
    @property
    def view_box(self) -> aspose.imaging.Rectangle:
        ...
    
    @view_box.setter
    def view_box(self, value : aspose.imaging.Rectangle):
        ...
    
    @property
    def type(self) -> str:
        '''Gets the type.'''
        ...
    
    @type.setter
    def type(self, value : str):
        '''Sets the type.'''
        ...
    
    ...

class OdEquation(OdGraphicObject):
    '''The open document equation'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.'''
        ...
    
    @property
    def formula(self) -> str:
        '''Gets the formula.'''
        ...
    
    @formula.setter
    def formula(self, value : str):
        '''Sets the formula.'''
        ...
    
    @property
    def value(self) -> float:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : float):
        '''Sets the value.'''
        ...
    
    ...

class OdFrame(OdStyledObject):
    '''The open document object frame'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    ...

class OdGraphicObject(aspose.imaging.fileformats.opendocument.OdObject):
    '''The open document graphic object.'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    ...

class OdImageObject(OdGraphicObject):
    '''The open document image'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def image_link(self) -> str:
        ...
    
    @image_link.setter
    def image_link(self, value : str):
        ...
    
    @property
    def bitmap(self) -> bytes:
        '''Gets the bitmap.'''
        ...
    
    @bitmap.setter
    def bitmap(self, value : bytes):
        '''Sets the bitmap.'''
        ...
    
    ...

class OdLine(OdStyledObject):
    '''The line object'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def point1(self) -> aspose.imaging.PointF:
        '''Gets the point1.'''
        ...
    
    @point1.setter
    def point1(self, value : aspose.imaging.PointF):
        '''Sets the point1.'''
        ...
    
    @property
    def point2(self) -> aspose.imaging.PointF:
        '''Gets the point2.'''
        ...
    
    @point2.setter
    def point2(self, value : aspose.imaging.PointF):
        '''Sets the point2.'''
        ...
    
    ...

class OdLineTo(OdGraphicObject):
    '''The enhanced lineTo'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def coordinates(self) -> aspose.imaging.PointF:
        '''Gets the coordinates.'''
        ...
    
    @coordinates.setter
    def coordinates(self, value : aspose.imaging.PointF):
        '''Sets the coordinates.'''
        ...
    
    @property
    def vertical(self) -> bool:
        '''Gets a value indicating whether this  is vertical.'''
        ...
    
    @vertical.setter
    def vertical(self, value : bool):
        '''Sets a value indicating whether this  is vertical.'''
        ...
    
    @property
    def horizontal(self) -> bool:
        '''Gets a value indicating whether this  is vertical.'''
        ...
    
    @horizontal.setter
    def horizontal(self, value : bool):
        '''Sets a value indicating whether this  is vertical.'''
        ...
    
    ...

class OdList(OdStyledObject):
    '''The List object'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    ...

class OdListItem(OdGraphicObject):
    '''The list item'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    ...

class OdMarker(OdGraphicObject):
    '''The Marker'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def path_commands(self) -> List[aspose.imaging.fileformats.opendocument.objects.graphic.OdGraphicObject]:
        ...
    
    @path_commands.setter
    def path_commands(self, value : List[aspose.imaging.fileformats.opendocument.objects.graphic.OdGraphicObject]):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.'''
        ...
    
    ...

class OdMeasure(OdStyledObject):
    '''The Measure'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def point1(self) -> aspose.imaging.PointF:
        '''Gets the point1.'''
        ...
    
    @point1.setter
    def point1(self, value : aspose.imaging.PointF):
        '''Sets the point1.'''
        ...
    
    @property
    def point2(self) -> aspose.imaging.PointF:
        '''Gets the point2.'''
        ...
    
    @point2.setter
    def point2(self, value : aspose.imaging.PointF):
        '''Sets the point2.'''
        ...
    
    @property
    def point3(self) -> aspose.imaging.PointF:
        '''Gets the point3.'''
        ...
    
    @point3.setter
    def point3(self, value : aspose.imaging.PointF):
        '''Sets the point3.'''
        ...
    
    @property
    def point4(self) -> aspose.imaging.PointF:
        '''Gets the point4.'''
        ...
    
    @point4.setter
    def point4(self, value : aspose.imaging.PointF):
        '''Sets the point4.'''
        ...
    
    ...

class OdMoveTo(OdGraphicObject):
    '''The Enhanced moveTo'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def coordinates(self) -> aspose.imaging.PointF:
        '''Gets the coordinates.'''
        ...
    
    @coordinates.setter
    def coordinates(self, value : aspose.imaging.PointF):
        '''Sets the coordinates.'''
        ...
    
    ...

class OdNoFillPath(OdGraphicObject):
    '''The no fill path marker'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    ...

class OdNoStrokePath(OdGraphicObject):
    '''Specifies that the current set of sub-paths will not be stroked.'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    ...

class OdPage(OdGraphicObject):
    '''The Open document page.'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def name(self) -> str:
        '''Gets the name.'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''Sets the name.'''
        ...
    
    @property
    def master_page_name(self) -> str:
        ...
    
    @master_page_name.setter
    def master_page_name(self, value : str):
        ...
    
    @property
    def style_name(self) -> str:
        ...
    
    @style_name.setter
    def style_name(self, value : str):
        ...
    
    ...

class OdPath(OdStyledObject):
    '''The open document object path'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def style_name(self) -> str:
        ...
    
    @style_name.setter
    def style_name(self, value : str):
        ...
    
    @property
    def text_style_name(self) -> str:
        ...
    
    @text_style_name.setter
    def text_style_name(self, value : str):
        ...
    
    @property
    def layer(self) -> str:
        '''Gets the layer.'''
        ...
    
    @layer.setter
    def layer(self, value : str):
        '''Sets the layer.'''
        ...
    
    @property
    def data(self) -> str:
        '''Gets the data.'''
        ...
    
    @data.setter
    def data(self, value : str):
        '''Sets the data.'''
        ...
    
    @property
    def enhanced_path(self) -> List[aspose.imaging.fileformats.opendocument.objects.graphic.OdGraphicObject]:
        ...
    
    @enhanced_path.setter
    def enhanced_path(self, value : List[aspose.imaging.fileformats.opendocument.objects.graphic.OdGraphicObject]):
        ...
    
    ...

class OdPolyLine(OdPolygon):
    '''The polyline'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def points(self) -> List[aspose.imaging.PointF]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.PointF]):
        '''Sets the points.'''
        ...
    
    ...

class OdPolygon(OdStyledObject):
    '''The polygon'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def points(self) -> List[aspose.imaging.PointF]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.PointF]):
        '''Sets the points.'''
        ...
    
    ...

class OdRectangle(OdStyledObject):
    '''The rectangle object'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def corner_radius(self) -> float:
        ...
    
    @corner_radius.setter
    def corner_radius(self, value : float):
        ...
    
    ...

class OdShortCurveTo(OdCurveTo):
    '''The short CurveTo'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def points(self) -> List[aspose.imaging.PointF]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.PointF]):
        '''Sets the points.'''
        ...
    
    ...

class OdStyledObject(OdGraphicObject):
    '''The open document styled graphic object.'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    ...

class OdText(aspose.imaging.fileformats.opendocument.OdObject):
    '''The text object'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
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

class OdTextBox(OdGraphicObject):
    '''The text box'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    ...

class OdTextMeasure(OdStyledObject):
    '''The text measure'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
        ...
    
    @property
    def text(self) -> str:
        '''Gets the value.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the value.'''
        ...
    
    @property
    def kind(self) -> aspose.imaging.fileformats.opendocument.enums.OdMeasureTextKind:
        '''Gets the kind.'''
        ...
    
    @kind.setter
    def kind(self, value : aspose.imaging.fileformats.opendocument.enums.OdMeasureTextKind):
        '''Sets the kind.'''
        ...
    
    ...

class OdTextParagraph(OdStyledObject):
    '''The text paragraph'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
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

class OdTextSpan(OdStyledObject):
    '''The text span'''
    
    def __init__(self, parent: aspose.imaging.fileformats.opendocument.OdObject):
        '''Initializes a new instance of the  class.
        
        :param parent: The parent.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.opendocument.OdObject:
        '''Gets the parent object.'''
        ...
    
    @property
    def items(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.OpenDocument.OdObject]]:
        '''Gets the items.'''
        ...
    
    @property
    def absolute_coordinates(self) -> bool:
        ...
    
    @absolute_coordinates.setter
    def absolute_coordinates(self, value : bool):
        ...
    
    @property
    def style(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Gets the style.'''
        ...
    
    @style.setter
    def style(self, value : aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle):
        '''Sets the style.'''
        ...
    
    @property
    def rectangle(self) -> aspose.imaging.RectangleF:
        '''Gets the rectangle.'''
        ...
    
    @rectangle.setter
    def rectangle(self, value : aspose.imaging.RectangleF):
        '''Sets the rectangle.'''
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

