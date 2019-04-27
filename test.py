#!/usr/bin/python
#-*- coding: utf8 -*-
import os
import sys
from os.path import expanduser
import sqlite3
import json
from StringIO import StringIO
from Crypto.PublicKey import RSA

homePath = expanduser("~")
booksPath = "books"
downloadPath = 'download'
deDrmOutputPath = "deDrmBooks"
dbPath = homePath + "/Library/Application Support/Readmoo/Local Storage/" + "app_readmoo_0.localstorage"
epubPathDownload = None
rsaPrivateKey = None
userId = None
userToken = None
userBooksLibraryData = None
currentBooksInLibrary = {}
toDecryptLocations = {}
clientId = '8bb43bdd60795d800b16eec7b73abb80'
epubDownloadUrl = 'https://api.readmoo.com/epub/'

def getEpubUrl(bookId):
	return epubDownloadUrl + bookId + '?client_id='+ clientId + '&access_token=' +userToken

def downloadEpub(bookId):
	import urllib2

	url = getEpubUrl(bookId)
	downloadToPath = os.path.join(downloadPath, userId)
	downloadToFileName = bookId + '.epub'
	outputFile = os.path.join(downloadToPath, downloadToFileName)
	if os.path.exists(outputFile):
		print outputFile, ' is exists. return.'
		return

	print 'open link: ', url
	response = urllib2.urlopen(url)

	#check folder
	if not os.path.exists(downloadToPath):
		os.makedirs(downloadToPath)
	
	print 'create file: ', outputFile
	file = open(outputFile, 'wb')
	print 'downloading...'
	file.write(response.read())
	print 'downloading finished.'
	

def extractEpub(bookId):
	import zipfile

	epubFile = os.path.join(downloadPath, userId, bookId + '.epub')
	toPath = os.path.join(os.path.dirname(epubFile), bookId)
	if not os.path.exists(toPath):
		os.makedirs(toPath)
	zf = zipfile.ZipFile(epubFile, mode='r')
	print 'extract epub file...'
	zf.extractall(toPath)
	zf.close()


def decryptAESKey(privateKey, cipherText):
	from Crypto.Cipher import PKCS1_v1_5
	from Crypto.PublicKey import RSA
	from Crypto import Random
	from Crypto.Hash import SHA
	import base64

	cipherText = base64.b64decode(cipherText)
	dsize = SHA.digest_size
	sentinel = Random.new().read(15+dsize)
	key = RSA.importKey(privateKey)
	rsaCipher = PKCS1_v1_5.new(key)
	decryptPvKey = rsaCipher.decrypt(cipherText, sentinel)
	return decryptPvKey

def decryptFiles(aesKey, bookId, encryptedFiles, outputRootPath):
	from Crypto.Cipher import AES

	rootPath = os.path.join(epubPathDownload, bookId)
	outputBookPath = outputRootPath + "/" + bookId
	print 'aes key ', aesKey.encode('hex')
	print 'input path ', rootPath
	print 'out path ', outputBookPath

	for file in encryptedFiles:
		filePath = rootPath + "/" + file
		outputFile = outputBookPath + "/" + file
		fileName = os.path.basename(filePath)
		dirName = os.path.dirname(outputFile)
		if not os.path.exists(dirName):
			os.makedirs(dirName)

		f = open(filePath, 'r')
		inputBytes = f.read()
		iv = inputBytes[:16]
		cipherText = inputBytes[16:]
		aesCipher = AES.new(aesKey, AES.MODE_CBC, iv)
		print "decrypting file: ", fileName
		decryptBytes = aesCipher.decrypt(cipherText)
		decryptBytesLen = len(decryptBytes)
		#remove padding
		lastByte = decryptBytes[decryptBytesLen-1: decryptBytesLen]
		paddingLength = 0
		print 'last 16 byte: ', decryptBytes[decryptBytesLen-16: decryptBytesLen].encode('hex')
		# print 'last byte: ', lastByte.encode('hex')
		for index in range(decryptBytesLen-1, decryptBytesLen-17, -1):
			if decryptBytes[index] == lastByte:
				paddingLength += 1
			else:
				break;
		print "padding: ", lastByte.encode('hex'), "  padding length: ", paddingLength


		print 'add new file: ', outputFile
		f = open(outputFile, 'w')
		f.write(decryptBytes[:decryptBytesLen-paddingLength])
		print "decrypt ", file, " is finished."

