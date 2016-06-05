# Chris Kuske
# COMP 529 Semester Project
# Distributed Backup System
# coding: utf-8
import StringIO
import base64
import datetime
import encodings
import encodings.bz2_codec
import hashlib
import os
import random
import signal
import socket
import sqlite3
import struct
import sys
import threading
import time
import traceback
import xml
from optparse import OptionParser
from xml.etree.ElementTree import *

DistributionCount = 1  # this is the amount of peers that should have each file and/of chunk of file
ServerIPPort = 50000  # the TCP/UDP ports to listen on
backupFileExt = '.dbsbak'

TCPServerSocket = 0
UDPServerSocket = 0
runThreads = True
encKey = ""
recoveryMode = False

blockSize = 1024 * 1024
optParser = OptionParser()
progOptions = {}  # options passed into the command line
dbsPeers = []  # nodes we have found or have manually added
blacklistedIPs = []  # nodes that we should not communicate with (like ourselves)
queuedFiles = []  # files that need to be sent to other nodes on the network
missingFiles = []  # files that have been detected as missing on the filesystem, but exist in the
# database
queuedDownloadChunks = []  # a container for the chunk data for each file in missingFiles
noCrypto = False  # whether PyCrypto is available on this machine


#############################################

class ClientThread(threading.Thread):
    def __init__(self):
        self.currentFile = ""
        threading.Thread.__init__(self)

    def run(self):
        while runThreads:
            if len(dbsPeers) > 0:
                fileidx = 0

                for filePath in missingFiles:
                    logToScreen('Restoring ' + filePath)
                    self.currentFile = filePath
                    if recoveryMode:
                        dbhash = sha256_for_bytes(encKey)
                        self.getFile([{'chunkChecksum': dbhash, 'chunkIdx': 1}])
                        missingFiles.remove(filePath)
                        os.rename(dbhash, 'dbs.db')
                        logToScreen('*** Database restored, terminating program. ***')
                        logToScreen('*** Relaunch to re-start normal operation.  ***')
                        shutdownScript()
                    else:
                        if self.getFile():
                            missingFiles.remove(filePath)
                        else:
                            logToScreen('getFile failed for ' + filePath)

                time.sleep(2)  # let us rest a second and settle

                for filePath in queuedFiles:
                    self.currentFile = filePath
                    logToScreen(self.currentFile + " is to be backed up")
                    if self.sendFile():
                        queuedFiles.remove(filePath)
                        fileidx += 1

                if fileidx > 0:  # the database has been modified, so let's back it up
                    self.buildDBChecksumsAndSend()

            if os.path.exists('dbs.db'):  # only check for new files if we have a database to check against!
                CheckAndCreateDB(progOptions.dbsFolder)
            time.sleep(5)

    # there is a very small chance that the DB could get altered between this
    # and sendFile(), but since this is single-threaded, it's doubtful
    def buildDBChecksumsAndSend(self):
        self.currentFile = 'dbs.db'
        self.sendFile(True)

    # this function takes the current file and computes the file checksum
    # next, it slices the file into 1MB slices.  Each of these slices are
    # then distributed to other peers in the DBS network.  Once all of the
    # slices have been distributed to at least the number of peers specified
    # in 'DistributionCount', the 'slice' data will be added to the sqlite
    # databasem and then the function will exit.
    def sendFile(self, dbsbackup=False):
        if len(dbsPeers) < DistributionCount:  # if we do not have enough notes to send to, postpone sending the file
            logToScreen('Postponing backup of {0:s} until more peers are available'.format(self.currentFile))
            return False

        f = open(self.currentFile, 'rb')
        # filesize = os.path.getsize(self.currentFile)
        chunk = 0
        data = f.read(blockSize)
        while len(data) > 0:
            if dbsbackup:
                datahash = sha256_for_bytes(encKey)
                slicedict = self.buildPutSliceXML(data, datahash)
            else:
                slicedict = self.buildPutSliceXML(data)
                datahash = slicedict['hash']
            datastr = slicedict['xml']

            backupcount = 0
            chunk += 1
            logToScreen('Sending chunk ' + str(chunk) + ' to ' + str(DistributionCount) + ' peers.')
            for dbsPeer in dbsPeers:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # do upload of chunk to peer
                sock.connect((dbsPeer, ServerIPPort))
                logToScreen(
                        'Uploading ' + self.currentFile + ' ' + str(chunk) + ' : ' + datahash + ' to ' + repr(dbsPeer))
                # logToScreen("Connected to " + dbsPeer)
                if sock.sendall(datastr) is None:  # none is success
                    backupcount += 1
                    # set backup count in DB
                if backupcount == DistributionCount:  # we have successfully send to enough nodes
                    addToFileChunkTable(self.currentFile, datahash, chunk)
                    break
                elif (len(dbsPeers) > 0) and (len(
                        dbsPeers) < DistributionCount):  # there are less nodes than we have available, so just move on
                    # if we have done as many as possible
                    if backupcount == len(dbsPeers):
                        addToFileChunkTable(self.currentFile, datahash, chunk)
                        break

            data = f.read(blockSize)
            time.sleep(.1)
        f.close()
        setFileAsBackedUp(self.currentFile)
        return True

    # this method polls the dbs network for nodes that have the file checksum
    # that is stored in the local sqlite database for thirty seconds, or less
    # if all the chunk requests are answered sooner.  The main processing is in done
    # in the UDP server.  Each chunk is then downloaded from the node that first replied
    # for that chunk request.  The download is done in order, so that the file can be
    # re-assembled from front to back.  This can be changed in the future to pre-allocate
    # the file, and write each chunk to the correct position so out-of-order downloads can happen.
    def getFile(self, chunklist=None):
        if chunklist is None:
            chunkdata = getFileChunkInfo(self.currentFile)
        else:
            chunkdata = chunklist
        i = 0
        while i < 5:  # poll for 5 seconds
            for chunk in chunkdata:
                # send broadcast - who has this chunk?
                top = Element('FP_REQ')
                child = SubElement(top, 'ID')
                child.text = str(random.randint(1, sys.maxint))

                child = SubElement(top, 'HASH')
                child.text = chunk['chunkChecksum']
                for ipAddr in dbsPeers:
                    sendUDPResponse(tostring(top), (ipAddr, ServerIPPort))

            if len(queuedDownloadChunks) == len(chunkdata):  # we have all the chunks
                break

            i += 1
            time.sleep(1)

        for chunk in chunkdata:
            for dbsNodeData in queuedDownloadChunks:
                if dbsNodeData[1] == chunk['chunkChecksum']:
                    dbspeer = dbsNodeData[0]
                    logToScreen(
                            'Download ' + self.currentFile + ' chunk ' + str(chunk['chunkIdx']) + '  with hash ' +
                            chunk[
                                'chunkChecksum'] + ' from ' + repr(dbspeer))
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    # do download of chunk from peer
                    sock.connect((dbspeer, ServerIPPort))
                    # logToScreen("Connected to " + dbsPeer)
                    xmlstr = self.buildGetSliceXML(dbsNodeData[1])
                    sock.send(xmlstr)

                    data = ""
                    while True:
                        # print "TCP Recv"
                        tmpdata = sock.recvfrom(4096)[0]
                        # print 'Recv' + tmpData
                        if not tmpdata:
                            break
                        else:
                            data += tmpdata
                    base64data = base64.b64decode(data)
                    decrypteddata = decryptBytes(base64data)
                    filechunkdata = encodings.bz2_codec.bz2_decode(decrypteddata)

                    # print fileChunkData[0]
                    f = open(self.currentFile, 'ab')
                    if f:
                        f.write(filechunkdata[0])
                        f.close()
                    sock.close()
        logToScreen('Restoration of {0:s} complete'.format(self.currentFile))
        return True

    # this function builds the XML of the File Storage Message
    def buildPutSliceXML(self, data, requestedhash=''):
        top = Element('PUT_FILE')
        child = SubElement(top, 'ID')
        child.text = str(random.randint(1, sys.maxint))

        tmp = encodings.bz2_codec.bz2_encode(data)
        encryptedbytes = encryptBytes(tmp[0])
        datastr = base64.b64encode(encryptedbytes)

        child = SubElement(top, 'HASH')
        if len(requestedhash) == 0:
            datahash = sha256_for_bytes(datastr)
        else:
            datahash = requestedhash
        child.text = datahash

        child = SubElement(top, 'DATA')
        child.text = datastr

        return {'xml': tostring(top), 'hash': datahash}

    # this builds the XML for the File Request TCP request
    def buildGetSliceXML(self, hashvalue):
        top = Element('GET_FILE')
        child = SubElement(top, 'ID')
        child.text = str(random.randint(1, sys.maxint))

        child = SubElement(top, 'HASH')
        child.text = hashvalue

        return tostring(top)


