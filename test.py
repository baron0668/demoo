#!/usr/bin/python
import os
booksPath = "books"
deDrmOutputPath = "deDrmBooks"

def sqliteTest():
	import sqlite3

	#read db to key/value
	result = {}
	conn = sqlite3.connect('app_readmoo_0.localstorage')
	cursor = conn.execute('SELECT * FROM ItemTable')
	for row in cursor:
		result[row[0]] = row[1]
	conn.close()

	#print result	
	for item in result:
		print item, ": ", result[item]

def Base64Decoder(inputString):
	import struct
	import binascii
	mapping = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
		'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
		'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 
		'a', 'b', 'c','d', 'e', 'f', 'g', 'h', 'i', 
		'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 
		's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 
		'0', '1', '2', '3', '4', '5', '6', '7', '8', 
		'9', '+', '/')
	equalSymbleCounts = inputString.count('=')
	print 'decode string size: ', ((len(inputString) - equalSymbleCounts)*6 - equalSymbleCounts*2)/8, " bytess"
	mappingResult = []
	groupResult = []
	for char in inputString:
		if char != '=':
			mappingResult.append(mapping.index(char))
	print "mapping result list size: ", len(mappingResult)
	for i in range(0, len(mappingResult)-3, 4) :
		result = 0
		a = mappingResult[i]
		b = mappingResult[i+1]
		c = mappingResult[i+2]
		d = mappingResult[i+3]
		result = result|(a<<(24-6))
		result = result|(b<<(24-12))
		result = result|(c<<(24-18))
		result = result|d
		groupResult.append(result)
		print "[", bin(a), bin(b), bin(c), bin(d), "] ", bin(result)

def getAllFiles():
	booksImagesPath = "OEBPS/Images"
	booksStylePath = "OEBPS/Styles"
	booksTextPath = "OEBPS/Text"
	files = []
	for r, d, f in os.walk(booksPath):
		for file in f:
			if (r.find(booksImagesPath) >= 0 or r.find(booksStylePath)>=0 or r.find(booksTextPath)>=0):
				files.append(os.path.join(r, file))
	return files

def checkAllFolderExist(files):
	print 'checking output folders...'
	for file in files:
		outputPath = file.replace(booksPath, deDrmOutputPath, 1)
		dirname = os.path.dirname(outputPath)
		isExist = os.path.exists(dirname)
		print dirname, " is existes: ", isExist
		if not isExist:
			os.makedirs(dirname)



def fileTest():

	encryptionFilePath = "META-INF/encryption.xml"
	booksImagesPath = "OEBPS/Images"
	booksStylePath = "OEBPS/Styles"
	booksTextPath = "OEBPS/Text"
	booksRoot = []
	files = []
	folders = []
	for r, d, f in os.walk(booksPath):
		for file in f:
			files.append(os.path.join(r, file))
		for folder in d:
			folders.append(os.path.join(r, folder))

	for file in files:
		print(file)


def DecryptBooks():
	import Crypto
	import base64
	from Crypto.Cipher import PKCS1_v1_5
	from Crypto.PublicKey import RSA
	from Crypto.Cipher import AES
	from Crypto import Random
	from Crypto.Hash import SHA

	pvkPem = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCUbnsB/meoYiE7ZhXYBLi2EAI3SFCrTcoFE2MYmBv0ZP8QcVtk
