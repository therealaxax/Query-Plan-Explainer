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

# def disable_config(config):
#     # Connect to postgres database
#     print("DISABLED " + config)
#     conn = psycopg2.connect(database=DB_NAME,
#                             user=DB_USER,
#                             password=DB_PASS,
#                             host=DB_HOST,
#                             port=DB_PORT)
#     print("Database connected successfully")

#     cur = conn.cursor()
#     cur.execute('SET ' + config + ' TO off;')

def set_password(password):
    global DB_PASS
    DB_PASS = password

def process_plan_dict(imp_results, string_collector_select, string_collector_from, string_collector_where):
    # process the dictionary to retrieve query plan information and put them into a string
    for item in imp_results.keys():
        if item=="Plan":
            string_collector_select, string_collector_from, string_collector_where = process_plan_dict(imp_results[item], string_collector_select, string_collector_from, string_collector_where)
        elif item=="Plans":
            # stripped = strip_unneeded_data(imp_results[item])
            # string_collector_select, string_collector_from, string_collector_where = process_plan_dict(stripped, string_collector_select, string_collector_from, string_collector_where)

            all_plans = imp_results[item]   # a list
            for plan in all_plans:
                string_collector_select, string_collector_from, string_collector_where = process_plan_dict(plan, string_collector_select, string_collector_from, string_collector_where)


        elif item=="Node Type":
            print(imp_results[item])
            print(imp_results)
            if imp_results[item] in SELECT_KEYWORDS:
                string_collector_select = string_collector_select + " | " + str(imp_results[item]) 
            elif imp_results[item] in FROM_KEYWORDS:
                string_collector_from = string_collector_from + " | " + str(imp_results[item]) 
            elif imp_results[item] in WHERE_KEYWORDS:
                string_collector_where = string_collector_where + " | " + str(imp_results[item]) 
            
        elif item=="Hash Cond":
            string_collector_where = string_collector_where + " -> " + str(imp_results[item]) + '\n'
        elif item=="Relation Name":
            string_collector_from = string_collector_from + " on " + str(imp_results[item]) + '\n'
        elif item=="Merge Cond":
            string_collector_where = string_collector_where + " -> " + str(imp_results[item]) + '\n'
        elif item=="Sort Key":
            string_collector_where = string_collector_where + " on " + str(imp_results[item]) + '\n'
        elif item=="Group Key":
            string_collector_select = string_collector_select + " on " + str(imp_results[item]) + '\n'
        

    return string_collector_select, string_collector_from, string_collector_where

def strip_unneeded_data(json_object):
    # strip away extra layers of the json object to get to the dictionary for processing
    # print("execute")
    if not isinstance(json_object, dict):
        return strip_unneeded_data(json_object[0])
    else:
        return json_object

def aqp_test_explain(select_text, from_text, where_text, AQP_CONFIGS_2):

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

    select_results, from_results, where_results = process_plan_dict(imp_results, "", "", "")
    print(select_results, from_results, where_results)

    # data = print_results
    # data = textwrap.wrap(data, 6)
    print('Data fetched successfully\n')

    conn.close()

    # Identify tables mentioned in query
    tables_text = from_text.strip('FROM ')
    tables = tables_text.split(',')
    print('Tables are: ', tables, '\n')

    return select_results, from_results, where_results

def test_explain(select_text, from_text, where_text):

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

    select_results, from_results, where_results = process_plan_dict(imp_results, "", "", "")
    print(select_results, from_results, where_results)

    # data = print_results
    # data = textwrap.wrap(data, 6)
    print('Data fetched successfully\n')

    conn.close()

    # Identify tables mentioned in query
    tables_text = from_text.strip('FROM ')
    tables = tables_text.split(',')
    print('Tables are: ', tables, '\n')

    return select_results, from_results, where_results
    

    




# def print_tree(root):
#     print_tree(root, horizontal=False)