import os
import cv2
import numpy as np
from typing import List
from tqdm import tqdm
from OpenGL.GL import *
from OpenGL.GLU import *
from .scene import Scene

# Pygameの警告を抑制
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

# オーディオ処理用ライブラリの試行インポート
try:
    import subprocess
    import json
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False


def has_audio_stream(video_path: str) -> bool:
    """Check if a video file has an audio stream using ffprobe.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        True if the video has at least one audio stream, False otherwise
    """
    if not HAS_FFMPEG:
        return False
    
    if not os.path.exists(video_path):
        return False
    
    try:
        # Use ffprobe to check for audio streams
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_streams', '-select_streams', 'a', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                streams = data.get('streams', [])
                return len(streams) > 0
            except json.JSONDecodeError:
                return False
        return False
        
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback: try to use OpenCV to detect audio properties
        try:
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                # Try to get audio properties - if they exist, there's likely audio
                audio_fourcc = cap.get(cv2.CAP_PROP_AUDIO_STREAM)
                cap.release()
                return audio_fourcc != -1.0 and audio_fourcc != 0.0
            cap.release()
        except:
            pass
        
        return False


class MasterScene:
    """マスターシーンクラス - 全体の動画を管理"""
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 60):
        self.width = width
        self.height = height
        self.fps = fps
        self.scenes: List[Scene] = []
        self.total_duration = 0.0
        self.output_filename = "output_video.mp4"
        self.audio_elements = []  # オーディオ要素を追跡
    
    def add(self, scene: Scene):
        """シーンを追加"""
        self.scenes.append(scene)
        # 全体の継続時間を更新
        scene_end_time = scene.start_time + scene.duration
        self.total_duration = max(self.total_duration, scene_end_time)
        
        # オーディオ要素を収集
        self._collect_audio_elements(scene)
        
        # マスターシーン全体の長さに合わせてBGMの持続時間を更新
        self._update_master_bgm_durations()
        return self
    
    def _update_master_bgm_durations(self):
        """マスターシーン全体の長さに合わせてBGMの持続時間を更新"""
        from .audio_element import AudioElement
        for audio_element in self.audio_elements:
            if isinstance(audio_element, AudioElement) and audio_element.loop_until_scene_end:
                # マスターシーン全体の長さまでBGMを拡張
                if self.total_duration > audio_element.duration:
                    audio_element.duration = self.total_duration
    
    def _collect_audio_elements(self, scene: Scene):
        """シーンからオーディオ要素を収集"""
        from .audio_element import AudioElement
        from .video_element import VideoElement
        for element in scene.elements:
            if isinstance(element, AudioElement):
                # Standalone audio elements are always valid
                self.audio_elements.append(element)
            elif isinstance(element, VideoElement):
                # Ensure the video element's audio element is created
                element._ensure_audio_element()
                audio_element = element.get_audio_element()
                if audio_element is not None:
                    # Only add if the video actually has audio
                    self.audio_elements.append(audio_element)
    
    def set_output(self, filename: str):
        """出力ファイル名を設定"""
        self.output_filename = filename
        return self
    
    def _init_opengl(self):
        """OpenGLの初期設定"""
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # 座標系を設定（左上が原点、ピクセル座標系）
        glOrtho(0, self.width, self.height, 0, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # ブレンディングを有効にしてアルファ値を使用可能に
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def _setup_video_writer(self):
        """動画書き込み設定"""
        # 出力ディレクトリを作成
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # オーディオ要素がある場合は一時ファイル、ない場合は指定ファイル名
        if self.audio_elements:
            # 一時ファイル名を作成
            base_name = os.path.splitext(self.output_filename)[0]
            temp_filename = f"{base_name}_temp_video_only.mp4"
            full_path = os.path.join(output_dir, temp_filename)
        else:
            full_path = os.path.join(output_dir, self.output_filename)
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        
        video_writer = cv2.VideoWriter(full_path, fourcc, self.fps, (self.width, self.height))
        
        if not video_writer.isOpened():
            raise Exception(f"動画ファイル {full_path} を作成できませんでした")
        
        return video_writer, full_path
    
    def _capture_frame(self):
        """現在の画面をキャプチャ"""
        pixels = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
        image = np.frombuffer(pixels, dtype=np.uint8)
        image = image.reshape((self.height, self.width, 3))
        image = np.flipud(image)  # OpenGLは左下が原点なので上下反転
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image
    
    def _create_audio_mix(self, video_path: str):
        """FFmpegを使ってビデオにオーディオを追加"""
        if not self.audio_elements:
            print("No audio elements found, skipping audio mixing")
            return video_path
        
        if not HAS_FFMPEG:
            print("Warning: subprocess not available, cannot mix audio")
            return video_path
        
        # FFmpegが利用可能かチェック
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: FFmpeg not found, cannot mix audio")
            print("Install FFmpeg to enable audio mixing:")
            print("  macOS: brew install ffmpeg")
            print("  Ubuntu: sudo apt install ffmpeg")
            return video_path
        
        output_dir = "output"
        final_output = os.path.join(output_dir, self.output_filename)
        
        # 複数のオーディオファイルを処理するためのコマンド構築
        cmd = ['ffmpeg', '-y', '-i', video_path]
        
        # 存在するオーディオファイルのみを追加（タイミング情報はfilter_complexで処理）
        valid_audio_files = []
        
        # オーディオタイミング検証および音声ストリーム確認
        for audio_element in self.audio_elements:
            if not os.path.exists(audio_element.audio_path):
                print(f"Warning: Audio file not found, skipping: {audio_element.audio_path}")
                continue
            
            # Check if the file has actual audio streams (for video files)
            if not has_audio_stream(audio_element.audio_path):
                print(f"Warning: No audio stream found in file, skipping: {audio_element.audio_path}")
                continue
            
            # 警告チェック
            if audio_element.start_time + audio_element.duration > self.total_duration + 0.1:  # 0.1s tolerance
                print(f"  WARNING: Audio extends beyond scene duration ({self.total_duration:.2f}s)")
            if audio_element.start_time < 0:
                print(f"  WARNING: Audio starts before scene start")
            
            # BGMモードでループが必要な場合は複数回入力を追加
            if getattr(audio_element, 'loop_until_scene_end', False) and audio_element.duration > audio_element.original_duration:
                # 必要なループ回数を計算
                loop_count = int((audio_element.duration / audio_element.original_duration) + 0.99)
                
                # 同じファイルを複数回入力として追加
                for i in range(loop_count):
                    cmd.extend(['-i', audio_element.audio_path])
                
            else:
                # 通常の単一入力
                cmd.extend(['-i', audio_element.audio_path])
            
            valid_audio_files.append(audio_element)
        
        if not valid_audio_files:
            print("No valid audio files found, keeping video-only output")
            return video_path
        
        # オーディオファイルのミキシング処理
        if len(valid_audio_files) == 1:
            # 単一オーディオファイルの場合、volume調整とduration制限を適用
            audio_element = valid_audio_files[0]
            volume = audio_element.volume if hasattr(audio_element, 'volume') else 1.0
            is_muted = getattr(audio_element, 'is_muted', False)

            # ミュート状態の場合は音量を0にする
            if is_muted:
                volume = 0.0
            
            # BGMのループが必要な場合
            if getattr(audio_element, 'loop_until_scene_end', False) and audio_element.duration > audio_element.original_duration:
                # 複数の入力ストリームを連結してループを作成
                loop_count = int((audio_element.duration / audio_element.original_duration) + 0.99)

                # 複数のストリームを連結
                input_streams = []
                for i in range(1, loop_count + 1):  # 1から開始（0はビデオ）
                    input_streams.append(f"[{i}:a]")
                
                # 連結フィルター
                concat_filter = ''.join(input_streams) + f"concat=n={loop_count}:v=0:a=1[looped];"
                
                # 遅延処理
                start_time = audio_element.start_time
                filter_chain = "[looped]"
                if start_time > 0:
                    delay_ms = int(start_time * 1000)
                    filter_chain += f"adelay={delay_ms}|{delay_ms},"
                
                # 音量調整と時間制限
                filter_chain += f"volume={volume},atrim=end={self.total_duration}"
                
                full_filter = concat_filter + filter_chain
                cmd.extend(['-filter_complex', full_filter, '-c:v', 'copy', '-c:a', 'aac', 
                           '-t', str(self.total_duration), final_output])
            else:
                # 単一ファイル、ループなしの場合
                filter_chain = ""
                
                # 遅延処理
                start_time = audio_element.start_time
                if start_time > 0:
                    delay_ms = int(start_time * 1000)
                    filter_chain += f"adelay={delay_ms}|{delay_ms},"
                
                # 音量調整と時間制限
                filter_chain += f"volume={volume},atrim=end={self.total_duration}"
                
                cmd.extend(['-filter:a', filter_chain, '-c:v', 'copy', '-c:a', 'aac', 
                           '-t', str(self.total_duration), final_output])
        else:
            # オーディオストリームをミキシングするfilter_complexを構築（adelayでタイミング制御）
            audio_inputs = []
            for i, audio_element in enumerate(valid_audio_files, 1):  # index 1から開始（index 0はビデオ）
                # 各オーディオストリームに対してvolume、delay、duration制限を適用
                volume = audio_element.volume if hasattr(audio_element, 'volume') else 1.0
                start_time = audio_element.start_time
                delay_ms = int(start_time * 1000)  # milliseconds for adelay

                # ミュート状態の場合は音量を0にする
                if getattr(audio_element, 'is_muted', False):
                    volume = 0.0
                
                # フィルターチェーンを構築
                filter_chain = f"[{i}:a]"
                
                # BGMの場合は最初にループ処理を適用
                if getattr(audio_element, 'loop_until_scene_end', False) and audio_element.duration > audio_element.original_duration:
                    # 必要な長さまでループさせる
                    # aloopを使用して無限ループし、その後atrimで必要な長さに切り取る
                    filter_chain += f"aloop=loop=-1:size={int(44100 * audio_element.original_duration)},atrim=end={audio_element.duration},"

                # 遅延を適用（0秒の場合はスキップ）
                if delay_ms > 0:
                    filter_chain += f"adelay={delay_ms}|{delay_ms},"  # ステレオの場合両チャンネルに適用
                
                # 音量調整を適用
                filter_chain += f"volume={volume}"
                
                # 最終的な時間制限を適用（全体の動画時間を超えないように）
                if getattr(audio_element, 'loop_until_scene_end', False):
                    filter_chain += f",atrim=end={self.total_duration}"
                else:
                    pass
                
                audio_inputs.append(f"{filter_chain}[a{i}]")
            
            # 全てのオーディオストリームをミキシング（正規化を無効にして音量を保持）
            mix_inputs = ''.join([f"[a{i}]" for i in range(1, len(valid_audio_files) + 1)])
            filter_complex = ';'.join(audio_inputs) + f";{mix_inputs}amix=inputs={len(valid_audio_files)}:normalize=0[aout]"
            
            cmd.extend(['-filter_complex', filter_complex, '-map', '0:v', '-map', '[aout]', 
                       '-c:v', 'copy', '-c:a', 'aac', '-t', str(self.total_duration), final_output])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # 一時ファイルを削除
                if os.path.exists(video_path) and "temp_video_only" in video_path:
                    os.remove(video_path)
                return final_output
            else:
                print(f"FFmpeg error: {result.stderr}")
                print("Keeping video-only output")
                return video_path
        except Exception as e:
            print(f"Error during audio mixing: {e}")
            print("Keeping video-only output")
            return video_path
    
    def render(self):
        """動画をレンダリング"""
        # 環境設定（ウィンドウを非表示）
        os.environ['SDL_VIDEODRIVER'] = 'cocoa'
        os.environ['SDL_VIDEO_WINDOW_POS'] = '-1000,-1000'
        
        # Pygameを初期化
        pygame.init()
        
        # OpenGLウィンドウを作成
        screen = pygame.display.set_mode(
            (self.width, self.height), 
            pygame.DOUBLEBUF | pygame.OPENGL | pygame.HIDDEN
        )
        
        # OpenGLを初期化
        self._init_opengl()
        
        # 動画書き込み設定
        video_writer, video_path = self._setup_video_writer()
        
        try:
            total_frames = int(self.total_duration * self.fps)

            # tqdmでプログレスバーを表示
            with tqdm(total=total_frames, desc="Rendering", unit="frames") as pbar:
                for frame_num in range(total_frames):
                    current_time = frame_num / self.fps
                    
                    # 画面をクリア
                    glClear(GL_COLOR_BUFFER_BIT)
                    
                    # 全シーンをレンダリング
                    for scene in self.scenes:
                        scene.render(current_time)
                    
                    # 描画を確定
                    pygame.display.flip()
                    
                    # フレームをキャプチャして動画に書き込み
                    frame = self._capture_frame()
                    video_writer.write(frame)
                    
                    # プログレスバーを更新
                    pbar.update(1)
            
        finally:
            # クリーンアップ
            video_writer.release()
            pygame.quit()
            
            # オーディオミキシング（ビデオ作成後）
            if self.audio_elements:
                final_output = self._create_audio_mix(video_path)