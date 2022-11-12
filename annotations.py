import psycopg2
import json
from collections import OrderedDict
 
 # Postgres TCP-H database parameters
DB_NAME = "TPC-H"
DB_USER = "postgres"
DB_PASS = ""
DB_HOST = "localhost"
DB_PORT = "5432"

# Data structures that stores Node Type keywords that we care about, to be extracted from the JSON that postgres returns after EXPLAIN is run
SELECT_KEYWORDS = ["Aggregate"]
FROM_KEYWORDS = ["Seq Scan", "Bitmap Index Scan", "Bitmap Heap Scan", "Index Scan", "Index Only Scan", "Tid Scan", "Index Skip Scan"]
WHERE_KEYWORDS = ["Hash Join", "Nested Loop", "Merge Join", "Sort"]

# Keep track of restrictions that can be toggled in postgres EXPLAIN command
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

# This mapping translates the key used by postgres JSON to plain speech format (we use this for formatting results later)
AQP_MAPPING = {'enable_bitmapscan':'Bitmap Index Scan', # special case: will be both Bitmap Heap Scan and Bitmap Index Scan
              'enable_hashjoin':'Hash Join',
              'enable_indexscan':'Index Scan',
              'enable_indexonlyscan':'Index Only Scan',
              'enable_mergejoin':'Merge Join',
              'enable_nestloop':'Nested Loop',
              'enable_seqscan':'Seq Scan',
}

# Global variable used for tree traversal
tree_levels = 0

def set_password(password):
    """
    This function sets user inputted password for postgres login
    """
    global DB_PASS
    DB_PASS = password

def process_plan(imp_results, string_collector, total_cost, tree_collector):
    """
    This function processes the results in dictionary format by extracting and generating key info into string formats.
    It returns string_collect, total_cost, and tree_collector, which are strings that store 
    important info on operations, total cost of each operation, and the branch of the tree, respectively.
    """

    global tree_levels
    last_text_len = 0

    # Iterates through each item in dictionary of results returned by postgres 
    for item in imp_results.keys():
        # If key == Plan or key == Plans, recursively unpack the dict, while generating tree
        if item=="Plan":
            tree_levels += 1
            tree_collector += '└─'
            string_collector, total_cost, tree_collector = process_plan(imp_results[item], string_collector, total_cost, tree_collector)
        
        elif item=="Plans":
            tree_levels += 1
            tree_collector = tree_collector + '\n' + str(tree_levels*'   ') + '├─'

            all_plans = imp_results[item]   # a list
            for plan in all_plans:
                string_collector, total_cost, tree_collector = process_plan(plan, string_collector, total_cost, tree_collector)
                # tree_collector += ' ─── '

        # If key == Node Type, this is an important operation/step we want to save the info
        elif item=="Node Type":
            tree_collector += str(imp_results[item]) + '─ '
            string_collector += str(imp_results[item])
            
        # This key is mapped to value of which relation the operation is performed on. This is info we want to extract.
        elif item=="Relation Name":
            string_collector += " on " + str(imp_results[item])
        
        # These keys give us the relations which the join is performed on. This is info we want to collect.
        elif item=="Group Key" or item=="Hash Cond" or item=="Merge Cond" or item=="Sort Key":
            # Some string slicing and manipulation is done to make sure order is correct (Total Cost displayed last)
            previous_text = string_collector[len(string_collector)-last_text_len:]
            string_collector = string_collector[:-last_text_len] + " on " + str(imp_results[item]) + previous_text
        
        # This key's value gives us the total cost of that operation. This is info we want to collect.
        elif item =="Total Cost":
            string_collector += " -- (Total Cost: " + str(imp_results[item]) + ")" + "\n"
            last_text_len = len(str(imp_results[item])) + 18 + len("\n")
            total_cost += imp_results[item]

    return string_collector, total_cost, tree_collector


def strip_unneeded_data(json_object):
    """
    This function strips away extra layers of JSON object
    """

    if not isinstance(json_object, dict):
        return strip_unneeded_data(json_object[0])
    else:
        return json_object


