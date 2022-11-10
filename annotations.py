import psycopg2
import json
from collections import OrderedDict
 
 # Postgres TCP-H database details
DB_NAME = "TPC-H"
DB_USER = "postgres"
DB_PASS = ""
DB_HOST = "localhost"
DB_PORT = "5432"

SELECT_KEYWORDS = ["Aggregate"]
FROM_KEYWORDS = ["Seq Scan", "Bitmap Index Scan", "Bitmap Heap Scan", "Index Scan", "Index Only Scan", "Tid Scan", "Index Skip Scan"]
WHERE_KEYWORDS = ["Hash Join", "Nested Loop", "Merge Join", "Sort"]
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

AQP_MAPPING = {'enable_bitmapscan':'Bitmap Index Scan', # special case: will be both Bitmap Heap Scan and Bitmap Index Scan
            #   'enable_hashagg':'Bitmap Scan',
              'enable_hashjoin':'Hash Join',
              'enable_indexscan':'Index Scan',
              'enable_indexonlyscan':'Index Only Scan',
            #   'enable_material':'Bitmap Scan',
              'enable_mergejoin':'Merge Join',
              'enable_nestloop':'Nested Loop',
              'enable_seqscan':'Seq Scan',
            #   'enable_sort':'Bitmap Scan',
            #   'enable_tidscan':'TID Scan'
}

tree_levels = 0


def set_password(password):
    global DB_PASS
    DB_PASS = password

def process_plan_dict(imp_results, string_collector, total_cost, tree_collector):
    # process the dictionary to retrieve query plan information and put them into a string
    global tree_levels

    last_text_len = 0
    for item in imp_results.keys():
        if item=="Plan":
            tree_levels += 1
            tree_collector += '└─'
            string_collector, total_cost, tree_collector = process_plan_dict(imp_results[item], string_collector, total_cost, tree_collector)
        
        elif item=="Plans":
            tree_levels += 1
            tree_collector = tree_collector + '\n' + str(tree_levels*'   ') + '├─'

            all_plans = imp_results[item]   # a list
            for plan in all_plans:
                string_collector, total_cost, tree_collector = process_plan_dict(plan, string_collector, total_cost, tree_collector)
                # tree_collector += ' ─── '


        elif item=="Node Type":
            print(imp_results[item])
            print(imp_results)

            tree_collector += str(imp_results[item]) + '─ '

            string_collector += str(imp_results[item])
            
        elif item=="Relation Name":
            string_collector += " on " + str(imp_results[item])
        
        elif item=="Group Key" or item=="Hash Cond" or item=="Merge Cond" or item=="Sort Key":
            # string_collector_len = len(string_collector)
            previous_text = string_collector[len(string_collector)-last_text_len:]
            string_collector = string_collector[:-last_text_len] + " on " + str(imp_results[item]) + previous_text
        
        elif item =="Total Cost":
            string_collector += " -- (Total Cost: " + str(imp_results[item]) + ")" + "\n"
            last_text_len = len(str(imp_results[item])) + 18 + len("\n")
            total_cost += imp_results[item]


    
    # # wrong starts here
    # to_reverse = string_collector.split(',')
    # print(to_reverse)
    # to_reverse.reverse()
    # string_collector = ''.join(to_reverse)

    return string_collector, total_cost, tree_collector


def strip_unneeded_data(json_object):
    # strip away extra layers of the json object to get to the dictionary for processing
    # print("execute")
    if not isinstance(json_object, dict):
        return strip_unneeded_data(json_object[0])
    else:
        return json_object


def explain_diff(qep_results, aqp_results):
    # perform 'diff' on qep_results and aqp_results - basically only getting unique lines
    select_explain_str = ''
    from_explain_str = ''
    where_explain_str = ''

    # convert respective results into lists first
    qep_list = qep_results.split('\n')
    aqp_list = aqp_results.split('\n')

    # go through each line in QEP
        # for each line, find matching line in AQP
            # if found, delete from both list 
            # then restart with updated lists
            
    unique_qep = []
    unique_aqp = []

    count = OrderedDict()

    for x in qep_list:
        # print(x)
        qep_line = x.split(' --')[0]
        count[qep_line] = count.get(qep_line, 0) + 1
    
    for y in aqp_list:
        # print(y)
        aqp_line = y.split(' --')[0]
        count[aqp_line] = count.get(aqp_line, 0) - 1
        # if aqp_line in count.keys():
        #     count[aqp_line] -= 1
    
    print(count)
    # at this point, any keys with value = 0 means common/matching/removed
    # positive means this extra unique key is in qep
    # negative means this extra unique key is in aqp

    # e.g. qep = hash join on relation X, index Scan
    # e.g. aqp = merge join on relation y, seq scan on X, merge join on relation X

    # logic is to go through each extra unique key in qep and find 1. type of op (scan/join) 2. on which relation
    print('PRINTTTTTT_2')
    for key, val in count.items():
        if val > 0:
            for _ in range(val):
                unique_qep.append(key)
        elif val < 0:
            for _ in range(val*-1):
                unique_aqp.append(key)

    # unique_qep only has things in the qep and not found in aqp, while unique_aqp only has things in the aqp and not found in qep
    # using 1 and 2, we can find the 'replacement' operation in aqp
    print('PRINTTTTTT_3')
    print(unique_qep)
    print(unique_aqp)

    for operation in unique_qep:
        print(operation)
        # only proceed if it is a Join or Scan
        if 'on' not in operation and 'Nested Loop' not in operation:
            continue

        if 'on' in operation:   
            temp = operation.split(' on ')
            print(temp)
            type_of_operation = temp[0][-4:]    # check if needed
            relation_or_join_condition = temp[1]

        elif 'Nested Loop' in operation:
            type_of_operation = 'Loop'
            relation_or_join_condition = None

        # search in unique_aqp
        for alt_operation in unique_aqp:
            print(alt_operation)

            # Case 1: qep operation is not a nested loop and aqp operation is not a nested loop
            if type_of_operation != 'Loop' and 'on' in alt_operation:  
                temp_alt = alt_operation.split(' on ')
                type_of_operation_alt = temp_alt[0][-4:]    # check if needed
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


    print(select_explain_str)
    print(from_explain_str)
    print(where_explain_str)
    # can have 3 separate explain_str for select, from, where
    return select_explain_str, from_explain_str, where_explain_str

