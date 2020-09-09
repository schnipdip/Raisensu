from encryption import encrypto
from time import sleep
import configparser
import datetime
import logging
import smtplib

#TODO: If monitor finds no items expiring, don't send SMTP message
#TODO: Add POSTGRES Support

def get_configParser():
    config = configparser.ConfigParser()
    config.read('monitor_settings.ini')

    return config

def connect_sqlite():
    import sqlite3

    #get configparser
    config = get_configParser()

    sqliteDatabase = config['database_sqlite']['sqlite_database']

    conn = sqlite3.connect(sqliteDatabase)
    cursor = conn.cursor()

    return conn, cursor

def connect_postgres():
    import psycopg2

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

def get_encrypt():
    #create encrypt object
    key_object = encrypto('secret.key')

    return key_object

def get_logger():
    #creates logger object
    logger = logging.getLogger(__name__)

    return logger

def set_logger(logger):
    #set log level
    logger.setLevel(logging.INFO)

    #define file handler and set formatter
    file_handler = logging.FileHandler('raisensu_log.log')
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)

    #add file handler to logger
    logger.addHandler(file_handler)

def get_databaseType():
    #get configparser
    config = get_configParser()

    #get database type
    databaseType = config['database_type']['type']

    return databaseType

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

def get_smtp_state(config):
    smtpState = config['email']['enable_email'].upper()

    return smtpState

def get_smtp(config):
    smtpServer = config['email']['smtp_server']
    smtpPort = config['email']['smtp_port']
    smtpObj = smtplib.SMTP(smtpServer, smtpPort)

    return smtpObj

def set_smtp(notify, config):
    from email.mime.text import MIMEText

    receiver_email = config['email']['receiver_email']
    sender_email = config['email']['sender_email']

    message = MIMEText('Here is the list of licenses that are about to expire:\n{}'.format(notify))
    message['Subject'] = '[ALERT] Raisensu License Asset Monitoring'
    message['From'] = sender_email
    message['To'] = receiver_email

    return message

def send_smtp(smtpObj, message, config):
    #read in monitor_settings file for SMTP objects
    config = get_configParser()

    receiver_email = config['email']['receiver_email']
    sender_email = config['email']['sender_email']
    smtp_username = config['email']['smtp_username']
    smtp_password = config['email']['smtp_password']

    try:
        #identify prompting server for supported features
        smtpObj.ehlo()

        #start tls connection if server supports tls
        if smtpObj.has_extn('STARTTLS'):
            smtpObj.starttls()
            smtpObj.ehlo()

        smtpObj.login(smtp_username, smtp_password)
        smtpObj.sendmail(sender_email, receiver_email, message.as_string())
    except Exception as e:
        print (e)
    finally:
        smtpObj.quit()

def diff_dates(date_today, comp_date):
    #convert comp_date to date object
    date_time_today = datetime.datetime.strptime(date_today, '%m/%d/%Y')
    date_time_comp = datetime.datetime.strptime(comp_date, '%m/%d/%Y')

    #return remaining days
    return abs(date_time_comp - date_time_today).days

def get_sql_statement(config, key_object, logger):
    databaseType = get_databaseType()

    conn, cursor = decide_databaseType()

    try:
        if databaseType == 'sqlite':
            column = conn.execute('SELECT ID, NAME, LICENSE, EXPIRES, HOSTNAME FROM ASSETS')
        elif databaseType == 'postgres':
            column = cursor.execute('SELECT ID, NAME, LICENSE, EXPIRES, HOSTNAME FROM ASSETS')
            column = cursor.fetchall()
    except Exception as e:
        print(e)

    #get todays date
    today = datetime.date.today()

    #str today day,month,year
    date_today = today.strftime("%m/%d/%Y")

    #read in from monitor_settings.ini
    notify_1 = int(config['dates']['notify_me_in_days_01'])
    notify_2 = int(config['dates']['notify_me_in_days_02'])
    notify_3 = int(config['dates']['notify_me_in_days_03'])

    #create a list of licenses going to expire
    state_store = []

    for row in column:
        '''
            row[0] return type: int -> ID
            row[1] return type: str -> NAME
            row[2] return type: str -> LICENSE
            row[3] return type: str -> EXPIRES
            row[4] return type: str -> HOSTNAME
        '''
        day_diff = diff_dates(date_today, row[3])

        try:
            if day_diff == notify_1:
                logger.info('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE {} ON THE HOST {}'.format(notify_1, row[1], key_object.decrypt(row[2]), row[3], row[4]))
                state_store.append(row)

                yield('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE {} ON THE HOST {}'.format(notify_1, row[1], key_object.decrypt(row[2]), row[3], row[4]))
            elif day_diff == notify_2:
                logger.info('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE {} ON THE HOST {}'.format(notify_2, row[1], key_object.decrypt(row[2]), row[3], row[4]))
                state_store.append(row)

                yield('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE {} ON THE HOST {}'.format(notify_2, row[1], key_object.decrypt(row[2]), row[3], row[4]))
            elif day_diff == notify_3:
                logger.info('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE {} ON THE HOST {}'.format(notify_3, row[1], key_object.decrypt(row[2]), row[3], row[4]))
                state_store.append(row)

                yield('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE {} ON THE HOST {}'.format(notify_3, row[1], key_object.decrypt(row[2]), row[3], row[4]))
        except Exception as e:
            print (e)

    #exit program safely if no licenses are to be returned.
    if not state_store:
        logger.info('No license expirations found.')
        exit(0)

if __name__ == "__main__":
    #logger
    logger = get_logger()
    set_logger(logger)

    #configparser
    config = get_configParser()

    #check the database backend
    decide_databaseType()

    #encryption
    key_object = get_encrypt()

    notify = get_sql_statement(config, key_object, logger)

    #smptp
    smtpState = get_smtp_state(config)

    bundle_message = []

    if smtpState == "TRUE":
        for note in notify:
            bundle_message.append(note)

        #convert list to string for formatting
        pretty_bundle = ' '.join([str('\n' + item + '\n') for item in bundle_message])

        try:
            smtpObj = get_smtp(config)
            message = set_smtp(pretty_bundle, config)

            send_smtp(smtpObj, message, config)
            sleep(1)
        except Exception as e:
            print(e)