#############################################
# this thread processes File Presence requests, Node Discovery/Response messages, and Shutdown messages.
class UDPServerThread(threading.Thread):
    def __init__(self, udpsocket):
        self.udpSocket = udpsocket
        threading.Thread.__init__(self)

    def run(self):
        # listen for file requests
        # print self.udpSocket
        while 1:
            try:
                (data, addr) = self.udpSocket.recvfrom(2048)
                # logToScreen('Addr: ' + str(addr) + ', data: ' + data)
                # dbs_FILE_QUERY:SHA_hash_here
                if len(data) > 0:
                    # print data
                    xmlroot = xml.etree.ElementTree.fromstring(data)
                    if xmlroot.tag == "FP_REQ":
                        logToScreen('Got File Presence Request from ' + addr[0])
                        foundpath = handleFileExistenceRequest(xmlroot)
                        top = Element('FP_RESP')

                        child = SubElement(top, 'REQUEST_ID')
                        child.text = str(random.randint(1, sys.maxint))

                        child = SubElement(top, 'MACHINE_NAME')
                        child.text = socket.gethostname()

                        child = SubElement(top, 'HASH')
                        child.text = xmlroot.find('HASH').text

                        child = SubElement(top, 'RESPONSE')
                        if len(foundpath) > 0:
                            child.text = 'OK'
                        else:
                            child.text = 'DOES_NOT_EXIST'
                        data = tostring(top)
                        sendUDPResponse(data, addr)
                    elif xmlroot.tag == 'FP_RESP':
                        if xmlroot.find('RESPONSE').text == 'OK':
                            # print (addr[0], xmlRoot.find('HASH').text,)
                            if len([i for i, v in enumerate(queuedDownloadChunks) if
                                    v[1] == xmlroot.find('HASH').text]) == 0:
                                queuedDownloadChunks.append((addr[0], xmlroot.find('HASH').text,))
                    elif xmlroot.tag == "NDR":
                        addDBSNode(addr[0])
                    elif xmlroot.tag == "NDB":
                        # print 'About to send response'
                        top = Element('NDR')
                        child = SubElement(top, 'SRC_MACHINE_NAME')
                        child.text = socket.gethostname()
                        ndrxml = tostring(top)
                        sendUDPResponse(ndrxml, addr)
                    elif xmlroot.tag == "DBS_SHUTDOWN":
                        # print 'About to send response'
                        print addr[0]
                        if addr[0] in dbsPeers:
                            logToScreen('Removing ' + addr[0] + ' from dbsPeers.')
                            dbsPeers.remove(addr[0])

            except:
                # traceback.print_exc(file=sys.stdout)
                pass


