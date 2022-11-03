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
    AQP_CONFIGS = ['enable_bitmapscan',
              'enable_hashagg',
              'enable_hashjoin',
              'enable_indexscan',
              'enable_indexonlyscan',
              'enable_material',
              'enable_mergejoin',
              'enable_nestloop',
              'enable_seqscan',
              'enable_sort',
              'enable_tidscan']

    AQP_CONFIGS_2 = {'enable_bitmapscan':'True',
              'enable_hashagg':'True',
              'enable_hashjoin':'True',
              'enable_indexscan':'True',
              'enable_indexonlyscan':'True',
              'enable_material':'True',
              'enable_mergejoin':'True',
              'enable_nestloop':'True',
              'enable_seqscan':'True',
              'enable_sort':'True',
              'enable_tidscan':'True'}

    # AQP_CHECKBOXES=['bitmapscan','hashagg','hashjoin','indexscan','indexonlyscan','material','mergejoin','nestloop','seqscan','sort','tidscan']

    sg.theme('DarkTeal12')

    col1 = [[
    sg.Text(size=(30, 4), font=('Helvetica', 12), justification='left', key='-DISPLAY_SELECT-')], 
    [sg.Text(size=(30, 4), font=('Helvetica', 12), justification='left', key='-DISPLAY_FROM-')],
    [sg.Text(size=(30, 4), font=('Helvetica', 12), justification='left', key='-DISPLAY_WHERE-')]]
    col2 = [[
    sg.Multiline(size=(30, 5), key='-EXPLAIN_SELECT-', justification='left')], 
    [sg.Multiline(size=(30, 5), key='-EXPLAIN_FROM-', justification='left')],
    [sg.Multiline(size=(30, 5), key='-EXPLAIN_WHERE-', justification='left')]]
    col3 = [[
    sg.Multiline(size=(30, 5), key='-EXPLAIN_SELECT_AQP-', justification='left')], 
    [sg.Multiline(size=(30, 5), key='-EXPLAIN_FROM_AQP-', justification='left')],
    [sg.Multiline(size=(30, 5), key='-EXPLAIN_WHERE_AQP-', justification='left')]]
    col4 = [[sg.Multiline(size=(30, 10), key='-EXPLANATION-', justification='left')]]

    layout = [
        [
            # [sg.Image('logo.png', size=(50,50))],

            [
            sg.Frame('Please enter your SQL query: ', [[
            sg.Text('SELECT Statement', font=('Helvetica', 14), justification='left', size =(15, 1)), sg.InputText(key='-SELECT-', font=('Helvetica', 14))],
            [sg.Text('FROM Statement', font=('Helvetica', 14), justification='left', size =(15, 1)), sg.InputText(key='-FROM-', font=('Helvetica', 14))],
            [sg.Text('WHERE Statement', font=('Helvetica', 14), justification='left', size =(15, 1)), sg.InputText(key='-WHERE-', font=('Helvetica', 14))],
            [sg.Button("Generate QEP", font=('Helvetica', 14), button_color=('Black', 'LightBlue'))]]),
            # ],

            # [
            sg.Frame('AQP options: ', [[
            sg.Checkbox('bitmapscan', key='enable_bitmapscan', enable_events=True, default=True), sg.Checkbox('hashagg', key='enable_hashagg', enable_events=True, default=True), sg.Checkbox('hashjoin', key='enable_hashjoin', enable_events=True, default=True), sg.Checkbox('indexscan', key='enable_indexscan', enable_events=True, default=True)],
            [sg.Checkbox('indexonlyscan', key='enable_indexonlyscan', enable_events=True, default=True), sg.Checkbox('material', key='enable_material', enable_events=True, default=True), sg.Checkbox('mergejoin', key='enable_mergejoin', enable_events=True, default=True), sg.Checkbox('nestloop', key='enable_nestloop', enable_events=True, default=True)],
            [sg.Checkbox('seqscan', key='enable_seqscan', enable_events=True, default=True), sg.Checkbox('sort', key='enable_sort', enable_events=True, default=True), sg.Checkbox('tidscan', key='enable_tidscan', enable_events=True, default=True)],
            [sg.Button("Generate AQP", font=('Helvetica', 14), button_color=('Black', 'LightBlue'), disabled=True)]])
            ],

            # [sg.Text('Please enter your SQL query\n', font=('Helvetica', 20))],
            # [
            # sg.Text('SELECT Statement', font=('Helvetica', 14), justification='left', size =(15, 1)), sg.InputText(key='-SELECT-', font=('Helvetica', 14)),
            # sg.Checkbox('bitmapscan', default=True),sg.Checkbox('hashagg', default=True),sg.Checkbox('hashjoin', default=True),sg.Checkbox('indexscan', default=True)],
            # [
            # sg.Text('FROM Statement', font=('Helvetica', 14), justification='left', size =(15, 1)), sg.InputText(key='-FROM-', font=('Helvetica', 14)),
            # sg.Checkbox('indexonlyscan', default=True),sg.Checkbox('material', default=True),sg.Checkbox('mergejoin', default=True),sg.Checkbox('nestloop', default=True)],
            # [
            # sg.Text('WHERE Statement', font=('Helvetica', 14), justification='left', size =(15, 1)), sg.InputText(key='-WHERE-', font=('Helvetica', 14)),
            # sg.Checkbox('seqscan', default=True),sg.Checkbox('sort', default=True),sg.Checkbox('tidscan', default=True)],
            # [sg.Text('')],
            # [sg.Button("Generate QEP", font=('Helvetica', 14), button_color=('Black', 'LightBlue')), sg.Button("Close", font=('Helvetica', 14), button_color=('Black', 'LightBlue'))],
            # [sg.Text('')],
            # [sg.Text('')],
            # [sg.Text('')],
            # [sg.Text('Output:', font=('Helvetica', 20))],
            # [sg.Text('')],
            
            # [sg.Text(font=('Helvetica', 14), key='-DISPLAY_MSG-')],

            [

            sg.Frame('QEP chosen by DBMS: ', [
            [sg.Column(col2)]]),

            sg.Frame('Query entered: ', [
            [sg.Column(col1)]]),

            sg.Frame('Your custom AQP: ', [
            [sg.Column(col3)]]),

            sg.Frame('Explanation: ', [
            [sg.Column(col4)]]),
            ],

            [
            sg.Frame('QEP execution sequence: ', [
            [sg.Text(size=(35, 10), font=('Helvetica', 12), justification='left', key='-QEP_TREE-')]]),
            sg.Text('                                            '), # this is just to add padding
            sg.VSeperator(),
            sg.Text('                                            '), # this is just to add padding
            sg.Frame('AQP execution sequence: ', [
            [sg.Text(size=(35, 10), font=('Helvetica', 12), justification='left', key='-AQP_TREE-')]]),
            ],

            # [sg.Column(col1),sg.Column(col2),sg.Column(col3),sg.Column(col4)],
            [sg.Button("New Query", font=('Helvetica', 14), button_color=('Black', 'LightBlue')),sg.Button("Close", font=('Helvetica', 14), button_color=('Black', 'LightBlue'))],
            
            [
            # sg.Text(size=(30, 2), font=('Helvetica', 12), justification='left', key='-DISPLAY_SELECT-'), 
            # sg.Multiline(size=(30, 5), key='-EXPLAIN_SELECT-', justification='left'),
            # sg.Multiline(size=(30, 5), key='-EXPLAIN_SELECT_AQP-', justification='left')
            ],
            [
            # sg.Text(size=(30, 2), font=('Helvetica', 12), justification='left', key='-DISPLAY_FROM-'),
            # sg.Multiline(size=(30, 5), key='-EXPLAIN_FROM-', justification='left'),
            # sg.Multiline(size=(30, 5), key='-EXPLAIN_FROM_AQP-', justification='left'),
            # sg.Multiline(size=(30, 15), key='-EXPLANATION-', justification='left')
            ],
            [
            # sg.Text(size=(30, 2), font=('Helvetica', 12), justification='left', key='-DISPLAY_WHERE-'),
            # sg.Multiline(size=(30, 5), key='-EXPLAIN_WHERE-', justification='left'),
            # sg.Multiline(size=(30, 5), key='-EXPLAIN_WHERE_AQP-', justification='left')
            ],
            # [sg.Text(size=(100, 20), font=('Helvetica', 14), justification='left', key='-RESULTS-')],
            # [sg.Text('')],
            # [sg.Text(size=(100, 100), font=('Helvetica', 14), justification='left', key='-OUTPUT-')]
        ]
    ]

    window = sg.Window("Query Plan Explainer", layout, size=(1100, 800))

    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Generate QEP":
            window['Generate QEP'].update(disabled=True)
            window['-SELECT-'].update(disabled=True)
            window['-FROM-'].update(disabled=True)
            window['-WHERE-'].update(disabled=True)
            window['Generate AQP'].update(disabled=False)
            # for event in AQP_CONFIGS:
            #     values[event] = True

            select_text = values['-SELECT-']
            from_text = values['-FROM-']
            where_text = values['-WHERE-']

            # FOR DEV ONLY
            # select_text = 'SELECT AVG(ps_supplycost)' 
            # from_text = 'FROM partsupp P, supplier S'
            # where_text = 'WHERE P.ps_suppkey = S.s_suppkey'

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

            # window['-DISPLAY_MSG-'].update('Query:                                             QEP chosen by DBMS:          Your custom AQP:')
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
            window['-QEP_TREE-'].update('QEP_TREE')

        elif event == "Generate AQP":
            select_text = values['-SELECT-']
            from_text = values['-FROM-']
            where_text = values['-WHERE-']

            # FOR DEV ONLY
            # select_text = 'SELECT AVG(ps_supplycost)' 
            # from_text = 'FROM partsupp P, supplier S'
            # where_text = 'WHERE P.ps_suppkey = S.s_suppkey'

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

            window['-DISPLAY_SELECT-'].update(select_text)
            window['-DISPLAY_FROM-'].update(from_text)
            window['-DISPLAY_WHERE-'].update(where_text)
            print(select_text, from_text, where_text)

            aqp_select_results, aqp_from_results, aqp_where_results = annotations.aqp_test_explain(select_text, from_text, where_text, AQP_CONFIGS_2)

            window['-EXPLAIN_SELECT_AQP-'].update(aqp_select_results)
            window['-EXPLAIN_FROM_AQP-'].update(aqp_from_results)
            window['-EXPLAIN_WHERE_AQP-'].update(aqp_where_results)
            window['-AQP_TREE-'].update('AQP_TREE')
            window['-EXPLANATION-'].update('EXPLANATION')

        elif event == "New Query":
            window['Generate AQP'].update(disabled=True)
            window['Generate QEP'].update(disabled=False)
            window['-SELECT-'].update(disabled=False)
            window['-FROM-'].update(disabled=False)
            window['-WHERE-'].update(disabled=False)

        elif event in AQP_CONFIGS:
            print(event + " OVER HERE ")
            if values[event] == False:
                print("HEREEEEEEEE")
                AQP_CONFIGS_2[event] = 'False'
                # annotations.disable_config(event)
            else:
                AQP_CONFIGS_2[event] = 'True'

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
