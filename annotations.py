import psycopg2
import textwrap
import re
import json
 
 # Postgres TCP-H database details
DB_NAME = "TPC-H"
DB_USER = "postgres"
DB_PASS = ""
DB_HOST = "localhost"
DB_PORT = "5432"

def setpassword(password):
    global DB_PASS
    DB_PASS = password

def explain(select_text, from_text, where_text):

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
    explain_command = 'EXPLAIN VERBOSE ' + query
    cur = conn.cursor()
    cur.execute(explain_command)
    data = str(cur.fetchall())
    print(data)
    # data = textwrap.wrap(data, 6)
    print('Data fetched successfully')
    conn.close()

    # Identify tables mentioned in query
    tables_text = from_text.strip('FROM ')
    tables = tables_text.split(',')
    print('Tables are: ', tables)
    
    # Find the info pertaining to each table, then return this value to be displayed!
    output = []
    for table_name in tables:
        search_string = "'" + '(.+?)' + 'on public.' + table_name

        m = re.search(search_string, data)
        if m:
            found = m.group(1)
            print(found + 'on public.' + table_name)
            output.append(found + 'on public.' + table_name)


    # Identify joins (if any)

    print(output)
    return data, output

def testexplain(select_text, from_text, where_text):

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
    # explain_command = 'EXPLAIN VERBOSE ' + query
    explain_command = 'EXPLAIN (COSTS true, FORMAT json) ' + query
    cur = conn.cursor()
    cur.execute(explain_command)
    results = cur.fetchall()
    moretestresults = json.dumps(results)
    testjsondict = json.loads(moretestresults)
    # print("here")
    # print(testjsondict)
    # print(testjsondict[0])
    # print(type(testjsondict))
    # print(len(testjsondict))

    testresults = striptoplan(testjsondict)
    # print(testresults)
    # print(len(testresults))
    printresults = processplandict(testresults, "")

    print(printresults)
    data = printresults
    # data = textwrap.wrap(data, 6)
    print('Data fetched successfully')

    conn.close()

    # Identify tables mentioned in query
    tables_text = from_text.strip('FROM ')
    tables = tables_text.split(',')
    print('Tables are: ', tables)
    
    # Find the info pertaining to each table, then return this value to be displayed!
    output = []
    for table_name in tables:
        search_string = "'" + '(.+?)' + 'on public.' + table_name

        m = re.search(search_string, data)
        if m:
            found = m.group(1)
            print(found + 'on public.' + table_name)
            output.append(found + 'on public.' + table_name)


    # Identify joins (if any)

    print(output)
    return data, output

def processplandict(dictdata, stringcollector):
    # process the dictionary to retrieve query plan information and put them into a string
    for item in dictdata.keys():
        if item=="Plan":
            stringcollector = processplandict(dictdata[item], stringcollector)
        elif item=="Node Type":
            print(dictdata[item])
            stringcollector = stringcollector + str(dictdata[item]) + " "
        elif item=="Plans":
            anotherdict = striptoplan(dictdata[item])
            stringcollector = processplandict(anotherdict, stringcollector)

    return stringcollector

def striptoplan(jsonobject):
    # strip away extra layers of the json object to get to the dictionary for processing
    # print("execute")
    if not isinstance(jsonobject, dict):
        return striptoplan(jsonobject[0])
    else:
        return jsonobject