################################################
# this thread processes File Requests and Storage Messages.
class TCPServerThread(threading.Thread):
    def __init__(self, serversocket):
        self.serverSocket = serversocket
        threading.Thread.__init__(self)

    def run(self):
        while True:
            (clientsocket, address) = self.serverSocket.accept()
            thread = threading.Thread(target=TCPHandler, args=(clientsocket,))
            thread.start()


def TCPHandler(tcpsocketdata):
    try:
        tcpsocket = tcpsocketdata
        data = ""
        while True:
            tmpdata = tcpsocket.recv(4096)
            if not tmpdata:
                break
            elif tmpdata.rfind('</GET_FILE>') >= 0:
                data += tmpdata
                break
            else:
                data += tmpdata

        if len(data) > 0:
            root = xml.etree.ElementTree.fromstring(data)
            requestid = root.find('ID').text
            sha256hash = root.find('HASH').text

            if root.tag == 'PUT_FILE':
                data = root.find('DATA').text
                # print 'Writing to ' + sha256Hash + backupFileExt
                f = open(sha256hash + backupFileExt, 'wb')
                if f:
                    f.write(data)
                    f.close()
            elif root.tag == 'GET_FILE':
                f = open(sha256hash + backupFileExt, 'rb')
                if f:
                    while True:
                        tmpdata = f.read(4096)
                        tcpsocket.send(tmpdata)
                        if not tmpdata:
                            break
                    f.close()
                    tcpsocket.close()
    except:
        # traceback.print_exc(file=sys.stdout)
        pass


################################################

