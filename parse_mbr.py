''' Decode partition table from MBR file

    In: file containing MBR data. Obtained with:
    dd if=/dev/sda of=mbr count=512   (on Linux)
    dd if=\\.\PhysicalDrive0 of=mbr count=1  (on Windows with dd from UnxUtils)

http://en.wikipedia.org/wiki/Master_boot_record    
    
'''
import getopt, sys
import struct

def usage():
    print '''Usage:
    python parse_mbr.py [-param=value]
    Params:
    -h, --help                      print this
    -i file, --input=file           set input file    
    
    E.g.: python parse_mbr.py -i mbr 
    '''

# All multi-byte fields in a 16-byte partition record are little-endian
# Use '<' when unpacking structs below
 
# Read an unsigned byte from current position in f
def read_ub(f):
    return struct.unpack('B', f.read(1))[0]

# Read a signed int (4 bytes) from current position in  f    
def read_ui(f):
    return struct.unpack('<I', f.read(4))[0]
    
# Read a short int (2 bytes) from current position in  f    
def read_s(f):
    return struct.unpack('<h', f.read(2))[0]

def is_mbr():
    # Check MBR signature. Must be 0x55AA
    f.seek(510)
    mbr_sig = read_s(f)
    print "Read MBR signature: 0x%04X" % (mbr_sig)
    if (mbr_sig == 0x55AA):
        print "Correct MBR signature"
    else:
        print "Incorrect MBR signature"

def parse_part_entry():
    bootable = read_ub(f)
    if (bootable == 0x00):
        print '  Non bootable'
    else:
        if (bootable == 0x80):
            print '  Bootable'
        else: 
            print '  Invalid bootable byte'
    
    start_head = read_ub(f)
    tmp = read_ub(f)
    start_sector = tmp & 0x3F
    start_cylinder = (((tmp & 0xC0)>>6)<<8) + read_ub(f)
    #print "  CHS of first sector: %d %d %d" % (start_cylinder, start_head, start_sector)
    part_type = read_ub(f)
    
    print "  Partition type: 0x%02X" % (part_type)
    
    end_head = read_ub(f)
    tmp = read_ub(f)
    end_sector = tmp & 0x3F
    end_cylinder = (((tmp & 0xC0)>>6)<<8) + read_ub(f)
    #print "  CHS of last sector: %d %d %d" % (end_cylinder, end_head, end_sector)
    
    lba = read_ui(f)
    print "  LBA of first absolute sector: %d" % (lba)    
    
    num_sectors = read_ui(f)    
    print "  Number of sectors in partition: %d" % (num_sectors)
                    
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
    
    is_mbr()
    
    for i in range(0,4):
        print "Partition %d" % (i+1)
        f.seek(446 + i * 16)
        parse_part_entry()
        