import argparse
import pandas as pd
import sqlite3
import re
from asset import buildAsset, assignAsset
from encryption import encrypto

def create_table():
    try:
        conn = sqlite3.connect('asset_database.db')
        cursor = conn.cursor()

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
    except Exception as e:
        print(e)
        exit(1)

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
    conn = sqlite3.connect('asset_database.db')

    #Insert New Asset
    conn.execute("""INSERT INTO ASSETS(NAME, LICENSE, QUANTITY, HOSTNAME, EXPIRES)\
                VALUES (?, ?, ?, ?, ?)""",(name, key_object.encrypt(license), quantity, hostname, expire))
    
    conn.commit()

    conn.close()

def del_asset(usrInput):
    
    conn = sqlite3.connect('asset_database.db')

    #Delete Asset
    conn.execute("DELETE FROM ASSETS WHERE ID = {0}".format(usrInput))

    #Restart Index to next available ID
    conn.execute("DELETE FROM SQLITE_SEQUENCE WHERE NAME = 'ASSETS'")
        
    conn.commit()

    conn.close()
   
def update_asset(key_object):
    '''
        :Param updateIndex - select updates the index row
        :Param updateColumn - select updates the particular column field
        :Param setValue 
    '''
    updateIndex = input("Which Index (ID) would you like to update? ")
    updateColumn = input("Which Column would you like to update? ").upper()
    setValue = input("New Value? ")

    conn = sqlite3.connect('asset_database.db')

    cursor = conn.cursor()
    
    columns = ["ID","NAME","LICENSE","QUANTITY", "HOSTNAME", "EXPIRES"]

    try:
        #encrypt the license if they want to change it
        if updateColumn not in columns:
            raise Exception ("Attempt to update unknown column: {0}".format(updateColumn))
        
        elif updateColumn == 'LICENSE':
            setValue = key_object.encrypt(setValue)
            setValue = setValue.decode()

            sql_update = "UPDATE ASSETS SET {0} = ? WHERE ID = ?".format(updateColumn)
            cursor.execute(sql_update, [setValue, updateIndex])

        elif updateColumn == 'EXPIRES':
            if re.search((r"[\d]{1,2}/[\d]{1,2}/[\d]{2}"), setValue):
                sql_update = "UPDATE ASSETS SET {0} = ? WHERE ID = ?".format(updateColumn)
                cursor.execute(sql_update, [setValue, updateIndex])

            else:
                print('Invalid date format. mm/dd/yyyy')
                exit(1)
        else:
            sql_update = "UPDATE ASSETS SET {0} = ? WHERE ID = ?".format(updateColumn)
            cursor.execute(sql_update, [setValue, updateIndex])
    
        conn.commit()
    except Exception as e:
        print(e)

    conn.close()

def select_asset(key_object):
    conn = sqlite3.connect('asset_database.db')

    cursor = conn.execute('SELECT * FROM ASSETS')
    
    for row in cursor:
        print('ID:', row[0], ' Name:', row[1], ' License:', key_object.decrypt(row[2]), ' Quantity:', row[3], ' Hostname:', row[4], ' Expires:', row[5])

    conn.commit()

    conn.close()

def export_asset(export, key_object):
    import csv
    try:
        conn = sqlite3.connect('asset_database.db')

        cursor = conn.execute('SELECT * FROM ASSETS')

        #open/create export .csv file
        file = open(export,'a+')

        #write column headers
        file.write('ID, NAME, LICENSE, QUANTITY, HOSTNAME, EXPIRES\n')

        #write database data to .csv
        for row in cursor:
            file.write('{0}, {1}, {2}, {3}, {4}, {5}\n'.format(row[0], row[1], key_object.decrypt(row[2]), row[3], row[4], row[5]))
        
        file.close()
    except Exception as e:
        print(e)
        
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Asset Management Database')
    parser.add_argument('-c', action='store_true', dest='spreadsheet', help='Parse through import.csv file')
    parser.add_argument('-d', action='store_true', dest='delete', help='Delete Asset')
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
    elif export:
        export_asset(export, key_object)
    else:
        build, assign = create_asset(name, hostname, license, quantity, expire)
        
        add_asset(name=build.get_name(), hostname=assign.get_hostname(), license=build.get_license(), \
                quantity=build.get_quantity(), expire=build.get_expire(), key_object=key_object)