# the applicable sockets are initialized here
def CreateSockets():
    logToScreen("Creating Sockets, binding to {0:s}:{1:d} ".format(progOptions.ipAddress, ServerIPPort, ))
    global TCPServerSocket, UDPServerSocket
    TCPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    TCPServerSocket.bind((progOptions.ipAddress, ServerIPPort))
    TCPServerSocket.listen(25)

    UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDPServerSocket.bind((progOptions.ipAddress, ServerIPPort))

    logToScreen("Sockets Initialized")


# adds to our list of DBS peers that get handled in the UDP server
def addDBSNode(nodeaddr):
    if nodeaddr.startswith('127.'):  # don't add loopback addresses
        return
    if nodeaddr not in blacklistedIPs:
        if nodeaddr not in dbsPeers:
            logToScreen("Adding {0:s} to dbsPeers".format(nodeaddr))
            dbsPeers.append(nodeaddr)
            logToScreen("dbs Peers: {0:s}".format(dbsPeers))


# returns the path to a particular file, if we have it.
def handleFileExistenceRequest(data):
    # this is where we look in our 'vault' for a filename with that is the hash
    hashstr = data.find('HASH').text
    if os.path.exists(hashstr + backupFileExt):
        pathstr = hashstr + backupFileExt
        return pathstr
    else:
        return ""


# adds information about a file 'chunk' to be used later.
def addToFileChunkTable(filename, hashvalue, filechunkidx):
    if filename == 'dbs.db':  # dont add ourselves
        return
    logToScreen("Adding entry for " + filename + ", " + str(filechunkidx) + ":" + hashvalue)
    conn = sqlite3.connect('dbs.db')
    c = conn.cursor()
    c.execute("INSERT INTO fileChunks (fileName,chunkChecksum,chunkIdx) VALUES (?,?,?)",
              (filename, hashvalue, filechunkidx,))
    conn.commit()
    conn.close()


# update the database to track that this entire file has been backed up
def setFileAsBackedUp(filepath):
    logToScreen("Incrementing file backup count for " + filepath)
    conn = sqlite3.connect('dbs.db')
    c = conn.cursor()
    # print "UPDATE files SET backedUp=%d WHERE fileName=%s", (1,str(filePath),)
    c.execute("UPDATE files SET backedUp=? WHERE fileName=?", (1, str(filepath),))
    conn.commit()
    conn.close()
    logToScreen('Backup of {0:s} complete.'.format(filepath))


