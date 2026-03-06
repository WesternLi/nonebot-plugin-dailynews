from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from typing import List, Union

from .news_fetcher import NewsItem


class ImageGenerator:
    def __init__(
        self,
        width: int = 1400,
        padding: int = 60,
        line_spacing: int = 14,
        title_size: int = 42,
        content_size: int = 28,
    ):
        self.width = width
        self.padding = padding
        self.line_spacing = line_spacing
        self.title_size = title_size
        self.content_size = content_size

    def _load_font(self, size: int) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        try:
            return ImageFont.truetype("msyh.ttc", size)
        except Exception:
            try:
                return ImageFont.truetype("simsun.ttc", size)
            except Exception:
                try:
                    return ImageFont.truetype("simhei.ttf", size)
                except Exception:
                    return ImageFont.load_default()

    def _wrap_text(self, draw, text: str, font: Union[ImageFont.FreeTypeFont, ImageFont.ImageFont], max_width: int) -> List[str]:
        lines = []
        words = text.replace("\n", " ").split()
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def generate_news_image(self, news_items: List[NewsItem], title: str = "每日新闻简报") -> BytesIO:
        title_font = self._load_font(self.title_size)
        content_font = self._load_font(self.content_size)
        small_font = self._load_font(18)

        header_height = 120
        footer_height = 60
        item_spacing = 30
        line_height = self.content_size + self.line_spacing

        temp_img = Image.new("RGB", (1, 1), color=(255, 255, 255))
        temp_draw = ImageDraw.Draw(temp_img)
        max_text_width = self.width - 2 * self.padding

        item_heights = []
        total_content_height = 0
        for item in news_items:
            title_lines = self._wrap_text(temp_draw, item.title, title_font, max_text_width)
            title_height = len(title_lines) * (self.title_size + self.line_spacing)
            desc_lines = []
            if item.description:
                desc_lines = self._wrap_text(temp_draw, item.description[:200], content_font, max_text_width)
            desc_height = len(desc_lines) * line_height
            source_height = 24
            item_height = title_height + desc_height + source_height + item_spacing * 2
            item_heights.append(item_height)
            total_content_height += item_height

        total_height = header_height + total_content_height + footer_height

        img = Image.new("RGB", (self.width, total_height), color=(248, 250, 252))
        draw = ImageDraw.Draw(img)

        header_gradient = Image.new("RGB", (self.width, header_height), color=(59, 130, 246))
        img.paste(header_gradient, (0, 0))

        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = bbox[2] - bbox[0]
        title_x = (self.width - title_width) // 2
        draw.text((title_x, 40), title, font=title_font, fill=(255, 255, 255))

        date_str = datetime.now().strftime("%Y年%m月%d日 %A")
        bbox = draw.textbbox((0, 0), date_str, font=small_font)
        date_width = bbox[2] - bbox[0]
        date_x = (self.width - date_width) // 2
        draw.text((date_x, 85), date_str, font=small_font, fill=(200, 200, 200))

        y_offset = header_height
        for idx, (item, item_height) in enumerate(zip(news_items, item_heights)):
            item_bg_color = (255, 255, 255) if idx % 2 == 0 else (250, 250, 250)
            draw.rectangle([self.padding, y_offset, self.width - self.padding, y_offset + item_height], fill=item_bg_color)

            title_lines = self._wrap_text(draw, item.title, title_font, max_text_width)
            current_y = y_offset + 15
            for line in title_lines:
                draw.text((self.padding, current_y), line, font=title_font, fill=(33, 37, 41))
                current_y += self.title_size + self.line_spacing

            if item.description:
                desc_text = item.description[:200]
                desc_lines = self._wrap_text(draw, desc_text, content_font, max_text_width)
                current_y += 10
                for line in desc_lines:
                    draw.text((self.padding + 20, current_y), line, font=content_font, fill=(100, 100, 100))
                    current_y += line_height

            source_text = f"来源: {item.source}"
            draw.text((self.padding + 20, y_offset + item_height - 30), source_text, font=small_font, fill=(150, 150, 150))

            y_offset += item_height

        draw.rectangle([0, total_height - footer_height, self.width, total_height], fill=(240, 240, 240))
        footer_text = "Generated by NoneBot2 DailyNews Plugin"
        bbox = draw.textbbox((0, 0), footer_text, font=small_font)
        footer_width = bbox[2] - bbox[0]
        footer_x = (self.width - footer_width) // 2
        draw.text((footer_x, total_height - 35), footer_text, font=small_font, fill=(150, 150, 150))

        buffer = BytesIO()
        img.save(buffer, format="PNG", quality=95)
        buffer.seek(0)
        return buffer