def checkOtherFiles(bookId, outputRootPath):
	rootPath = os.path.join(epubPathDownload, bookId)
	outPath = outputRootPath + "/" + bookId

	for r, d, f in os.walk(rootPath):
		for name in d:
			outputDir = os.path.join(r, name)
			outputDir = os.path.relpath(outputDir, rootPath)
			outputDir = os.path.join(outPath, outputDir)
			if not os.path.exists(outputDir):
				#create folder
				print "create folder: ", outputDir
				os.makedirs(outputDir)
		for name in f:
			basename = os.path.basename(name)
			if basename != 'encryption.xml':
				outputFile = os.path.join(r, name)
				outputFile = os.path.relpath(outputFile, rootPath)
				outputFile = os.path.join(outPath, outputFile)
				if not os.path.exists(outputFile):
					#copy file
					srcFile = os.path.join(r, name)
					file = open(srcFile, 'r')
					inputData = file.read()
					print "create file: ", outputFile
					file = open(outputFile, 'w')
					file.write(inputData)

def outputDecryptedEpubFile(bookId, outputPath):
	import zipfile
	outputZipFilePath = outputPath + "/" + bookId + ".epub"
	booksPath = outputPath + "/" + bookId
	print 'create zip file: ', outputZipFilePath 
	zf = zipfile.ZipFile(outputZipFilePath, mode='w')
	for r, d, f in os.walk(booksPath):
		for name in f:
			filePath = os.path.join(r, name)
			zipFilePath = os.path.relpath(filePath, booksPath)
			file = open(filePath, 'r')
			fileByte = file.read()
			zf.writestr(zipFilePath, fileByte)

	print zf.printdir()
	zf.close()

def decryptBook(bookId):
	import xml.etree.ElementTree as ET

	#find encryption.xml
	encryptonFilePath = 'META-INF/encryption.xml'
	bookTopPath = os.path.join(epubPathDownload, bookId)
	xmlTree = ET.parse(os.path.join(bookTopPath, encryptonFilePath))
	root = xmlTree.getroot()
	#get the cipher of encrypted key
	mainEncryptedKey = root.find('{http://www.w3.org/2001/04/xmlenc#}EncryptedKey')
	for child in mainEncryptedKey.iter('{http://www.w3.org/2001/04/xmlenc#}CipherValue'):
		mainEncryptedKey = child.text

	#get all cipher ref of encrypted files
	encryptedFilesReference = []
	for child in root.iter('{http://www.w3.org/2001/04/xmlenc#}CipherReference'):
		encryptedFilesReference.append(child.attrib['URI'])

	#decrypt aes key
	aesKey = decryptAESKey(rsaPrivateKey, mainEncryptedKey)

	decryptFiles(aesKey, bookId, encryptedFilesReference, "output")
	print "checking other files..."
	checkOtherFiles(bookId, "output")
	outputDecryptedEpubFile(bookId, "output")
	
#check platform
if sys.platform != 'darwin':
	print 'not support for ', sys.platform, ". return."
	sys.exit()

#read db from readmoo
conn = sqlite3.connect(dbPath)
cursor = conn.execute('SELECT * FROM ItemTable')
for row in cursor:
	if row[0] == 'rsa_privateKey':
		rsaPrivateKey = str(row[1]).decode('utf16')
	elif row[0] == '-nw-library':
		userBooksLibraryData = str(row[1]).decode('utf16')
	elif row[0] == '-nw-access_token':
		userToken = str(row[1]).decode('utf16')
	elif row[0] == '-nw-userid':
		userId = str(row[1]).decode('utf16')
conn.close()

epubPathDownload = os.path.join(downloadPath, userId)

#parse book info
io = StringIO(userBooksLibraryData)
userBooksLibraryData = json.load(io)
for item in userBooksLibraryData:
	bookId = item['library_item']['book']['id']
	title = item['library_item']['book']['title']
	currentBooksInLibrary.update({bookId: title})

allBooksId = currentBooksInLibrary.keys()
if len(allBooksId) <= 0:
	print 'there is no book to encrypt. finish.'
	sys.exit()
else:
	print 'user id: ', userId
	print 'all your books:'
	#print books list
	for index in range(0, len(allBooksId)):
		bookId = allBooksId[index]
		print '    #', index, currentBooksInLibrary[bookId], '(', bookId, ')' 
	print ''

	inputNumber = -1
	while inputNumber < 0 or inputNumber >= len(allBooksId):
		inputNumber = input('input the number to decrypt: ')
	#process the book
	choosedBookId = allBooksId[inputNumber]

	downloadEpub(choosedBookId)
	extractEpub(choosedBookId)
	decryptBook(choosedBookId)