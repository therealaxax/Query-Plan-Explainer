import PySimpleGUI as sg
import os.path
import io

sg.theme('DarkTeal12')

# Function displays GUI, this is called by project.py
def display():
    layout = [
        [
            # [sg.Image('logo.png', size=(50,50))],
            [sg.Text('Please enter your SQL query')],
            [sg.Text('SELECT Statement', size =(25, 1)), sg.InputText(key='-SELECT-')],
            [sg.Text('FROM Statement', size =(25, 1)), sg.InputText(key='-FROM-')],
            [sg.Text('WHERE Statement', size =(25, 1)), sg.InputText(key='-WHERE-')],
            [sg.Button("Send", button_color=('Black', 'LightBlue'))],
            [sg.Text('')],
            [sg.Text('')],
            [sg.Text('')],
            [sg.Text('The statement is:')],
            [sg.Text(size=(50, 2), font=('Helvetica', 20), justification='left', key='-DISPLAY_SELECT-')],
            [sg.Text(size=(50, 2), font=('Helvetica', 20), justification='left', key='-DISPLAY_FROM-')],
            [sg.Text(size=(50, 2), font=('Helvetica', 20), justification='left', key='-DISPLAY_WHERE-')]
        ]
    ]

    window = sg.Window("Query Plan Explainer", layout, size=(500, 500))

    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Send":
            select_text = values['-SELECT-']
            from_text = values['-FROM-']
            where_text = values['-WHERE-']
            print(select_text, from_text, where_text)
            
            # TODO
            # This is the part to call annotation.py with the parameters of the user input SQL text
            # And get back the return values from annotations.py

            # Use returned values to label the frontend

            window['-DISPLAY_SELECT-'].update(select_text)
            window['-DISPLAY_FROM-'].update(from_text)
            window['-DISPLAY_WHERE-'].update(where_text)
        
    
    
    window.close()