def find_difference(qep_results, aqp_results):
    """
    This function finds what operations are different between QEP and AQP selected, 
    and generates an explanation for this difference. 
    Explanations are tagged to the respective line of the user query for annotation.
    """

    select_explain_str = ''
    from_explain_str = ''
    where_explain_str = ''
    unique_qep = []
    unique_aqp = []
    count = OrderedDict()

    # Convert respective results into lists first
    qep_list = qep_results.split('\n')
    aqp_list = aqp_results.split('\n')
            
    # The following 2 for loops go through QEP and AQP operations to find the unique operations in each side
    # This effectively means finding the operations that were changed in the AQP
    for operation in qep_list:
        qep_line = operation.split(' --')[0]
        count[qep_line] = count.get(qep_line, 0) + 1
    
    for operation in aqp_list:
        aqp_line = operation.split(' --')[0]
        count[aqp_line] = count.get(aqp_line, 0) - 1

    # At this point, in count data struct, any keys with value = 0 means common/matching/removed
    # Positive means this extra unique key is in qep
    # Negative means this extra unique key is in aqp

    # Separate unique operations into QEP and AQP
    for key, val in count.items():
        if val > 0:
            for _ in range(val):
                unique_qep.append(key)
        elif val < 0:
            for _ in range(val*-1):
                unique_aqp.append(key)

    # This section goes through each operation that changed in QEP, and finds the replacement operation in AQP, then generates an explanation
    for operation in unique_qep:
        # Operation is not a scan not a join - not interested
        if 'on' not in operation and 'Nested Loop' not in operation:
            continue

        if 'on' in operation:   
            temp = operation.split(' on ')
            type_of_operation = temp[0][-4:]    
            relation_or_join_condition = temp[1]

        elif 'Nested Loop' in operation:
            type_of_operation = 'Loop'
            relation_or_join_condition = None

        # Search through AQP operations for the one that replaced QEP operation
        # Generate explanations that are tagged to the respective line of the user query for annotation
        for alt_operation in unique_aqp:
            print(alt_operation)

            # Case 1: qep operation is not a nested loop and aqp operation is not a nested loop
            if type_of_operation != 'Loop' and 'on' in alt_operation:  
                temp_alt = alt_operation.split(' on ')
                type_of_operation_alt = temp_alt[0][-4:]    
                relation_or_join_condition__alt = temp_alt[1]

                if type_of_operation == type_of_operation_alt and relation_or_join_condition == relation_or_join_condition__alt:
                    if type_of_operation == 'Aggregate':
                        select_explain_str += operation + ' was chosen over ' + alt_operation + ' because total cost is lower (refer to detailed steps)\n' 

                    elif type_of_operation == 'Scan':
                            from_explain_str += operation + ' was chosen over ' + alt_operation + ' because total cost is lower (refer to detailed steps)\n' 

                    elif type_of_operation == 'Join':
                            where_explain_str += operation + ' was chosen over ' + alt_operation + ' because total cost is lower (refer to detailed steps)\n' 
            
            # Case 2: qep operation is a nested loop and aqp operation is a join
            elif type_of_operation == 'Loop' and 'Join on' in alt_operation:
                where_explain_str += operation + ' was chosen over ' + alt_operation + ' because total cost is lower (refer to detailed steps)\n' 

            # Case 3: qep is a join and the aqp operation is a nested loop
            elif type_of_operation == 'Join' and 'Nested Loop' in alt_operation:
                where_explain_str += operation + ' was chosen over ' + alt_operation + ' because total cost is lower (refer to detailed steps)\n' 

    return select_explain_str, from_explain_str, where_explain_str

