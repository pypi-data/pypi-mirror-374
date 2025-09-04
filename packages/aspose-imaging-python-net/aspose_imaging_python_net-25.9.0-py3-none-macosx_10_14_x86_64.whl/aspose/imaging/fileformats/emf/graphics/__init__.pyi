"""The namespace contains Emf/Emf+ graphics."""
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

class EmfRecorderGraphics2D(MetafileRecorderGraphics2D):
    '''The Emf recorder graphics'''
    
    def __init__(self, frame: aspose.imaging.Rectangle, device_size: aspose.imaging.Size, device_size_mm: aspose.imaging.Size):
        '''Initializes a new instance of the  class.
        
        :param frame: The frame.
        :param device_size: Size of the device.
        :param device_size_mm: The device size mm.'''
        ...
    
    @overload
    def draw_image(self, image: aspose.imaging.RasterImage, location: aspose.imaging.Point):
        '''Draws the specified Image, using its original physical size, at the specified location.
        
        :param image: The image to draw.
        :param location: The location of the upper-left corner of the drawn image.'''
        ...
    
    @overload
    def draw_image(self, image: aspose.imaging.RasterImage, dest_rect: aspose.imaging.Rectangle, src_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the specified portion of the specified Image at the specified location and with the specified size.
        
        :param image: The image to draw.
        :param dest_rect: Rectangle structure that specifies the location and size of the drawn image. The image is scaled to fit the rectangle.
        :param src_rect: Rectangle structure that specifies the portion of the image object to draw.
        :param src_unit: The units of measure used by the srcRect parameter.'''
        ...
    
    @overload
    def draw_image(self, image_bytes: bytes, dest_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the image.
        
        :param image_bytes: The image bytes.
        :param dest_rect: The dest rect.
        :param src_unit: The source unit.'''
        ...
    
    @overload
    def draw_image(self, stream: io.RawIOBase, dest_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the image.
        
        :param stream: The stream.
        :param dest_rect: The dest rect.
        :param src_unit: The source unit.'''
        ...
    
    @overload
    def draw_line(self, pen: aspose.imaging.Pen, x1: int, y1: int, x2: int, y2: int):
        '''Draws the line.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param x1: The x-coordinate of the first point.
        :param y1: The y-coordinate of the first point.
        :param x2: The x-coordinate of the second point.
        :param y2: The y-coordinate of the second point.'''
        ...
    
    @overload
    def draw_line(self, pen: aspose.imaging.Pen, pt1: aspose.imaging.Point, pt2: aspose.imaging.Point):
        '''Draws the line.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param pt1: The first point.
        :param pt2: The second point.'''
        ...
    
    @overload
    def fill_polygon(self, brush: aspose.imaging.Brush, points: List[aspose.imaging.Point]):
        '''Fills the polygon.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param points: The points.'''
        ...
    
    @overload
    def fill_polygon(self, brush: aspose.imaging.Brush, points: List[aspose.imaging.Point], fill_mode: aspose.imaging.FillMode):
        '''Fills the polygon.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param points: The points.
        :param fill_mode: The fill mode.'''
        ...
    
    @overload
    def draw_rectangle(self, pen: aspose.imaging.Pen, x: int, y: int, width: int, height: int):
        '''Draws the rectangle.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param x: The x-coordinate of the upper-left corner of the rectangle to draw.
        :param y: The y-coordinate of the upper-left corner of the rectangle to draw.
        :param width: The width of the rectangle to draw.
        :param height: The height of the rectangle to draw.'''
        ...
    
    @overload
    def draw_rectangle(self, pen: aspose.imaging.Pen, rectangle: aspose.imaging.Rectangle):
        '''Draws the rectangle.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param rectangle: The rectangle to draw.'''
        ...
    
    @overload
    def draw_string(self, string: str, font: aspose.imaging.Font, color: aspose.imaging.Color, x: int, y: int):
        '''Draws the string.
        
        :param string: The string.
        :param font: Font that defines the text format of the string.
        :param color: The text color.
        :param x: The x-coordinate of the upper-left corner of the drawn text.
        :param y: The y-coordinate of the upper-left corner of the drawn text.'''
        ...
    
    @overload
    def draw_string(self, string: str, font: aspose.imaging.Font, color: aspose.imaging.Color, x: int, y: int, angle: float):
        '''Draws the string.
        
        :param string: The string.
        :param font: Font that defines the text format of the string.
        :param color: The text color.
        :param x: The x-coordinate of the upper-left corner of the drawn text.
        :param y: The y-coordinate of the upper-left corner of the drawn text.
        :param angle: The angle in degrees, between the escapement vector and the x-axis of the device.
        The escapement vector is parallel to the base line of a row of text.'''
        ...
    
    @overload
    def exclude_clip(self, rect: aspose.imaging.Rectangle):
        '''Updates the clip region of this Graphics to exclude the area specified by a Rectangle structure.
        
        :param rect: Rectangle structure that specifies the rectangle to exclude from the clip region.'''
        ...
    
    @overload
    def exclude_clip(self, region: aspose.imaging.Region):
        '''Updates the clip region of this Graphics to exclude the area specified by a Region.
        
        :param region: Region that specifies the region to exclude from the clip region.'''
        ...
    
    @overload
    def intersect_clip(self, rect: aspose.imaging.RectangleF):
        '''Updates the clip region of this Graphics to the intersection of the current clip region and the specified Rectangle structure.
        
        :param rect: Rectangle structure to intersect with the current clip region.'''
        ...
    
    @overload
    def intersect_clip(self, region: aspose.imaging.Region):
        '''Updates the clip region of this Graphics to the intersection of the current clip region and the specified Region.
        
        :param region: Region to intersect with the current region.'''
        ...
    
    @overload
    def multiply_transform(self, matrix: aspose.imaging.Matrix):
        '''Multiplies the world transformation of this Graphics and specified the Matrix.
        
        :param matrix: The matrix that multiplies the world transformation.'''
        ...
    
    @overload
    def multiply_transform(self, matrix: aspose.imaging.Matrix, order: aspose.imaging.MatrixOrder):
        '''Multiplies the world transformation of this Graphics and specified the Matrix in the specified order.
        
        :param matrix: The matrix that multiplies the world transformation.
        :param order: The order of the multiplication.'''
        ...
    
    @overload
    def translate_transform(self, x: float, y: float):
        '''Changes the origin of the coordinate system by prepending the specified translation to the transformation matrix of this Graphics.
        
        :param x: The x-coordinate of the translation.
        :param y: The y-coordinate of the translation.'''
        ...
    
    @overload
    def translate_transform(self, x: float, y: float, order: aspose.imaging.MatrixOrder):
        '''Changes the origin of the coordinate system by applying the specified translation to the transformation matrix of this Graphics in the specified order.
        
        :param x: The x-coordinate of the translation.
        :param y: The y-coordinate of the translation.
        :param order: Specifies whether the translation is prepended or appended to the transformation matrix.'''
        ...
    
    @overload
    def rotate_transform(self, angle: float):
        '''Applies the specified rotation to the transformation matrix of this Graphics.
        
        :param angle: Angle of rotation in degrees.'''
        ...
    
    @overload
    def rotate_transform(self, angle: float, center: aspose.imaging.PointF, order: aspose.imaging.MatrixOrder):
        '''Applies the specified rotation to the transformation matrix of this Graphics in the specified order.
        
        :param angle: Angle of rotation in degrees.
        :param center: The rotating center.
        :param order: Specifies whether the rotation is appended or prepended to the matrix transformation..'''
        ...
    
    @overload
    def scale_transform(self, sx: float, sy: float):
        '''Applies the specified scaling operation to the transformation matrix of this Graphics by prepending it to the object's transformation matrix.
        
        :param sx: Scale factor in the x direction.
        :param sy: Scale factor in the y direction.'''
        ...
    
    @overload
    def scale_transform(self, sx: float, sy: float, order: aspose.imaging.MatrixOrder):
        '''Applies the specified scaling operation to the transformation matrix of this Graphics in the specified order.
        
        :param sx: Scale factor in the x direction.
        :param sy: Scale factor in the y direction.
        :param order: Specifies whether the scaling operation is prepended or appended to the transformation matrix.'''
        ...
    
    def clear(self):
        '''Clears the state of the graphics object'''
        ...
    
    def draw_arc(self, pen: aspose.imaging.Pen, rect: aspose.imaging.Rectangle, start_angle: float, arc_angle: float):
        '''Draws an arc representing a portion of an ellipse specified by a Rectangle structure.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param rect: The boundaries of the ellipse.
        :param start_angle: Angle in degrees measured clockwise from the x-axis to the starting point of the arc.
        :param arc_angle: Angle in degrees measured clockwise from the startAngle parameter to ending point of the arc.'''
        ...
    
    def draw_cubic_bezier(self, pen: aspose.imaging.Pen, pt1: aspose.imaging.Point, pt2: aspose.imaging.Point, pt3: aspose.imaging.Point, pt4: aspose.imaging.Point):
        '''Draws the cubic bezier.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param pt1: The starting point of the curve.
        :param pt2: The first control point for the curve.
        :param pt3: The second control point for the curve.
        :param pt4: The ending point of the curve.'''
        ...
    
    def draw_poly_cubic_bezier(self, pen: aspose.imaging.Pen, points: List[aspose.imaging.Point]):
        '''Draws the poly cubic bezier.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param points: The points.'''
        ...
    
    def draw_ellipse(self, pen: aspose.imaging.Pen, rect: aspose.imaging.Rectangle):
        '''Draws the ellipse.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param rect: The boundaries of the ellipse.'''
        ...
    
    def fill_ellipse(self, brush: aspose.imaging.Brush, rect: aspose.imaging.Rectangle):
        '''Fills the ellipse.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param rect: The boundaries of the ellipse.'''
        ...
    
    def draw_image_from_bytes(self, image_bytes: bytes, dest_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the image.
        
        :param image_bytes: The image bytes.
        :param dest_rect: The dest rect.
        :param src_unit: The source unit.'''
        ...
    
    def draw_image_from_stream(self, stream: io.RawIOBase, dest_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the image.
        
        :param stream: The stream.
        :param dest_rect: The dest rect.
        :param src_unit: The source unit.'''
        ...
    
    def draw_polyline(self, pen: aspose.imaging.Pen, points: List[aspose.imaging.Point]):
        '''Draws the polyline.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param points: The points.'''
        ...
    
    def draw_path(self, pen: aspose.imaging.Pen, path: aspose.imaging.GraphicsPath):
        '''Draws the path.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param path: The path to draw.'''
        ...
    
    def fill_path(self, pen: aspose.imaging.Pen, brush: aspose.imaging.Brush, path: aspose.imaging.GraphicsPath):
        '''Fills the path.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param brush: Brush that determines the characteristics of the fill.
        :param path: The path to fill.'''
        ...
    
    def draw_pie(self, pen: aspose.imaging.Pen, rect: aspose.imaging.Rectangle, start_angle: float, sweep_angle: float):
        '''Draws the pie.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param rect: The boundaries of the ellipse.
        :param start_angle: Angle in degrees measured clockwise from the x-axis to the starting point of the arc.
        :param sweep_angle: Angle in degrees measured clockwise from the startAngle parameter to ending point of the arc.'''
        ...
    
    def fill_pie(self, brush: aspose.imaging.Brush, rect: aspose.imaging.Rectangle, start_angle: float, sweep_angle: float):
        '''Fills the pie.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param rect: The boundaries of the ellipse.
        :param start_angle: Angle in degrees measured clockwise from the x-axis to the starting point of the arc.
        :param sweep_angle: Angle in degrees measured clockwise from the startAngle parameter to ending point of the arc.'''
        ...
    
    def draw_polygon(self, pen: aspose.imaging.Pen, points: List[aspose.imaging.Point]):
        '''Draws the polygon.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param points: The points.'''
        ...
    
    def fill_rectangle(self, brush: aspose.imaging.Brush, rectangle: aspose.imaging.Rectangle):
        '''Fills the rectangle.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param rectangle: The rectangle to fill.'''
        ...
    
    def exclude_clip_rect(self, rect: aspose.imaging.Rectangle):
        '''Updates the clip region of this Graphics to exclude the area specified by a Rectangle structure.
        
        :param rect: Rectangle structure that specifies the rectangle to exclude from the clip region.'''
        ...
    
    def exclude_clip_rgn(self, region: aspose.imaging.Region):
        '''Updates the clip region of this Graphics to exclude the area specified by a Region.
        
        :param region: Region that specifies the region to exclude from the clip region.'''
        ...
    
    def intersect_clip_rect_f(self, rect: aspose.imaging.RectangleF):
        '''Updates the clip region of this Graphics to the intersection of the current clip region and the specified Rectangle structure.
        
        :param rect: Rectangle structure to intersect with the current clip region.'''
        ...
    
    def intersect_clip_rgn(self, region: aspose.imaging.Region):
        '''Updates the clip region of this Graphics to the intersection of the current clip region and the specified Region.
        
        :param region: Region to intersect with the current region.'''
        ...
    
    def reset_clip(self):
        '''Resets the clip.'''
        ...
    
    def get_transform(self) -> aspose.imaging.Matrix:
        '''Gets the world transform.
        
        :returns: The transform matrix.'''
        ...
    
    def set_transform(self, transform: aspose.imaging.Matrix):
        '''Sets the transform.
        
        :param transform: The new transform matrix.'''
        ...
    
    def end_recording(self) -> aspose.imaging.fileformats.emf.EmfImage:
        '''Ends the recording.
        
        :returns: The result image.'''
        ...
    
    @staticmethod
    def from_emf_image(emf_image: aspose.imaging.fileformats.emf.EmfImage) -> aspose.imaging.fileformats.emf.graphics.EmfRecorderGraphics2D:
        '''Gets an instance of the  containing all records from the Emf image.
        
        :param emf_image: The Emf image to read records from.
        :returns: An instance of the'''
        ...
    
    @property
    def clip(self) -> aspose.imaging.Region:
        '''Gets a Region that limits the drawing region of this Graphics'''
        ...
    
    @clip.setter
    def clip(self, value : aspose.imaging.Region):
        '''Sets a Region that limits the drawing region of this Graphics'''
        ...
    
    @property
    def clip_bounds(self) -> aspose.imaging.RectangleF:
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    @property
    def background_mode(self) -> aspose.imaging.fileformats.emf.emf.consts.EmfBackgroundMode:
        ...
    
    @background_mode.setter
    def background_mode(self, value : aspose.imaging.fileformats.emf.emf.consts.EmfBackgroundMode):
        ...
    
    ...

class MetafileRecorderGraphics2D:
    '''The metafiles recorder graphics'''
    
    @overload
    def draw_image(self, image: aspose.imaging.RasterImage, location: aspose.imaging.Point):
        '''Draws the specified Image, using its original physical size, at the specified location.
        
        :param image: The image to draw.
        :param location: The location of the upper-left corner of the drawn image.'''
        ...
    
    @overload
    def draw_image(self, image: aspose.imaging.RasterImage, dest_rect: aspose.imaging.Rectangle, src_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the specified portion of the specified Image at the specified location and with the specified size.
        
        :param image: The image to draw.
        :param dest_rect: Rectangle structure that specifies the location and size of the drawn image. The image is scaled to fit the rectangle.
        :param src_rect: Rectangle structure that specifies the portion of the image object to draw.
        :param src_unit: The units of measure used by the srcRect parameter.'''
        ...
    
    @overload
    def draw_image(self, image_bytes: bytes, dest_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the image.
        
        :param image_bytes: The image bytes.
        :param dest_rect: The dest rect.
        :param src_unit: The source unit.'''
        ...
    
    @overload
    def draw_image(self, stream: io.RawIOBase, dest_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the image.
        
        :param stream: The stream.
        :param dest_rect: The dest rect.
        :param src_unit: The source unit.'''
        ...
    
    @overload
    def draw_line(self, pen: aspose.imaging.Pen, x1: int, y1: int, x2: int, y2: int):
        '''Draws the line.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param x1: The x-coordinate of the first point.
        :param y1: The y-coordinate of the first point.
        :param x2: The x-coordinate of the second point.
        :param y2: The y-coordinate of the second point.'''
        ...
    
    @overload
    def draw_line(self, pen: aspose.imaging.Pen, pt1: aspose.imaging.Point, pt2: aspose.imaging.Point):
        '''Draws the line.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param pt1: The first point.
        :param pt2: The second point.'''
        ...
    
    @overload
    def fill_polygon(self, brush: aspose.imaging.Brush, points: List[aspose.imaging.Point]):
        '''Fills the polygon.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param points: The points.'''
        ...
    
    @overload
    def fill_polygon(self, brush: aspose.imaging.Brush, points: List[aspose.imaging.Point], fill_mode: aspose.imaging.FillMode):
        '''Fills the polygon.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param points: The points.
        :param fill_mode: The fill mode.'''
        ...
    
    @overload
    def draw_rectangle(self, pen: aspose.imaging.Pen, x: int, y: int, width: int, height: int):
        '''Draws the rectangle.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param x: The x-coordinate of the upper-left corner of the rectangle to draw.
        :param y: The y-coordinate of the upper-left corner of the rectangle to draw.
        :param width: The width of the rectangle to draw.
        :param height: The height of the rectangle to draw.'''
        ...
    
    @overload
    def draw_rectangle(self, pen: aspose.imaging.Pen, rectangle: aspose.imaging.Rectangle):
        '''Draws the rectangle.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param rectangle: The rectangle to draw.'''
        ...
    
    @overload
    def draw_string(self, string: str, font: aspose.imaging.Font, color: aspose.imaging.Color, x: int, y: int):
        '''Draws the string.
        
        :param string: The string.
        :param font: Font that defines the text format of the string.
        :param color: The text color.
        :param x: The x-coordinate of the upper-left corner of the drawn text.
        :param y: The y-coordinate of the upper-left corner of the drawn text.'''
        ...
    
    @overload
    def draw_string(self, string: str, font: aspose.imaging.Font, color: aspose.imaging.Color, x: int, y: int, angle: float):
        '''Draws the string.
        
        :param string: The string.
        :param font: Font that defines the text format of the string.
        :param color: The text color.
        :param x: The x-coordinate of the upper-left corner of the drawn text.
        :param y: The y-coordinate of the upper-left corner of the drawn text.
        :param angle: The angle in degrees, between the escapement vector and the x-axis of the device.
        The escapement vector is parallel to the base line of a row of text.'''
        ...
    
    @overload
    def exclude_clip(self, rect: aspose.imaging.Rectangle):
        '''Updates the clip region of this Graphics to exclude the area specified by a Rectangle structure.
        
        :param rect: Rectangle structure that specifies the rectangle to exclude from the clip region.'''
        ...
    
    @overload
    def exclude_clip(self, region: aspose.imaging.Region):
        '''Updates the clip region of this Graphics to exclude the area specified by a Region.
        
        :param region: Region that specifies the region to exclude from the clip region.'''
        ...
    
    @overload
    def intersect_clip(self, rect: aspose.imaging.RectangleF):
        '''Updates the clip region of this Graphics to the intersection of the current clip region and the specified Rectangle structure.
        
        :param rect: Rectangle structure to intersect with the current clip region.'''
        ...
    
    @overload
    def intersect_clip(self, region: aspose.imaging.Region):
        '''Updates the clip region of this Graphics to the intersection of the current clip region and the specified Region.
        
        :param region: Region to intersect with the current region.'''
        ...
    
    @overload
    def multiply_transform(self, matrix: aspose.imaging.Matrix):
        '''Multiplies the world transformation of this Graphics and specified the Matrix.
        
        :param matrix: The matrix that multiplies the world transformation.'''
        ...
    
    @overload
    def multiply_transform(self, matrix: aspose.imaging.Matrix, order: aspose.imaging.MatrixOrder):
        '''Multiplies the world transformation of this Graphics and specified the Matrix in the specified order.
        
        :param matrix: The matrix that multiplies the world transformation.
        :param order: The order of the multiplication.'''
        ...
    
    @overload
    def translate_transform(self, x: float, y: float):
        '''Changes the origin of the coordinate system by prepending the specified translation to the transformation matrix of this Graphics.
        
        :param x: The x-coordinate of the translation.
        :param y: The y-coordinate of the translation.'''
        ...
    
    @overload
    def translate_transform(self, x: float, y: float, order: aspose.imaging.MatrixOrder):
        '''Changes the origin of the coordinate system by applying the specified translation to the transformation matrix of this Graphics in the specified order.
        
        :param x: The x-coordinate of the translation.
        :param y: The y-coordinate of the translation.
        :param order: Specifies whether the translation is prepended or appended to the transformation matrix.'''
        ...
    
    @overload
    def rotate_transform(self, angle: float):
        '''Applies the specified rotation to the transformation matrix of this Graphics.
        
        :param angle: Angle of rotation in degrees.'''
        ...
    
    @overload
    def rotate_transform(self, angle: float, center: aspose.imaging.PointF, order: aspose.imaging.MatrixOrder):
        '''Applies the specified rotation to the transformation matrix of this Graphics in the specified order.
        
        :param angle: Angle of rotation in degrees.
        :param center: The rotating center.
        :param order: Specifies whether the rotation is appended or prepended to the matrix transformation..'''
        ...
    
    @overload
    def scale_transform(self, sx: float, sy: float):
        '''Applies the specified scaling operation to the transformation matrix of this Graphics by prepending it to the object's transformation matrix.
        
        :param sx: Scale factor in the x direction.
        :param sy: Scale factor in the y direction.'''
        ...
    
    @overload
    def scale_transform(self, sx: float, sy: float, order: aspose.imaging.MatrixOrder):
        '''Applies the specified scaling operation to the transformation matrix of this Graphics in the specified order.
        
        :param sx: Scale factor in the x direction.
        :param sy: Scale factor in the y direction.
        :param order: Specifies whether the scaling operation is prepended or appended to the transformation matrix.'''
        ...
    
    def clear(self):
        '''Clears the state of the graphics object'''
        ...
    
    def draw_arc(self, pen: aspose.imaging.Pen, rect: aspose.imaging.Rectangle, start_angle: float, arc_angle: float):
        '''Draws an arc representing a portion of an ellipse specified by a Rectangle structure.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param rect: The boundaries of the ellipse.
        :param start_angle: Angle in degrees measured clockwise from the x-axis to the starting point of the arc.
        :param arc_angle: Angle in degrees measured clockwise from the startAngle parameter to ending point of the arc.'''
        ...
    
    def draw_cubic_bezier(self, pen: aspose.imaging.Pen, pt1: aspose.imaging.Point, pt2: aspose.imaging.Point, pt3: aspose.imaging.Point, pt4: aspose.imaging.Point):
        '''Draws the cubic bezier.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param pt1: The starting point of the curve.
        :param pt2: The first control point for the curve.
        :param pt3: The second control point for the curve.
        :param pt4: The ending point of the curve.'''
        ...
    
    def draw_poly_cubic_bezier(self, pen: aspose.imaging.Pen, points: List[aspose.imaging.Point]):
        '''Draws the poly cubic bezier.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param points: The points.'''
        ...
    
    def draw_ellipse(self, pen: aspose.imaging.Pen, rect: aspose.imaging.Rectangle):
        '''Draws the ellipse.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param rect: The boundaries of the ellipse.'''
        ...
    
    def fill_ellipse(self, brush: aspose.imaging.Brush, rect: aspose.imaging.Rectangle):
        '''Fills the ellipse.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param rect: The boundaries of the ellipse.'''
        ...
    
    def draw_image_from_bytes(self, image_bytes: bytes, dest_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the image.
        
        :param image_bytes: The image bytes.
        :param dest_rect: The dest rect.
        :param src_unit: The source unit.'''
        ...
    
    def draw_image_from_stream(self, stream: io.RawIOBase, dest_rect: aspose.imaging.Rectangle, src_unit: aspose.imaging.GraphicsUnit):
        '''Draws the image.
        
        :param stream: The stream.
        :param dest_rect: The dest rect.
        :param src_unit: The source unit.'''
        ...
    
    def draw_polyline(self, pen: aspose.imaging.Pen, points: List[aspose.imaging.Point]):
        '''Draws the polyline.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param points: The points.'''
        ...
    
    def draw_path(self, pen: aspose.imaging.Pen, path: aspose.imaging.GraphicsPath):
        '''Draws the path.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param path: The path to draw.'''
        ...
    
    def fill_path(self, pen: aspose.imaging.Pen, brush: aspose.imaging.Brush, path: aspose.imaging.GraphicsPath):
        '''Fills the path.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param brush: Brush that determines the characteristics of the fill.
        :param path: The path to fill.'''
        ...
    
    def draw_pie(self, pen: aspose.imaging.Pen, rect: aspose.imaging.Rectangle, start_angle: float, sweep_angle: float):
        '''Draws the pie.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param rect: The boundaries of the ellipse.
        :param start_angle: Angle in degrees measured clockwise from the x-axis to the starting point of the arc.
        :param sweep_angle: Angle in degrees measured clockwise from the startAngle parameter to ending point of the arc.'''
        ...
    
    def fill_pie(self, brush: aspose.imaging.Brush, rect: aspose.imaging.Rectangle, start_angle: float, sweep_angle: float):
        '''Fills the pie.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param rect: The boundaries of the ellipse.
        :param start_angle: Angle in degrees measured clockwise from the x-axis to the starting point of the arc.
        :param sweep_angle: Angle in degrees measured clockwise from the startAngle parameter to ending point of the arc.'''
        ...
    
    def draw_polygon(self, pen: aspose.imaging.Pen, points: List[aspose.imaging.Point]):
        '''Draws the polygon.
        
        :param pen: Pen that determines the color, width, and style of the figure.
        :param points: The points.'''
        ...
    
    def fill_rectangle(self, brush: aspose.imaging.Brush, rectangle: aspose.imaging.Rectangle):
        '''Fills the rectangle.
        
        :param brush: Brush that determines the characteristics of the fill.
        :param rectangle: The rectangle to fill.'''
        ...
    
    def exclude_clip_rect(self, rect: aspose.imaging.Rectangle):
        '''Updates the clip region of this Graphics to exclude the area specified by a Rectangle structure.
        
        :param rect: Rectangle structure that specifies the rectangle to exclude from the clip region.'''
        ...
    
    def exclude_clip_rgn(self, region: aspose.imaging.Region):
        '''Updates the clip region of this Graphics to exclude the area specified by a Region.
        
        :param region: Region that specifies the region to exclude from the clip region.'''
        ...
    
    def intersect_clip_rect_f(self, rect: aspose.imaging.RectangleF):
        '''Updates the clip region of this Graphics to the intersection of the current clip region and the specified Rectangle structure.
        
        :param rect: Rectangle structure to intersect with the current clip region.'''
        ...
    
    def intersect_clip_rgn(self, region: aspose.imaging.Region):
        '''Updates the clip region of this Graphics to the intersection of the current clip region and the specified Region.
        
        :param region: Region to intersect with the current region.'''
        ...
    
    def reset_clip(self):
        '''Resets the clip.'''
        ...
    
    def get_transform(self) -> aspose.imaging.Matrix:
        '''Gets the world transform.
        
        :returns: The transform matrix.'''
        ...
    
    def set_transform(self, transform: aspose.imaging.Matrix):
        '''Sets the transform.
        
        :param transform: The new transform matrix.'''
        ...
    
    @property
    def clip(self) -> aspose.imaging.Region:
        '''Gets a Region that limits the drawing region of this Graphics'''
        ...
    
    @clip.setter
    def clip(self, value : aspose.imaging.Region):
        '''Sets a Region that limits the drawing region of this Graphics'''
        ...
    
    @property
    def clip_bounds(self) -> aspose.imaging.RectangleF:
        ...
    
    @property
    def background_color(self) -> aspose.imaging.Color:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.imaging.Color):
        ...
    
    ...

