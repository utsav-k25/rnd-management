import paramiko
import subprocess
import sys
import time
import re

ipaddr='172.17.0.'
user='root'
password='root'
mainPath='/home/ece792/RND-TOOL/rnd_lab/projects/'


def client_ssh(ip,username,password):
    remote_conn_pre=paramiko.SSHClient()
    remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    remote_conn_pre.connect(ip, port=22, username=username, password=password, look_for_keys=False, allow_agent=False)
    return remote_conn_pre

def sftp(conn_ssh,operation,src,dest):
    conn=conn_ssh.open_sftp()
    if operation=='get':
	conn.get(src,dest)
    elif operation=='put':
	conn.put(src,dest)
    else:
	print "Wrong operation"

def cmd_op(connection, command):
    stdin,stdout,stderr=connection.exec_command(command)
#    print stderr
    return stdout.readlines()
   
def check_path(dst_path):
    try:
        output=subprocess.check_output('ls '+dst_path,shell=True)
    except  subprocess.CalledProcessError:	
        folders=dst_path.split('/')
	path='/'
	for folder in folders[1:]:
	    try:
		subprocess.check_output('ls '+path+folder,shell=True)
	    except:
		subprocess.call('mkdir '+path+folder,shell=True)
	    path=path+folder+'/'
	subprocess.call('mkdir '+dst_path+'/configs',shell=True)
	subprocess.call('mkdir '+dst_path+'/container',shell=True)
	subprocess.call('cp /home/ece792/RND-TOOL/rnd_lab/connectivitymat.txt '+dst_path+'/connectivitymat.txt',shell=True)
	
