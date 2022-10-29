import psycopg2
import textwrap
import re
 
 # Postgres TCP-H database details
DB_NAME = "TPC-H"
DB_USER = "postgres"
DB_PASS = "123 "
DB_HOST = "localhost"
DB_PORT = "5432"

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