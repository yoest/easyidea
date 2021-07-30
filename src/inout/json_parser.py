import json

class JSONInputParser:
    """ Used to get data from the input JSON. """

    def __init__(self):
        self.INPUT_PATH = "./data/input.json"

        with open(self.INPUT_PATH) as json_file:
            self.DATA = json.load(json_file)
        

    def get_data(self, index:int):
        """ Get data by index.

            Attributes :
                index -> int : index of the data to get.
        """
        for value in self.DATA:
            if value['index'] == index:
                return value
    
        # Raise an error if the data doesn't exist in the JSON.
        raise Exception("There is no data for this index.")



class JSONOutputParser:
    """ Used to put data in the output JSON. """

    def __init__(self, index:int):
        """ Attributes :
                index -> int : index of the data to put in the JSON (or edit).
        """
        self.OUTPUT_PATH = "./data/output.json"
        self.INDEX = index

        with open(self.OUTPUT_PATH) as json_file:
            self.DATA = json.load(json_file)


    def add_font(self, font):
        """ Add a font to the output. """
        self.font = font


    def add_list_fonts_index(self, list_fonts_index):
        """ Add a list of font index to the output. """
        self.list_fonts_index = list_fonts_index


    def add_type_writing(self, type_writing):
        """ Set the type writing to the output. """
        self.type_writing = type_writing

    
    def save(self):
        """ Save the design to the JSON output file. """
        data = {
            "index": self.INDEX,
            "font": self.font,
            "list_fonts_index": self.list_fonts_index,
            "type_writing": self.type_writing
        }

        # Append the new data to the current data.
        with open(self.OUTPUT_PATH) as json_file:
            current_data = json.load(json_file)
        self.__remove_if_exists(current_data)
        current_data.append(data)

        # Write every data to the file.
        with open(self.OUTPUT_PATH, "w") as json_file:
            json_file.write(json.dumps(current_data, indent=4))


    def __remove_if_exists(self, data:list):
        """ Remove the data if it already exists. 
        
            Attributes :
                data -> list : JSON data list.
        """
        for value in data:
            if value["index"] == self.INDEX:
                data.remove(value)
                return


    def get_data(self):
        """ Get data associated with the index. """
        for value in self.DATA:
            if value['index'] == self.INDEX:
                return value
    
        # Raise an error if the data doesn't exist in the JSON.
        raise Exception("There is no data for this index.")