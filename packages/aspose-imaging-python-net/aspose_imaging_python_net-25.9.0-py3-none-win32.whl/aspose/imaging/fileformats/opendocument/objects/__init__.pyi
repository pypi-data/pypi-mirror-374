"""The Open document objects"""
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

class OdGraphicStyle:
    '''The open document graphic style.'''
    
    def __init__(self):
        ...
    
    def copy(self) -> aspose.imaging.fileformats.opendocument.objects.OdGraphicStyle:
        '''Copies this instance.
        
        :returns: Gets the copy of this instance.'''
        ...
    
    @property
    def brush(self) -> aspose.imaging.fileformats.opendocument.objects.brush.OdBrush:
        '''Gets the brush.'''
        ...
    
    @brush.setter
    def brush(self, value : aspose.imaging.fileformats.opendocument.objects.brush.OdBrush):
        '''Gets the brush.'''
        ...
    
    @property
    def pen(self) -> aspose.imaging.fileformats.opendocument.objects.pen.OdPen:
        '''Gets the pen.'''
        ...
    
    @property
    def font(self) -> aspose.imaging.fileformats.opendocument.objects.font.OdFont:
        '''Gets the font.'''
        ...
    
    @property
    def text_color(self) -> int:
        ...
    
    @text_color.setter
    def text_color(self, value : int):
        ...
    
    @property
    def text_align(self) -> aspose.imaging.fileformats.opendocument.enums.OdTextAlignModeFlags:
        ...
    
    @text_align.setter
    def text_align(self, value : aspose.imaging.fileformats.opendocument.enums.OdTextAlignModeFlags):
        ...
    
    @property
    def line_height(self) -> int:
        ...
    
    @line_height.setter
    def line_height(self, value : int):
        ...
    
    @property
    def transform_info(self) -> aspose.imaging.fileformats.opendocument.objects.OdTransformInfo:
        ...
    
    @property
    def start_marker(self) -> aspose.imaging.fileformats.opendocument.objects.graphic.OdMarker:
        ...
    
    @start_marker.setter
    def start_marker(self, value : aspose.imaging.fileformats.opendocument.objects.graphic.OdMarker):
        ...
    
    @property
    def end_marker(self) -> aspose.imaging.fileformats.opendocument.objects.graphic.OdMarker:
        ...
    
    @end_marker.setter
    def end_marker(self, value : aspose.imaging.fileformats.opendocument.objects.graphic.OdMarker):
        ...
    
    @property
    def start_marker_width(self) -> float:
        ...
    
    @start_marker_width.setter
    def start_marker_width(self, value : float):
        ...
    
    @property
    def end_marker_width(self) -> float:
        ...
    
    @end_marker_width.setter
    def end_marker_width(self, value : float):
        ...
    
    @property
    def opacity(self) -> int:
        '''Gets the opacity.'''
        ...
    
    @opacity.setter
    def opacity(self, value : int):
        '''Sets the opacity.'''
        ...
    
    @property
    def space_before(self) -> float:
        ...
    
    @space_before.setter
    def space_before(self, value : float):
        ...
    
    @property
    def padding_top(self) -> float:
        ...
    
    @padding_top.setter
    def padding_top(self, value : float):
        ...
    
    @property
    def padding_left(self) -> float:
        ...
    
    @padding_left.setter
    def padding_left(self, value : float):
        ...
    
    @property
    def padding_right(self) -> float:
        ...
    
    @padding_right.setter
    def padding_right(self, value : float):
        ...
    
    @property
    def padding_bottom(self) -> float:
        ...
    
    @padding_bottom.setter
    def padding_bottom(self, value : float):
        ...
    
    @property
    def margin_bottom(self) -> float:
        ...
    
    @margin_bottom.setter
    def margin_bottom(self, value : float):
        ...
    
    @property
    def margin_top(self) -> float:
        ...
    
    @margin_top.setter
    def margin_top(self, value : float):
        ...
    
    @property
    def start_guide(self) -> float:
        ...
    
    @start_guide.setter
    def start_guide(self, value : float):
        ...
    
    @property
    def end_guide(self) -> float:
        ...
    
    @end_guide.setter
    def end_guide(self, value : float):
        ...
    
    @property
    def measure_line_distance(self) -> float:
        ...
    
    @measure_line_distance.setter
    def measure_line_distance(self, value : float):
        ...
    
    @property
    def style_position(self) -> float:
        ...
    
    @style_position.setter
    def style_position(self, value : float):
        ...
    
    ...