def explanation(qep_results, aqp_results, AQP_CONFIGS_2):
    """
    This function generates more theory-based explanations on why QEP operation was chosen over AQP operation.
    Explanations are tagged to the respective line of the user query for annotation.
    """
    select_explanation = []
    from_explanation = []
    where_explanation = []
    
    # Scans 
    if (qep_results.count('Seq Scan') > aqp_results.count('Seq Scan')):
        string = 'The QEP chooses Sequential Scan when a large portion of the rows in a table are selected, as Sequential Scan looks through all records in the table, and it is cost-effective as it only requires 1 IO operation per row'
        from_explanation.append(string)
    if (qep_results.count('Index Only Scan') > aqp_results.count('Index Only Scan')):
        string = 'The QEP chooses Index Only Scan when only one/a few rows from the table are selected and all queried data is available in the index'
        from_explanation.append(string)
    if (qep_results.count('Index Scan') > aqp_results.count('Index Scan')):
        string = 'The QEP chooses Index Scan when only one/a few rows from the table are selected, but not all queried data is available in the index'
        from_explanation.append(string)
    if (qep_results.count('Bitmap Index Scan') > aqp_results.count('Bitmap Index Scan')):
        string = 'The QEP chooses Bitmap Index Scan in tandem with Bitmap Heap Scan, and enables more than one index to be used to scan a table'
        from_explanation.append(string)
    if (qep_results.count('Bitmap Heap Scan') > aqp_results.count('Bitmap Heap Scan')):
        string = 'The QEP chooses Bitmap Heap Scan when the result set will have a high selectivity rate with respect to the search conditions (i.e., there is a high percentage of rows that satisfy the search criteria)'
        from_explanation.append(string)
    if (qep_results.count('Tid Scan') > aqp_results.count('Tid Scan')):
        string = 'The QEP chooses Tid Scan when there is TID (Tuple Identifier) in the predicate'
        from_explanation.append(string)

    # Joins
    if (qep_results.count('Hash Join') > aqp_results.count('Hash Join')):
        string = 'The QEP chooses Hash Join over Nested Loop/Merge Join when the input size is large, or when projections of the joined tables are not already sorted on the join columns'
        where_explanation.append(string)
    if (qep_results.count('Merge Join') > aqp_results.count('Merge Join')):
        string = 'The QEP chooses Merge Join over Nested Loop/Hash Join when the two projections of the joined tables have already been sorted on the join columns'
        where_explanation.append(string)
    if (qep_results.count('Nested Loop') > aqp_results.count('Nested Loop')):
        string = 'The QEP chooses Nested Loop Join over Hash Join/Merge Join when one join input is small, as it requires the least I/O operations'
        where_explanation.append(string)

    # Special case: explanations for seq scan, sort, nested loop, material (which cannot be completed turned off)
    if (qep_results.count('Seq Scan') == aqp_results.count('Seq Scan') and aqp_results.count('Seq Scan') > 0 and AQP_CONFIGS_2['enable_seqscan'] == "False"):
        string = "It is impossible to suppress sequential scans for this query entirely. Turning this variable off discourages the planner from using one if there are other methods available. Thus, Seq Scan is still utlised in the AQP, although cost is a lot higher."
        from_explanation.append(string)
    if (qep_results.count('Sort') == aqp_results.count('Sort') and aqp_results.count('Sort') > 0 and AQP_CONFIGS_2['enable_sort'] == "False"):
        string = "It is impossible to suppress sorting for this query entirely. Turning this variable off discourages the planner from using one if there are other methods available. Thus, Sort is still utlised in the AQP, although cost is a lot higher."
        select_explanation.append(string)
    if (qep_results.count('Nested Loop') == aqp_results.count('Nested Loop') and aqp_results.count('Nested Loop') > 0 and AQP_CONFIGS_2['enable_nestloop'] == "False"):
        string = "It is impossible to suppress nested loops for this query entirely. Turning this variable off discourages the planner from using one if there are other methods available. Thus, Nested Loop is still utlised in the AQP, although cost is a lot higher."
        where_explanation.append(string)
    if (qep_results.count('Material') == aqp_results.count('Material') and aqp_results.count('Material') > 0 and AQP_CONFIGS_2['enable_material'] == "False"):
        string = "It is impossible to suppress material for this query entirely. Turning this variable off discourages the planner from using one if there are other methods available. Thus, Material is still utlised in the AQP, although cost is a lot higher."
        select_explanation.append(string)
    
    return select_explanation, from_explanation, where_explanation

