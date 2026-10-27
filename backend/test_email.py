import smtplib
from email.mime.text import MIMEText

msg = MIMEText('ShopLedger email alert is working!')
msg['Subject'] = 'ShopLedger Test Email'
msg['From'] = 'abisheksaji02@gmail.com'
msg['To'] = 'abisheksaji02@gmail.com'

s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login('abisheksaji02@gmail.com', 'jgvi vhvt xrgm fmci')
s.sendmail('abisheksaji02@gmail.com', 'abisheksaji02@gmail.com', msg.as_string())
s.quit()

print('Email sent successfully!')