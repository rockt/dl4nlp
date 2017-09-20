import os
import struct
from binascii import b2a_base64

from IPython.display import *


def _safe_exists(path):
    """Check path, but don't let exceptions raise"""
    try:
        return os.path.exists(path)
    except Exception:
        return False


# constants for identifying png/jpeg data
_PNG = b'\x89PNG\r\n\x1a\n'
_JPEG = b'\xff\xd8'


def _pngxy(data):
    """read the (width, height) from a PNG header"""
    ihdr = data.index(b'IHDR')
    # next 8 bytes are width/height
    return struct.unpack('>ii', data[ihdr + 4:ihdr + 12])


def _jpegxy(data):
    """read the (width, height) from a JPEG header"""
    # adapted from http://www.64lines.com/jpeg-width-height

    idx = 4
    while True:
        block_size = struct.unpack('>H', data[idx:idx + 2])[0]
        idx = idx + block_size
        if data[idx:idx + 2] == b'\xFF\xC0':
            # found Start of Frame
            iSOF = idx
            break
        else:
            # read another block
            idx += 2

    h, w = struct.unpack('>HH', data[iSOF + 5:iSOF + 9])
    return w, h


def _gifxy(data):
    """read the (width, height) from a GIF header"""
    return struct.unpack('<HH', data[6:10])


