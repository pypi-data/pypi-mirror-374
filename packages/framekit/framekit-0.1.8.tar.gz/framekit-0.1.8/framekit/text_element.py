import os
from typing import Tuple, Optional, List, Dict, Any, Literal, Union
import numpy as np
from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont
from .video_base import VideoBase


class TextElement(VideoBase):
    """Text element for rendering text with various styling options.
    
    This class extends VideoBase to provide text rendering capabilities with support for
    multi-line text, different alignments, custom fonts, colors, and styling options.
    
    Attributes:
        text: The text content to display
        size: Font size in pixels
        color: RGB color tuple for text color
        font_path: Optional path to custom font file
        bold: Whether to render text in bold
        texture_id: OpenGL texture ID for the rendered text
        texture_width: Width of the texture in pixels
        texture_height: Height of the texture in pixels
        alignment: Text alignment for multi-line text
        line_spacing: Additional spacing between lines in pixels
    """
    
    def __init__(self, text: str, size: int = 50, color: Tuple[int, int, int] = (255, 255, 255), 
                 font_path: Optional[str] = None, bold: bool = False) -> None:
        """Initialize a new TextElement.
        
        Args:
            text: Text content to display (supports multi-line with \n)
            size: Font size in pixels
            color: RGB color tuple (0-255 for each component)
            font_path: Optional path to custom font file. Falls back to system fonts if None
            bold: Whether to render text in bold style
        """
        super().__init__()
        self.text: str = text
        self.size: int = size
        self.color: Tuple[int, int, int] = color
        self.font_path: Optional[str] = font_path
        self.bold: bool = bold
        self.texture_id: Optional[int] = None
        self.texture_width: int = 0
        self.texture_height: int = 0
        
        # Multi-line and alignment settings
        self.alignment: Literal['left', 'center', 'right'] = 'left'
        self.line_spacing: int = 0
        
        self._create_text_texture()
        # 初期化時にサイズを計算
        self.calculate_size()
    
    
    def set_alignment(self, alignment: Literal['left', 'center', 'right']) -> 'TextElement':
        """Set text alignment for multi-line text.
        
        Args:
            alignment: Text alignment ('left', 'center', or 'right')
            
        Returns:
            Self for method chaining
        """
        if alignment in ['left', 'center', 'right']:
            self.alignment = alignment
            # テクスチャを再作成する必要がある
            self.texture_created = False
            # サイズを再計算
            self.calculate_size()
        return self
    
    def set_line_spacing(self, spacing: int) -> 'TextElement':
        """Set line spacing for multi-line text.
        
        Args:
            spacing: Additional spacing between lines in pixels
            
        Returns:
            Self for method chaining
        """
        self.line_spacing = spacing
        # テクスチャを再作成する必要がある
        self.texture_created = False
        # サイズを再計算
        self.calculate_size()
        return self
    
    def _create_text_texture(self) -> None:
        """Prepare text texture creation (deferred until OpenGL context is available).
        
        This method marks the texture as needing creation but doesn't actually create it
        until an OpenGL context is available during rendering.
        """
        # テクスチャ作成は後でrender時に行う（OpenGLコンテキストが必要なため）
        self.texture_created = False
    
    def _create_texture_now(self) -> None:
        """Create OpenGL texture for the text within an OpenGL context.
        
        This method handles font loading, text measurement, multi-line rendering,
        background/border application, and OpenGL texture creation.
        """
        try:
            # 高解像度レンダリング用にフォントサイズを調整
            high_res_size = int(self.size * self.render_scale)
            
            # フォントを読み込み
            if self.font_path and os.path.exists(self.font_path):
                font = ImageFont.truetype(self.font_path, high_res_size)
            else:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", high_res_size)
                except:
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", high_res_size)
                    except:
                        font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 複数行テキストを分割
        lines = self.text.split('\n')
        
        # 各行のサイズを測定（高解像度で）
        dummy_img = Image.new('RGBA', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        line_info = []
        max_width = 0
        total_height = 0
        high_res_line_spacing = int(self.line_spacing * self.render_scale)
        
        for i, line in enumerate(lines):
            if line.strip():  # 空行でない場合
                bbox = dummy_draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
                y_offset = -bbox[1]
            else:  # 空行の場合
                line_width = 0
                line_height = font.getmetrics()[0]  # ascent only
                y_offset = 0
            
            line_info.append({
                'text': line,
                'width': line_width,
                'height': line_height,
                'y_offset': y_offset
            })
            
            max_width = max(max_width, line_width)
            total_height += line_height
            if i < len(lines) - 1:  # 最後の行でなければ行間を追加
                total_height += high_res_line_spacing
        
        # テキスト用の画像を作成（パディングなし）
        content_width = max_width
        content_height = total_height
        
        # 最小サイズを保証
        content_width = max(content_width, 1)
        content_height = max(content_height, 1)
        
        # テキスト用の画像を作成
        img = Image.new('RGBA', (content_width, content_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # テキストを描画
        current_y = 0
        
        for line_data in line_info:
            if line_data['text'].strip():  # 空行でない場合のみ描画
                # 水平位置を計算（配置設定に基づく）
                if self.alignment == 'left':
                    x_pos = 0
                elif self.alignment == 'center':
                    x_pos = (content_width - line_data['width']) // 2
                else:  # right
                    x_pos = content_width - line_data['width']
                
                # テキストを描画（太字の場合はstroke_widthを使用）
                high_res_stroke_width = max(1, int(2 * self.render_scale))
                if self.bold:
                    draw.text((x_pos, current_y + line_data['y_offset']), 
                             line_data['text'], 
                             font=font, 
                             fill=(*self.color, 255),
                             stroke_width=high_res_stroke_width,
                             stroke_fill=(*self.color, 255))
                else:
                    draw.text((x_pos, current_y + line_data['y_offset']), 
                             line_data['text'], 
                             font=font, 
                             fill=(*self.color, 255))
            
            # 次の行の位置を計算
            current_y += line_data['height'] + high_res_line_spacing
        
        # 背景と枠線を適用
        img = self._apply_border_and_background_to_image(img)
        
        # 高解像度画像を最終サイズにダウンサンプリング（アンチエイリアシング効果）
        if self.render_scale > 1.0:
            final_width = int(img.size[0] / self.render_scale)
            final_height = int(img.size[1] / self.render_scale)
            img = img.resize((final_width, final_height), Image.Resampling.LANCZOS)
        
        # 実際のテクスチャサイズを更新
        self.texture_width = img.size[0]
        self.texture_height = img.size[1]
        
        # ボックスサイズを更新（背景・枠線を含む最終サイズ）
        self.width = self.texture_width
        self.height = self.texture_height
        
        # 画像をNumPy配列に変換
        img_data = np.array(img)
        
        # OpenGLテクスチャを生成
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # テクスチャパラメータを設定
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        # テクスチャデータをアップロード
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.texture_width, self.texture_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        
        glBindTexture(GL_TEXTURE_2D, 0)
        self.texture_created = True

    def calculate_size(self) -> None:
        """Pre-calculate text box size including padding and styling.
        
        This method measures the text content and calculates the final box size
        including background padding and border width to set the width and height attributes.
        """
        try:
            # フォントを読み込み
            if self.font_path and os.path.exists(self.font_path):
                font = ImageFont.truetype(self.font_path, self.size)
            else:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", self.size)
                except:
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", self.size)
                    except:
                        font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 複数行テキストを分割
        lines = self.text.split('\n')
        
        # 各行のサイズを測定
        dummy_img = Image.new('RGBA', (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        max_width = 0
        total_height = 0
        
        for i, line in enumerate(lines):
            if line.strip():  # 空行でない場合
                bbox = dummy_draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
            else:  # 空行の場合
                line_width = 0
                line_height = font.getmetrics()[0]  # ascent only
            
            max_width = max(max_width, line_width)
            total_height += line_height
            if i < len(lines) - 1:  # 最後の行でなければ行間を追加
                total_height += self.line_spacing
        
        # コンテンツサイズ
        content_width = max(max_width, 1)
        content_height = max(total_height, 1)
        
        # パディングを含むキャンバスサイズを計算
        canvas_width = content_width + self.padding['left'] + self.padding['right']
        canvas_height = content_height + self.padding['top'] + self.padding['bottom']
        
        # 最小サイズを保証
        canvas_width = max(canvas_width, 1)
        canvas_height = max(canvas_height, 1)
        
        # ボックスサイズを更新
        self.width = canvas_width
        self.height = canvas_height

    def render(self, time: float) -> None:
        """Render the text element with OpenGL.
        
        Args:
            time: Current time in seconds for animation updates
        """
        if not self.is_visible_at(time):
            return
        
        # アニメーションプロパティを適用
        self.update_animated_properties(time)
        
        # テクスチャがまだ作成されていない場合は作成
        if not self.texture_created:
            self._create_texture_now()
        
        if self.texture_id is None:
            return
        
        # Get actual render position using anchor calculation
        render_x, render_y, _, _ = self.get_actual_render_position()
        
        # 変換行列を保存
        glPushMatrix()
        
        # 中心点を基準に変換を適用
        center_x = render_x + self.texture_width / 2
        center_y = render_y + self.texture_height / 2
        
        # 中心点に移動
        glTranslatef(center_x, center_y, 0)
        
        # 回転を適用
        if hasattr(self, 'rotation') and self.rotation != 0:
            glRotatef(self.rotation, 0, 0, 1)
        
        # スケールを適用
        if hasattr(self, 'scale') and self.scale != 1.0:
            glScalef(self.scale, self.scale, 1.0)
        
        # 中心点を戻す
        glTranslatef(-center_x, -center_y, 0)
        
        # テクスチャを有効にする
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        # アルファブレンディングを有効にする
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # アルファ値を適用（アニメーション考慮）
        alpha_value = 1.0
        if hasattr(self, 'background_alpha'):
            alpha_value = self.background_alpha / 255.0
        glColor4f(1.0, 1.0, 1.0, alpha_value)
        
        # テクスチャ付きの四角形を描画
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(render_x, render_y)
        
        glTexCoord2f(1.0, 0.0)
        glVertex2f(render_x + self.texture_width, render_y)
        
        glTexCoord2f(1.0, 1.0)
        glVertex2f(render_x + self.texture_width, render_y + self.texture_height)
        
        glTexCoord2f(0.0, 1.0)
        glVertex2f(render_x, render_y + self.texture_height)
        glEnd()
        
        # テクスチャを無効にする
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)
        
        # 変換行列を復元
        glPopMatrix()
    
    def __del__(self) -> None:
        """Destructor to clean up OpenGL texture resources.
        
        Safely deletes the OpenGL texture if it was created to prevent memory leaks.
        """
        if self.texture_id:
            try:
                glDeleteTextures(1, [self.texture_id])
            except:
                pass