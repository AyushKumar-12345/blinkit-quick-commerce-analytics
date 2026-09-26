"""
Blinkit Analytics Dashboard - Automated Canvas & Theme Generator
Author: Ayush Kumar
"""

import os
from typing import Tuple
from PIL import Image, ImageDraw


class DashboardCanvasGenerator:
    COLOR_CANVAS_BG = (17, 24, 39)
    COLOR_SIDEBAR_BG = (15, 20, 31)
    COLOR_CARD_BG = (30, 41, 59)
    COLOR_CARD_BORDER = (51, 65, 85)
    COLOR_BRAND_YELLOW = (248, 203, 70)
    COLOR_BRAND_GREEN = (12, 131, 70)

    def __init__(self, width: int = 1920, height: int = 1080, sidebar_width: int = 280):
        self.width = width
        self.height = height
        self.sidebar_width = sidebar_width
        self.image = Image.new("RGBA", (self.width, self.height), self.COLOR_CANVAS_BG)
        self.draw = ImageDraw.Draw(self.image)

    def _render_layout_structure(self) -> None:
        self.draw.rectangle([(0, 0), (self.sidebar_width, self.height)], fill=self.COLOR_SIDEBAR_BG)
        self.draw.rectangle([(self.sidebar_width - 4, 0), (self.sidebar_width - 2, self.height)], fill=self.COLOR_BRAND_GREEN)
        self.draw.rectangle([(self.sidebar_width - 2, 0), (self.sidebar_width, self.height)], fill=self.COLOR_BRAND_YELLOW)
        header_height = 80
        self.draw.line([(self.sidebar_width, header_height), (self.width, header_height)], fill=self.COLOR_CARD_BORDER, width=1)

    def _render_card_container(self, bounds: Tuple[int, int, int, int], corner_radius: int = 12, accent_color: Tuple[int, int, int] = None) -> None:
        x0, y0, x1, y1 = bounds
        self.draw.rounded_rectangle(bounds, radius=corner_radius, fill=self.COLOR_CARD_BG, outline=self.COLOR_CARD_BORDER, width=1)
        if accent_color:
            self.draw.rounded_rectangle([(x0, y0), (x1, y0 + 6)], radius=corner_radius, fill=accent_color)

    def build_canvas(self, output_path: str = "Blinkit_Background.png") -> None:
        self._render_layout_structure()
        kpi_y0, kpi_y1 = 110, 220
        kpi_width = 370
        spacing = 24
        start_x = self.sidebar_width + 30

        for i, accent in enumerate([self.COLOR_BRAND_YELLOW, self.COLOR_BRAND_GREEN, (59, 130, 246), (168, 85, 247)]):
            x0 = start_x + i * (kpi_width + spacing)
            x1 = x0 + kpi_width
            self._render_card_container((x0, kpi_y0, x1, kpi_y1), accent_color=accent)

        mid_y0, mid_y1 = 250, 620
        mid_w1, mid_w2 = 1000, 560
        self._render_card_container((start_x, mid_y0, start_x + mid_w1, mid_y1))
        self._render_card_container((start_x + mid_w1 + spacing, mid_y0, start_x + mid_w1 + spacing + mid_w2, mid_y1))

        bot_y0, bot_y1 = 650, 1030
        bot_w = (mid_w1 + spacing + mid_w2 - spacing) // 2
        self._render_card_container((start_x, bot_y0, start_x + bot_w, bot_y1))
        self._render_card_container((start_x + bot_w + spacing, bot_y0, start_x + bot_w + spacing + bot_w, bot_y1))

        self.image.convert("RGB").save(output_path, "PNG", quality=95)
        print(f"Canvas saved to: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    generator = DashboardCanvasGenerator()
    generator.build_canvas()