qLS/2RW5ZRcpYl4gacf4xKgg7/VZDCaYGpEoIPWGKRfDKl7b7Pd/RuRxYua587KC
8PXfwgGuswpoN2cFgO/4plK6AUa190j46ZFXOV2tR8VahajF7+2CpYyghwIDAQAB
AoGAcKrT8BV99VBXTVEV75zV4EySgggAQ6eOWv/2TmrXfVFUUtTYvLVaTe2oEcvs
Itup+wyQYAJWZHoAUBFrEjXIS/I+yI+4AX8HJPvI5/dclQ1VkxO5YwHlWf4CLk+r
w19sR7WCM7AQcZMac7Kw6fxTGayj1MbR9SU6//s44NcoYsECQQDruAPxv+hfAS9r
X92bmsxXJJDsLrknJKXip9+T7xW98zk3FGxaWPN5tRpTXQ+esphetUgqIZyg8loQ
nUk3QmCXAkEAoTPcUpLapR3SCZMVZ4qBKt5pFPRCMPGy5HcWxvPy5OfT0DFmbhqu
imOD1rNUxLcBy+a1HUaOO+h3be3cU53NkQJABqdpJRffvV7RMdzA6rWR8xvLI3+m
Jl64eA95Fjn3iScmhFGFRX+hT9w25AeKe1ZbSsEfSmEshLaSqEloWbD7/QJAaTHd
kekRU3TNTsAz1JiWx/HRowHue+AN/HcWXwhstiHuoErMbAdvZRGhxCbMp35BZt0L
zanwQXnnDc6N2+b7cQJBANP2MDAP9ewAJ5cpu/HLQ8zI0HAtwIEk+WdTAK1CSB/3
LNMDjn/fC4zTOimkc66WPB3lfhHBE98JAuhzJiWK5Hc=
-----END RSA PRIVATE KEY-----"""
	encryptDataBase64 = "jphU5T4jjnu48N2kvKB4xmGZZZZw9VJexNMteLUeD8yIaILm9j51F6T3dMH6S4q/fu723U9U7gwcz5/s/ai2tOc200WgOU/7ef+LDR9AY1ti6/dnaAd2gloINQRqp7a3NYWHkBfSrk0dLVyN8cvxoNwwD960/SBtoCH6MwqlT1w="
	encryptData = base64.b64decode(encryptDataBase64)
	print "cypher: ", encryptData.encode('hex')
	dsize = SHA.digest_size
	sentinel = Random.new().read(15+dsize)
	key = RSA.importKey(pvkPem)
	rsaCipher = PKCS1_v1_5.new(key)
	decryptPvKey = rsaCipher.decrypt(encryptData, sentinel)
	print "private key: ", decryptPvKey.encode('hex')
	#get all files
	encryptedFiles = getAllFiles()
	checkAllFolderExist(encryptedFiles)
	for file in encryptedFiles:
		outputPath = file.replace(booksPath, deDrmOutputPath, 1)
		fileName = os.path.basename(file)
		print "read in file: ", file
		f = open(file, 'r')
		inputBytes = f.read()
		iv = inputBytes[:16]
		cipherText = inputBytes[16:]
		aesCipher = AES.new(decryptPvKey, AES.MODE_CBC, iv)
		print "decrypting"
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

		print "write out to file: ", outputPath
		f = open(outputPath, 'w')
		f.write(decryptBytes[:decryptBytesLen-paddingLength])
		print "decrypt ", file, " is finished."



	# #read file to decrypt by aes
	# fileInput = "Cover.jpg"
	# subName = fileInput[fileInput.index('.')+1:]
	# fileOutput = fileInput[:fileInput.index('.')] + "_d." + subName
	# f = open(fileInput, 'r')
	# decryptSample = f.read()
	# # print "input file: ", decryptSample.encode('hex')
	# print "first 16 bytes: ", decryptSample[:16].encode('hex')
	# print "aes block size: ", AES.block_size
	# iv = decryptSample[:16]
	# cipherText = decryptSample[16:]
	# aesCipher = AES.new(decryptPvKey, AES.MODE_CBC, iv)
	# msg = aesCipher.decrypt(cipherText)
	# f = open(fileOutput, 'w')
	# f.write(msg)
	# print "decrypt msg len: ", len(msg)

def EncryptTest():
	import Crypto
	from Crypto.PublicKey import RSA

	text = "Can you see me?"
	f = open("testkey.pem", 'r')
	key = RSA.importKey(f.read())
	encryptedText = key.encrypt(text, 32)
	encryptedTextBytes = str(encryptedText[0])

	pvkString = """-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQC2F3ZzZhR+dW1e9vM5fFUiMoK+P4nSClroDqkkuJg45o1jGRCE
2P1ISaqRa4o5jTNnWZWjJdFxCHJN0kJgp3qIId5lDEAI1Cz2rUrwCeWDHrfXJalk
ZQYHLO994mypg9K2XFnH3yN86Ec8uHftxWf3xqJPH1SGihcwrD1kYdAClQIDAQAB
AoGAIxvK/t0Dvo4tlE3Q/5h1Ya6TftMJY7ITbQLGognlb7MkN6MxiCu+Sh3KAVfW
wtnyu06Oh3JXO5ABWffcTH5+JUXwLs9bWsfl+lKhL5a7gUACJPfoq6/dCcqzuwPR
/e2i+Gwuv4cDe+J8bxC99AeuPSFpiy8T8/KL/+3xW4S+VdECQQDghDH/dSvzCBnl
LHF7yj+ik/ccWxy7AsjYsJ6UutcKDXtArC9o0hsbOi/cRsjxGIUh6C5Wp4uMJvAM
PON8EoZLAkEAz6BISpSvmBz06zf5+mRcSuGQ5sAQ3xP8IETqVXQymDj+Lzmit+Xd
1KmA9tU7FO7Vb6yAZYCXWGDYc5EglNOOnwJBAKet03GI3yQJXt2sDa14ZYJUo+/H
lHOPJtW/QxCtYkEdxHmOn3HXyWrSUEBhlV2LBJNIRqNtSmmIAywApZ1acHUCQFSM
sOOuKNOI9zPSV7nfpLXZpWhSToyJVuLNLaAe8XuLufcBQYIh2XQAksPxkV205LXV
SXQMKZWT2pE1SE9S14ECQE1UGFqBQDUw1/won1Aa+iPXm3aivvz0hi5koaYdIIlO
DmAJzqBEPUCfWf34g8MieR2FmP1eVGyPKax09awOJoE=
-----END RSA PRIVATE KEY-----"""

	key = RSA.importKey(pvkString)
	decryptedText = key.decrypt(encryptedTextBytes)
	print decryptedText

# files = getAllFiles()
# checkAllFolderExist(files)
DecryptBooks()

# import base64
# encodeString = "SGVsbG8gQmFzZTY0ISEhISEhISEhIQ=="
# decodeResult = base64.b64decode(encodeString)
# print "base64 encode string: ", encodeString
# print "correct result is: ", decodeResult, "(", len(decodeResult), ")"

# Base64Decoder(encodeString)




