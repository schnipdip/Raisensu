from asset import buildAsset, assignAsset
from encryption import encrypto
import pandas as pd
import argparse
import psycopg2
import sqlite3
import re

def get_configParser():
    import configparser

    config = configparser.ConfigParser()
    config.read('database_settings.ini')

    return config

def get_databaseType():
    #get configparser
    config = get_configParser()

    #get database type
    databaseType = config['database_type']['type']

    return databaseType

def connect_sqlite():
    #get configparser
    config = get_configParser()

    sqliteDatabase = config['database_sqlite']['sqlite_database']

    conn = sqlite3.connect(sqliteDatabase)
    cursor = conn.cursor()

    return conn, cursor

def connect_postgres():
    #get configparser
    config = get_configParser()

    #import configuration information to connect to remote postrgre database
    postgresServer   = config['database_postgres']['postgres_server']
    postgrestPort    = config['database_postgres']['postgres_port']
    postgresDatabase = config['database_postgres']['postgres_database']
    postgresUsername = config['database_postgres']['postgres_username']
    postgresPassword = config['database_postgres']['postgres_password']

    conn = psycopg2.connect(host=postgresServer,
                            database=postgresDatabase,
                            port=postgrestPort,
                            user=postgresUsername,
                            password=postgresPassword)
    cursor = conn.cursor()

    conn.commit()

    return conn, cursor

def decide_databaseType():
    #get database type
    databaseType = get_databaseType()

    if databaseType == 'sqlite':
        conn, cursor = connect_sqlite()
    elif databaseType == 'postgres':
        conn, cursor = connect_postgres()
    else:
        print('Unsupported Database Type.')
        exit(0)

    return conn, cursor

def create_table():
    conn, cursor = decide_databaseType()

    #get database type
    databaseType = get_databaseType()

    try:
        if databaseType == 'sqlite':
            sql_create_asset_table = ('''CREATE TABLE IF NOT EXISTS ASSETS (
            ID        INTEGER       PRIMARY KEY AUTOINCREMENT,
            NAME      VARCHAR(255)  NOT NULL,
            LICENSE   VARCHAR(255)  NOT NULL,
            QUANTITY  INT           NOT NULL,
            HOSTNAME  VARCHAR(255)  NOT NULL,
            EXPIRES   VARCHAR(255)  NOT NULL);''')

            cursor.execute(sql_create_asset_table)

            #Commit Changes to Database
            conn.commit()

            #Close Database Connection
            conn.close()
        elif databaseType == 'postgres':
            sql_create_asset_table = ('''CREATE TABLE IF NOT EXISTS ASSETS (
            ID        SERIAL PRIMARY KEY,
            NAME      TEXT  NOT NULL,
            LICENSE   TEXT  NOT NULL,
            QUANTITY  INT   NOT NULL,
            HOSTNAME  TEXT  NOT NULL,
            EXPIRES   TEXT  NOT NULL);''')

            cursor.execute(sql_create_asset_table)

            #Commit Changes to Database
            conn.commit()

            #Close Database Connection
            conn.close()
    except Exception as e:
        print(e)
        exit(0)

def get_csv(key_object):
    #imports csv file
    data = pd.read_csv('import.csv')

    #iterate through csv get variables
    df = pd.DataFrame(data, columns=['name', 'license', 'hostname', 'quantity','expires'])

    counter = 0
    while counter < len(df):
        name = df.loc[counter, 'name']
        license = df.loc[counter, 'license']
        hostname = df.loc[counter, 'hostname']
        quantity = df.loc[counter, 'quantity']
        expire = df.loc[counter, 'expires']

        build, assign = create_asset(name, hostname, license, quantity, expire)

        add_asset(name=build.get_name(), hostname=assign.get_hostname(), license=build.get_license(), \
                quantity=build.get_quantity(), expire=build.get_expire(), key_object=key_object)

        counter += 1

def get_encrypt():
    #create encrypt object
    key_object = encrypto('secret.key')

    return (key_object)

def create_asset(name, hostname, license, quantity, expire):
    build = buildAsset(name, license, quantity, expire)
    assign = assignAsset(hostname)

    return (build, assign)

def add_asset(name, hostname, license, quantity, expire, key_object):
    #conn = sqlite3.connect('asset_database.db')
    conn, cursor = decide_databaseType()

    #get database type
    databaseType = get_databaseType()

    if databaseType == 'sqlite':
        #Insert New Asset
        conn.execute("""INSERT INTO ASSETS(NAME, LICENSE, QUANTITY, HOSTNAME, EXPIRES)\
                    VALUES (?, ?, ?, ?, ?)""",(name, key_object.encrypt(license), quantity, hostname, expire))

        conn.commit()

        conn.close()
    elif databaseType == 'postgres':
        #encrypt the license
        encrypt_license = key_object.encrypt(license)

        #convert the byte code to str
        encrypt_license = encrypt_license.decode('utf-8')

        #Insert New Asset
        cursor.execute("""INSERT INTO ASSETS(NAME, LICENSE, QUANTITY, HOSTNAME, EXPIRES)\
                    VALUES (%s, %s, %s, %s, %s)""",(name, encrypt_license, quantity, hostname, expire))

        conn.commit()

        conn.close()

