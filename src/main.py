from design.svg_editor import SVGEditor
from design.place_finder import PlaceFinder
from design.design_handler import DesignHandler

from inout.json_parser import JSONOutputParser

import os
import time

import printer as pr

def main():
    # What do you want to do ?
    what_to_do = input("Creating or re-creating ? ")

    if what_to_do.lower() == "creating":
        create()
    else:
        index = int(input("Which is the index of the design to re-create ? "))
        recreate(index)
    
    # Clear everyhting we have created.
    clear_waiting_folder()
    os.remove("pywhatkit_dbs.txt") # Bug of 'import'.


def create():
    """ Create a design. """
    list_of_results = []
    start_time = time.time()

    # Creation questions.
    number_of_templates = int(input("How many templates do you want to generate ? "))
    index = int(input("Which design index do you want to create ? "))

    print("\n-------- " + pr.bold_print("STARTING CREATION") + " --------")

    # Generate the templates.
    for i in range(number_of_templates):
        print(f"- Template {i} : {pr.blue_print('[STARTED]')}")
        creator = DesignHandler(index, template_number=i)
        result = creator.build()

        list_of_results.append(result)
        load_process = int((i + 1) / number_of_templates * 100)
        print(f"+ Template {i} : " + pr.green_print('[FINISHED - ' + str(load_process) + "%]"))

    end_time = time.time()
    timer = format_time(start_time, end_time)
    print(f"\n----- {pr.green_print('[CREATION FINISHED]')} {pr.bold_print(str(timer))} -----")

    # Ask the user which one to keep.
    template_to_keep = input("Which one do you want to keep ? ")

    if template_to_keep.lower() == "none":
        # Restart ?
        try_again = input("Do you want to try another creation ? (Y/N) : ")
        if try_again.lower() == "y":
            main()
    else:
        list_of_results[int(template_to_keep)].save()

        print("\n-------- " + pr.bold_print("STARTING RE-CREATION") + " --------")

        recreate(index)


def recreate(index):
    """ Re-create a design. """
    for color in ["white", "black"]:
        print(f"- Recreating {color} design : {pr.blue_print('[STARTED]')}")
        creator = DesignHandler(index, is_recreating=True, color=color)
        creator.build()
        print(f"+ Recreating {color} design : {pr.green_print('[FINISHED]')}")


def clear_waiting_folder():
    """ Clear all the files in the waiting folder. """
    tmp_folder_path = "./images/waiting/"
    for filename in os.listdir(tmp_folder_path):
        os.remove(tmp_folder_path+ filename)


def format_time(start_time:float, end_time:float):
    """ Format a time to be readable by human. 
    
        Attributes :
            start_time -> float : start time of the timer.
            end_time -> float : end time of the timer.
    """
    real_time = int(end_time - start_time)

    minutes = real_time // 60
    seconds = real_time % 60
    return f"Time : {minutes}:{seconds}"

if __name__ == '__main__':
    main()
    