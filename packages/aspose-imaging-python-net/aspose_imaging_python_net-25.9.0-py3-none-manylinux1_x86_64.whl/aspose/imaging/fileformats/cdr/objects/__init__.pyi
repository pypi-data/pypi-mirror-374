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

class CdrArrow(CdrDictionaryItem):
    '''The cdr arrow'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    @property
    def points(self) -> List[aspose.imaging.fileformats.cdr.types.PointD]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.fileformats.cdr.types.PointD]):
        '''Sets the points.'''
        ...
    
    @property
    def point_types(self) -> bytes:
        ...
    
    @point_types.setter
    def point_types(self, value : bytes):
        ...
    
    ...

class CdrArtisticText(CdrGraphicObject):
    '''The cdr Artistic text'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the x.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the y.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def bounds_in_pixels(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounds_in_pixels.setter
    def bounds_in_pixels(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def clip_id(self) -> int:
        ...
    
    @clip_id.setter
    def clip_id(self, value : int):
        ...
    
    @property
    def origin(self) -> aspose.imaging.fileformats.cdr.types.PointD:
        '''Gets the origin.'''
        ...
    
    @origin.setter
    def origin(self, value : aspose.imaging.fileformats.cdr.types.PointD):
        '''Sets the origin.'''
        ...
    
    @property
    def text_index(self) -> int:
        ...
    
    @text_index.setter
    def text_index(self, value : int):
        ...
    
    ...

class CdrBbox(CdrObjectContainer):
    '''The cdr box'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    @property
    def x0(self) -> float:
        '''Gets the x0.'''
        ...
    
    @x0.setter
    def x0(self, value : float):
        '''Sets the x0.'''
        ...
    
    @property
    def y0(self) -> float:
        '''Gets the y0.'''
        ...
    
    @y0.setter
    def y0(self, value : float):
        '''Sets the y0.'''
        ...
    
    @property
    def x1(self) -> float:
        '''Gets the x1.'''
        ...
    
    @x1.setter
    def x1(self, value : float):
        '''Sets the x1.'''
        ...
    
    @property
    def y1(self) -> float:
        '''Gets the y1.'''
        ...
    
    @y1.setter
    def y1(self, value : float):
        '''Sets the y1.'''
        ...
    
    @property
    def x(self) -> float:
        '''Gets the x.'''
        ...
    
    @property
    def y(self) -> float:
        '''Gets the y.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the width.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the height.'''
        ...
    
    ...

class CdrBmp(CdrDictionaryItem):
    '''he cdr bmp'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    @property
    def color_model(self) -> int:
        ...
    
    @color_model.setter
    def color_model(self, value : int):
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height.'''
        ...
    
    @property
    def bpp(self) -> int:
        '''Gets the BPP.'''
        ...
    
    @bpp.setter
    def bpp(self, value : int):
        '''Sets the BPP.'''
        ...
    
    @property
    def bytes_per_line(self) -> int:
        ...
    
    @bytes_per_line.setter
    def bytes_per_line(self, value : int):
        ...
    
    @property
    def palette(self) -> List[int]:
        '''Gets the palette.'''
        ...
    
    @palette.setter
    def palette(self, value : List[int]):
        '''Sets the palette.'''
        ...
    
    ...

class CdrCurve(CdrGraphicObject):
    '''The cdr curve'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the x.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the y.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def bounds_in_pixels(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounds_in_pixels.setter
    def bounds_in_pixels(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def clip_id(self) -> int:
        ...
    
    @clip_id.setter
    def clip_id(self, value : int):
        ...
    
    @property
    def points(self) -> List[aspose.imaging.fileformats.cdr.types.PointD]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.fileformats.cdr.types.PointD]):
        '''Sets the points.'''
        ...
    
    @property
    def point_types(self) -> bytes:
        ...
    
    @point_types.setter
    def point_types(self, value : bytes):
        ...
    
    ...

