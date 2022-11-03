# from __future__ import annotations
import PySimpleGUI as sg
import os.path
import io

import annotations



# Variable keeps track of 

# This function is for the user to enter the db password
def set_password():
    dbpassword = input("Please enter your password to access PostGreSQL: ")
    annotations.set_password(dbpassword)

# Function displays GUI, this is called by project.py
def display():
    sg.theme('DarkTeal12')

    layout = [
        [
            # [sg.Image('logo.png', size=(50,50))],
            [sg.Text('Please enter your SQL query\n', font=('Helvetica', 20))],
            [sg.Text('SELECT Statement', font=('Helvetica', 14), justification='left', size =(25, 1)), sg.InputText(key='-SELECT-', font=('Helvetica', 14))],
            [sg.Text('FROM Statement', font=('Helvetica', 14), justification='left', size =(25, 1)), sg.InputText(key='-FROM-', font=('Helvetica', 14))],
            [sg.Text('WHERE Statement', font=('Helvetica', 14), justification='left', size =(25, 1)), sg.InputText(key='-WHERE-', font=('Helvetica', 14))],
            [sg.Text('')],
            [sg.Button("Send", font=('Helvetica', 14), button_color=('Black', 'LightBlue')), sg.Button("Close", font=('Helvetica', 14), button_color=('Black', 'LightBlue'))],
            [sg.Text('')],
            [sg.Text('')],
            [sg.Text('')],
            [sg.Text('Output:', font=('Helvetica', 20))],
            [sg.Text('')],
            [sg.Text(font=('Helvetica', 14), key='-DISPLAY_MSG-')],
            [sg.Text(size=(30, 2), font=('Helvetica', 18), justification='left', key='-DISPLAY_SELECT-'), sg.Multiline(size=(60, 5), key='-EXPLAIN_SELECT-', justification='left')],
            [sg.Text(size=(30, 2), font=('Helvetica', 18), justification='left', key='-DISPLAY_FROM-'), sg.Multiline(size=(60, 5), key='-EXPLAIN_FROM-', justification='left')],
            [sg.Text(size=(30, 2), font=('Helvetica', 18), justification='left', key='-DISPLAY_WHERE-'), sg.Multiline(size=(60, 5), key='-EXPLAIN_WHERE-', justification='left')],
            [sg.Text(size=(100, 20), font=('Helvetica', 14), justification='left', key='-RESULTS-')],
            [sg.Text('')],
            [sg.Text(size=(100, 100), font=('Helvetica', 14), justification='left', key='-OUTPUT-')]
        ]
    ]

    window = sg.Window("Query Plan Explainer", layout, size=(1000, 800))

    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Send":
            select_text = values['-SELECT-']
            from_text = values['-FROM-']
            where_text = values['-WHERE-']

            # FOR DEV ONLY
            select_text = 'SELECT AVG(ps_supplycost)' 
            from_text = 'FROM partsupp P, supplier S'
            where_text = 'WHERE P.ps_suppkey = S.s_suppkey'

            # select_text = 'SELECT *'
            # from_text = 'FROM region'

            # select_text = 'SELECT COUNT(r_name)'
            # from_text = 'FROM region'

            # select_text = 'SELECT COUNT(r_name)'
            # from_text = 'FROM region LIMIT 3'

            # select_text = 'SELECT c_acctbal'
            # from_text = 'FROM customer'
            # where_text = 'WHERE c_acctbal > (SELECT AVG(c_acctbal) FROM customer)'
            # THIS IS FOR DEVELOPMENT 

            window['-DISPLAY_MSG-'].update('The query to explain is:                                                 Explanation:')
            window['-DISPLAY_SELECT-'].update(select_text)
            window['-DISPLAY_FROM-'].update(from_text)
            window['-DISPLAY_WHERE-'].update(where_text)
            print(select_text, from_text, where_text)
            
            # This is the part to call annotation.py with the parameters of the user input SQL text
            # And get back the return values from annotations.py
            # raw_data, output = annotations.explain(select_text, from_text, where_text)

            select_results, from_results, where_results = annotations.test_explain(select_text, from_text, where_text)
 

            # Use returned values to label the frontend
            # window['-RESULTS-'].update(results)

            # Update each of the 3 text boxes
            window['-EXPLAIN_SELECT-'].update(select_results)
            window['-EXPLAIN_FROM-'].update(from_results)
            window['-EXPLAIN_WHERE-'].update(where_results)



        elif event == "Close":
            break
        
    
    window.close()

def error_message():
    sg.theme('LightBlue')
    layout = [
        [
            [sg.Text('There is an error. Please check your SQL query and try again.\n', font=('Helvetica', 14), justification='center')],
            [sg.Button("OK", font=('Helvetica', 14), button_color=('Black', 'LightBlue'))],
        ]
    ]
    window = sg.Window("Error Message", layout, size=(500, 80))
    while True:
        event, _ = window.read()
        if event == "OK" or event == sg.WIN_CLOSED:
            break
