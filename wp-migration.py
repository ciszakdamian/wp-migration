#!/usr/bin/python
#wp-migration
#Script to auto migration wp
#Author: Damian Ciszak
#Contact: ciszakdamian@gmail.com

#defines
import sys
import os
import shutil
import re
import fileinput
from time import sleep
from ftplib import FTP

#define colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#create tmp directory
tmpDir = 'tmp-wp-migration'
os.mkdir(tmpDir)


#functions 
#def ftpConnect(login, host, password):
#	os.system('clear')
#	print(bcolors.WARNING+"Please wait connecting to "+host+""+bcolors.ENDC)
#	ftp = FTP(host)
#	return ftp.login(user=login, passwd=password)
#	os.system('clear')

def fileSearch(x, name):
	os.chdir(tmpDir)
	file = open(name, "r")
	for line in file:
		if re.search(x, line):
			result = line		
	file.close()
	os.chdir('..')
	return result

def fileSed(old, new, file):
	with fileinput.FileInput(file, inplace=True) as file:
    		for line in file:
        		print(line.replace(old, new), end='')


#check sum argv
if len(sys.argv) < 6:
	sys.exit(bcolors.FAIL+"Podaj poprawne parametry w formie:\n"+bcolors.ENDC+"python wp-migration login host password domena(z protokolem) nowa_baza")

#argv
login = sys.argv[1]
host = sys.argv[2]
password = sys.argv[3]
domena = sys.argv[4]
databaseN = sys.argv[5]

#FTP connect to remote server
os.system('clear')
print(bcolors.WARNING+"Please wait connecting to "+host+""+bcolors.ENDC)
ftp = FTP(host)
ftp.login(user=login, passwd=password)
os.system('clear')

#ftp block
ftp.retrlines('LIST')

#set WP dir
 
while True:
	ftpWpDir = input(bcolors.OKGREEN+"Podaj folder z WP: "+bcolors.ENDC)
	os.system('clear')
	ftp.cwd(ftpWpDir)
	ftp.retrlines('LIST')
	n = input(bcolors.OKGREEN+"Czy podany folder jest poprawny (y/n): "+bcolors.ENDC)
	if n.strip() == 'y':
		break
ftpWpPwd = ftp.pwd()
os.system('clear')

#get out mysql pass
confFile = 'wp-config.php'
ftp.retrbinary("RETR " + confFile, open(''+tmpDir+'/wp-config.php', 'wb').write)

dbN = fileSearch('DB_NAME', confFile)
dbU = fileSearch('DB_USER', confFile)
dbP = fileSearch('DB_PASSWORD', confFile)
dbH = fileSearch('DB_HOST', confFile)

print(bcolors.HEADER+"###---Check DB pass--###"+bcolors.ENDC)

x = 0
while True:
	if x != 0:
		dbName = input(bcolors.OKGREEN+"Wprowadz poprawne dane: "+bcolors.ENDC)
	else:
		dbName = dbN
		dbName = dbName[19:-4]
	print("From config: "+bcolors.WARNING+dbN+bcolors.ENDC)
	print("From wp-migration: "+bcolors.WARNING+dbName+bcolors.ENDC)
	x += 1	
	n = input(bcolors.OKGREEN+"Czy dane sa poprawne? (y/n): "+bcolors.ENDC)
	if n.strip() == 'y':
		break
x = 0
while True:
	if x != 0:
		dbUser = input(bcolors.OKGREEN+"Wprowadz poprawne dane: "+bcolors.ENDC)
	else:
		dbUser = dbU
		dbUser = dbUser[19:-4]
	print("From config: "+bcolors.WARNING+dbU+bcolors.ENDC)
	print("From wp-migration: "+bcolors.WARNING+dbUser+bcolors.ENDC)
	x += 1	
	n = input(bcolors.OKGREEN+"Czy dane sa poprawne? (y/n): "+bcolors.ENDC)
	if n.strip() == 'y':
		break

