import PySimpleGUI as sg

import annotations


def set_password():
    """
    This function is for the user to enter the db password
    """

    dbpassword = input("Please enter your password to access PostGreSQL: ")
    annotations.set_password(dbpassword)
    
def display():
    """
    This function:
    - displays the GUI, and is called by project.py
    - handles the logic of button-clicking and each event that follows
    - calls the main functions, explain() and aqp_explain() in annotations.py 
    """

    # AQP_CONFIGS and AQP_CONFIGS_2 are config settings for AQP generation later on in the program
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

    sg.theme('Reddit')

    # The following sg.Column nested lists are for formatting the GUI. Should be self-explanatory with the names
    qep_col1 = [
        [sg.Text('QEP chosen by DBMS:', font=('Helvetica', 14))],
        [sg.Multiline(size=(35, 8), key='-QEP_TREE-', justification='left')],
    ]

    qep_col2 = [
        [sg.Text('QEP detailed steps:', font=('Helvetica', 14))],
        [sg.Multiline(size=(50, 8), key='-QEP_STEPS-', justification='left')],
    ]

    qep_main = [
        [sg.Text('Please enter your SQL query\n', font=('Helvetica', 16), key='-ERROR_MESSAGE-')],
        [sg.Text('SELECT Statement', font=('Helvetica', 14), size =(25, 1)), sg.InputText(key='-SELECT-', font=('Helvetica', 14))],
        # [sg.Text('')],
        [sg.Text('FROM Statement', font=('Helvetica', 14), size =(25, 1)), sg.InputText(key='-FROM-', font=('Helvetica', 14))],
        # [sg.Text('')],
        [sg.Text('WHERE Statement', font=('Helvetica', 14), size =(25, 1)), sg.InputText(key='-WHERE-', font=('Helvetica', 14))],
        # [sg.Text('')],
        [sg.Text('')],
        [sg.Button("Generate QEP", font=('Helvetica', 14), button_color=('Black', 'LightBlue')), sg.Button("Reset", font=('Helvetica', 14), button_color=('Black', 'LightBlue'))],
        # [sg.Text('')],
        # [sg.Text('')],
        [sg.Text('')],
        [sg.Column(qep_col1), sg.Column(qep_col2)]

    ]

    aqp_col1 = [
        [sg.Text('AQP chosen by DBMS:', font=('Helvetica', 14))],
        [sg.Multiline(size=(35, 8), key='-AQP_TREE-', justification='left')],
    ]

    aqp_col2 = [
        [sg.Text('AQP detailed steps:', font=('Helvetica', 14))],
        [sg.Multiline(size=(50, 8), key='-AQP_STEPS-', justification='left')],
    ]

    aqp_main = [
        [sg.Text('Please select AQP by restricting operations DBMS considers', font=('Helvetica', 16))],
        [sg.Text('')],
        [sg.Checkbox('bitmapscan', font=('Helvetica', 14), key='enable_bitmapscan', enable_events=True, default=True), sg.Checkbox('hashjoin', key='enable_hashjoin', font=('Helvetica', 14), enable_events=True, default=True)],
        [sg.Checkbox('indexscan', font=('Helvetica', 14), key='enable_indexscan', enable_events=True, default=True), sg.Checkbox('indexonlyscan', font=('Helvetica', 14), key='enable_indexonlyscan', enable_events=True, default=True)],
        [sg.Checkbox('nestloop', font=('Helvetica', 14), key='enable_nestloop', enable_events=True, default=True), sg.Checkbox('seqscan', font=('Helvetica', 14), key='enable_seqscan', enable_events=True, default=True)],
        [sg.Checkbox('mergejoin', font=('Helvetica', 14), key='enable_mergejoin', enable_events=True, default=True)],
        # [sg.Text('')],
        # [sg.Text('')],
        # [sg.Text('')],
        [sg.Button("Generate AQP", font=('Helvetica', 14), button_color=('Black', 'LightBlue'), disabled=True)],
        # [sg.Text('')],
        [sg.Column(aqp_col1), sg.Column(aqp_col2)]

    ]

    # The main layout of all the elements in the GUI
    layout = [
        [sg.Column(qep_main),sg.Column(aqp_main)],
        [sg.Text('Explanation of differences', font=('Helvetica', 16)), sg.Text('', font=('Helvetica', 16), key='-USER_QUERY_TITLE-')],
        [sg.Multiline(size=(80, 4), key='-EXPLANATION_SELECT-', justification='l', font=('Helvetica', 11)), sg.Text('', key='-SELECT_STATEMENT-', font=('Helvetica', 14))],
        [sg.Multiline(size=(80, 4), key='-EXPLANATION_FROM-', justification='l', font=('Helvetica', 11)), sg.Text('', key='-FROM_STATEMENT-', font=('Helvetica', 14))],
        [sg.Multiline(size=(80, 4), key='-EXPLANATION_WHERE-', justification='l', font=('Helvetica', 11)), sg.Text('', key='-WHERE_STATEMENT-', font=('Helvetica', 14))],
    ]

    # Declaring the window and the window sizes. Note that resizable=True so User can resize the window to fit dimensions of User's local machine
    window = sg.Window("Query Plan Explainer", layout, resizable=True, size=(1200, 700))

    # This is the main logic loop for GUI events and buttons
    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
        # Generate QEP button is pressed
        elif event == "Generate QEP":
            # Read user inputs
            select_text = values['-SELECT-']
            from_text = values['-FROM-']
            where_text = values['-WHERE-']

            # Call explain() function from annotations, which runs EXPLAIN command on postgres. 
            try:
                qep_results, total_cost, tree = annotations.explain(select_text, from_text, where_text)
                window['-ERROR_MESSAGE-'].update("Please enter your SQL query\n")
            except:
                window['-ERROR_MESSAGE-'].update("The SQL Query or password might be wrong. Please try again!\n")
                continue
            
            # Update GUI to allow next steps and prevent editting submitted query
            window['Generate QEP'].update(disabled=True)
            window['-SELECT-'].update(disabled=True)
            window['-FROM-'].update(disabled=True)
            window['-WHERE-'].update(disabled=True)
            window['Generate AQP'].update(disabled=False)

            # Update GUI with results
            window['-QEP_STEPS-'].update(qep_results + "\n\n" + "Total Cost of plan: " + str(total_cost))
            window['-QEP_TREE-'].update(tree)
            
            window['-SELECT_STATEMENT-'].update('----------> ' + select_text)
            window['-FROM_STATEMENT-'].update('----------> ' + from_text)
            window['-WHERE_STATEMENT-'].update('----------> ' + where_text)

        # Generate AQP button is pressed
        elif event == "Generate AQP":
            select_text = values['-SELECT-']
            from_text = values['-FROM-']
            where_text = values['-WHERE-']

            # Call aqp_explain which passes in certain restrictions to postgres when EXPLAIN command is run.
            aqp_results, total_cost, tree = annotations.aqp_explain(select_text, from_text, where_text, AQP_CONFIGS_2)

            # If at least one restriction is selected for AQP generation on GUI, then find difference between QEP and AQP and generate explanation
            if "False" in AQP_CONFIGS_2.values():
                select_explain_specific, from_explain_specific, where_explain_specific = annotations.find_difference(qep_results, aqp_results)
                select_explanation, from_explanation, where_explanation = annotations.explanation(qep_results, aqp_results, AQP_CONFIGS_2) # list
                select_explanation_text = "\n".join(select_explanation) # turn list into text, split each element by newline
                from_explanation_text = "\n".join(from_explanation)
                where_explanation_text = "\n".join(where_explanation)

                select_explanation_text = select_explain_specific + select_explanation_text
                from_explanation_text = from_explain_specific + from_explanation_text
                where_explanation_text = where_explain_specific + where_explanation_text

                window['-EXPLANATION_SELECT-'].update(select_explanation_text)
                window['-EXPLANATION_FROM-'].update(from_explanation_text)
                window['-EXPLANATION_WHERE-'].update(where_explanation_text)

                if qep_results == aqp_results:
                    window['-EXPLANATION_SELECT-'].update("QEP results are same as AQP results because no AQP is possible with this restriction.")
                    window['-EXPLANATION_FROM-'].update("QEP results are same as AQP results because no AQP is possible with this restriction.")
                    window['-EXPLANATION_WHERE-'].update("QEP results are same as AQP results because no AQP is possible with this restriction.")
            
            # No restriction is selected, hence postgres will choose most optimal plan without restrictions, which is QEP.
            else:
                window['-EXPLANATION_SELECT-'].update("QEP is the same as AQP because no operator restrictions were selected.")
                window['-EXPLANATION_FROM-'].update("QEP is the same as AQP because no operator restrictions were selected.")
                window['-EXPLANATION_WHERE-'].update("QEP is the same as AQP because no operator restrictions were selected.")

            window['-AQP_STEPS-'].update(aqp_results + "\n\n" + "Total Cost of plan: " + str(total_cost))
            window['-AQP_TREE-'].update(tree)
        
        # Reset button is pressed - usually done when user wants to input new query
        elif event == "Reset":
            window['Generate AQP'].update(disabled=True)
            window['Generate QEP'].update(disabled=False)
            window['-SELECT-'].update(disabled=False)
            window['-FROM-'].update(disabled=False)
            window['-WHERE-'].update(disabled=False)
            window['-SELECT-'].update("")
            window['-FROM-'].update("")
            window['-WHERE-'].update("")
            window['-EXPLANATION_SELECT-'].update("")
            window['-EXPLANATION_FROM-'].update("")
            window['-EXPLANATION_WHERE-'].update("")
            window['-SELECT_STATEMENT-'].update('')
            window['-FROM_STATEMENT-'].update('')
            window['-WHERE_STATEMENT-'].update('')
            window['-QEP_STEPS-'].update('')
            window['-QEP_TREE-'].update('')
            window['-AQP_STEPS-'].update('')
            window['-AQP_TREE-'].update('')
            window['-ERROR_MESSAGE-'].update('Please enter your SQL query\n')
        
        # This section enables/disables the various operations when generating AQP, based on checkbox selection.
        elif event in AQP_CONFIGS:
            if values[event] == False:
                AQP_CONFIGS_2[event] = 'False'
            else:
                AQP_CONFIGS_2[event] = 'True'

        elif event == "Close":
            break
    
    # Always close window in case
    window.close()