def explanation(qep_results, aqp_results, AQP_CONFIGS_2):
    select_explanation = []
    from_explanation = []
    where_explanation = []
    
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

    if (qep_results.count('Hash Join') > aqp_results.count('Hash Join')):
        string = 'The QEP chooses Hash Join over Nested Loop/Merge Join when the input size is large, or when projections of the joined tables are not already sorted on the join columns'
        where_explanation.append(string)

    if (qep_results.count('Merge Join') > aqp_results.count('Merge Join')):
        string = 'The QEP chooses Merge Join over Nested Loop/Hash Join when the two projections of the joined tables have already been sorted on the join columns'
        where_explanation.append(string)
    if (qep_results.count('Nested Loop') > aqp_results.count('Nested Loop')):
        string = 'The QEP chooses Nested Loop Join over Hash Join/Merge Join when one join input is small, as it requires the least I/O operations'
        where_explanation.append(string)

    # include explanations for seq scan, sort, nested loop, material (which cannot be completed turned off)
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

# Generate AQPs
def aqp_test_explain(select_text, from_text, where_text, AQP_CONFIGS_2):
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

    for config in AQP_CONFIGS_2.keys():
        if AQP_CONFIGS_2[config] == 'False':
            cur.execute('SET ' + config + ' TO off;')
        else:
            cur.execute('SET ' + config + ' TO on;')

    cur.execute(explain_command)
    raw_results = cur.fetchall()
    # print(raw_results,'\n')

    # Get JSON string
    raw_results = json.dumps(raw_results)
    # print(raw_results,'\n')

    # Convert JSON string to dict
    results = json.loads(raw_results)
    # print(results,'\n')

    # Call strip_to_plan function to remove unneccesary data in dict
    imp_results = strip_unneeded_data(results)
    # print(imp_results,'\n')

    results, total_cost, tree = process_plan_dict(imp_results, "", 0, "")
    tree_levels = 0
    # print(results, total_cost, tree)

    # Order of steps starts from bottom of tree structure
    # print(results)
    to_reverse = []
    for line in results.splitlines():
        to_reverse.append(line)
    # print(to_reverse)
    to_reverse = to_reverse[::-1]
    # print(to_reverse)
    results = '\n'.join(to_reverse)

    # data = print_results
    # data = textwrap.wrap(data, 6)
    print('Data fetched successfully\n')

    conn.close()

    # Identify tables mentioned in query
    # tables_text = from_text.strip('FROM ')
    # tables = tables_text.split(',')
    # print('Tables are: ', tables, '\n')

    return results, total_cost, tree

def test_explain(select_text, from_text, where_text):
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

    for config in AQP_CONFIGS:
        cur.execute('SET ' + config + ' TO on;')

    cur.execute(explain_command)
    raw_results = cur.fetchall()
    # print(raw_results,'\n')

    # Get JSON string
    raw_results = json.dumps(raw_results)
    # print(raw_results,'\n')

    # Convert JSON string to dict
    results = json.loads(raw_results)
    # print(results,'\n')

    # Call strip_to_plan function to remove unneccesary data in dict
    imp_results = strip_unneeded_data(results)
    # print(imp_results,'\n')

    # imp_results = imp_results['Plan']
    # print(imp_results)

    results, total_cost, tree = process_plan_dict(imp_results, "", 0, "")
    tree_levels = 0
    # print(results, total_cost, tree)

    # Order of steps starts from bottom of tree structure
    # print(results)
    to_reverse = []
    for line in results.splitlines():
        to_reverse.append(line)
    # print(to_reverse)
    to_reverse = to_reverse[::-1]
    # print(to_reverse)
    results = '\n'.join(to_reverse)

    # data = print_results
    # data = textwrap.wrap(data, 6)
    print('Data fetched successfully\n')

    conn.close()

    # # Identify tables mentioned in query
    # tables_text = from_text.strip('FROM ')
    # tables = tables_text.split(',')
    # print('Tables are: ', tables, '\n')

    return results, total_cost, tree
