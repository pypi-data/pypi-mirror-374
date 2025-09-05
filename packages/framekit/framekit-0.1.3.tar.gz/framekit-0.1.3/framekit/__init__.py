# PyOpenGL workaround for import issues
import os
os.environ.setdefault('PYOPENGL_PLATFORM', 'osmesa')

try:
    import OpenGL
    # Force proper OpenGL arrays import
    from OpenGL import arrays
    if not hasattr(arrays, 'lists'):
        # Fallback import
        import OpenGL.arrays.vbo
except ImportError as e:
    print(f"Warning: PyOpenGL import issue: {e}")

from .master_scene_element import *
from .scene_element import *
from .text_element import *
from .image_element import *
from .video_element import *
from .audio_element import *
from .animation import *
from .video_base import *