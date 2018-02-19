#!/usr/bin/python

import serial, time, sys, time
#initialization and open the port

if not len(sys.argv) == 4:
   print "Usage: serialTest port baudrate fileNameToSend"
   print "Example: serialTest /dev/ttyUSB0 57600 test_small.gco"
   exit()

current_milli_time = lambda: int(round(time.time() * 1000))

#possible timeout values:
#    1. None: wait forever, block call
#    2. 0: non-blocking mode, return immediately
#    3. x, x is bigger than 0, float allowed, timeout block call

ser = serial.Serial()
ser.port = sys.argv[1]
#ser.port = "\\.\COM4"
#ser.port = "/dev/ttyS2"
ser.baudrate = int(sys.argv[2])
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
#ser.timeout = None          #block read
ser.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
ser.xonxoff = False     #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2     #timeout for write

try: 
    ser.open()
except Exception, e:
    print "error open serial port: " + str(e)
    exit()

if ser.isOpen():

    try:
        ser.flushInput() #flush input buffer, discarding all its contents
        ser.flushOutput()#flush output buffer, aborting current output 
                 #and discard all that is in buffer
        numOfLines = 0

        done = False
        while True:
            response = ser.readline()
            print("rsp: " + response)
            #print("rec: " + ":".join("{:02x}".format(ord(c)) for c in response))

            if ("SD card ok" in response):
                ser.write("M28 "+ sys.argv[3]+"\n")

            if ("Writing to file:" in response):
                with open(sys.argv[3]) as f:
                    startTime = current_milli_time()
                    for line in f:
                        numOfLines += 1
                        if (numOfLines % 100 == 0):
                           sys.stdout.write(".")
                           sys.stdout.flush()
                        command_to_send = "N" + str(numOfLines) + " " + line.rstrip()
                        checksum = 0
                        for c in bytearray(command_to_send):
			                checksum ^= c
                        command_to_send = command_to_send + "*" + str(checksum)+"\n"
                        print(command_to_send)
                        ser.write(command_to_send)                                     
                        if ser.in_waiting > 0:
                           inByte = ser.read(1)
                           if ord(inByte[0]) == 19:
                              while True:
                                    inByte = ser.read(1)
                                    if ord(inByte[0]) == 17:
                                       break;
                    ser.flushOutput()
                    endTime = current_milli_time()
                    deltaTime = endTime - startTime
                    print("Done in ")
                    print(deltaTime)
                    print("Sending M29")
                    ser.write("M29 \n")
            if ("Done saving file." in response):
                break
        ser.flushOutput()    
        ser.close()            
    except Exception, e1:
        print "error communicating...: " + str(e1)

else:
    print "cannot open serial port "
