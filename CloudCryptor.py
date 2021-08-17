import glob
import PySimpleGUI as sg
from PIL import Image, ImageTk
import sys
import secrets
import string
import cryptography
from PIL import Image
import io
from cryptography.fernet import Fernet
import base64


def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new("RGBA", (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def load_image(path, window, key_file):
    try:
#         image = Image.open(path)
        img_enc = open(path, "rb")
        img_enc = img_enc.read()
        
        key = open(key_file, "rb")
        key = key.read()
        f = Fernet(key)
        
        img_dec = f.decrypt(img_enc)
        image_decrypted = Image.open(io.BytesIO(img_dec))
        image = image_decrypted


        aspect_ratio = (window.size[0]/window.size[1])/(image.size[0]/image.size[1])

        if aspect_ratio > 1:
            # vertical
            if image.size[1]>window.size[1]:
                margin_horizontal = int(((image.size[1] * window.size[0] / window.size[1])-image.size[0])/2)+50
                margin_vertical = 0
                image = add_margin(image, margin_vertical, margin_horizontal, margin_vertical, margin_horizontal, (0, 0, 0,0))
                image.thumbnail((window.size[0],window.size[1]-50))
            else:
#                 margin_horizontal = int(((image.size[1] * window.size[0] / window.size[1])-image.size[0])/2)+50
                margin_horizontal = int((window.size[0] - image.size[0])/2)
                margin_vertical = int((window.size[1] - image.size[1])/2)
                image = add_margin(image, margin_vertical, margin_horizontal, margin_vertical, margin_horizontal, (0, 0, 0,0))
                image.thumbnail((window.size[0],window.size[1]))
                
        else:
            # horizontal
            if image.size[0]>window.size[0]:
                margin_horizontal = 0
                margin_vertical = int(((image.size[0] * window.size[1] / window.size[0])-image.size[1])/2)
                image = add_margin(image, margin_vertical, margin_horizontal, margin_vertical, margin_horizontal, (0, 0, 0,0))
                image.thumbnail((window.size[0],window.size[1]))
            else:
                margin_horizontal = int((window.size[0] - image.size[0])/2)
                margin_vertical = int((window.size[1] - image.size[1])/2)
                image = add_margin(image, margin_vertical, margin_horizontal, margin_vertical, margin_horizontal, (0, 0, 0,0))
                image.thumbnail((window.size[0],window.size[1]))

        photo_img = ImageTk.PhotoImage(image)
        window["image"].update(data=photo_img)
        return image_decrypted
    except:
        print(f"Unable to open {path}!")
        
def login_form():
    sg.theme('DarkBlue') 
    layout = [
        [
            sg.Text("Authentication Key"),
            sg.Input(size=(25, 1), enable_events=True, key="file"),
            sg.FileBrowse(file_types=(("Key Files", "*.key"),)),
            sg.Button("Ok")
        ]
    ]
    window = sg.Window('Encrypted Image Viewer', layout, resizable=True)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            sys.exit()
        if event == "file":
            key_file = values["file"]
            print(key_file)
        if event == "Ok" and key_file:
            window.close()
            return key_file
        
def encryption_key_form():
    sg.theme('DarkBlue') 
    layout = [
        [
            sg.Text("Encryption Key"),
            sg.Input(size=(100, 1), enable_events=True, key="file"),
            sg.FileBrowse(file_types=(("Key Files", "*.key"),)),
            sg.Button("Ok"),
            sg.FileSaveAs("Generate Key",  file_types=(("Key Files", "*.key"),), target = "file")
        ]
    ]
    window = sg.Window('Encrypted Image Viewer', layout, resizable=True)
    while True:
        event, values = window.read()
        print(event)
        if event == "Exit" or event == sg.WIN_CLOSED:
            sys.exit()
        if event == "file":
            key_file = values["file"]
            print(values)
            print(key_file)
        if event == "Ok" and key_file:
            window.close()
            return key_file
        if values["Generate Key"]:
            window.close()
            key = secrets.token_bytes(32)
            key = base64.urlsafe_b64encode(key)
            with open(values["Generate Key"], 'wb') as f:
                f.write(key)
            return key_file
        
        
def encryption_form():
    key_file = encryption_key_form()
    sg.theme('DarkBlue') 
    layout = [
        [
            sg.Text("Image Files"),
            sg.Input(size=(50, 1), enable_events=True, key="file"),
            sg.FilesBrowse(file_types=(("Images", "*.png"),("Images", "*.jpg"), ("Images", "*.jpeg"), ("Images", "*.webp"), ("Images", "*.jfif") )),
            sg.Button("Encrypt"),
        ]
    ]
    window = sg.Window('Encrypt Images', layout, resizable=True)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            sys.exit()
        if event == "file":
            img_list = values["file"].split(';')
#             if images:
#                 image_decrypted = load_image(images[0], window, key_file)
        if event == "Encrypt" and key_file and img_list:
#             window.close()
            key = open(key_file, "rb")
            key = key.read()
            f = Fernet(key)
            
            for img_name in img_list:
                img = Image.open(img_name, mode='r')
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()

                img_enc = f.encrypt(img_bytes)

                filename = img_name[:-img_name[::-1].index(".")-1]+ ".enc"

                with open(filename, 'wb') as file:
                    file.write(img_enc)
            answer = sg.popup_yes_no('Done! Any more files?')
            if answer == "Yes":
                continue
            else:
                window.close()
                selection_form()
    
    
def selection_form():
    sg.theme('DarkBlue') 
    layout = [
        [
            sg.Button("Encrypt Files"),
            sg.Button("View Images")
        ]
    ]
    
    window = sg.Window('Encrypted Image Viewer', layout)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
#             break
            sys.exit()
        if event == "Encrypt Files":
            window.close()
            encryption_form()
            
        if event == "View Images":
            window.close()
            image_viewer()
    
    
def image_viewer():
    key_file = login_form()
    sg.theme('DarkBlue') 
    layout = [
        [
            sg.Text("Image File"),
            sg.Input(size=(25, 1), enable_events=True, key="file"),
            sg.FilesBrowse(file_types=(("Encrypted Images", "*.enc"),)),
            sg.Button("Prev"),
            sg.Button("Next"),
            sg.Button("Export")
        ],
        [sg.Image(key="image")]
    ]

    window = sg.Window('Encrypted Image Viewer', layout, resizable=True).Finalize()
    window.Maximize()
    images = []
    location = 0
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
#             break
            sys.exit()
        if event == "file":
            images = values["file"].split(';')
            if images:
                image_decrypted = load_image(images[0], window, key_file)
        if event == "Next" and images:
            if location == len(images) - 1:
                location = 0
            else:
                location += 1
            image_decrypted = load_image(images[location], window, key_file)
        if event == "Prev" and images:
            if location == 0:
                location = len(images) - 1
            else:
                location -= 1
            image_decrypted = load_image(images[location], window, key_file)
            
        if event == "Export" and images:
            image_decrypted.show()
#             load_image(images[location], window)
    window.close()
    
        
def main():
    selection_form()
    
    
if __name__ == "__main__":
    main()