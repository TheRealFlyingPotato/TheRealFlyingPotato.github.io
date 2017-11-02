
# # import smtplib
# # import time
# # import imaplib
# # import email
# # import sys, os

# # # -------------------------------------------------
# # #
# # # Utility to read email from Gmail Using Python
# # #
# # # ------------------------------------------------

# # ORG_EMAIL   = "@gmail.com"
# # FROM_EMAIL  = "myredditbots" + ORG_EMAIL
# # FROM_PWD    = "1m0nf1r3"
# # SMTP_SERVER = "imap.gmail.com"
# # SMTP_PORT   = 993

# # def read_email_from_gmail():
# #     try:
# #         mail = imaplib.IMAP4_SSL(SMTP_SERVER)
# #         mail.login(FROM_EMAIL,FROM_PWD)
# #         mail.select('inbox')

# #         type, data = mail.search(None, 'ALL')
# #         mail_ids = data[0]

# #         id_list = mail_ids.split()   
# #         first_email_id = int(id_list[0])
# #         latest_email_id = int(id_list[-1])


# #         for i in range(latest_email_id,first_email_id, -1):
# #             typ, data = mail.fetch(i, '(RFC822)' )

# #             for response_part in data:
# #                 if isinstance(response_part, tuple):
# #                     msg = email.message_from_string(response_part[1])
# #                     email_subject = msg['subject']
# #                     email_from = msg['from']
# #                     print ('From : ' + email_from + '\n')
# #                     print ('Subject : ' + email_subject + '\n')

# #     except Exception as e:
# #         exc_type, exc_obj, exc_tb = sys.exc_info()
# #         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
# #         print(exc_type, fname, exc_tb.tb_lineno)
# # if __name__ == '__main__':
# #     read_email_from_gmail()


# # reading emails

# # import imaplib

# # msrvr = imaplib.IMAP4_SSL('imap.gmail.com', 993)

# # unm = 'myredditbots'
# # pwd = '1m0nf1r3'
# # msrvr.login(unm, pwd)

# # stat, cnt = msrvr.select('inbox')
# # stat, dta = msrvr.fetch(cnt[0], cnt[])

# import email, imaplib, getpass

# mail = imaplib.IMAP4_SSL('imap.gmail.com', 993) #server
# unm = 'myredditbots'
# pwd = '1m0nf1r3'
# mail.login(unm, pwd)
# mail.select('INBOX')

# def loop():
#     mail.select('INBOX')
#     n = 0
#     retcode, messages = mail.search(None, ('UNSEEN'))
#     if retcode == 'OK':
#         for num in messages[0].split():
#             n += 1
#             print(n)
#             typ, data, = mail.fetch(num, '(RFC822)')
#         for response_part in data:
#             if isinstance(response_part, tuple):
#                 try:
#                     original = email.message_from_string(response_part[1])
#                     print(original['From'])
#                     print(original['Subject'])
#                     typ, data = mail.store(num, '+FLAGS', '\\Seen')
#                 except:
#                     print('except: ')
#                     print(response_part[1])



# if __name__ == '__main__':
#     while True:
#         loop()

global PRINTTEST
PRINTTEST = True
RESPONSE_SUBJECT = 'Log Recieved'
WEB_PATH = 'https://therealflyingpotato.github.io/'
RESPONSE_BODY = 'Your log has been recieved and posted to:\n' + WEB_PATH
import string
VALID_CHARS = "-_.%s%s" % (string.ascii_letters, string.digits)

def fixfname(s):
    return ''.join(c for c in s if c in VALID_CHARS)

def dc(s):
    l = list(s)
    for i,x in enumerate(l):
        l[i] = chr(ord(x) - (i+1))
    return ''.join(l)

def ec(s):
    l = list(s)
    for i, x in enumerate(l):
        l[i] = chr(ord(x) + (i+1))
    return ''.join(l)

import smtplib
def sendmsg(link_address, to_email):
    content = 'Subject: ' + RESPONSE_SUBJECT + '\r\n\r\n' + RESPONSE_BODY + link_address
    m = smtplib.SMTP('smtp.gmail.com',587)
    m.ehlo()
    m.starttls()
    m.login('myredditbots@gmail.com',PWD)
    m.sendmail('myredditbots@gmail.com',to_email, content)
    m.close()

def tprint(*args):
    tprint.count += 1
    global PRINTTEST
    if type(args[0]) is int:
        n = args[0].pop(0)
    else:
        n = -1
    if PRINTTEST == 1 or n == PRINTTEST:
        print('\n=={}=='.format(tprint.count))
        for x in args:
            print(x, ' ')
        print('=={}==\n'.format("="*len(str(tprint.count))))
    return '::'
tprint.count = 0

import email
import imaplib
from time import sleep
import os
import urllib.request
import re

def getUnlock(s):
    reg = re.findall(r'You just unlocked the promo card: .*?!', s)
    if reg == []:
        return 0
    return reg[0][34:-1]    

def waitLoop():
    for i in range(5):
        sleep(.5)
        print("Listening" + "."*(i+1), "        ", end="\r")


