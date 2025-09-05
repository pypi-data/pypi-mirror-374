from typing import List
from .video_base import VideoBase


class Scene:
    """Scene class for managing multiple video elements as a group.
    
    A Scene groups multiple VideoBase elements (text, images, videos, audio) and manages
    their collective timing. Scenes can be positioned at specific times in the timeline
    and automatically handle BGM duration adjustments.
    
    Attributes:
        elements: List of VideoBase elements in this scene
        start_time: Start time of the scene in seconds
        duration: Total duration of the scene in seconds
    """
    
    def __init__(self) -> None:
        """Initialize a new Scene with no elements."""
        self.elements: List[VideoBase] = []
        self.start_time: float = 0.0
        self.duration: float = 0.0
    
    def add(self, element: VideoBase) -> 'Scene':
        """Add an element to this scene.
        
        Args:
            element: VideoBase element to add (text, image, video, or audio)
            
        Returns:
            Self for method chaining
        """
        from .audio_element import AudioElement
        from .video_element import VideoElement
        from .image_element import ImageElement
        
        self.elements.append(element)
        
        # BGMモードでないオーディオ要素とループモードでないビデオ/画像要素と他の要素のみがシーン時間に影響
        is_bgm_audio = isinstance(element, AudioElement) and getattr(element, 'loop_until_scene_end', False)
        is_loop_video = isinstance(element, VideoElement) and (getattr(element, 'loop_until_scene_end', False) or getattr(element, '_wants_scene_duration', False))
        is_loop_image = isinstance(element, ImageElement) and (getattr(element, 'loop_until_scene_end', False) or getattr(element, '_wants_scene_duration', False))
        
        if not (is_bgm_audio or is_loop_video or is_loop_image):
            element_end_time = element.start_time + element.duration
            self.duration = max(self.duration, element_end_time)
        
        # BGMモードのオーディオ要素とループモードのビデオ/画像要素の持続時間を更新（シーン時間決定後）
        self._update_loop_element_durations()
        return self
    
    def _update_loop_element_durations(self) -> None:
        """Update loop element durations to match scene length.
        
        This method finds all audio, video, and image elements with loop_until_scene_end=True
        and updates their duration to match the scene's total duration.
        """
        from .audio_element import AudioElement
        from .video_element import VideoElement
        from .image_element import ImageElement
        
        for element in self.elements:
            if isinstance(element, AudioElement) and element.loop_until_scene_end:
                element.update_duration_for_scene(self.duration)
            elif isinstance(element, VideoElement) and (element.loop_until_scene_end or getattr(element, '_wants_scene_duration', False)):
                element.update_duration_for_scene(self.duration)
            elif isinstance(element, ImageElement) and (element.loop_until_scene_end or getattr(element, '_wants_scene_duration', False)):
                element.update_duration_for_scene(self.duration)
    
    def start_at(self, time: float) -> 'Scene':
        """Set the start time of this scene.
        
        Args:
            time: Start time in seconds
            
        Returns:
            Self for method chaining
        """
        self.start_time = time
        return self
    
    def render(self, time: float) -> None:
        """Render all elements in this scene at the given time.
        
        Args:
            time: Current time in seconds (absolute time, not relative to scene)
        """
        scene_time = time - self.start_time
        if scene_time < 0 or scene_time > self.duration:
            return
        
        for element in self.elements:
            element.render(scene_time)