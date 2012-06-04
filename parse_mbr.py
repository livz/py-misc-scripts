''' Decode partition table from MBR file

    In: file containing MBR data. Obtained with:
    dd if=/dev/sda of=mbr count=512   (on Linux)
    dd if=\\.\PhysicalDrive0 of=mbr count=1  (on Windows with dd from UnxUtils)

http://en.wikipedia.org/wiki/Master_boot_record    
    
'''
import getopt, sys
import struct
from wsgiref.validate import check_status

def usage():
    print '''Usage:
    python parse_mbr.py [--param=value]
    Params:
    -h, --help                      print this
    -i file, --input=file           set input file    
    
    E.g.: python parse_mbr.py -i mbr 
    '''

# All multi-byte fields in a 16-byte partition record are little-endian!
# Use '<' when unpacking structs below
 
# Read an unsigned byte from data block
def read_ub(data):
    return struct.unpack('B', data[0])[0]
  
# Read an unsigned short int (2 bytes) from data block    
def read_us(data):
    return struct.unpack('<H', data[0:2])[0]

# Read an unsigned int (4 bytes) from data block    
def read_ui(data):
    return struct.unpack('<I', data[0:4])[0]

class PartitionEntry:
    def __init__(self, data):
        self.Status = read_ub(data)
        self.StartHead = read_ub(data[1])
        tmp = read_ub(data[2])
        self.StartSector = tmp & 0x3F
        self.StartCylinder = (((tmp & 0xC0)>>6)<<8) + read_ub(data[3])
        self.PartType = read_ub(data[4])
        self.EndHead = read_ub(data[5])
        tmp = read_ub(data[6])
        self.EndSector = tmp & 0x3F
        self.EndCylinder = (((tmp & 0xC0)>>6)<<8) + read_ub(data[7])
        self.LBA = read_ui(data[8:12])
        self.NumSectors = read_ui(data[12:16])    
    
    def print_partition(self):
        self.check_status()
        print "CHS of first sector: %d %d %d" % \
            (self.StartCylinder, self.StartHead, self.StartSector)
        print "Part type: 0x%02X" % self.PartType
        print "CHS of last sector: %d %d %d" % \
            (self.EndCylinder, self.EndHead, self.EndSector)
        print "LBA of first absolute sector: %d" % (self.LBA)
        print "Number of sectors in partition: %d" % (self.NumSectors)
                
    def check_status(self):
        if (self.Status == 0x00):
            print 'Non bootable'
        else:
            if (self.Status == 0x80):
                print 'Bootable'
            else: 
                print 'Invalid bootable byte'
        
# Table of four primary partitions        
class PartitionTable:
    def __init__(self, data):
        self.Partitions =[PartitionEntry(data[16*i:16*(i+1)]) for i in range (0, 4)]

# Master Boot Record        
class MBR:
    def __init__(self, data):
        self.BootCode = data[:440]
        self.DiskSig = data[441:444]
        self.Unused = data[444:446]        
        self.PartitionTable = PartitionTable(data[446:510])        
        self.MBRSig = data[510:512]
        
    def check_mbr_sig(self):
        mbr_sig = read_us(self.MBRSig)
        print "Read MBR signature: 0x%04X" % (mbr_sig)
        if (mbr_sig == 0xAA55):
            print "Correct MBR signature"
        else:
            print "Incorrect MBR signature"        
                      
if __name__=="__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:h", ["help", "input="])
    except getopt.GetoptError, err:
        print str(err) # will print something like "option -x not recognized"
        usage()
        sys.exit(2)
        
    input = None
    
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--input"):
            input = a
        else:
            assert False, "Unhandled option"

    if not input:
        usage()
        sys.exit()
        
    f = open(input, 'rb')
    data = f.read()
    print "Read: %d bytes" % (len(data))
    
    master_br = MBR(data)    
    master_br.check_mbr_sig()
    
    for partition in master_br.PartitionTable.Partitions:
        print ""
        partition.print_partition()    
    
    f.close()