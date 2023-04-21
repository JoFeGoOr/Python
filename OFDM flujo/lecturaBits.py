import numpy


pathin = "/home/uno/Python/OFDM flujo/bit-in.txt"
pathout = "/home/uno/Python/OFDM flujo/bit-out.txt"

fin = numpy.fromfile(pathin,numpy.byte)
fout = numpy.fromfile(pathout,numpy.byte)

print("largo de bits entrantes : ",len(fin),sep="")
print("largo de bits salientes : ",len(fout),sep="")

