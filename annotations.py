import psycopg2
import json
 
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

            string_collector += "\n" + str(imp_results[item])
            
        elif item=="Relation Name":
            string_collector += " on " + str(imp_results[item])
        
        elif item=="Group Key" or item=="Hash Cond" or item=="Merge Cond" or item=="Sort Key":
            # string_collector_len = len(string_collector)
            previous_text = string_collector[len(string_collector)-last_text_len:]
            string_collector = string_collector[:-last_text_len] + " on " + str(imp_results[item]) + previous_text
        
        elif item =="Total Cost":
            string_collector += " -- (Total Cost: " + str(imp_results[item]) + ")"
            last_text_len = len(str(imp_results[item])) + 18
            total_cost += imp_results[item]

        
    return string_collector, total_cost, tree_collector


def strip_unneeded_data(json_object):
    # strip away extra layers of the json object to get to the dictionary for processing
    # print("execute")
    if not isinstance(json_object, dict):
        return strip_unneeded_data(json_object[0])
    else:
        return json_object

def explanation(qep_results, aqp_results):
    explanation = []
    
    if (qep_results.count('Seq Scan') > aqp_results.count('Seq Scan')):
        string = 'The QEP chooses Sequential Scan when a large portion of the rows in a table are selected, as Sequential Scan looks through all records in the table, and it is cost-effective as it only requires 1 IO operation per row'
        explanation.append(string)
    if (qep_results.count('Index Only Scan') > aqp_results.count('Index Only Scan')):
        string = 'The QEP chooses Index Only Scan when only one/a few rows from the table are selected and all queried data is available in the index'
        explanation.append(string)
    if (qep_results.count('Index Scan') > aqp_results.count('Index Scan')):
        string = 'The QEP chooses Index Scan when only one/a few rows from the table are selected, but not all queried data is available in the index'
        explanation.append(string)
    if (qep_results.count('Bitmap Index Scan') > aqp_results.count('Bitmap Index Scan')):
        string = 'The QEP chooses Bitmap Index Scan in tandem with Bitmap Heap Scan, and enables more than one index to be used to scan a table'
        explanation.append(string)
    if (qep_results.count('Bitmap Heap Scan') > aqp_results.count('Bitmap Heap Scan')):
        string = 'The QEP chooses Bitmap Heap Scan when the result set will have a high selectivity rate with respect to the search conditions (i.e., there is a high percentage of rows that satisfy the search criteria)'
        explanation.append(string)
    if (qep_results.count('Tid Scan') > aqp_results.count('Tid Scan')):
        string = 'The QEP chooses Tid Scan when there is TID (Tuple Identifier) in the predicate'
        explanation.append(string)


    if (qep_results.count('Hash Join') > aqp_results.count('Hash Join')):
        string = 'The QEP chooses Hash Join over Nested Loop/Merge Join when the input size is large, or when projections of the joined tables are not already sorted on the join columns'
        explanation.append(string)
    if (qep_results.count('Merge Join') > aqp_results.count('Merge Join')):
        string = 'The QEP chooses Merge Join over Nested Loop/Hash Join when the two projections of the joined tables have already been sorted on the join columns'
        explanation.append(string)
    if (qep_results.count('Nested Loop') > aqp_results.count('Nested Loop')):
        string = 'The QEP chooses Nested Loop Join over Hash Join/Merge Join when one join input is small, as it requires the least I/O operations'
        explanation.append(string)

    # include explanations for seq scan, sort, nested loop, material (which cannot be completed turned off)
    if (qep_results.count('Seq Scan') == aqp_results.count('Seq Scan') and aqp_results.count('Seq Scan') > 0):
        string = "It is impossible to suppress sequential scans for this query entirely. Turning this variable off discourages the planner from using one if there are other methods available. Thus, Seq Scan is still utlised in the AQP, although cost is a lot higher."
        explanation.append(string)

    if (qep_results.count('Sort') == aqp_results.count('Sort') and aqp_results.count('Sort') > 0):
        string = "It is impossible to suppress sorting for this query entirely. Turning this variable off discourages the planner from using one if there are other methods available. Thus, Sort is still utlised in the AQP, although cost is a lot higher."
        explanation.append(string)

    if (qep_results.count('Nested Loop') == aqp_results.count('Nested Loop') and aqp_results.count('Nested Loop') > 0):
        string = "It is impossible to suppress nested loops for this query entirely. Turning this variable off discourages the planner from using one if there are other methods available. Thus, Nested Loop is still utlised in the AQP, although cost is a lot higher."
        explanation.append(string)

    if (qep_results.count('Material') == aqp_results.count('Material') and aqp_results.count('Material') > 0):
        string = "It is impossible to suppress material for this query entirely. Turning this variable off discourages the planner from using one if there are other methods available. Thus, Material is still utlised in the AQP, although cost is a lot higher."
        explanation.append(string)
    
    return explanation

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
    print(raw_results,'\n')

    # Get JSON string
    raw_results = json.dumps(raw_results)
    # print(raw_results,'\n')

    # Convert JSON string to dict
    results = json.loads(raw_results)
    # print(results,'\n')

    # Call strip_to_plan function to remove unneccesary data in dict
    imp_results = strip_unneeded_data(results)
    print(imp_results,'\n')

    results, total_cost, tree = process_plan_dict(imp_results, "", 0, "")
    tree_levels = 0
    print(results, total_cost, tree)

    # data = print_results
    # data = textwrap.wrap(data, 6)
    print('Data fetched successfully\n')

    conn.close()

    # Identify tables mentioned in query
    tables_text = from_text.strip('FROM ')
    tables = tables_text.split(',')
    print('Tables are: ', tables, '\n')

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
    cur.execute(explain_command)
    raw_results = cur.fetchall()
    print(raw_results,'\n')

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
    print(imp_results)

    results, total_cost, tree = process_plan_dict(imp_results, "", 0, "")
    tree_levels = 0
    print(results, total_cost, tree)

    # data = print_results
    # data = textwrap.wrap(data, 6)
    print('Data fetched successfully\n')

    conn.close()

    # Identify tables mentioned in query
    tables_text = from_text.strip('FROM ')
    tables = tables_text.split(',')
    print('Tables are: ', tables, '\n')

    return results, total_cost, tree