class CdrDictionaryItem(CdrObject):
    '''The cdr dictionary item'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    ...

class CdrDisp(CdrObjectContainer):
    '''The cdr Disp'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    ...

class CdrDocument(CdrObjectContainer):
    '''The cdr root object'''
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    @property
    def texts(self) -> aspose.imaging.fileformats.cdr.types.CdrTextCollection:
        '''Gets the texts.'''
        ...
    
    @property
    def clip_ids(self) -> System.Collections.Generic.List`1[[System.Int16]]:
        ...
    
    @clip_ids.setter
    def clip_ids(self, value : System.Collections.Generic.List`1[[System.Int16]]):
        ...
    
    @property
    def last_text_index(self) -> int:
        ...
    
    @last_text_index.setter
    def last_text_index(self, value : int):
        ...
    
    @property
    def version(self) -> int:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets the version.'''
        ...
    
    ...

class CdrEllipse(CdrGraphicObject):
    '''The cdr Ellipse'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the x.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the y.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def bounds_in_pixels(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounds_in_pixels.setter
    def bounds_in_pixels(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def clip_id(self) -> int:
        ...
    
    @clip_id.setter
    def clip_id(self, value : int):
        ...
    
    @property
    def angle1(self) -> float:
        '''Gets the angle1.'''
        ...
    
    @angle1.setter
    def angle1(self, value : float):
        '''Sets the angle1.'''
        ...
    
    @property
    def angle2(self) -> float:
        '''Gets the angle2.'''
        ...
    
    @angle2.setter
    def angle2(self, value : float):
        '''Sets the angle2.'''
        ...
    
    @property
    def pie(self) -> bool:
        '''Gets a value indicating whether this  is pie.'''
        ...
    
    @pie.setter
    def pie(self, value : bool):
        '''Sets a value indicating whether this  is pie.'''
        ...
    
    ...

class CdrFill(CdrDictionaryItem):
    '''The cdr fill'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    @property
    def fill_type(self) -> aspose.imaging.fileformats.cdr.enum.CdrFillType:
        ...
    
    @fill_type.setter
    def fill_type(self, value : aspose.imaging.fileformats.cdr.enum.CdrFillType):
        ...
    
    @property
    def color1(self) -> aspose.imaging.fileformats.cdr.types.CdrColor:
        '''Gets the color1.'''
        ...
    
    @color1.setter
    def color1(self, value : aspose.imaging.fileformats.cdr.types.CdrColor):
        '''Sets the color1.'''
        ...
    
    @property
    def color2(self) -> aspose.imaging.fileformats.cdr.types.CdrColor:
        '''Gets the color2.'''
        ...
    
    @color2.setter
    def color2(self, value : aspose.imaging.fileformats.cdr.types.CdrColor):
        '''Sets the color2.'''
        ...
    
    @property
    def gradient(self) -> aspose.imaging.fileformats.cdr.types.CdrGradient:
        '''Gets the gradient.'''
        ...
    
    @gradient.setter
    def gradient(self, value : aspose.imaging.fileformats.cdr.types.CdrGradient):
        '''Sets the gradient.'''
        ...
    
    @property
    def image_fill(self) -> aspose.imaging.fileformats.cdr.types.CdrImageFill:
        ...
    
    @image_fill.setter
    def image_fill(self, value : aspose.imaging.fileformats.cdr.types.CdrImageFill):
        ...
    
    ...

class CdrFillTransform(CdrObjectContainer):
    '''the cdr fill transform'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    @property
    def transform(self) -> aspose.imaging.Matrix:
        '''Gets the transform.'''
        ...
    
    @transform.setter
    def transform(self, value : aspose.imaging.Matrix):
        '''Sets the transform.'''
        ...
    
    ...

class CdrFlgs(CdrObject):
    '''The cdr flags'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def value(self) -> int:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : int):
        '''Sets the value.'''
        ...
    
    ...

class CdrFont(CdrDictionaryItem):
    '''the cdr Font'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    @property
    def font_name(self) -> str:
        ...
    
    @font_name.setter
    def font_name(self, value : str):
        ...
    
    @property
    def encoding(self) -> int:
        '''Gets the encoding.'''
        ...
    
    @encoding.setter
    def encoding(self, value : int):
        '''Sets the encoding.'''
        ...
    
    ...

class CdrGraphicObject(CdrObject):
    '''The cdr graphic object'''
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the x.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the y.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def bounds_in_pixels(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounds_in_pixels.setter
    def bounds_in_pixels(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def clip_id(self) -> int:
        ...
    
    @clip_id.setter
    def clip_id(self, value : int):
        ...
    
    ...

class CdrIcc(CdrObjectContainer):
    '''The cdr Icc profile'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    ...

class CdrListObjects(CdrObjectContainer):
    '''The cdr list objects'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    @property
    def page_width(self) -> float:
        ...
    
    @page_width.setter
    def page_width(self, value : float):
        ...
    
    @property
    def page_height(self) -> float:
        ...
    
    @page_height.setter
    def page_height(self, value : float):
        ...
    
    @property
    def fill_id(self) -> int:
        ...
    
    @fill_id.setter
    def fill_id(self, value : int):
        ...
    
    @property
    def opacity_fill_id(self) -> int:
        ...
    
    @opacity_fill_id.setter
    def opacity_fill_id(self, value : int):
        ...
    
    @property
    def out_line_id(self) -> int:
        ...
    
    @out_line_id.setter
    def out_line_id(self, value : int):
        ...
    
    @property
    def style_id(self) -> int:
        ...
    
    @style_id.setter
    def style_id(self, value : int):
        ...
    
    @property
    def opacity(self) -> float:
        '''Gets the opacity.'''
        ...
    
    @opacity.setter
    def opacity(self, value : float):
        '''Sets the opacity.'''
        ...
    
    ...

class CdrMcfg(CdrObject):
    '''The cdr configuration object'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the width.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the width.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the height.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the height.'''
        ...
    
    ...

class CdrObject(aspose.imaging.DisposableObject):
    '''The cdr object'''
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    ...

class CdrObjectContainer(CdrObject):
    '''The cdr object container'''
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    ...

class CdrOutline(CdrDictionaryItem):
    '''The cdr out line'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    @property
    def line_type(self) -> int:
        ...
    
    @line_type.setter
    def line_type(self, value : int):
        ...
    
    @property
    def caps_type(self) -> int:
        ...
    
    @caps_type.setter
    def caps_type(self, value : int):
        ...
    
    @property
    def join_type(self) -> int:
        ...
    
    @join_type.setter
    def join_type(self, value : int):
        ...
    
    @property
    def line_width(self) -> float:
        ...
    
    @line_width.setter
    def line_width(self, value : float):
        ...
    
    @property
    def stretch(self) -> float:
        '''Gets the stretch.'''
        ...
    
    @stretch.setter
    def stretch(self, value : float):
        '''Sets the stretch.'''
        ...
    
    @property
    def aangle(self) -> float:
        '''Gets the angle.'''
        ...
    
    @aangle.setter
    def aangle(self, value : float):
        '''Sets the angle.'''
        ...
    
    @property
    def color(self) -> aspose.imaging.fileformats.cdr.types.CdrColor:
        '''Gets the color.'''
        ...
    
    @color.setter
    def color(self, value : aspose.imaging.fileformats.cdr.types.CdrColor):
        '''Sets the color.'''
        ...
    
    @property
    def dash_array(self) -> System.Collections.Generic.List`1[[System.Int32]]:
        ...
    
    @dash_array.setter
    def dash_array(self, value : System.Collections.Generic.List`1[[System.Int32]]):
        ...
    
    @property
    def start_marker_id(self) -> int:
        ...
    
    @start_marker_id.setter
    def start_marker_id(self, value : int):
        ...
    
    @property
    def end_marker_id(self) -> int:
        ...
    
    @end_marker_id.setter
    def end_marker_id(self, value : int):
        ...
    
    ...

class CdrPage(CdrObjectContainer):
    '''The cdr page'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    ...

class CdrParagraph(CdrGraphicObject):
    '''The cdr Paragraph'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the x.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the y.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def bounds_in_pixels(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounds_in_pixels.setter
    def bounds_in_pixels(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def clip_id(self) -> int:
        ...
    
    @clip_id.setter
    def clip_id(self, value : int):
        ...
    
    @property
    def text_index(self) -> int:
        ...
    
    @text_index.setter
    def text_index(self, value : int):
        ...
    
    ...

class CdrPathObject(CdrGraphicObject):
    '''The Cdr path'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the x.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the y.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def bounds_in_pixels(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounds_in_pixels.setter
    def bounds_in_pixels(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def clip_id(self) -> int:
        ...
    
    @clip_id.setter
    def clip_id(self, value : int):
        ...
    
    @property
    def points(self) -> List[aspose.imaging.fileformats.cdr.types.PointD]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.fileformats.cdr.types.PointD]):
        '''Sets the points.'''
        ...
    
    @property
    def point_types(self) -> bytes:
        ...
    
    @point_types.setter
    def point_types(self, value : bytes):
        ...
    
    ...

class CdrPattern(CdrDictionaryItem):
    '''The cdr bitmap'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    @property
    def width(self) -> int:
        '''Gets the width.'''
        ...
    
    @width.setter
    def width(self, value : int):
        '''Sets the width.'''
        ...
    
    @property
    def height(self) -> int:
        '''Gets the height.'''
        ...
    
    @height.setter
    def height(self, value : int):
        '''Sets the height.'''
        ...
    
    ...

class CdrPolygon(CdrGraphicObject):
    '''The cdr polygon'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the x.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the y.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def bounds_in_pixels(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounds_in_pixels.setter
    def bounds_in_pixels(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def clip_id(self) -> int:
        ...
    
    @clip_id.setter
    def clip_id(self, value : int):
        ...
    
    @property
    def points(self) -> List[aspose.imaging.fileformats.cdr.types.PointD]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.fileformats.cdr.types.PointD]):
        '''Sets the points.'''
        ...
    
    @property
    def point_types(self) -> bytes:
        ...
    
    @point_types.setter
    def point_types(self, value : bytes):
        ...
    
    ...

class CdrPolygonTransform(CdrObjectContainer):
    '''The polygon transform'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    @property
    def x_radius(self) -> float:
        ...
    
    @x_radius.setter
    def x_radius(self, value : float):
        ...
    
    @property
    def y_radius(self) -> float:
        ...
    
    @y_radius.setter
    def y_radius(self, value : float):
        ...
    
    @property
    def position(self) -> aspose.imaging.fileformats.cdr.types.PointD:
        '''Gets the position.'''
        ...
    
    @position.setter
    def position(self, value : aspose.imaging.fileformats.cdr.types.PointD):
        '''Sets the position.'''
        ...
    
    @property
    def num_angles(self) -> int:
        ...
    
    @num_angles.setter
    def num_angles(self, value : int):
        ...
    
    @property
    def next_point(self) -> int:
        ...
    
    @next_point.setter
    def next_point(self, value : int):
        ...
    
    ...

class CdrPpdt(CdrGraphicObject):
    '''The cdr knot vector object'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the x.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the y.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def bounds_in_pixels(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounds_in_pixels.setter
    def bounds_in_pixels(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def clip_id(self) -> int:
        ...
    
    @clip_id.setter
    def clip_id(self, value : int):
        ...
    
    @property
    def points(self) -> List[aspose.imaging.fileformats.cdr.types.PointD]:
        '''Gets the points.'''
        ...
    
    @points.setter
    def points(self, value : List[aspose.imaging.fileformats.cdr.types.PointD]):
        '''Sets the points.'''
        ...
    
    @property
    def knot_vecor(self) -> List[int]:
        ...
    
    @knot_vecor.setter
    def knot_vecor(self, value : List[int]):
        ...
    
    ...

class CdrRectangle(CdrGraphicObject):
    '''The cdr rectangle'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def width(self) -> float:
        '''Gets the x.'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''Sets the x.'''
        ...
    
    @property
    def height(self) -> float:
        '''Gets the y.'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''Sets the y.'''
        ...
    
    @property
    def bounds_in_pixels(self) -> aspose.imaging.RectangleF:
        ...
    
    @bounds_in_pixels.setter
    def bounds_in_pixels(self, value : aspose.imaging.RectangleF):
        ...
    
    @property
    def clip_id(self) -> int:
        ...
    
    @clip_id.setter
    def clip_id(self, value : int):
        ...
    
    @property
    def r3(self) -> float:
        '''Gets the r3.'''
        ...
    
    @r3.setter
    def r3(self, value : float):
        '''Sets the r3.'''
        ...
    
    @property
    def r2(self) -> float:
        '''Gets the r2.'''
        ...
    
    @r2.setter
    def r2(self, value : float):
        '''Sets the r2.'''
        ...
    
    @property
    def r1(self) -> float:
        '''Gets the r1.'''
        ...
    
    @r1.setter
    def r1(self, value : float):
        '''Sets the r1.'''
        ...
    
    @property
    def r0(self) -> float:
        '''Gets the r0.'''
        ...
    
    @r0.setter
    def r0(self, value : float):
        '''Sets the r0.'''
        ...
    
    @property
    def corner_type(self) -> int:
        ...
    
    @corner_type.setter
    def corner_type(self, value : int):
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

class CdrSpnd(CdrDictionaryItem):
    '''The cdr span'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    @property
    def value(self) -> int:
        '''Gets the value.'''
        ...
    
    @value.setter
    def value(self, value : int):
        '''Sets the value.'''
        ...
    
    ...

class CdrStyd(CdrObjectContainer):
    '''The cdr style'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    ...

class CdrStyle(CdrDictionaryItem):
    '''The cdr style'''
    
    def __init__(self):
        ...
    
    def copy(self) -> aspose.imaging.fileformats.cdr.objects.CdrStyle:
        '''Copies this instance.
        
        :returns: The current style copy'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
        ...
    
    @property
    def font_name(self) -> str:
        ...
    
    @font_name.setter
    def font_name(self, value : str):
        ...
    
    @property
    def charset(self) -> int:
        '''Gets the character set.'''
        ...
    
    @charset.setter
    def charset(self, value : int):
        '''Sets the character set.'''
        ...
    
    @property
    def font_size(self) -> float:
        ...
    
    @font_size.setter
    def font_size(self, value : float):
        ...
    
    @property
    def font_weight(self) -> int:
        ...
    
    @font_weight.setter
    def font_weight(self, value : int):
        ...
    
    @property
    def fill(self) -> aspose.imaging.fileformats.cdr.objects.CdrFill:
        '''Gets the fill.'''
        ...
    
    @fill.setter
    def fill(self, value : aspose.imaging.fileformats.cdr.objects.CdrFill):
        '''Sets the fill.'''
        ...
    
    @property
    def out_line(self) -> aspose.imaging.fileformats.cdr.objects.CdrOutline:
        ...
    
    @out_line.setter
    def out_line(self, value : aspose.imaging.fileformats.cdr.objects.CdrOutline):
        ...
    
    @property
    def align(self) -> int:
        '''Gets the align.'''
        ...
    
    @align.setter
    def align(self, value : int):
        '''Sets the align.'''
        ...
    
    @property
    def right_indent(self) -> float:
        ...
    
    @right_indent.setter
    def right_indent(self, value : float):
        ...
    
    @property
    def first_indent(self) -> float:
        ...
    
    @first_indent.setter
    def first_indent(self, value : float):
        ...
    
    @property
    def left_indent(self) -> float:
        ...
    
    @left_indent.setter
    def left_indent(self, value : float):
        ...
    
    @property
    def parent_id(self) -> int:
        ...
    
    @parent_id.setter
    def parent_id(self, value : int):
        ...
    
    ...

class CdrText(CdrDictionaryItem):
    '''The cdr text'''
    
    def __init__(self):
        '''Initializes a new instance of the  class.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.
        For legacy compatibility'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.
        For legacy compatibility'''
        ...
    
    @property
    def text(self) -> str:
        '''Gets the CDR text boxes.'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''Sets the CDR text boxes.'''
        ...
    
    @property
    def char_descriptors(self) -> bytes:
        ...
    
    @char_descriptors.setter
    def char_descriptors(self, value : bytes):
        ...
    
    @property
    def styles(self) -> List[aspose.imaging.fileformats.cdr.objects.CdrStyle]:
        '''Adds the text box.'''
        ...
    
    @styles.setter
    def styles(self, value : List[aspose.imaging.fileformats.cdr.objects.CdrStyle]):
        '''Adds the text box.'''
        ...
    
    @property
    def style_id(self) -> int:
        ...
    
    @style_id.setter
    def style_id(self, value : int):
        ...
    
    ...

class CdrTransforms(CdrObject):
    '''The cdr transforms object'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def transforms(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.Matrix]]:
        '''Gets the transforms.'''
        ...
    
    @transforms.setter
    def transforms(self, value : System.Collections.Generic.List`1[[Aspose.Imaging.Matrix]]):
        '''Sets the transforms.'''
        ...
    
    ...

class CdrUdta(CdrObjectContainer):
    '''The cdr udta'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    ...

class CdrUserPalette(CdrObjectContainer):
    '''The cdr user palette'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    ...

class CdrVectorPattern(CdrDictionaryItem):
    '''The cdr vector pattern'''
    
    def __init__(self):
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def id(self) -> int:
        '''Gets the identifier.'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''Sets the identifier.'''
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

class CdrVersion(CdrObjectContainer):
    '''The cdr Version'''
    
    def __init__(self):
        ...
    
    def add_child_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Adds the child object.
        
        :param cdr_object: The CDR object.'''
        ...
    
    def insert_object(self, cdr_object: aspose.imaging.fileformats.cdr.objects.CdrObject):
        '''Inserts the object
        
        :param cdr_object: The CDR object.'''
        ...
    
    @property
    def disposed(self) -> bool:
        '''Gets a value indicating whether this instance is disposed.'''
        ...
    
    @property
    def parent(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        '''Gets the parent.'''
        ...
    
    @parent.setter
    def parent(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        '''Sets the parent.'''
        ...
    
    @property
    def document(self) -> aspose.imaging.fileformats.cdr.objects.CdrDocument:
        '''Gets the document.'''
        ...
    
    @document.setter
    def document(self, value : aspose.imaging.fileformats.cdr.objects.CdrDocument):
        '''Sets the document.'''
        ...
    
    @property
    def childs(self) -> System.Collections.Generic.List`1[[Aspose.Imaging.FileFormats.Cdr.Objects.CdrObject]]:
        '''Gets the objects.'''
        ...
    
    @property
    def load_to_last_child(self) -> bool:
        ...
    
    @load_to_last_child.setter
    def load_to_last_child(self, value : bool):
        ...
    
    @property
    def last_child(self) -> aspose.imaging.fileformats.cdr.objects.CdrObjectContainer:
        ...
    
    @last_child.setter
    def last_child(self, value : aspose.imaging.fileformats.cdr.objects.CdrObjectContainer):
        ...
    
    @property
    def hidden(self) -> bool:
        '''Gets a value indicating whether this  is visible.'''
        ...
    
    @hidden.setter
    def hidden(self, value : bool):
        '''Sets a value indicating whether this  is visible.'''
        ...
    
    @property
    def version(self) -> int:
        '''Gets the version.'''
        ...
    
    @version.setter
    def version(self, value : int):
        '''Sets the version.'''
        ...
    
    ...