def del_asset(usrInput):
    #conn = sqlite3.connect('asset_database.db')
    conn, cursor = decide_databaseType()

    #get database type
    databaseType = get_databaseType()

    if databaseType == 'sqlite':
        #Delete Asset
        conn.execute("DELETE FROM ASSETS WHERE ID = {0};".format(usrInput))

        #Restart Index to next available ID
        conn.execute("DELETE FROM SQLITE_SEQUENCE WHERE NAME = 'ASSETS';")

        conn.commit()

        conn.close()
    elif databaseType == 'postgres':
        #Delete Asset
        cursor.execute("DELETE FROM ASSETS WHERE ID = %s;",(usrInput))

        #Restart Index to next available ID
        cursor.execute("SELECT setval('assets_id_seq', max(ID)) FROM ASSETS;")

        conn.commit()

        conn.close()

def del_all_asset():
    #conn = sqlite3.connect('asset_database.db')
    conn, cursor = decide_databaseType()

    #get database type
    databaseType = get_databaseType()

    if databaseType == 'sqlite':
        #Delete Asset
        conn.execute("DELETE FROM ASSETS;")

        #Restart Index to next available ID
        conn.execute("DELETE FROM SQLITE_SEQUENCE WHERE NAME = 'ASSETS';")

        conn.commit()

        conn.close()
    elif databaseType == 'postgres':
        #Delete Asset
        cursor.execute("DELETE FROM ASSETS;")

        #Restart Index to next available ID
        cursor.execute("ALTER SEQUENCE assets_id_seq RESTART;")

        conn.commit()

        conn.close()

def update_asset(key_object):
    '''
        :Param updateIndex - select updates the index row
        :Param updateColumn - select updates the particular column field
        :Param setValue - set the new value
    '''

    updateIndex = input("Which Index (ID) would you like to update? ")
    updateColumn = input("Which Column would you like to update? ").upper()
    setValue = input("New Value? ")

    #conn = sqlite3.connect('asset_database.db')
    conn, cursor = decide_databaseType()

    cursor = conn.cursor()

    #get database type
    databaseType = get_databaseType()

    columns = ["ID","NAME","LICENSE","QUANTITY", "HOSTNAME", "EXPIRES"]

    try:
        #encrypt the license if they want to change it
        if updateColumn not in columns:
            raise Exception ("Attempted to update unknown column: {0}".format(updateColumn))

        elif updateColumn == 'LICENSE':
            #encrypt updated value
            setValue = key_object.encrypt(setValue)
            setValue = setValue.decode()

            if databaseType == 'sqlite':
                sql_update = "UPDATE ASSETS SET {0} = ? WHERE ID = ?;".format(updateColumn)
                cursor.execute(sql_update, [setValue, updateIndex])

            elif databaseType == 'postgres':
                sql_update = "UPDATE ASSETS SET {0} = %s WHERE ID = %s;".format(updateColumn)
                cursor.execute(sql_update, [setValue, updateIndex])


        elif updateColumn == 'EXPIRES':
            if re.search((r"[\d]{1,2}/[\d]{1,2}/[\d]{2}"), setValue):
                if databaseType == 'sqlite':
                    sql_update = "UPDATE ASSETS SET {0} = ? WHERE ID = ?;".format(updateColumn)
                    cursor.execute(sql_update, [setValue, updateIndex])

                elif databaseType == 'postgres':
                    sql_update = "UPDATE ASSETS SET {0} = %s WHERE ID = %s;".format(updateColumn)
                    cursor.execute(sql_update, [setValue, updateIndex])
            else:
                print('Invalid date format. mm/dd/yyyy')
                exit(0)
        else:
            if databaseType == 'sqlite':
                sql_update = "UPDATE ASSETS SET {0} = ? WHERE ID = ?;".format(updateColumn)
                cursor.execute(sql_update, [setValue, updateIndex])

            elif databaseType == 'postgres':
                sql_update = "UPDATE ASSETS SET {0} = %s WHERE ID = %s;".format(updateColumn)
                cursor.execute(sql_update, [setValue, updateIndex])
    except Exception as e:
        print(e)

    conn.commit()

    conn.close()