class Image(DisplayObject):
    _read_flags = 'rb'
    _FMT_JPEG = u'jpeg'
    _FMT_PNG = u'png'
    _FMT_GIF = u'gif'
    _ACCEPTABLE_EMBEDDINGS = [_FMT_JPEG, _FMT_PNG, _FMT_GIF]
    _MIMETYPES = {
        _FMT_PNG: 'image/png',
        _FMT_JPEG: 'image/jpeg',
        _FMT_GIF: 'image/gif',
    }

    def __init__(self, data=None, url=None, filename=None, format=None,
                 embed=None, width=None, height=None, retina=False,
                 unconfined=False, metadata=None):
        """Create a PNG/JPEG/GIF image object given raw data.

        When this object is returned by an input cell or passed to the
        display function, it will result in the image being displayed
        in the frontend.

        Parameters
        ----------
        data : unicode, str or bytes
            The raw image data or a URL or filename to load the data from.
            This always results in embedded image data.
        url : unicode
            A URL to download the data from. If you specify `url=`,
            the image data will not be embedded unless you also specify `embed=True`.
        filename : unicode
            Path to a local file to load the data from.
            Images from a file are always embedded.
        format : unicode
            The format of the image data (png/jpeg/jpg/gif). If a filename or URL is given
            for format will be inferred from the filename extension.
        embed : bool
            Should the image data be embedded using a data URI (True) or be
            loaded using an <img> tag. Set this to True if you want the image
            to be viewable later with no internet connection in the notebook.

            Default is `True`, unless the keyword argument `url` is set, then
            default value is `False`.

            Note that QtConsole is not able to display images if `embed` is set to `False`
        width : int
            Width in pixels to which to constrain the image in html
        height : int
            Height in pixels to which to constrain the image in html
        retina : bool
            Automatically set the width and height to half of the measured
            width and height.
            This only works for embedded images because it reads the width/height
            from image data.
            For non-embedded images, you can just set the desired display width
            and height directly.
        unconfined: bool
            Set unconfined=True to disable max-width confinement of the image.
        metadata: dict
            Specify extra metadata to attach to the image.

        Examples
        --------
        # embedded image data, works in qtconsole and notebook
        # when passed positionally, the first arg can be any of raw image data,
        # a URL, or a filename from which to load image data.
        # The result is always embedding image data for inline images.
        Image('http://www.google.fr/images/srpr/logo3w.png')
        Image('/path/to/image.jpg')
        Image(b'RAW_PNG_DATA...')

        # Specifying Image(url=...) does not embed the image data,
        # it only generates `<img>` tag with a link to the source.
        # This will not work in the qtconsole or offline.
        Image(url='http://www.google.fr/images/srpr/logo3w.png')

        """
        if filename is not None:
            ext = self._find_ext(filename)
        elif url is not None:
            ext = self._find_ext(url)
        elif data is None:
            raise ValueError("No image data found. Expecting filename, url, or data.")
        elif isinstance(data, str) and (
                    data.startswith('http') or _safe_exists(data)
        ):
            ext = self._find_ext(data)
        else:
            ext = None

        if format is None:
            if ext is not None:
                if ext == u'jpg' or ext == u'jpeg':
                    format = self._FMT_JPEG
                if ext == u'png':
                    format = self._FMT_PNG
                if ext == u'gif':
                    format = self._FMT_GIF
                else:
                    format = ext.lower()
            elif isinstance(data, bytes):
                # infer image type from image data header,
                # only if format has not been specified.
                if data[:2] == _JPEG:
                    format = self._FMT_JPEG

        # failed to detect format, default png
        if format is None:
            format = self._FMT_PNG

        if format.lower() == 'jpg':
            # jpg->jpeg
            format = self._FMT_JPEG

        self.format = format.lower()
        self.embed = embed if embed is not None else (url is None)

        if self.embed and self.format not in self._ACCEPTABLE_EMBEDDINGS:
            raise ValueError("Cannot embed the '%s' image format" % (self.format))
        if self.embed:
            self._mimetype = self._MIMETYPES.get(self.format)

        self.width = width
        self.height = height
        self.retina = retina
        self.unconfined = unconfined
        super(Image, self).__init__(data=data, url=url, filename=filename,
                                    metadata=metadata)

        if self.width is None and self.metadata.get('width', {}):
            self.width = metadata['width']

        if self.height is None and self.metadata.get('height', {}):
            self.height = metadata['height']

        if retina:
            self._retina_shape()

    def _retina_shape(self):
        """load pixel-doubled width and height from image data"""
        if not self.embed:
            return
        if self.format == self._FMT_PNG:
            w, h = _pngxy(self.data)
        elif self.format == self._FMT_JPEG:
            w, h = _jpegxy(self.data)
        elif self.format == self._FMT_GIF:
            w, h = _gifxy(self.data)
        else:
            # retina only supports png
            return
        self.width = w // 2
        self.height = h // 2

    def reload(self):
        """Reload the raw data from file or URL."""
        if self.embed:
            super(Image, self).reload()
            if self.retina:
                self._retina_shape()

    def _repr_html_(self):
        if not self.embed:
            width = height = klass = ''
            if self.width:
                width = ' width="%d"' % self.width if isinstance(self.width, int) else ' width="%s"' % self.width
            if self.height:
                height = ' height="%d"' % self.height if isinstance(self.height, int) else ' height="%s"' % self.height
            if self.unconfined:
                klass = ' class="unconfined"'
            return u'<img src="{url}"{width}{height}{klass}/>'.format(
                url=self.url,
                width=width,
                height=height,
                klass=klass,
            )

    def _repr_mimebundle_(self, include=None, exclude=None):
        """Return the image as a mimebundle

        Any new mimetype support should be implemented here.
        """
        if self.embed:
            mimetype = self._mimetype
            data, metadata = self._data_and_metadata(always_both=True)
            if metadata:
                metadata = {mimetype: metadata}
            return {mimetype: data}, metadata
        else:
            return {'text/html': self._repr_html_()}

    def _data_and_metadata(self, always_both=False):
        """shortcut for returning metadata with shape information, if defined"""
        b64_data = b2a_base64(self.data).decode('ascii')
        md = {}
        if self.metadata:
            md.update(self.metadata)
        if self.width:
            md['width'] = self.width
        if self.height:
            md['height'] = self.height
        if self.unconfined:
            md['unconfined'] = self.unconfined
        if md or always_both:
            return b64_data, md
        else:
            return b64_data

    def _repr_png_(self):
        if self.embed and self.format == self._FMT_PNG:
            return self._data_and_metadata()

    def _repr_jpeg_(self):
        if self.embed and self.format == self._FMT_JPEG:
            return self._data_and_metadata()

    def _find_ext(self, s):
        return s.split('.')[-1].lower()
