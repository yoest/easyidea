from inout.json_parser import JSONInputParser, JSONOutputParser

from design.place_finder import PlaceFinder
from design.svg_editor import SVGEditor
from text.text_creator import TextCreator

from PIL import Image
import cv2
import numpy as np

import random

class DesignHandler:
    """ Used to generate many designs. """
    
    def __init__(self, index:int, template_number:int = 1, is_recreating:bool = False, color:str = "white"):
        """ Attributes :
                index -> int : index of the data in the JSON file.
                template_number -> int : number of the template to create.
                is_recreating -> bool : do we want to recreate the design.
                color -> str : color of the design.
        """
        self.DATA = JSONInputParser().get_data(index)
        self.BLANK_IMG = "./images/svg/blank.png"
        self.WAITING_FILE = f"./images/waiting/{self.DATA['design']}-{template_number}.png"

        if is_recreating:
            self.WAITING_FILE = f"./images/output/{self.DATA['design']}-{template_number}-{color}.png"
        self.is_recreating = is_recreating

        self.JSON_OUTPUT = JSONOutputParser(index)
        self.OUTPUT_DATA = self.JSON_OUTPUT.get_data() if is_recreating else None

        self.color = color


    def build(self):
        """ Build mutliple designs. """
        blank_image = cv2.imread(self.BLANK_IMG, cv2.IMREAD_UNCHANGED)
        self.img_result = blank_image[:, :, :].copy()

        self.editor = SVGEditor(self.DATA['design'])
        keyword_font_color = self.editor.get_best_key_color()

        self.__handle_text(keyword_font_color)
        self.__handle_image()

        # Save the created image to the output.
        self.JSON_OUTPUT.add_list_fonts_index(self.list_fonts_index)
        
        return self.JSON_OUTPUT


    def __handle_text(self, keyword_font_color:str):
        """ Handle the text positionning. 
        
            Attributes :
                keyword_font_color -> str : font color to apply to the keyword.
        """
        text_creator = TextCreator(self.DATA['text'], self.DATA['keywords'], self.img_result, self.color, keyword_font_color, self.OUTPUT_DATA)

        # Randomize the template.
        type_writing = random.randint(0, 1) == 0 if not self.is_recreating else self.OUTPUT_DATA['type_writing']
        self.img_result, self.text_positions = text_creator.write_text(type_writing)
        self.list_fonts_index = text_creator.CURRENT_LIST_FONTS_INDEX

        self.JSON_OUTPUT.add_font(text_creator.USED_FONT)
        self.JSON_OUTPUT.add_type_writing(type_writing)

        # Save the image.
        cv2.imwrite(self.WAITING_FILE, self.img_result)


    def __handle_image(self):
        """ Handle the design positionning. """
        # Find the best place to put the image into the design.
        design_size = Image.open(self.BLANK_IMG).size
        image_size = self.editor.get_svg_size()
        finder = PlaceFinder(self.text_positions, design_size, image_size, True)
        x, y, w, h = finder.find_best_place()

        # Edit the image.
        border_color = "#FFFFFF" if self.color == "white" else "#000000"
        self.editor.draw_border(border_color)
        self.editor.resize(w, h)
        image_path = self.editor.convert_to_png()

        # Create the design.
        icon_image = cv2.imread(image_path, -1)

        alpha_mask = icon_image[:, :, 3] / 255.0
        img_overlay = icon_image[:, :, :]
        output_image = self.__overlay_image_alpha(self.img_result, img_overlay, x, y, alpha_mask)

        # Save the image.
        cv2.imwrite(self.WAITING_FILE, output_image)
        self.editor.clear()


    def __overlay_image_alpha(self, img, img_overlay, x, y, alpha_mask):
        """ Overlay "img_overlay" onto "img" at (x, y) and blend using "alpha_mask". 

            Code taken here : 
                https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv
        """
        # Image ranges
        y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
        x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

        # Overlay ranges
        y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
        x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

        # Exit if nothing to do
        if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
            return

        # Blend overlay within the determined ranges
        img_crop = img[y1:y2, x1:x2]
        img_overlay_crop = img_overlay[y1o:y2o, x1o:x2o]
        alpha = alpha_mask[y1o:y2o, x1o:x2o, np.newaxis]
        alpha_inv = 1.0 - alpha

        img_crop[:] = alpha * img_overlay_crop + alpha_inv * img_crop

        return img
