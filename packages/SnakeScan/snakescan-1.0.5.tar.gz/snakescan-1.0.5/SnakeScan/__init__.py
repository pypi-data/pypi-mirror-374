"""Module SnakeScan"""
__version__="1.0.5"
import socket
from art import tprint
from datetime import datetime
from tqdm import tqdm
portsopen=0
portsclosed=0
Run_now=True
Bool=True
boolean=0
#PORT-LIST(ALL-PORTS)
OpenPorts=[]
ports = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
    25: "SMTP", 43: "WHOIS", 53: "DNS", 80: "http",
    115: "SFTP", 123: "NTP", 143: "IMAP", 161: "SNMP",
    179: "BGP", 443: "HTTPS", 445: "MICROSOFT-DS",
    514: "SYSLOG", 515: "PRINTER", 993: "IMAPS",
    995: "POP3S", 1080: "SOCKS", 1194: "OpenVPN",
    1433: "SQL Server", 1723: "PPTP", 3128: "HTTP",
    3268: "LDAP", 3306: "MySQL", 3389: "RDP",
    5432: "PostgreSQL", 5900: "VNC", 8080: "Tomcat", 10000: "Webmin" }
def is_port_open(host,port):
	s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	try:
		#Connecting...
		s.connect((host,port))
		#Port//(Closed<--or-->Open)
	except:
		s.close()
		return False
	else:
		s.close()
		return True
print("–"*60)
tprint("SnakeScan")
print(" \033[1;32;1m                                       Made by DEN*RAM\033[0;0m".rjust(50))
print("–"*60)
print("V1.0.0".rjust(60))
print("#ToolsforEveryone/SnakeScan.py:")
print("Skip/Error:|Host:localhost Port:4000 ports|")
while Run_now:
	host=input("[$]Host/Skip-->")
	if host == "Exit"  or host == "exit":
		break
	if host == "":
		host=socket.gethostbyname(socket.gethostname())		
	port_user=input("[$]Port/Range/Skip-->")
	if port_user == "Exit" or port_user == "Exit":
		break
	if port_user:
		try:
			length=int(port_user)
		except:
			port_user="4000"
		for i in range(0,len(port_user)):
			if port_user[i] == " ":
				port_user=4000
				break
		port_user=int(port_user)
		length=port_user	
	else:
		port_user=4000
		length=port_user
	print(f"[!]Listening {host} please wait...")
#|-----------------Starting---------------------|
	length=int(length)+1
	is_port_open(host,port_user)
	start=datetime.now()
	for port in tqdm(range(1,length)):
						if is_port_open(host,port):
							for name in ports:
									if port == name:
										OpenPorts=[port]
										portsopen+=1
						else:
							portsclosed+=1
						if port_user  != "":
										if int(port_user) == port:
											if port_user == "":
												pass
											elif int(port_user) == port:
												if is_port_open(host,port):
													Bool=True
													boolean+=1
										else:
											Bool=False												
	if boolean == 1:
		pass
	print("".center(60,"-"))
	for i in OpenPorts:
		print(f"Open:{i}//{ports[i]}")
	print(f"{host}".center(60,"-"))
	print(f"Closed:{portsclosed}")
	portsclosed=0
	print(f"Open:{portsopen}")
	portsopen=0
	ends=datetime.now()
	print("Time:{}".format(ends-start)[:12],"\033[0;0m")
	print("-"*60) 
#//////////////////////////////
#VERSION[1.0.0]
#/////////////////////////////
#FOR USE ONLY
