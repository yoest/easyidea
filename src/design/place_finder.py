import numpy as np
import math

class PlaceFinder:
    """ Used to find a place where to put an image into a design. """

    def __init__(self, text_positions:list, design_size:tuple, image_size:tuple, has_to_be_centered:bool = False, reduce_ratio:int = 100):
        """ Attributes :
                text_positions -> list : list of 4-tuple that represents each text positions.
                design_size -> 2-tuple : size of the design.
                image_size -> 2-tuple : size of the image to put in the design.
                reduce_ratio -> int : ratio to help reduce faster the size of the design (performance issue).
        """
        self.text_positions = text_positions
        self.design_size = design_size
        self.has_to_be_centered = has_to_be_centered
        self.reduce_ratio = reduce_ratio
        self.step = max(1, self.reduce_ratio // 10)

        # Find the ratio of the image.
        if image_size[0] > image_size[1]:
            self.ratio = 1, image_size[1] / image_size[0]
            self.width, self.height = tuple([self.design_size[0] * i for i in self.ratio])
        else:
            self.ratio = image_size[0] / image_size[1], 1
            self.width, self.height = tuple([self.design_size[1] * i for i in self.ratio])


    def find_best_place(self):
        """ Find the best place where to put the image.
            Return a 4-tuple representing the x, y, width and height of the best position.
         """
        while self.width > 0 and self.height > 0:
            w, h = math.ceil(self.width), math.ceil(self.height)
            result = self.__find_overlap_by_size(w, h)

            if result != None:
                return self.__center_result(result)

            # Prepare the next iteration
            self.width -= (self.ratio[0] * self.reduce_ratio)
            self.height -= (self.ratio[1] * self.reduce_ratio)

        return False


    def __center_result(self, result:tuple):
        """ Center the received result.
        
            Attributes :
                result -> tuple : 4-tuple representing the x, y, width and height of the best position.
        """
        if self.has_to_be_centered:
            x = (self.design_size[0] - result[2]) // 2
            result = x, result[1], result[2], result[3]
        return result


    def __find_overlap_by_size(self, w:int, h:int):
        """ See if a rectangle can be put into the design.
        
            Attributes :
                w -> int : width of the rectangle to place.
                h -> int : height of the rectangle to place.
        """
        for x in range(0, self.design_size[0] - w + 1, self.step):
            for y in range(0, self.design_size[1] - h + 1, self.step):
                if self.__can_be_placed(x, y, w, h):
                    return x, y, w, h

        return None
                

    def __can_be_placed(self, x:int, y:int, w:int, h:int):
        """ See if a rectangle can be put at this position. 
        
            Attributes :
                x -> int : x position where to put the rectangle.
                y -> int : y position where to put the rectangle.
                w -> int : width of the rectangle to place.
                h -> int : height of the rectangle to place.
        """
        for text_position in self.text_positions:
            check_left = x + w <= text_position[0]
            check_right = x >= text_position[0] + text_position[2]
            check_top = y + h <= text_position[1]
            check_bottom = y >= text_position[1] + text_position[3]

            if not (check_left or check_right or check_top or check_bottom):
                return False
        return True


    def print_test(self, best_places:tuple):
        """ Print the image representation to a text file for testing. 
        
            Attributes :
                best_places -> 4-tuple : best places positions.
        """
        self.__build_matrix(best_places)
        result = ""
        reverse_matrix = np.transpose(self.matrix)

        # Draw the 'image'.
        for x in reverse_matrix:
            for y in x:
                result += str(y) + " "
            result += "\n"
        
        # Write the result to a file.
        with open("test.txt", "w") as file:
            file.write(result)


    def __build_matrix(self, best_places:tuple):
        """ Build the matrix representing the image.

            Attributes :
                best_places -> 4-tuple : best places positions.
        """
        self.matrix = []

        for x in range(self.design_size[0]):
            self.column = []

            for y in range(self.design_size[1]):
                is_on_it = False

                # Add the text positions to the matrix.
                for text_x, text_y, text_width, text_height in self.text_positions:
                    check_x = text_x <= x < text_x + text_width
                    check_y = text_y <= y < text_y + text_height

                    if check_x and check_y:
                        is_on_it = True

                self.column.append(1 if is_on_it else 0)
            self.matrix.append(self.column)

        # Add the best place.
        for x in range(best_places[0], best_places[0] + best_places[2]):
            for y in range(best_places[1], best_places[1] + best_places[3]):
                self.matrix[x][y] = 2
