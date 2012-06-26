import sys
import mmap

# JPEG header
header = reduce(lambda x, y: x+y, map(chr, [0xff, 0xd8, 0xff, 0xe0]))
# Other types:
# 0xffd8ffdb, 0xffd8ffe1, 0xffd8ffe2, 0xffd8ffe3, 0xffd8ffe8]

# JPEG trailer
trailer = reduce(lambda x, y: x+y, map(chr, [0xff, 0xd9]))

def extract_jpg(fname):
    found_idx = 0
    with open(fname, "r+b") as f:
        # memory-map the file, size 0 means whole file
        fmap = mmap.mmap(f.fileno(), 0)
    
        pos = fmap.find(header)
        while pos != -1:
            print "Found possible jpeg header at 0x%x" % (pos)
            pos_old = pos
                        
            pos_tr = fmap.find(trailer, pos + 4)
            print "Found possible jpeg trailer at 0x%x" % (pos_tr)
                      
            # Search for other occurences
            pos = fmap.find(header, pos + 2)
            
            # Create output file
            fout = open("out\jpeg" + str(found_idx) + ".jpg", "wb")
            fmap.seek(pos_old)
            if pos == -1 :
                fout.write(fmap.read(pos_tr - pos_old + 2))
            else :
                fout.write(fmap.read(min(pos,pos_tr) - pos_old + 2))
            fout.close()
            found_idx = found_idx + 1
                    
        # close the map
        fmap.close()
    
if __name__=="__main__":
    extract_jpg(sys.argv[1])