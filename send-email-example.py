import smtplib # Simple mail transfer protocol library

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# NOTE: For gmail, enable `Less secure apps` ON for script to run
gmail_user = "" # <Put username here>
gmail_pwd = "" # <Put password here>



def basic_email():
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) # TLS based connection
        # server = smtplib.SMTP_SSL('smtp.gmail.com', 465) # SSL based
        server.ehlo()
        server.starttls()
        server.login(user=gmail_user, password=gmail_pwd)

        message = 'hi from python'
        server.sendmail(from_addr=gmail_user, to_addrs=gmail_user, msg=message)
        server.quit()
    except smtplib.SMTPAuthenticationError as e:
        print(e)
    except smtplib.SMTPNotSupportedError as e2:
        pass
    except smtplib.SMTPHeloError as e3:
        pass

# MIME - multipurpose internet media extension

from email.mime.multipart import MIMEMultipart

def email_with_MIMEText():
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = gmail_user
    msg['Subject'] = 'test_plain'

    body = """
        This is an e-mail message to be sent in HTML format

        <b>This is HTML message.</b>
        <h1>This is headline.</h1>
        """
    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(user=gmail_user, password=gmail_pwd)

    print(msg.as_string())
    server.sendmail(gmail_user, gmail_user, msg.as_string())
    server.quit()

from email.mime.multipart import MIMEBase
from email import encoders

def email_with_attachment():
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = gmail_user
    msg['Subject'] = 'test'

    body = """From: From Person <from@fromdomain.com>
    To: To Person <to@todomain.com>
    MIME-Version: 1.0
    Content-type: text/html
    Subject: SMTP HTML e-mail test
    
    This is an e-mail message to be sent in HTML format
    
    <b>This is HTML message.</b>
    <h1>This is headline.</h1>
    """
    msg.attach(MIMEText(body, 'html'))

    filename = "CH08-OOP.ppt"
    attachment = open(filename, 'rb')

    # Attaching encrypted file to MIMEMultipart
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    print(p.as_string())
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)

    s = smtplib.SMTP("smtp.gmail.com", 587)
    s.ehlo()
    s.starttls()
    s.login(gmail_user, gmail_pwd)

    # s.send_message(msg, from_addr="prateep.iiith@gmail.com", to_addrs="prateep.iiith@gmail.com")
    s.sendmail(from_addr=gmail_user, to_addrs=gmail_user, msg=msg.as_string())

    print('email sent')
    s.quit()

if __name__ == "__main__":
    # basic_email()
    # email_with_MIMEText()
    email_with_attachment()


# TO = 'prateep.iiith@gmail.com'
# SUBJECT = "Testing sending using gmail"
# TEXT = "Testing sending mail using gmail servers"
# server = smtplib.SMTP("smtp.gmail.com", 587)
# server.ehlo()
# server.starttls()
# server.ehlo()
# server.login(gmail_user, gmail_pwd)
# BODY = '\r\n'.join(['To: %s' % TO,
#         'From: %s' % gmail_user,
#         'Subject: %s' % SUBJECT,
#         '', TEXT])
#
# server.sendmail(gmail_user, [TO], BODY)
# print ('email sent')