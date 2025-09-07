from .main import *
def get_insert_tables(dbName,dbType,env_path = None):
    tablePath = get_table_path(dbName,dbType,env_path=env_path)
    return safe_read_from_json(tablePath)
def get_insert_table(tableName):
    insertTable = [table for table in TableManager().insert_list if tableName == table.get('tableName').lower()]
    if insertTable:
        insertTable= insertTable[0]
    return insertTable or {}
def get_insert(tableName):
    tableName = tableName.lower()
    return TableManager().get_insert(tableName)
    
def add_unique_header(uniqueHeader,tableName,dbName,dbType):
    TableManager().add_unique_header(uniqueHeader,tableName,dbName,dbType)
def add_table_config(dbName,dbType):
    TableManager().add_table_config(dbName,dbType)
def get_table_path(dbName,dbType,env_path=None):
    key = f"{dbName.upper()}_{dbType.upper()}_CONFIGPATH"
    return get_env_value(path=env_path or TableManager().env_path,key=key)


def getInsertType(tableName):
    return TableManager().get_insert(tableName)

async def search_Db(tableName, searchValue,**kwargs):
    insertType = getInsertType(tableName)
    if not insertType:
        print(f"No data structure for {tableName}")
        return

    search_query = getSearchQuery(insertType.get('tableName'), '*', insertType.get('columnSearch'))
    try:
        result = await getQuery(search_query, (searchValue,))
        if result:
            print(f"Found in {tableName}: {result}")
            return result
        else:
            print(f"No data found in {tableName} for {searchValue}")
    except Exception as e:
        print(f"Error searching in {tableName}: {str(e)}")
        
async def insert_Db(tableName, searchValue, insertValue,**kwargs):
    insertType = getInsertType(tableName)
    if not insertType:
        print(f"No insert type found for table: {tableName}")
        return

    # Check if entry exists
    existing_entry = await search_Db(insertType.get('tableName'), searchValue)
    if existing_entry:
        print(f"Entry already exists in {tableName} with value {searchValue}")
        return existing_entry

    if not isinstance(insertValue, tuple):
        insertValue = (searchValue, dump_if_json(insertValue))
    
    insert_query = "INSERT INTO {} ({}) VALUES ({})".format(insertType.get('tableName'), insertType('insertQuery'), getInsertQueryS(insertType('insertQuery')))
    try:
        await getQuery(insert_query, insertValue)
        #print(f"Inserted into {tableName}: {searchValue}")
    except Exception as e:
        print(f"Error using {insert_query} inserting {instype} with a value of {query} into {tableName}: {str(e)}")




async def universal_db_function(method,  params, check_identical_params=None, doNotCall=None, url=None, data={}):
    # Ensure the table is ready for operations
    insertType = getInsertType(method)
    if not inputs:
        print(f"Unable to find or create table: {method}")
        return

    # Extract the unique identifier for database operations
    unique_identifier = params[0]

    # Attempt to find an existing entry in the database
    existing_entry = await search_Db(tableName, unique_identifier)

    # Determine if the existing entry should be ignored based on the parameters
    if check_identical_params and existing_entry:
        all_match = all(params[k] == existing_entry.get(k, None) for k in params if k in existing_entry)
        if not all_match:
            existing_entry = None

    # If instructed not to make external calls and an entry exists, return it
    if doNotCall and existing_entry:
        return existing_entry

    # If there's no existing entry or it's ignored based on parameters, make an external call if allowed
    if not existing_entry and not doNotCall:
        response_data = await (asyncPostRequest(url=url, data=data, endpoint=method) if url else makeLimitedCall(method, params))

        # Handle unsuccessful responses or errors
        if not response_data or (isinstance(response_data, dict) and response_data.get('error')):
            print(f"Failed to get a valid response for {unique_identifier} in {tableName}: {response_data}")
            return response_data

        # If the response is successful, insert it into the database
        await insert_Db(insertType.get('tableName'), unique_identifier, (unique_identifier, dump_if_json(response_data)))
        #print(f"Inserted {unique_identifier} in {tableName}")
        return response_data

    # Return the existing entry if all checks pass and no external call is made
    return existing_entry

def getSearchQuery(tableName, valueSelect='*', columnName=''):
    return f"SELECT {valueSelect} FROM {tableName} WHERE {columnName} = $1"

def getsearchquery(tableName):
    insertType = getInsertType(tableName)
    return getSearchQuery(insertType.get('tableName'), '*', insertType['columnSearch'])

def getInsertQueryS(insertQuery):
    parts = [part.strip() for part in insertQuery[1:-1].split(',')]
    placeholders = ', '.join(f'${i + 1}' for i in range(len(parts)))
    return placeholders


def setup_database(tables, conn):
    """ Create database tables based on provided configurations """
    cur = conn.cursor()
    try:
        for table in tables:
            cur.execute(table['table'])
        conn.commit()
    except psycopg2.Error as e:
        print("Error setting up database tables:", e)
        conn.rollback()
    finally:
        cur.close()

def fetch_data(search_query, search_value, conn):
    """ Fetch data from the database using the specified query and value """
    cur = conn.cursor()
    try:
        cur.execute(search_query, (search_value,))
        return cur.fetchone()
    finally:
        cur.close()

def insert_data(insert_query, values, conn):
    """ Insert data into the database using the specified query and values """
    cur = conn.cursor()
    try:
        cur.execute(insert_query, values)
        conn.commit()
    except psycopg2.Error as e:
        print("Failed to insert data:", e)
        conn.rollback()
    finally:
        cur.close()
        
def search_multiple_fields(query,conn,**kwargs):
    """Search the database using a query."""
    cur = conn.cursor()
    try:
        cur.execute(query)
        return cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error querying JSONB data: {e}")
    finally:
        cur.close()
        conn.close()
def perform_database_operations(operation_type, tableName, searchValue,insertValue, conn):
    """ Perform dynamic database operations based on type and table info """
    insertInfo = get_insert(tableName)
    if operation_type == 'fetch':
        return fetch_data(insertInfo['searchQuery'], searchValue, conn)
    elif operation_type == 'insert':
        insert_data(insertInfo['insertQuery'], searchValue, conn)

def fetchFromDb(insertInfo,searchValue,conn):
    cached_response = fetch_data(insertInfo['searchQuery'], searchValue, conn)
    if cached_response:
        return cached_response

def insert_intoDb(insertInfo,searchValue,insertValue,conn):
    if isinstance(insertValue,dict):
        insertValue = json.dumps(insertValue)
    return insert_data(insertInfo['insertQuery'], (searchValue,insertValue), conn)
