import xml.etree.ElementTree as ET
import os
import os.path

from PIL import Image, ImageDraw, ImageFilter

import pywhatkit as kt

class SVGEditor:
    """ Used to edit the raw SGV icon. """

    def __init__(self, filename:str):
        """ Attributes :
                filename -> str : name of the SVG file (WITHOUT THE EXTENSION /!\).
        """
        self.RAW_FILENAME = filename
        self.SVG_FILE_PATH = "./images/svg/"
        self.TMP_FILE_PATH = "./images/tmp/"

        self.SVG_FILENAME = self.SVG_FILE_PATH + filename + ".svg"
        self.SVG_TMP_FILENAME = self.TMP_FILE_PATH + self.RAW_FILENAME + ".svg"

        # Open the SVG file as XML.
        self.__tree = ET.parse(self.SVG_FILENAME)
        self.__root = self.__tree.getroot()


    def resize(self, max_new_width:float, max_new_height:float):
        """ Resize the SVG file by changing the attributes 'width' and 'height' in the SVG file. 
        
            Attributes :
                max_new_width -> float : maximum width of the resized image.
                max_new_height -> float : maximum height of the resized image.
        """
        width, height = self.get_svg_size()

        factor = max_new_width / width
        if height * factor > max_new_height:
            factor = max_new_height / height

        # Edit the XML tree.
        self.__root.set("width", str(width * factor))
        self.__root.set("height", str(height * factor))

        # Change also the viewbox to take into account the border.
        border_size = 3
        x, y, new_width, new_height = -border_size / 2, -border_size / 2, str(width + border_size), str(height + border_size)
        self.__root.set("viewBox", f"{x} {y} {new_width} {new_height}")

        self.__save_tmp_svg()


    def get_svg_size(self):
        """ Get the size of the SVG image. """
        width, height = self.__root.get("viewBox").split()[2:4]
        return float(width), float(height)


    def __save_tmp_svg(self):
        """ Rewrite the XML tree to a new SVG file. """
        ET.register_namespace("", "http://www.w3.org/2000/svg")

        with open(self.SVG_TMP_FILENAME, 'wb') as svg_file:
            self.__tree.write(svg_file)


    def convert_to_png(self):
        """ Convert a SVG file to an output PNG file (Not a temporary file !). """
        return self.__convert_to_png(True)


    def __convert_to_png(self, output:bool = False, resolution:int = 96):
        """ Convert a SVG file to a PNG file.
            Thanks to this amazing person : https://stackoverflow.com/a/62867864

            ---

            Attributes :
                output -> bool : it is an output file or a temporary file ?
                resolution -> int : resolution of the PNG image, 96 seems to keep the appropriate size.
        """
        from wand.api import library
        import wand.color
        import wand.image

        # Create the SVG temporary file if it doesn't exists.
        if not os.path.isfile(self.SVG_TMP_FILENAME):
            self.__save_tmp_svg() 

        with open(self.SVG_TMP_FILENAME, "r") as svg_file:
            with wand.image.Image() as image:
                with wand.color.Color('transparent') as background_color:
                    library.MagickSetBackgroundColor(image.wand, background_color.resource) 
                svg_blob = svg_file.read().encode('utf-8')
                image.read(blob = svg_blob, resolution = resolution)
                png_image = image.make_blob("png32")

        # Decide the folder in which save the image.
        image_png_path = self.TMP_FILE_PATH + self.RAW_FILENAME + ".png" if output else self.TMP_FILE_PATH + self.RAW_FILENAME + ".png"

        with open(image_png_path, "wb") as out:
            out.write(png_image)

        return image_png_path


    def clear(self):
        """ Clear the temporary created file. """
        for filename in os.listdir(self.TMP_FILE_PATH):
            os.remove(self.TMP_FILE_PATH + filename)


    def draw_border(self, color:str = "#FFFFFF"):
        """ Draw a border around the SVG image. 
        
            Attributes :
                color -> str : color of the border.
        """
        current_style = self.__root.get("style")
        style_to_add = f"fill: none;stroke: {color}; stroke-width: 0.2px;"
        new_style = style_to_add if not current_style else current_style + ";" + style_to_add

        self.__root.set("style", new_style)
        self.__save_tmp_svg()
        

    def __get_colors(self, amount:int = 5):
        """ Get the colors from the SVG file in a sorted list of tuples. 
        
            Attributes :
                amount -> str : amount of colors to put in the list.
        """
        tmp_png = self.__convert_to_png()

        # Retrieve the colors and sort the list.
        png_image = Image.open(tmp_png)
        image_pixel_number = png_image.size[0] * png_image.size[1]
        colors = png_image.convert('RGB').getcolors(maxcolors=image_pixel_number)
        sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)

        os.remove(tmp_png)
        return sorted_colors[:amount]


    def get_best_key_color(self):
        """ Get the best color for keyword. """
        colors = self.__get_colors()

        # Remove black and white colors.
        best_color = None
        for color in colors:
            rgb_value = color[1]
            if not rgb_value[0] == rgb_value[1] == rgb_value[2]:
                best_color = color[1]
                break

        # Inverse color.
        best_color = best_color[2], best_color[1], best_color[0]
        return best_color


    def transform_to_ascii(self, color:str = "#FFFFFF"):
        """ Transform the image to an ASCII version. 
        
            Attributes :
                color -> str : color of the border.
        """
        tmp_png = self.__convert_to_png()
        result = kt.image_to_ascii_art(tmp_png, "output")

        # Find the size of the image.
        lines = result.split("\n")
        width, height = len(lines[0]) * 6, len(lines) * 15

        # Transform the text into a transparent image.
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.text((0, 0), result, fill=color)
        img.save(self.TMP_FILE_PATH + self.RAW_FILENAME + "-ascii.png", 'PNG')

        # Delete all created file.
        os.remove(tmp_png)
        os.remove("output.txt")