x = 0
while True:
	if x != 0:
		dbPassword = input(bcolors.OKGREEN+"Wprowadz poprawne dane: "+bcolors.ENDC)
	else:
		dbPassword = dbP
		dbPassword = dbPassword[23:-4]
	print("From config: "+bcolors.WARNING+dbP+bcolors.ENDC)
	print("From wp-migration: "+bcolors.WARNING+dbPassword+bcolors.ENDC)
	x += 1	
	n = input(bcolors.OKGREEN+"Czy dane sa poprawne? (y/n): "+bcolors.ENDC)
	if n.strip() == 'y':
		break
x = 0
while True:
	if x != 0:
		dbHost = input(bcolors.OKGREEN+"Wprowadz poprawne dane: "+bcolors.ENDC)
	else:
		dbHost = dbH
		dbHost = dbHost[19:-4]
	print("From config: "+bcolors.WARNING+dbH+bcolors.ENDC)
	print("From wp-migration: "+bcolors.WARNING+dbHost+bcolors.ENDC)
	x += 1	
	n = input(bcolors.OKGREEN+"Czy dane sa poprawne? (y/n): "+bcolors.ENDC)
	if n.strip() == 'y':
		break

#print(dbName+" "+dbUser+" "+dbPassword+" "+dbHost)

#create php dump script

dbScript = "dbdump.php"
dbFile = "baza.sql.gz"

dumpScript = open(""+tmpDir+"/"+dbScript+"", "w")

dumpScript.write("<?php\n"
"set_time_limit (10000);\n"
"$db=\'"+dbName+"\';\n"
"$user=\'"+dbUser+"\';\n"
"$pass=\'"+dbPassword+"\';\n"
"$host=\'"+dbHost+"\';\n"
"$plik=\'"+dbFile+"\';\n"
"system('mysqldump '.$db.' -u'.$user.' -p'.$pass.' -h'.$host.'|gzip>'.$plik);\n"
"system('du '.$plik.'|cut -f1')\n"
"?>\n")

dumpScript.close()

os.system('clear')

print("PHP dump script "+dbScript+" create:"+bcolors.OKGREEN+" successfull"+bcolors.ENDC)

#upload php dump script
tmpDirRemote = 'tmpdump'
os.chdir(tmpDir)

ftp.mkd(tmpDirRemote)
ftp.cwd(tmpDirRemote)
ftp.storbinary('STOR '+dbScript, open(dbScript, 'rb'))

os.chdir('..')

print("Script "+dbScript+" upload to "+tmpDirRemote+": "+bcolors.OKGREEN+"successfull"+bcolors.ENDC)

#curl run dump script
request = domena+"/"+tmpDirRemote+"/"+dbScript
print("DB file size:")
os.system("curl "+request)

#download database 
ftp.retrbinary("RETR " + dbFile, open(''+tmpDir+'/'+dbFile+'', 'wb').write)

#load mysql
dbFileSql = dbFile[:-3]
os.chdir(tmpDir)
print("DB "+dbFileSql+" load to "+databaseN+":")
os.system("zcat "+dbFile+" >> "+dbFileSql)
os.system("pv "+dbFileSql+" | mysql "+databaseN)
sleep(2)
print("DB "+dbName+" migration to "+databaseN+": "+bcolors.OKGREEN+"successfull"+bcolors.ENDC)
sleep(3)
os.system("clear")

#change wp-config.php
shutil.copyfile(confFile, confFile+".original")

databaseP = "ZMIEN"

sedN = "define( 'DB_NAME', '"+databaseN+"' );"
sedU = "define( 'DB_USER', '"+databaseN+"' );"
sedP = "define( 'DB_PASSWORD', '"+databaseP+"' );"
sedH = "define( 'DB_HOST', 'localhost' );"

fileSed(dbN, sedN, confFile);
fileSed(dbU, sedU, confFile);
fileSed(dbP, sedP, confFile);
fileSed(dbH, sedH, confFile);


#ftp mirror 
os.chdir('..')

os.system("lftp -e \"set ftp:ssl-allow false; mirror -c '.' '"+domena+"' \" -u \""+login+"\",\""+password+"\" '"+host+"'")



ftp.close()

#remove tmp directory

#shutil.rmtree(tmpDir)
