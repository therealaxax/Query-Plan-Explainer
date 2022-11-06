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

    sg.theme('Reddit')

    qep_col1 = [
        [sg.Text('QEP chosen by DBMS:', font=('Helvetica', 16))],
        [sg.Multiline(size=(40, 15), key='-QEP_TREE-', justification='left', font=('Helvetica', 12))],
    ]

    qep_col2 = [
        [sg.Text('QEP detailed steps:', font=('Helvetica', 16))],
        [sg.Multiline(size=(60, 15), key='-QEP_STEPS-', justification='left', font=('Helvetica', 12))],
    ]

    qep_main = [
        [sg.Text('Please enter your SQL query\n', font=('Helvetica', 20), key='-ERROR_MESSAGE-')],
        [sg.Text('SELECT Statement', font=('Helvetica', 14), size =(25, 1)), sg.InputText(key='-SELECT-', font=('Helvetica', 14))],
        [sg.Text('')],
        [sg.Text('FROM Statement', font=('Helvetica', 14), size =(25, 1)), sg.InputText(key='-FROM-', font=('Helvetica', 14))],
        [sg.Text('')],
        [sg.Text('WHERE Statement', font=('Helvetica', 14), size =(25, 1)), sg.InputText(key='-WHERE-', font=('Helvetica', 14))],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Button("Generate QEP", font=('Helvetica', 14), button_color=('Black', 'LightBlue')), sg.Button("Reset", font=('Helvetica', 14), button_color=('Black', 'LightBlue'))],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Column(qep_col1), sg.Column(qep_col2)]

    ]


    aqp_col1 = [
        [sg.Text('AQP chosen by DBMS:', font=('Helvetica', 16))],
        [sg.Multiline(size=(40, 15), key='-AQP_TREE-', justification='left', font=('Helvetica', 12))],
    ]

    aqp_col2 = [
        [sg.Text('AQP detailed steps:', font=('Helvetica', 16))],
        [sg.Multiline(size=(60, 15), key='-AQP_STEPS-', justification='left', font=('Helvetica', 12))],
    ]

    aqp_main = [
        [sg.Text('Please select AQP by restricting operations that DBMS considers\n', font=('Helvetica', 20))],
        [sg.Checkbox('bitmapscan', font=('Helvetica', 14), key='enable_bitmapscan', enable_events=True, default=True), sg.Checkbox('hashagg', font=('Helvetica', 14), key='enable_hashagg', enable_events=True, default=True), sg.Checkbox('hashjoin', key='enable_hashjoin', font=('Helvetica', 14), enable_events=True, default=True)],
        [sg.Checkbox('indexscan', font=('Helvetica', 14), key='enable_indexscan', enable_events=True, default=True), sg.Checkbox('indexonlyscan', font=('Helvetica', 14), key='enable_indexonlyscan', enable_events=True, default=True)],
        [sg.Checkbox('material', font=('Helvetica', 14), key='enable_material', enable_events=True, default=True), sg.Checkbox('mergejoin', font=('Helvetica', 14), key='enable_mergejoin', enable_events=True, default=True)],
        [sg.Checkbox('nestloop', font=('Helvetica', 14), key='enable_nestloop', enable_events=True, default=True), sg.Checkbox('seqscan', font=('Helvetica', 14), key='enable_seqscan', enable_events=True, default=True)],
        [sg.Checkbox('sort', font=('Helvetica', 14), key='enable_sort', enable_events=True, default=True), sg.Checkbox('tidscan', font=('Helvetica', 14), key='enable_tidscan', enable_events=True, default=True)],
        [sg.Text('')],
        [sg.Button("Generate AQP", font=('Helvetica', 14), button_color=('Black', 'LightBlue'), disabled=True)],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Column(aqp_col1), sg.Column(aqp_col2)]

    ]



    layout = [
        [sg.Column(qep_main),sg.Column(aqp_main)],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('                  Explanation of differences', font=('Helvetica', 20))],
        [sg.Text('                             '), sg.Multiline(size=(200, 15), key='-EXPLANATION-', justification='l', font=('Helvetica', 14))],
    ]


    window = sg.Window("Query Plan Explainer", layout, size=(1600, 800))

    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        elif event == "Generate QEP":
            

            # Read user inputs
            select_text = values['-SELECT-']
            from_text = values['-FROM-']
            where_text = values['-WHERE-']

            print(select_text, from_text, where_text)

            try:
                qep_results, total_cost, tree = annotations.test_explain(select_text, from_text, where_text)
                window['-ERROR_MESSAGE-'].update("Please enter your SQL query")
            except:
                window['-ERROR_MESSAGE-'].update("The SQL Query might be wrong. Please try again!")
                continue
            
            window['Generate QEP'].update(disabled=True)
            window['-SELECT-'].update(disabled=True)
            window['-FROM-'].update(disabled=True)
            window['-WHERE-'].update(disabled=True)
            window['Generate AQP'].update(disabled=False)

            window['-QEP_STEPS-'].update(qep_results + "\n\n\n" + "Total Cost of plan: " + str(total_cost))
            window['-QEP_TREE-'].update(tree)


        elif event == "Generate AQP":
            select_text = values['-SELECT-']
            from_text = values['-FROM-']
            where_text = values['-WHERE-']

            print(select_text, from_text, where_text)

            aqp_results, total_cost, tree = annotations.aqp_test_explain(select_text, from_text, where_text, AQP_CONFIGS_2)

            # If AQP_CONFIGS_2 is all true, explanation msg 
            print(AQP_CONFIGS_2.values())
            if "False" in AQP_CONFIGS_2.values():
                # Generate explanation
                explanation = annotations.explanation(qep_results, aqp_results, AQP_CONFIGS_2) # list
                explanation_text = "\n\n".join(explanation) # turn list into text, split each element by newline
                window['-EXPLANATION-'].update(explanation_text)
            else:
                window['-EXPLANATION-'].update("QEP is the same as AQP because no operator restrictions were selected.")
 
            window['-AQP_STEPS-'].update(aqp_results + "\n\n\n" + "Total Cost of plan: " + str(total_cost))
            window['-AQP_TREE-'].update(tree)

        elif event == "Reset":
            window['Generate AQP'].update(disabled=True)
            window['Generate QEP'].update(disabled=False)
            window['-SELECT-'].update(disabled=False)
            window['-FROM-'].update(disabled=False)
            window['-WHERE-'].update(disabled=False)
            window['-SELECT-'].update("")
            window['-FROM-'].update("")
            window['-WHERE-'].update("")

        elif event == "Generate AQP":
            select_text = values['-SELECT-']
            from_text = values['-FROM-']
            where_text = values['-WHERE-']

        elif event in AQP_CONFIGS:
            if values[event] == False:
                AQP_CONFIGS_2[event] = 'False'
            else:
                AQP_CONFIGS_2[event] = 'True'

        elif event == "Close":
            break
    
    window.close()


