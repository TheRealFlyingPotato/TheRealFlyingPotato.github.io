
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
RESPONSE_BODY = 'Your log has been recieved and posted to:\nhttps://therealflyingpotato.github.io/logs/'


import smtplib
def sendmsg(link_address, to_email):
    content = 'Subject: ' + RESPONSE_SUBJECT + '\r\n\r\n' + RESPONSE_BODY + link_address
    m = smtplib.SMTP('smtp.gmail.com',587)
    m.ehlo()
    m.starttls()
    m.login('myredditbots@gmail.com','1m0nf1r3')
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
tprint.count = 0

import email
import imaplib
from time import sleep
import os
import uuid

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

        print("\n\n---Recieved message\nSubject: {}\nFrom: {}\n------------------------\n".format(email_message['subject'], email_message['from']))

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


        fname = uuid.uuid4()
        with open("logs/{}.txt".format(fname), 'w') as fout:
            fout.write(final)


        try:
            fout = open('logs/index.html', 'a')
        except:
            fout = open('logs/index.html', 'w')
        fout.write('<li><a href="{}.txt">{}</a></li>'.format(fname, fname))
        fout.close()

        commands = [
            'git pull',
            'git add logs/.',
            'git commit -m "update: {}.txt"'.format(fname),
            'git push'
        ]

        for cmd in commands:
            os.system('echo ' + cmd)
            os.system(cmd)

        fpath = fname
        sendmsg(fpath, email_message['from'])
        mail.close()
        mail.logout()



if __name__ == "__main__":
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