def select_asset(key_object):
    #conn = sqlite3.connect('asset_database.db')
    conn, cursor = decide_databaseType()

    #get database type
    databaseType = get_databaseType()

    if databaseType == 'sqlite':
        selectAll = conn.execute('SELECT * FROM ASSETS ORDER BY ID')
        for row in selectAll:
            print('ID:', row[0], ' Name:', row[1], ' License:', key_object.decrypt(row[2]), ' Quantity:', row[3], ' Hostname:', row[4], ' Expires:', row[5])

    elif databaseType == 'postgres':
        cursor.execute('SELECT * FROM ASSETS ORDER BY ID')

        selectAll = cursor.fetchall()

        for row in selectAll:
            print('ID:', row[0], ' Name:', row[1], ' License:', key_object.decrypt(row[2]), ' Quantity:', row[3], ' Hostname:', row[4], ' Expires:', row[5])


    #TODO: add the ability to decrypt only what your unique secret.key can decrypt. Display everything else as encrypted.
    #for row in cursor:

    conn.commit()

    conn.close()

def export_asset(export, key_object):
    import csv

    try:
        #conn = sqlite3.connect('asset_database.db')
        conn, cursor = decide_databaseType()

        #get database type
        databaseType = get_databaseType()

        if databaseType == 'sqlite':
            selectAll = conn.execute('SELECT * FROM ASSETS;')

            #open/create export .csv file
            file = open(export,'a+')

            #write column headers
            file.write('ID, NAME, LICENSE, QUANTITY, HOSTNAME, EXPIRES\n')

            #write database data to .csv
            for row in selectAll:
                file.write('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(str(row[0]), row[1], key_object.decrypt(row[2]), row[3], row[4], row[5]))

            file.close()
        elif databaseType == 'postgres':
            cursor.execute('SELECT * FROM ASSETS;')

            #open/create export .csv file
            file = open(export,'a+')

            #write column headers
            file.write('ID, NAME, LICENSE, QUANTITY, HOSTNAME, EXPIRES\n')

            selectAll = cursor.fetchall()

            for row in selectAll:
                write = (row[0], row[1], key_object.decrypt(row[2]), row[3], row[4], row[5])

                file.write(str(write).replace('(', '').replace(')',''))
                file.write('\n')

            file.close()

    except Exception as e:
        print(e)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Asset Management Database')
    parser.add_argument('-c', action='store_true', dest='spreadsheet', help='Parse through import.csv file')
    parser.add_argument('-d', action='store_true', dest='delete', help='Delete Asset')
    parser.add_argument('--delete_all', action='store_true', dest='deleteAll', help='Delete all records in table')
    parser.add_argument('-t', action='store_true', dest='database', help='Create a New Table if it has not been created already')
    parser.add_argument('-v', action='store_true', dest='view', help='View all entries')
    parser.add_argument('-u', action='store_true', dest='update', help='Update an entry')
    parser.add_argument('-n', action='store', dest='name', type=str, help='Name of the License Product')
    parser.add_argument('-a', action='store', dest='hostname', type=str, help='Name of the hostname the license is attached to')
    parser.add_argument('-l', action='store', dest='license', type=str, help='License data')
    parser.add_argument('-q', action='store', dest='quantity', type=int, default=0, help='Total Number of licenses')
    parser.add_argument('-x', action='store', dest='expire', default=0, help='License expiration date')
    parser.add_argument('-e', action='store', dest='export', type=str, help='Export SQL Database to CSV file')

    result = parser.parse_args()

    name = result.name
    hostname = result.hostname
    license = result.license
    quantity = result.quantity
    delete = result.delete
    spreadsheet = result.spreadsheet
    database = result.database
    view = result.view
    update = result.update
    export = result.export
    expire = result.expire
    deleteAll = result.deleteAll

    #configure encryption
    key_object = get_encrypt()

    if update is True:
        select_asset(key_object)
        update_asset(key_object)
    elif view is True:
        select_asset(key_object)
    #check if database table has been set
    elif database is True:
        create_table()
    #check if spreadsheet has been set
    elif spreadsheet is True:
        get_csv(key_object)
    #check if delete has been set
    elif delete is True:
        while delete is True:
            #if identifying name is not set, prompt for asset name
            if name != '':
                usrInput = input('Enter the ID of the Asset to delete or return list (y): ')
                if usrInput == 'y' or usrInput == 'Y':
                    select_asset(key_object)
                elif usrInput.isdigit():
                    #deletes user entry
                    del_asset(usrInput)
                    exit(0)
                else:
                    print('Invalid Entry, Must Be An Integer')
                    exit(1)
    elif deleteAll is True:
        accept = input('Confirm you want to delete all records (y): ')
        accept = accept.lower()
        if accept == 'y':
            del_all_asset()
        else:
            exit(0)
    elif export:
        export_asset(export, key_object)
    else:
        build, assign = create_asset(name, hostname, license, quantity, expire)

        add_asset(name=build.get_name(), hostname=assign.get_hostname(), license=build.get_license(), \
                quantity=build.get_quantity(), expire=build.get_expire(), key_object=key_object)
