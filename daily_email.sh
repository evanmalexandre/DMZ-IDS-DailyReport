#!/bin/bash -l
DATE=$(date +%Y-%m-%d)
rm -rf /home/monitor/Desktop/Commands/test.pdf
/usr/bin/python /home/monitor/Desktop/Commands/make_pdf_report.py
cat /home/monitor/Desktop/daily_email.txt | mail -s "$DATE Daily Report" root@localhost -A /home/monitor/Desktop/Commands/test.pdf -a "From: dmzalerts@fixit.expert"