def explain(select_text, from_text, where_text):
    """
    This function connects to postgres DBMS.
    The user query is formatted.
    EXPLAIN command is called on DBMS to generate QEP.
    It then calls strip_unneeded_data() and process_plan() functions.
    Results of explanation, total cost, and the plan tree are formatted and returned to GUI (interface.py).
    """
    global tree_levels

    # Connect to postgres database
    conn = psycopg2.connect(database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS,
                            host=DB_HOST,
                            port=DB_PORT)
    print("Database connected successfully")

    # Construct SQL query text to EXPLAIN
    query = select_text + '\n' + from_text + '\n' + where_text

    # Execute EXPLAIN command on user's input query 
    explain_command = 'EXPLAIN (ANALYSE, COSTS true, FORMAT json) ' + query
    cur = conn.cursor()
    cur.execute(explain_command)
    raw_results = cur.fetchall()
    raw_results = json.dumps(raw_results)
    results = json.loads(raw_results)

    # Call strip_to_plan function to remove unneccesary data in dict
    imp_results = strip_unneeded_data(results)

    # Processes the results from DMBS to generate annotations
    results, total_cost, tree = process_plan(imp_results, "", 0, "")

    # Reset tree_levels
    tree_levels = 0

    # Reverse results since DMBS executes operations from the bottom
    to_reverse = []
    for line in results.splitlines():
        to_reverse.append(line)
    to_reverse = to_reverse[::-1]
    results = '\n'.join(to_reverse)

    print('Data fetched successfully\n')
    conn.close()    # Always remember to close connection

    return results, total_cost, tree

def aqp_explain(select_text, from_text, where_text, AQP_CONFIGS_2):
    """
    This function connects to postgres DBMS.
    The user query is formatted and user selections on restrictions to operations DBMS can use is factored in. 
    EXPLAIN command is called on DBMS to generate AQP.
    It then calls strip_unneeded_data() and process_plan() functions.
    Results of explanation, total cost, and the plan tree are formatted and returned to GUI (interface.py).
    """
    global tree_levels

    # Connect to postgres database
    conn = psycopg2.connect(database=DB_NAME,
                            user=DB_USER,
                            password=DB_PASS,
                            host=DB_HOST,
                            port=DB_PORT)
    print("Database connected successfully")

    # Construct SQL query text to EXPLAIN
    query = select_text + '\n' + from_text + '\n' + where_text

    # Execute EXPLAIN command on user's input query 
    explain_command = 'EXPLAIN (ANALYSE, COSTS true, FORMAT json) ' + query
    cur = conn.cursor()

    # This is the main difference between this function and explain()
    # This sets configs so that some operations are disabled when running EXPLAIn command on DBMS
    for config in AQP_CONFIGS_2.keys():
        if AQP_CONFIGS_2[config] == 'False':
            cur.execute('SET ' + config + ' TO off;')
        else:
            cur.execute('SET ' + config + ' TO on;')

    cur.execute(explain_command)
    raw_results = cur.fetchall()
    raw_results = json.dumps(raw_results)
    results = json.loads(raw_results)

    # Call strip_to_plan function to remove unneccesary data in dict
    imp_results = strip_unneeded_data(results)

    # Processes the results from DMBS to generate annotations
    results, total_cost, tree = process_plan(imp_results, "", 0, "")

    # Reset tree level
    tree_levels = 0 

    # Reverse results since DMBS executes operations from the bottom
    to_reverse = []
    for line in results.splitlines():
        to_reverse.append(line)
    to_reverse = to_reverse[::-1]
    results = '\n'.join(to_reverse)

    print('Data fetched successfully\n')
    conn.close()

    return results, total_cost, tree


