#!/usr/bin/env python

"""
 parse the MESA/star log output file.

 this assumes a specific format:

                          1                           2                           3...
               model_number                   num_zones                initial_mass...
                       4750                        1172     2.9999999999999999E-001...

                          1                           2                           3... 
                       zone                        logT                      logRho... 
                         1     4.5031064327826922E+000    -8.4229776040919830E+000 ...
                         2     4.5109540241070087E+000    -8.3780544160374770E+000 ...
                         ...

where the header is on the first three lines, then a blank line,
then the column definitions, then the data.

DLK 2010-07-29

"""


import sys,datetime
import pyfits,numpy,math
import os
import getopt

######################################################################
def main():

    if (len(sys.argv[1:]) == 0):
        usage()
        sys.exit(0)

    for infilename in sys.argv[1:]:
	infileroot,ext=os.path.splitext(infilename)
	outfilename=infileroot + '.fits'
	
	try:
	    f=open(infilename,'r')
	except:
	    print "Could not open input file %s",infilename
	    sys.exit(1)
	lines=f.readlines()
	params={}
	columns={}
	columnnames=[]
	types=[]
	
	for linenumber in xrange(len(lines)):
	    line=lines[linenumber]
	    # get rid of newline
	    line=str(line[:-1])
	    if (linenumber == 1):
	        # this has the parameter definitions
	        paramnames=line.split()
	    elif (linenumber == 2):
	        # this has the parameter values
	        paramvalues=line.split()
	        for paramname,paramvalue in zip(paramnames,paramvalues):
	            if ("." in paramvalue):
	                params[paramname]=float(paramvalue)
	            else:
	                params[paramname]=int(paramvalue)                    
	    elif (linenumber == 5):
	        columnnames=line.split()
	        for columnname in columnnames:
	            columns[columnname]=[]
	    else:
	        data=line.split()
	        for columnnumber in xrange(len(columnnames)):
	            columns[columnnames[columnnumber]].append(data[columnnumber])
	
	fitsp=pyfits.PrimaryHDU()
	for param in params.keys():
	    fitsp.header.update('hierarch ' + param,params[param])
        fitsp.header.update('LOGFILE',os.path.abspath(infilename))
        now=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        fitsp.header.update('CONVDATE',now)
	Cols=[]
	for i in xrange(len(columnnames)):
	    if not any(['.' in x for x in columns[columnnames[i]]]):
	        types.append('I')
	        data=numpy.array([int(x) for x in columns[columnnames[i]]])
	    else:
	        types.append('D')
	        data=numpy.array([float(x) for x in columns[columnnames[i]]])
	    Cols.append(pyfits.Column(name=columnnames[i],format=types[i],array=data))
	fitsc=pyfits.new_table(Cols)
	hdus=pyfits.HDUList([fitsp,fitsc])        
	hdus.verify('fix')
	if (os.path.exists(outfilename)):
	    os.remove(outfilename)
	hdus.writeto(outfilename)
	print "Converted %s to %s" % (infilename, outfilename)
        
######################################################################

def usage():
    (xdir,xname)=os.path.split(sys.argv[0])
    print "Usage:"
    print "\t%s\t<filename1.log> [<filename2.log>...]" % xname
    print "\tConverts each of the MESA log files given as input to FITS tables"
    
######################################################################

if __name__=="__main__":
    main()