class OdMetadata(aspose.imaging.fileformats.opendocument.OdObject):
    '''The Metadata of open document'''
    
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
    def generator(self) -> str:
        '''Gets the generator.'''
        ...
    
    @generator.setter
    def generator(self, value : str):
        '''Sets the generator.'''
        ...
    
    @property
    def title(self) -> str:
        '''Gets the title.'''
        ...
    
    @title.setter
    def title(self, value : str):
        '''Sets the title.'''
        ...
    
    @property
    def description(self) -> str:
        '''Gets the description.'''
        ...
    
    @description.setter
    def description(self, value : str):
        '''Sets the description.'''
        ...
    
    @property
    def subject(self) -> str:
        '''Gets the subject.'''
        ...
    
    @subject.setter
    def subject(self, value : str):
        '''Sets the subject.'''
        ...
    
    @property
    def keywords(self) -> str:
        '''Gets the keywords.'''
        ...
    
    @keywords.setter
    def keywords(self, value : str):
        '''Sets the keywords.'''
        ...
    
    @property
    def initial_creator(self) -> str:
        ...
    
    @initial_creator.setter
    def initial_creator(self, value : str):
        ...
    
    @property
    def creator(self) -> str:
        '''Gets the creator.'''
        ...
    
    @creator.setter
    def creator(self, value : str):
        '''Sets the creator.'''
        ...
    
    @property
    def printed_by(self) -> str:
        ...
    
    @printed_by.setter
    def printed_by(self, value : str):
        ...
    
    @property
    def creation_date_time(self) -> str:
        ...
    
    @creation_date_time.setter
    def creation_date_time(self, value : str):
        ...
    
    @property
    def modification_date_time(self) -> str:
        ...
    
    @modification_date_time.setter
    def modification_date_time(self, value : str):
        ...
    
    @property
    def print_date_time(self) -> str:
        ...
    
    @print_date_time.setter
    def print_date_time(self, value : str):
        ...
    
    @property
    def document_template(self) -> str:
        ...
    
    @document_template.setter
    def document_template(self, value : str):
        ...
    
    @property
    def automatic_reload(self) -> str:
        ...
    
    @automatic_reload.setter
    def automatic_reload(self, value : str):
        ...
    
    @property
    def hyperlink_behavior(self) -> str:
        ...
    
    @hyperlink_behavior.setter
    def hyperlink_behavior(self, value : str):
        ...
    
    @property
    def language(self) -> str:
        '''Gets the language.'''
        ...
    
    @language.setter
    def language(self, value : str):
        '''Sets the language.'''
        ...
    
    @property
    def editing_cycles(self) -> str:
        ...
    
    @editing_cycles.setter
    def editing_cycles(self, value : str):
        ...
    
    @property
    def editing_duration(self) -> str:
        ...
    
    @editing_duration.setter
    def editing_duration(self, value : str):
        ...
    
    @property
    def document_statistics(self) -> str:
        ...
    
    @document_statistics.setter
    def document_statistics(self, value : str):
        ...
    
    ...

class OdTransformInfo:
    '''The open document translate info'''
    
    def __init__(self):
        ...
    
    def copy(self) -> aspose.imaging.fileformats.opendocument.objects.OdTransformInfo:
        '''Copies this instance.
        
        :returns: Get the instance of OdTransformInfo'''
        ...
    
    @property
    def rotate_angle(self) -> float:
        ...
    
    @rotate_angle.setter
    def rotate_angle(self, value : float):
        ...
    
    @property
    def translate_x(self) -> float:
        ...
    
    @translate_x.setter
    def translate_x(self, value : float):
        ...
    
    @property
    def translate_y(self) -> float:
        ...
    
    @translate_y.setter
    def translate_y(self, value : float):
        ...
    
    @property
    def skew_x(self) -> float:
        ...
    
    @skew_x.setter
    def skew_x(self, value : float):
        ...
    
    @property
    def skew_y(self) -> float:
        ...
    
    @skew_y.setter
    def skew_y(self, value : float):
        ...
    
    ...

