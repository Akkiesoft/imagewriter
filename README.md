# -*- coding:utf-8 -*-

"""
oledscreen / oledmenu module

Copyright 2019 @Akkiesoft
akkiesoft@marokun.net
The MIT License
https://opensource.org/licenses/mit-license.php

* Required module and libraries(config, SH1106):
  Waveshare 1.3 inch OLED HAT
    https://www.waveshare.com/wiki/1.3inch_OLED_HAT
"""

from PIL import Image,ImageDraw,ImageFont

class oledscreen:
    def __init__(self, width, height, font_path, font_size, line_height, cursor = 0):
        self.width = width
        self.height = height
        self.font = ImageFont.truetype(font_path, font_size)
        self.line_height = line_height
        self.image = Image.new('1', (self.width, self.height), "WHITE")
        self.draw = ImageDraw.Draw(self.image)
        self.__draw_circle()

    def __draw_circle(self):
        w = self.width - 1
        h = self.height - 1
        lh = self.line_height
        self.draw.line([(0, lh),(w, lh)], fill = 0)
        self.draw.line([(0, lh),(0, h)], fill = 0)
        self.draw.line([(0, h),(w, h)], fill = 0)
        self.draw.line([(w, lh),(w, h)], fill = 0)
        self.draw.rectangle((0, 0, w, lh - 1), fill = 0)

    def settitle(self, title):
        self.title = title
        w = self.width - 1
        lh = self.line_height
        self.draw.rectangle((0, 0, w, lh - 1), fill = 0)
        self.draw.text((2, 0), title, font = self.font, fill = 1)

    def text(self, l, t):
        lh = self.line_height
        h = lh * (l + 1) + 2
        self.draw.rectangle((3, h, self.width - 2, h + lh), fill = 1)
        self.draw.text((3, h), t, font = self.font, fill = 0)

class oledmenu(oledscreen):
    def __init__(self, width, height, font_path, font_size, line_height, max_lines, cursor = 0):
        super().__init__(width, height, font_path, font_size, line_height, cursor)
        self.max_lines = max_lines
        self.setcursor(cursor)
        self.type = "menu"

    def __draw_cursor(self):
        h = self.height - 2
        lh = self.line_height
        # フォントの1文字あたりの横幅次第問題
        self.draw.rectangle((3, lh + 1, 6, h), fill = 1)

        h = self.line_height * (self.cursor + 1) + 2
        self.draw.text((3, h), ">", font = self.font, fill = 0)

    def setmenu(self, menu):
        # TODO: max_lines
        self.menu = menu
        for c,i in enumerate(menu):
            h = self.line_height * (c + 1) + 2
            self.draw.text((8, h), i, font = self.font, fill = 0)
        self.__draw_cursor()

    def setparent(self, menu):
        self.parent = menu
        self.child = False

    def setchild(self, menu):
        self.child = menu
        self.parent = False

    def is_parent(self):
        if self.child:
            return True

    def is_child(self):
        if self.parent:
            return True

    def setcursor(self, cursor):
        self.cursor = cursor
        self.__draw_cursor()

    def moveup(self):
        if (self.cursor < 1):
            return
        self.setcursor(self.cursor - 1)

    def movedown(self):
        if (len(self.menu) <= self.cursor + 1):
            return
        self.setcursor(self.cursor + 1)