# gets information from the sqlite database about a particular file chunk.
def getFileChunkInfo(filepath):
    chunksinfo = []
    conn = sqlite3.connect('dbs.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM fileChunks WHERE fileName=? ORDER BY chunkIdx ASC", (filepath,))
    for row in c:
        chunksinfo.append(row)
    conn.close()
    return chunksinfo


# sends a response message back to a UDP client
def sendUDPResponse(datatosend, addr):
    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cs.sendto(datatosend, (addr[0], ServerIPPort))
    except:
        traceback.print_exc(file=sys.stdout)
        pass


# sends a broadcast out on the local network.  It changes the last octet of the IP address
# and changes it to end in '.255' so the broadcast works successfully
def sendBroadcast(strdata):
    try:
        cs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cs.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        for ipAddress in socket.gethostbyname_ex(socket.gethostname())[2]:
            # if not ipAddress in blacklistedIPs:
            array = ipAddress.split('.')
            array[3] = '255'  # change the last octet of the address to the broadcast address
            tmp = array[0] + '.' + array[1] + '.' + array[2] + '.' + array[3]
            # logToScreen('Sending broadcast to ' + tmp)
            cs.sendto(strdata, (tmp, ServerIPPort))
    except:
        traceback.print_exc(file=sys.stdout)
        pass


# creates the DBS sqlite database
def CheckAndCreateDB(path):
    import uuid
    global encKey, recoveryMode

    # os.remove('dbs.db')
    # print 'Checking path: ' + path
    if not os.path.exists('dbs.db'):
        if not recoveryMode:
            recoveringstr = raw_input('Are you attempting to recover existing data? (y/n) : ')
            if recoveringstr == 'y' or recoveringstr == 'Y':
                enckeyin = raw_input('Input your identifier that was created on first use: ')
                print ''
                if len(enckeyin) > 0:
                    encKey = enckeyin
                    recoveryMode = True
                    missingFiles.append(sha256_for_bytes(encKey))
                    return

        logToScreen("Creating metadata DB")
        dbuuid = str(uuid.uuid4())
        dbuuid = dbuuid.replace("-", "")
        encKey = dbuuid

        print '*** Your DB Identifier is: ' + str(dbuuid) + ' ***'
        print '*** SAVE THIS IDENTIFIER IN CASE OF TOTAL FILE SYSTEM LOSS  ***'
        print '*** THIS IS IDENTIFIER IS NEEDED TO GET YOUR FILES BACK!    ***'
        print '***                PRESS ENTER TO CONTINUE                  ***'
        raw_input('')

        conn = sqlite3.connect('dbs.db')
        c = conn.cursor()
        c.execute('CREATE TABLE ident (uuid text)')
        c.execute('INSERT INTO ident (uuid) VALUES (?)', (str(dbuuid),))
        c.execute('CREATE TABLE files (fileName text, fileChecksum text, fileModDate text, backedUp int)')
        c.execute('CREATE TABLE fileChunks (fileName text, chunkChecksum text, chunkIdx int, backupCount int)')
        conn.commit()
        conn.close()

    filesinvault = getVaultFiles(path)

    conn = sqlite3.connect('dbs.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('SELECT uuid from ident')
    sqlresult = c.fetchone()
    if sqlresult:
        encKey = sqlresult[0]

    # determine if we have a entry for these files
    # if we do not, create an entry in the files table
    # if we do, check the file mod time.  If it is different
    # delete the existing data, and update it with the new hash and modification
    # time
    for filePath in filesinvault:
        # filePathTup = os.path.split(filePath)
        # print repr(filePath)
        c.execute("SELECT * FROM files WHERE fileName=?", (filePath,))
        sqlresult = c.fetchone()
        if sqlresult is None:
            c.execute("INSERT INTO files VALUES (?,?,?,?)",
                      (filePath, sha256_for_file(filePath), os.path.getmtime(filePath), 0,))
            if filePath not in queuedFiles:
                queuedFiles.append(filePath)
            conn.commit()
        else:
            dbfiledate = sqlresult['fileModDate']
            if os.path.exists(filePath):
                fsfiledate = os.path.getmtime(filePath)
                if round(float(dbfiledate), 2) != round(float(fsfiledate), 2):
                    if sha256_for_file(filePath) != sha256_for_file(filePath):
                        c.execute("SELECT chunkChecksum FROM fileChunks WHERE fileName=?", (filePath,))
                        for row in c:  # remove old chunks from other nodes
                            top = Element('DELETE_CHUNK')
                            child = SubElement(top, 'HASH')
                            child.text = row[0]
                            sendBroadcast(tostring(top))
                        c.execute("DELETE FROM fileChunks WHERE fileName=?", (filePath,))
                        c.execute("UPDATE files SET fileModDate=?,fileChecksum=?,backedUp=0 WHERE fileName=?",
                                  (fsfiledate, sha256_for_file(filePath), filePath,))
                        conn.commit()
                        if filePath not in queuedFiles:
                            queuedFiles.append(filePath)
                if int(sqlresult["backedUp"]) == 0:
                    if filePath not in queuedFiles:
                        queuedFiles.append(filePath)
            else:
                if filePath not in queuedFiles:
                    queuedFiles.append(filePath)

    # find files that are not on the filesystem that exist in the DB
    c.execute('SELECT fileName FROM files')
    for row in c:
        # print row["fileName"]
        if not (str(row["fileName"]) in filesinvault):
            if not (str(row["fileName"]) in missingFiles):
                logToScreen('*** File in DB but not on filesystem: ' + row["fileName"] + ' ***')
                missingFiles.append(row["fileName"])

    conn.close()


# computes the SHA-256 hash of a byte array
def sha256_for_bytes(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


# computes the SHA-256 hash of a file
def sha256_for_file(filename, block_size=2 ** 20):
    sha256 = hashlib.sha256()
    f = open(filename)
    while True:
        data = f.read(block_size)
        if not data:
            break
        sha256.update(data)
    f.close()
    return sha256.hexdigest()


# returns information about the files that are to be backed up
# see the --folder argument
def getVaultFiles(currentdir):
    try:
        filelist = []
        for root, dirs, files in os.walk(currentdir):  # Walk directory tree
            for f in files:
                fullpath = os.path.join(root, f)
                ext = os.path.splitext(fullpath)[1]
                if not ext == backupFileExt:
                    filelist.append(fullpath.decode('utf-8'))
        # print infos
        return filelist
    except:
        traceback.print_exc(file=sys.stdout)
        pass


# logs data to the scrren for later analysis
def logToScreen(logmessage):
    print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " - " + logmessage


# terminates script operation, and broadcasts a message to other peers, so that this
# node may be removed from their dbsPeers list.
def shutdownScript():
    sendBroadcast('DBS_SHUTDOWN')
    global runThreads
    runThreads = False
    os._exit(1)


# catched SIGTERMs and calls the shutdown function
def sighandler(signum, frame):
    logToScreen('Caught SIGTERM')
    shutdownScript()


def fix_bytes(byte_list):
    # bytes function is broken in python < 3. It appears to be an alias to str()
    # Either that or I have insufficient magic to make it work properly. Calling bytes on my
    # array returns a string of the list as if you fed the list to print() and captured stdout
    tmpstr = ''
    for i in byte_list:
        tmpstr += chr(i)
    return


# uses PyCrypto to encrypt a datastream using AES encryption
def encryptBytes(data):
    global noCrypto
    if noCrypto:
        return data

    from Crypto.Cipher import AES
    infile = StringIO.StringIO(data)
    iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
    encryptor = AES.new(encKey, AES.MODE_CBC, iv)

    infile.seek(0)
    outfile = StringIO.StringIO()
    outfile.write(struct.pack('<Q', len(data)))
    outfile.write(iv)

    chunksize = 64 * 1024
    while True:
        chunk = infile.read(chunksize)
        if len(chunk) == 0:
            break
        elif len(chunk) % 16 != 0:
            chunk += ' ' * (16 - len(chunk) % 16)
        outfile.write(encryptor.encrypt(chunk))

    infile.close()
    outfile.flush()
    strval = outfile.getvalue()
    outfile.close()

    return strval


# uses PyCrypto to decrypt a datastream using AES encryption
def decryptBytes(data):
    global noCrypto
    if noCrypto:
        return data
    from Crypto.Cipher import AES
    infile = StringIO.StringIO(data)
    outfile = StringIO.StringIO()

    infile.seek(0)
    origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
    iv = infile.read(16)
    decryptor = AES.new(encKey, AES.MODE_CBC, iv)

    chunksize = 64 * 1024
    while True:
        chunk = infile.read(chunksize)
        if len(chunk) == 0:
            break
        outfile.write(decryptor.decrypt(chunk))

    infile.close()
    outfile.flush()
    outfile.truncate(origsize)
    strval = outfile.getvalue()
    outfile.close()
    return strval


# reports whether a Python module is available
def module_exists(module_name):
    try:
        __import__(module_name)
    except ImportError:
        return False
    else:
        return True


# the 'driver' for the application
def main():
    global runThreads
    global progOptions
    global noCrypto
    global DistributionCount
    global dbsPeers

    logToScreen("##### Distributed Backup System v0.1 #####")
    optParser.add_option("--ip", action="store", type="string", dest="ipAddress", default="0.0.0.0")
    optParser.add_option("--folder", action="store", type="string", dest="dbsFolder", default=os.path.sys.path[0])
    optParser.add_option("--distcount", action="store", type="int", dest="distCount", default=1)
    optParser.add_option("--crypto", action="store", type="string", dest="crypto", default="yes")
    optParser.add_option("--dbspeers", action="store", type="string", dest="dbsPeers", default="")
    (progOptions, args) = optParser.parse_args()

    if (not module_exists('Crypto')) or (progOptions.crypto != 'yes'):
        noCrypto = True
        logToScreen('Crypto Disabled')

    if len(progOptions.dbsPeers) > 0:
        dbsPeers = progOptions.dbsPeers.replace(' ', '').split(',')

    DistributionCount = progOptions.distCount

    CheckAndCreateDB(progOptions.dbsFolder)
    CreateSockets()

    # Get the interfaces on this machine.  We dont' want to add ourselves to the
    # dbs node list
    for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
        blacklistedIPs.append(ip)

    runThreads = True
    clientthread = ClientThread()
    tcpserverthread = TCPServerThread(TCPServerSocket)
    udpserverthread = UDPServerThread(UDPServerSocket)
    clientthread.start()
    tcpserverthread.start()
    udpserverthread.start()
    signal.signal(signal.SIGINT, sighandler)

    top = Element('NDB')
    child = SubElement(top, 'MACHINE_NAME')
    child.text = socket.gethostname()
    ndbxml = tostring(top)

    while runThreads:
        sendBroadcast(ndbxml)
        time.sleep(5)


main()
