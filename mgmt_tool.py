import paramiko
import subprocess
import sys
import re
import access
from multiprocessing import Process
import optparse

def getConf(ip_addr,dest_path,i,routers):
	conn=access.client_ssh(ip_addr+str(i+2),access.user,access.password)
	access.cmd_op(conn,"vtysh -c wr")
	access.sftp(conn,'get','/etc/frr/frr.conf',dest_path+'/configs/'+routers[i]+'.txt')
	getContainerState(conn,dest_path,routers[i])
	conn.close()

def getContainerState(conn,dest_path,R):
	output=access.cmd_op(conn,'iptables -S')
	text=open(dest_path+'/container/'+R+'.txt','a')
	for line in output:
        	text.write('iptables '+line)

def backup(Path):
	routers=getRouters('backup',Path)
	ip_addr=access.ipaddr
	dest_path=access.mainPath+Path
	access.check_path(dest_path)
	p=[]
	for i in range(0,len(routers)):
		p = Process(target=getConf, args=(ip_addr,dest_path,i,routers))
		p.start()

def restore(path):
	routers=getRouters('restore',access.mainPath+path)
	print routers
	subprocess.call('cp '+access.mainPath+path+'/connectivitymat.txt /home/ece792/RND-TOOL/rnd_lab/scripts/connectivitymat.txt',shell=True)
	print "Run RND tool, matrix copied ..."
	print "tool ran ? (y/n)"
	flag=raw_input() 
	if flag=='y':
		ip_addr=access.ipaddr
		for i in range(0,len(routers)):
			conn=access.client_ssh(ip_addr+str(i+2),access.user,access.password)
			access.sftp(conn,'put',access.mainPath+path+'/configs/'+routers[i]+'.txt', '/etc/frr/frr.conf')
			access.cmd_op(conn,'/etc/init.d/frr restart')
	else:
		print "Failed..."

def getRouters(mode,path):
	if mode=="backup":
		matpath='/home/ece792/RND-TOOL/rnd_lab/scripts/connectivitymat.txt'
	elif mode=="restore":
		matpath=path+'/connectivitymat.txt'
	else:
		print "Unknown mode"
	with open(matpath,'r') as mat:
		Rlist=mat.readlines()[0]
		Rlist=Rlist.split('\n')[0]
		Rlist=Rlist.split('\t')
		Rlist.remove('')
		mat.close()
	return Rlist

def cmdop(i,router,options):
	ip_addr=access.ipaddr
	dest_path=access.mainPath+options.path	
	with open(dest_path+'/outputs/'+router+'_output.txt', 'w') as outputfile: 
		conn=access.client_ssh(ip_addr+str(i+2),access.user,access.password)
		if options.clear is not None:
			print "Clearing on router "+ router
			output=access.cmd_op(conn,"/etc/init.d/frr restart\n")
		if options.shellcmd is not None:
			print "Shell command '"+options.shellcmd +"' on "+router
			output=access.cmd_op(conn,options.shellcmd)
		if options.cmd is not None:
			print "frr command '"+options.cmd+"' on "+ router
			output=access.cmd_op(conn,"vtysh -c '"+options.cmd+"'")
		for line in output:
			outputfile.write(line)
		outputfile.close()

def cmdRun(cmd,Path,options):
	routers=getRouters("backup",Path)
	ip_addr=access.ipaddr
	p=[]
	print "---Creating log file in project directory---"
	for i in range(0,len(routers)):
		p = Process(target=cmdop, args=(i,routers[i],options))
		p.start()

parser = optparse.OptionParser()
parser.add_option('-w', '--operation', action="store", dest="operation", help="\toperation to be carried out, restore, backup, cmdRun", default=None)
parser.add_option('-p', '--path', action="store", dest="path", help="\tpath of the project", default=None)
parser.add_option('-s', '--cmd', action="store", dest="cmd", help="\tshow command to be executed", default=None)
parser.add_option('-c', '--clear', action="store", dest="clear", help="\tclearing all daemons", default=None)
parser.add_option('-a', '--shellcmd', action="store", dest="shellcmd", help="\tshell command to be executed", default=None)
options, args = parser.parse_args()

if options.operation=="backup":
	if options.path is not None:
		print "Taking backup on project" + options.path
		backup(options.path)
elif options.operation=="restore":
	if options.path is not None:
		print "restoring project" + options.path
		restore(options.path)
elif options.operation=="cmdRun":
	if options.path is not None:
		print "Running command in project"+options.path
		cmdRun(options.cmd,options.path,options)
else:
	print "Unknown request"