def mainloop(last_parsed_uid):
    while True:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login('myredditbots@gmail.com', '1m0nf1r3')
        mail.select('inbox')
        result, data = mail.uid('search', None, "ALL")
        latest_email_uid = data[0].split()[-1]
        # tprint([latest_email_uid.decode('UTF-8'), last_parsed_uid])
        if latest_email_uid.decode('UTF-8') == last_parsed_uid:
            # tprint('sleeping')
            waitLoop()
            mail.close()
            mail.logout()
            continue
        print("")
        result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        # tprint('latest_email_uid', latest_email_uid, 'raw_email: ', raw_email)

        email_message = email.message_from_string(raw_email.decode('UTF-8'))
        # tprint(email_message)

        # whenRecieved = email_message['date']
        whenRecieved = re.sub('\-\d*?\ ', '',email_message['date'])
        whenRecieved = re.sub('[\ ,\(\):]','_', whenRecieved).replace('__','_')[:-1]
        print("\n\n---Recieved message\nSubject: {}\nFrom: {}\nTime: {}\n------------------------\n".format(email_message['subject'], email_message['from'], whenRecieved))

        last_parsed_uid = latest_email_uid.decode('UTF-8')
        with open('lastuid', 'w') as fout:
            fout.write(str(last_parsed_uid))

        if email_message['subject'] == 'Log Recieved':
            continue

        if email_message.is_multipart():
            final = email_message.get_payload()[0].get_payload()
            # omega = email_message.get_payload()
            # for x in omega:
                # tprint(x)
            # for payload in email_message.get_payload():
            # for payload in omega:
                # final += payload.get_payload(decode=True).decode('UTF-8')
        else:
            final = email_message.get_payload()

        final = str(final)
        for keep in [')','.','!']:
            final = final.replace(keep + '\r\n', keep + '\n')
        final = final.replace('\r\n',' ')      

        variantName = getUnlock(final)
        fname = "{}_{}".format(whenRecieved, fixfname(email_message['subject']))
        if variantName:
            fpath = "logs/{}/{}.txt".format(variantName, fname)
        else:
            fpath = "logs/failed/{}.txt".format(fname)

        # make file and folders and necessary
        
        # tprint(fpath)
        os.makedirs(os.path.dirname(fpath.replace(' ', '_')), exist_ok=True)
        with open(fpath.replace(' ', '_'), 'w') as fout:
            fout.write(final)

        if variantName:
            variantName = variantName.replace(" ", "_")
      
        variants = []
        try:
            with open('vnames.txt') as fin:
                variants = fin.readlines()
        except:
            pass
        

        if variantName:
            if variantName not in variants:
                variants.append(variantName)
                with open('vnames.txt', 'w') as fout:
                    for v in variants:
                        fout.write(v)

        
        #create the log landing page
        with open('logs/index.html', 'w') as fout:
            fout.write('<h3><a href="failed/index.html">Failure logs</a></h3\n')
            fout.write('<h3>Success Logs</h3>\n')
            for v in variants:
                # tprint(v)
                fout.write('<li><a href="{}/index.html">{}</a></li>\n'.format(v, v.replace("_"," ")))
        

        #alter specific variant or failed log index
        currentPath = 'failed'
        if variantName:
            currentPath = variantName
        try:
            with open('logs/{}/index.html'.format(currentPath), 'a') as fout:
                fout.write('<li><a href="{}.txt">{}</a></li>\n'.format(fname, fname))
        except:
            with open('logs/{}/index.html'.format(currentPath), 'w+') as fout:
                fout.write('<li><a href="{}.txt">{}</a></li>\n'.format(fname, fname))
        

        commands = [
            'git pull',
            'git add logs/.',
            'git add lastuid',
            'git commit -m "update: {}.txt"'.format(fname),
            'git push'
        ]

        for cmd in commands:
            os.system('echo ' + cmd)
            os.system(cmd)

        # fpath = str(fname) + '.txt'

        # count = 0
        # while True:
        #     tprint(LOGS_PATH + fpath)
        #     try:
        #         with urllib.request.urlopen(LOGS_PATH + fpath) as response:
        #             html = response.read()
        #     except:
        #         print("Not found #{}".format(count), end = '\r')
        #         count += 1
        #         sleep(2)
        #         continue
        #     tprint(html.decode('UTF-8'))
        #     tprint('File not found' in html.decode('UTF-8'))
        #     if 'File not found' in html.decode('UTF-8'):
        #         print("Not found #{}".format(count), end = '\r')
        #         count += 1
        #         sleep(2)
        #         continue
        #     print('\nLog Uploaded Successfully')
        #     break
        r = 15
        for i in range(r):
            print('waiting {} more seconds...  '.format(r-i), end='\r')
            sleep(1)
        print('\n')
        sendmsg(fpath.replace(' ','_'), email_message['from'])
        mail.close()
        mail.logout()



if __name__ == "__main__":
    PWD = dc('2o3rk7y;')
    try:
        with open("lastuid") as fin:
            holder_uid = fin.read().replace('\n','')
    except:
        with open("lastuid", "w") as fout: 
            fout.write('0')
        holder_uid = '0'
    holder_uid = '0'
    mainloop(holder_uid)


# tprint(email_message['To'], email.utils.parseaddr(email_message['From']), email_message.items())

# --- sequential ---
# result, data = mail.uid(None, 'ALL')

# tprint('result: ', result,'data: ', data)
# ids = data[0].decode('UTF-8')
# id_list = ids.split()
# latest_email_id = id_list[-1] #latest email
# tprint('ids:', ids, 'id_list:', id_list, 'latest_email_id', latest_email_id)

# r, d = mail.fetch(latest_email_id, '(RFC822)') # fetch the email
# tprint('r: ', r, 'd: ', d)

# -------------------------