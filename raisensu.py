import argparse
import pandas as pd
import sqlite3
from asset import buildAsset, assignAsset

def get_csv():
    # imports csv file
    data = pd.read_csv('import.csv')

    # iterate through csv get variables
    df = pd.DataFrame(data, columns=['name', 'license', 'hostname', 'quantity'])

    counter = 0
    while counter < len(df):
        '''
            TODO: Can replace these with lambda functions to increase efficiency
        '''
        name = df.loc[counter, 'name']
        license = df.loc[counter, 'license']
        hostname = df.loc[counter, 'hostname']
        quantity = df.loc[counter, 'quantity']
        
        build, assign = create_asset(name, hostname, license, quantity)
        
        add_asset(name=build.get_name(), hostname=assign.get_hostname(), license=build.get_license(), quantity=build.get_quantity())
        
        counter += 1

def create_table():
    try:
        conn = sqlite3.connect('asset_database.db')
        cursor = conn.cursor()

        sql_create_asset_table = ('''CREATE TABLE IF NOT EXISTS ASSETS (
        ID        INTEGER       PRIMARY KEY AUTOINCREMENT,
        NAME      VARCHAR(255)  NOT NULL,
        LICENSE   VARCHAR(255)  NOT NULL,
        QUANTITY  INT           NOT NULL,
        HOSTNAME  VARCHAR(255)  NOT NULL);''')

        cursor.execute(sql_create_asset_table)
        
        # Commit Changes to Database
        conn.commit()

        # Close Database Connection
        conn.close()
    except:
        exit(1)

def create_asset(name, hostname, license, quantity):
    build = buildAsset(name, license, quantity)
    assign = assignAsset(hostname)

    return (build, assign)

def add_asset(name, hostname, license, quantity):
    conn = sqlite3.connect('asset_database.db')

    # Insert New Asset
    conn.execute("""INSERT INTO ASSETS(NAME, LICENSE, QUANTITY, HOSTNAME)\
                VALUES (?, ?, ?, ?)""",(name, license, quantity, hostname))
    
    conn.commit()

    conn.close()

def del_asset(usrInput):
    conn = sqlite3.connect('asset_database.db')

    # Delete Asset
    conn.execute('DELETE FROM ASSETS WHERE ID = ?', (usrInput))

    # Restart Index to next available ID
    conn.execute("DELETE FROM SQLITE_SEQUENCE WHERE NAME = 'ASSETS'")
    
    conn.commit()

    conn.close()

def update_asset():
    '''
        :Param updateIndex - select updates the index row
        :Param updateColumn - select updates the particular column field
        :Param setValue 
    '''

    updateIndex = input("Which Index (ID) would you like to update? ")
    updateColumn = input("Which Column would you like to update? ")
    setValue = input("New Value? ")

    conn = sqlite3.connect('asset_database.db')

    cursor = conn.cursor()
    
    try:
        sql_update = "UPDATE ASSETS SET {0} = '{1}' WHERE ID = {2}".format(updateColumn, setValue, updateIndex)

        cursor.execute(sql_update)
    
        conn.commit()
    except Exception as e:
        print (e)
    conn.close()

def select_asset():
    conn = sqlite3.connect('asset_database.db')

    cursor = conn.execute('SELECT * FROM ASSETS')
    
    for row in cursor:
        print('ID:', row[0], ' Name:', row[1], ' License:', row[2], ' Quantity:', row[3], ' Hostname:', row[4])

    conn.commit()

    conn.close()


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
    
    if update is True:
        select_asset()
        update_asset()
    elif view is True:
        select_asset()
    #check if database table has been set
    elif database is True:
        create_table()
    #check if spreadsheet has been set
    elif spreadsheet is True:
        get_csv()
    #check if delete has been set
    elif delete is True:
        while delete is True:
            #if identifying name is not set, prompt for asset name
            if name is not '':
                usrInput = input('Enter the ID of the Asset to delete or return list (y): ')
                if usrInput == 'y' or usrInput == 'Y':
                    select_asset()
                    pass
                elif usrInput.isdigit():
                    #deletes user entry
                    del_asset(usrInput)
                    exit(0)
                else:
                    print('Invalid Entry, Must Be An Integer')
                    exit(1)
    else:
        build, assign = create_asset(name, hostname, license, quantity)
        
        add_asset(name=build.get_name(), hostname=assign.get_hostname(), license=build.get_license(), quantity=build.get_quantity())
