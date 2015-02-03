def notify():
    import smtplib
    addresses = ['kriegsmeister@gmail.com','dgingi@gmail.com','ilaiom@gmail.com']
    for add in addresses:
        TO = add
        SUBJECT = 'Finished test'
        TEXT = 'Finished the test'
        
        # Gmail Sign In
        gmail_sender = 'kriegsmeister@gmail.com'
        gmail_passwd = 'sirpsycho'
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_sender, gmail_passwd)
        
        BODY = '\r\n'.join(['To: %s' % TO,
                            'From: %s' % gmail_sender,
                            'Subject: %s' % SUBJECT,
                            '', TEXT])
        
        try:
            server.sendmail(gmail_sender, [TO], BODY)
            print ('email sent')
        except:
            print ('error sending mail')
    
        server.quit()