from encryption import encrypto
from time import sleep
import configparser
import datetime
import sqlite3
import logging
import smtplib

def get_parser():
    config = configparser.ConfigParser()

    return config

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

def get_smtp_state(config):
    #read in monitor_settings file for SMTP objects
    config.read('monitor_settings.ini')

    smtpState = config['email']['enable_email'].upper()

    return smtpState        

def get_smtp(config):
    #read in monitor_settings file for SMTP objects
    config.read('monitor_settings.ini')

    smtpServer = config['email']['smtp_server']
    smtpPort = config['email']['smtp_port']
    smtpObj = smtplib.SMTP(smtpServer, smtpPort)

    return smtpObj

def set_smtp(notify, config):
    from email.mime.text import MIMEText
    
    #read in monitor_settings file for SMTP objects
    config.read('monitor_settings.ini')

    receiver_email = config['email']['receiver_email']
    sender_email = config['email']['sender_email']

    message = MIMEText('Here is the list of licenses that are about to expire:\n{}'.format(notify))
    message['Subject'] = '[ALERT] Raisensu License Asset Monitoring'
    message['From'] = sender_email
    message['To'] = receiver_email

    return message

def send_smtp(smtpObj, message, config):
    #read in monitor_settings file for SMTP objects
    config.read('monitor_settings.ini')

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
    #Read in monitor_settings.ini
    config.read('monitor_settings.ini')

    conn = sqlite3.connect('asset_database.db')

    cursor = conn.execute('SELECT ID, NAME, LICENSE, EXPIRES, HOSTNAME FROM ASSETS')

    #get todays date
    today = datetime.date.today()

    #str today day,month,year
    date_today = today.strftime("%m/%d/%Y")

    #read in from monitor_settings.ini
    notify_1 = int(config['dates']['notify_me_in_days_01'])
    notify_2 = int(config['dates']['notify_me_in_days_02'])
    notify_3 = int(config['dates']['notify_me_in_days_03'])

    for row in cursor:
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
                logger.info('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE. EXPIRES {} ON THE HOST {}'.format(notify_1, row[1], key_object.decrypt(row[2]), row[3], row[4]))

                yield('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE. EXPIRES {} ON THE HOST {}'.format(notify_1, row[1], key_object.decrypt(row[2]), row[3], row[4]))
            elif day_diff == notify_2:
                logger.info('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE. EXPIRES {} ON THE HOST {}'.format(notify_2, row[1], key_object.decrypt(row[2]), row[3], row[4]))
                
                yield('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} AND EXPIRES {} ON THE HOST {}'.format(notify_2, row[1], key_object.decrypt(row[2]), row[3], row[4]))
            elif day_diff == notify_3:
                logger.info('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE. EXPIRES {} ON THE HOST {}'.format(notify_3, row[1], key_object.decrypt(row[2]), row[3], row[4]))               
                
                yield('WARNING {} DAYS FOR THE ASSET {} WITH THE LICENSE {} TO EXPIRE. EXPIRES {} ON THE HOST {}'.format(notify_3, row[1], key_object.decrypt(row[2]), row[3], row[4]))
        except Exception as e:
            print (e)

if __name__ == "__main__":
    #logger
    logger = get_logger()
    set_logger(logger)

    #configparser
    config = get_parser()

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