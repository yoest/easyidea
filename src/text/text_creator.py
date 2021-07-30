import os
import random

from PIL import Image, ImageFont, ImageDraw
import numpy as np
import cv2

class TextCreator:
    """ Used to create and place the text on an image. """

    def __init__(self, words:list, keywords:list, output_image:object, color:str, keyword_font_color:str, output_data:object = None):
        """ Attributes : 
                words -> list : list of words to write on the image.
                keywords -> list : list of keywords to write differently on the image.
                output_image -> object : opencv output image.
                color -> str : color of the design.
                keyword_font_color -> str : color to apply to the keyword.
                output_data -> object : output data, used to recreate a design.
        """
        self.FONT_FOLDER = "./fonts/"
        self.USED_FONT = self.__choose_random_font() if output_data == None else output_data['font']

        self.words = words
        self.keywords = keywords
        self.output_image = output_image
        self.text_color = color
        self.keyword_font_color = keyword_font_color
        self.text_positions = []

        self.FONT_PADDING_TOP_RATIO = 6
        self.output_data = output_data
        self.CURRENT_LIST_FONTS_INDEX = []


    def __choose_random_font(self):
        """ Choose a random font in the font folder. """
        list_fonts = [x[0] for x in os.walk(self.FONT_FOLDER)]

        # Remove the first one which is the font folder.
        list_fonts = list_fonts[1:]
        list_fonts = [x.split("/")[2] for x in list_fonts]

        # choose randomly
        index = random.randint(0, len(list_fonts) - 1)
        font = list_fonts[index]

        return font


    def write_text(self, type_writing:bool):
        """ Write the text on the image. 
        
            Attributes :
                type_writing -> bool : does we write everything on top or put the design in the middle.
        """
        x, y = 0, 0

        # Make into PIL Image.
        image_pil = Image.fromarray(self.output_image)

        # Write each word.
        for index, word in enumerate(self.words):
            self.current_word_index = index

            pos = x, y
            self.type_writing = type_writing and word == self.words[len(self.words) - 1] # Last word.

            # Look for keyword.
            current_keyword = None
            for keyword in self.keywords:
                if keyword in word:
                    current_keyword = keyword

            # Write the text on the image.
            if current_keyword == None:
                image, x, y, text_width, text_height = self.__write_text_without_keyword(word, image_pil, self.text_color, pos)
            else:
                image, x, y, text_width, text_height = self.__write_text_with_keyword(word, current_keyword, image_pil, self.text_color, pos)

            self.text_positions.append((x, y, text_width, text_height))
            y += text_height

        return image, self.text_positions


    def __write_text_without_keyword(self, word:str, image_pil:object, text_color:str, pos:tuple):
        """ Write some text when there is no keyword. 
        
            Attributes :
                word -> str : the word to write.
                image_pil -> object : PIL image.
                text_color -> str : color of the text.
                pos -> tuple : 2-tuple where to write the text.
        """
        font_size = 50
        text_width, text_height = 0, 0

        # Choose the extension : regular or light.
        extensions = ["regular", "light"]
        font_index = random.randint(0, 1) if self.output_data == None else self.output_data['list_fonts_index'][self.current_word_index]
        self.CURRENT_LIST_FONTS_INDEX.append(font_index)
        extension = extensions[font_index]

        while text_width < self.output_image.shape[1] - 20:
            font = ImageFont.truetype(f"./fonts/{self.USED_FONT}/{self.USED_FONT}-{extension}.ttf", font_size)
            text_width, text_height = font.getsize(word)
            font_size += 1

        x, y = pos
        if self.type_writing:
            x, y = x, self.output_image.shape[0] - text_height

        # Handle the problem with padding on custom font.
        font_top_padding = font_size / self.FONT_PADDING_TOP_RATIO

        # Insert the text and transform it ingo a OpenCV image again. 
        draw = ImageDraw.Draw(image_pil)
        draw.text((x, y), word, text_color, font)
        image = np.array(image_pil)

        return image, x, y + font_top_padding, text_width, text_height


    def __write_text_with_keyword(self, word:str, keyword:str, image_pil:object, text_color:str, pos:tuple):
        """ Write some text when there is some keyword. 
        
            Attributes :
                word -> str : the word to write.
                keyword -> str : the keyword to write differently.
                image_pil -> object : PIL image.
                text_color -> str : color of the text.
                pos -> tuple : 2-tuple where to write the text.
        """
        font_size = 50
        text_width_1, text_height_1 = 0, 0
        text_width_2, text_height_2 = 0, 0
        keyword_width, keyword_height = 0, 0

        parts = word.split(keyword)

        # Choose the extension : regular or light.
        extensions = ["regular", "light"]
        font_index = random.randint(0, 1) if self.output_data == None else self.output_data['list_fonts_index'][self.current_word_index]
        self.CURRENT_LIST_FONTS_INDEX.append(font_index)
        extension = extensions[font_index]

        while text_width_1 + keyword_width + text_width_2 < self.output_image.shape[1] - 20:
            font = ImageFont.truetype(f"./fonts/{self.USED_FONT}/{self.USED_FONT}-{extension}.ttf", font_size)
            keyword_font = ImageFont.truetype(f"./fonts/{self.USED_FONT}/{self.USED_FONT}-bold.ttf", font_size)

            text_width_1, text_height_1 = font.getsize(parts[0])
            text_width_2, text_height_2 = font.getsize(parts[1])
            keyword_width, keyword_height = keyword_font.getsize(keyword)

            full_width, full_height = text_width_1 + keyword_width + text_width_2, max(text_height_1, text_height_2, keyword_height)

            font_size += 1

        # Handle the positionning of the last words.
        x, y = pos
        if self.type_writing:
            x, y = x, self.output_image.shape[0] - full_height - 20 # 20 for padding.

        # Handle the problem with padding on custom font.
        font_top_padding = font_size / self.FONT_PADDING_TOP_RATIO

        # Insert the text and transform it ingo a OpenCV image again. 
        stroke_width = font_size // 70
        draw = ImageDraw.Draw(image_pil)
        draw.text((x, y), parts[0], text_color, font)
        draw.text((x + text_width_1, y), keyword, self.keyword_font_color, keyword_font, stroke_fill=text_color, stroke_width=stroke_width)
        draw.text((x + text_width_1 + keyword_width, y), parts[1], text_color, font)
        image = np.array(image_pil)

        return image, x, y + font_top_padding, full_width, full_height