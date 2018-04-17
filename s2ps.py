#!/usr/bin/python

import sys, os
import math
import datetime
import tempfile
import errno
from decimal import *

TWOPLACES = Decimal(10) ** -2

def div(x, y, fp=TWOPLACES):
    return (x / y).quantize(fp)

def mul(x, y, fp=TWOPLACES):
    return (x * y).quantize(fp)

def loadTemplate(filename):
    "Takes ASPtempl.txt as argument, loads the template into an array and returns it"
    ASPbuf = []
    with open(filename, 'rU') as f:
            for line in f:
                ASPbuf.append(line)
            ASPbuf[0] = ASPbuf[0].rstrip()
            ASPbuf[0] = ASPbuf[0] + "\r\n"
            return ASPbuf

class HeaderLn:
	def __init__(self, headerStr):
		self.HeaderBuf = str(headerStr)
		self.VoucherNum = self.HeaderBuf[0:6]
		self.VendCode = self.HeaderBuf[19:29]
		self.AS_CID = self.HeaderBuf[183:]
		(self.AddrSeq, self.CustID) = self.extractId(self.AS_CID)
                
        def extractId(self, AS_CID):
            VB1 = AS_CID.find('|')
            if(VB1 == -1):
                    AddrSeq = "   "
                    CustID = "                              "
                    return (AddrSeq, CustID)
            else:
                    VB2 = AS_CID.find('|', VB1+1)
                    AddrSeq = AS_CID[VB1+1:VB2]
                    VB3 = AS_CID.find('|', VB2+1)
                    if(VB3 == -1):
                            CustID = "                              "
                    else:
                            CustID = AS_CID[VB2+1:VB3]
                    return (AddrSeq, CustID)

class DetailLn:
    def __init__(self, detailStr):
        self.DetailBuf = str(detailStr)
        self.InvoiceNum = self.DetailBuf[56:72] 
        self.CostC = float(div(float_to_decimal(float(self.DetailBuf[72:86])), float_to_decimal(100.00)))
        self.ShippingC = float(div(float_to_decimal(float(self.DetailBuf[114:128])), float_to_decimal(100.00)))
        self.DiscountC = float(div(float_to_decimal(float(self.DetailBuf[128:142])), float_to_decimal(100.00)))
        self.FRSAcct = self.DetailBuf[20:40]
	self.ASPOrigin = self.Origin(self.InvoiceNum)
        self.NoteField = self.DetailBuf[183:207]
	(self.DBASPacct, self.DBMOcode, self.MOacct) = self.buildMOacct(self.FRSAcct)
        
    def Origin(self, InvoiceNum):
        ch = InvoiceNum[0]
        if(ch == '#'):
                return "CC7"
        elif(ch  == '@'):
                return "CC2"
        else:
                return str(sys.argv[3])
    
    def buildMOacct(self, FRSAcct):
        dashLoc = FRSAcct.find('-')
        DB_MOcode = FRSAcct[:dashLoc]
        DB_ASPacct = FRSAcct[dashLoc+1:]
        MOacct = DB_MOcode.strip() + "-" + DB_ASPacct.strip()
        return (DB_ASPacct, DB_MOcode, MOacct)

def validDate(date_str):
    try:
        datetime.datetime.strptime(date_str, '%m/%d/%Y')
    except ValueError:
        raise ValueError("Incorrect date format, should be MM/DD/YYYY")

def isWritable(path):
    try:
        testfile = tempfile.TemporaryFile(dir = path)
        testfile.close()
    except OSError as e:
        if e.errno == errno.EACCES: # 13
            return False
        e.filename = path
        raise
    return True

def validArgs():
    "This function checks that input arguments meet requirements."
    # Check number of arguments
    if len(sys.argv) != 5:
        print "Error: Incorrect input arguments\nUsage is: %s chargeact.out MM/DD/YYYY {CLB/LSO} destination_directory" % (str(sys.argv[0]))
        sys.exit(1)
    # Check input filename
    #if sys.argv[1].lower().strip() != "chargeact.out":
        #print "Warning: input filename is NOT chargeact.out"
    # Check date string format
    validDate(sys.argv[2])
    # Check organization str
    if (sys.argv[3].upper().strip() != "CLB") and (sys.argv[3].upper().strip() != "LSO"):
        print "Error: ORG must be one of {CLB/LSO}" 
        sys.exit(1)
    # Check destination dir
    if(os.path.exists(sys.argv[4]) is False):
        print "Error: directory does not exist: %s" % (sys.argv[4])
        sys.exit(1)
    else:
        if (os.path.isdir(sys.argv[4]) is False):
            print "Error: file exists but is not a directory: %s" % (sys.argv[4])
            sys.exit(1)
        else:
            if (isWritable(sys.argv[4]) is False):
                print "Error: Cannot write to directory: %s" % (sys.argv[4])
                sys.exit(1)

def insert_string(str1, str2, startpos):
        "Puts str1 into str2 at startpos" 
        newStr = str2[0:startpos] + str(str1) + str2[startpos+len(str1):]
        return newStr

def currency_to_str(currency):
    "Check number of digits in the numeric value. Convert numeric value to string and pad with appropriate number of zeros"
    # https://docs.python.org/release/2.6.7/library/decimal.html#decimal-faq 
    # See question #3 
    currency_dec = mul(float_to_decimal(currency), float_to_decimal(100.00)) 
    if currency >= 0:
        currency_str = "%017d" % float(currency_dec)
    else:
        currency_str = "%016d" % float(currency_dec)
    return currency_str.strip()

def uniq(input):
    "Turn a list into a set of unique values while maintaining the order of the original list"
    output = []
    for x in input:
        if x not in output:
            output.append(x)
    return output

def float_to_decimal(f):
    "Convert a floating point number to a Decimal with no loss of information. Necessary for Python 2.6"
    n, d = f.as_integer_ratio()
    numerator, denominator = Decimal(n), Decimal(d)
    ctx = Context(prec=60)
    result = ctx.divide(numerator, denominator)
    while ctx.flags[Inexact]:
        ctx.flags[Inexact] = False
        ctx.prec *= 2
        result = ctx.divide(numerator, denominator)
    return result

def read_inputFile(inFile, outFile): 
    "Main function, extracts info from input file and writes to output file"
    # hshAcct{MOcode} => index associated w/ MOCode in currency arrays
    hshAcct = {}    
    TAccTotalsC = []
    done = False
    detailDone = False 
    # Store the last detail object when we reach the EOF 
    lastDetail = ""
    with open(inFile, 'rU') as f: 
        with open(outFile, 'w') as outfile:
            # Write 999 line 
            outfile.write(ASPtempl[0])
            mainDate = sys.argv[2]
            DateObj = datetime.date(int(mainDate[6:10]), int(mainDate[0:2]), int(mainDate[3:5]));
            mainDate = DateObj.strftime("%Y/%m/%d")
            # Read first line
            HdrObj = HeaderLn(f.readline())
            # Beginning of main loop - assumes new line in HdrBuf
            # Terminates when entire file has been processed
            while True:
                NoteFields = []
                # Empty dictionary
                hshAcct.clear()
                ArrEndElement = 0
                allCount = 0
                # Zero currency arrays
                TCostC = [] 
                TShippingC = []
                TDiscountC = []
                ASP_GTotalC = 0
                # Zero totals
                allMOCode = []
                allCostC = []
                allShippingC = []
                allDiscountC = []
                # Get fresh template buffers to insert strings into 
                ASP_000buf = ASPtempl[1]
                ASP_001buf = ASPtempl[2]

                # Read next line after header (detail)
                DetailObj = DetailLn(f.readline())
                
                # Insert fields found up to this point into the template
                ASP_000buf = insert_string(mainDate, ASP_000buf, 46)
                ASP_000buf = insert_string(HdrObj.VendCode, ASP_000buf, 61)
                ASP_000buf = insert_string(HdrObj.AddrSeq, ASP_000buf, 81)
                ASP_000buf = insert_string(mainDate, ASP_000buf, 106)
                # Should we check ASP_Origin here? or just the input arg?
                if sys.argv[3] == "LSO":
                    # LSO type would like the opportunity to put a description here 
                    ASP_000buf = insert_string("INSERTDESC", ASP_000buf, 588)
                    # LSO type we put NoteField in this place
                    ASP_001buf = insert_string(DetailObj.NoteField, ASP_001buf, 49)
                elif sys.argv[3] == "CLB":
                    ASP_000buf = insert_string(HdrObj.VoucherNum, ASP_000buf, 588)
                    ASP_001buf = insert_string(HdrObj.CustID, ASP_001buf, 49)
                ASP_000buf = ASP_000buf.rstrip()
                ASP_000buf = ASP_000buf + "\r\n"
                    
                #if (DetailObj.DBASPacct is None) or (DetailObj.DBMOcode is None):
                #    errStr = "Account not found: %s" % ( DetailObj.FRSAcct) 
                #    outfile.write(errStr)

                # Insert fields into template
                ASP_000buf = insert_string(DetailObj.InvoiceNum, ASP_000buf, 16)
                ASP_000buf = insert_string(DetailObj.ASPOrigin, ASP_000buf, 90)
            
                # Process dictionary 
                #(look for MOacct in dictionary -> get index of MOacct in currency arrays)
                if hshAcct.has_key(DetailObj.MOacct):
                    ArrIndex = hshAcct.get(DetailObj.MOacct, None)
                    if ArrIndex is None: 
                        # Shouldn't ever get here
                        print "Error in hash lookup" 
                        sys.exit(1)
                    else:
                        # Add current amounts to total
                        TCostC[ArrIndex] += DetailObj.CostC
                        TShippingC[ArrIndex] += DetailObj.ShippingC
                        TDiscountC[ArrIndex] += DetailObj.DiscountC
                else:
                    # Append values to array(s) 
                    TCostC.append(DetailObj.CostC)
                    TShippingC.append(DetailObj.ShippingC)
                    TDiscountC.append(DetailObj.DiscountC)
                    # Add key + index to dictionary 
                    hshAcct[str(DetailObj.MOacct)] = len(TCostC)-1

                # Change to append?
                allMOCode.append(DetailObj.MOacct)
                allCostC.append(DetailObj.CostC)
                allShippingC.append(DetailObj.ShippingC)
                allDiscountC.append(DetailObj.DiscountC)
                allCount += 1

                # The third line determines whether there are multiple detail lines for this header
                GenBuf = f.readline()
                # Check for EOF 
                if (GenBuf.find("ALLDONE") != -1):
                    done = True 
                    detailDone = True
                else:
                    detailDone = False 
                # Check if third line is header or detail 
                if (GenBuf.find("VENNAME") == -1 and done == False):
                    # Multiple detail lines
                    # Loop through remaining lines & add amounts to arrays 
                    NoteFields.append(DetailObj.NoteField);
                    DetailObj = DetailLn(GenBuf)
                    # The following loop terminates on detailDone == True  
                    # Emulates a do-while
                    while True:
                        NoteFields.append(DetailObj.NoteField);
                        # (look for MOacct in dictionary -> get index of MOacct in currency arrays)
                        if hshAcct.has_key(DetailObj.MOacct):
                            ArrIndex = hshAcct.get(DetailObj.MOacct, None)
                            if ArrIndex is None: 
                                # Shouldn't ever get here
                                print "Error in hash lookup" 
                                sys.exit(1)
                            else:
                                # Add current amounts to total
                                TCostC[ArrIndex] += DetailObj.CostC
                                TShippingC[ArrIndex] += DetailObj.ShippingC
                                TDiscountC[ArrIndex] += DetailObj.DiscountC
                        else:
                            # Append values to array(s) 
                            TCostC.append(DetailObj.CostC)
                            TShippingC.append(DetailObj.ShippingC)
                            TDiscountC.append(DetailObj.DiscountC)
                            # Add key + index to dictionary 
                            hshAcct[str(DetailObj.MOacct)] = len(TCostC)-1

                        allMOCode.append(DetailObj.MOacct)
                        allCostC.append(DetailObj.CostC)
                        allShippingC.append(DetailObj.ShippingC)
                        allDiscountC.append(DetailObj.DiscountC)
                        allCount += 1
                        
                        # Check if next line is EOF, Detail, or Header 
                        GenBuf = f.readline()
                        # Check for EOF 
                        if (GenBuf.find("ALLDONE") != -1): 
                            #print "ALLDONE Found inner"
                            lastDetail = DetailObj
                            done = True 
                            detailDone = True
                        else:
                            detailDone = False 
                        # Check if detail/header 
                        if (GenBuf.find("VENNAME") != -1):
                            detailDone = True
                            HdrObj = HeaderLn(GenBuf)
                        else:
                            # new detail line 
                            DetailObj = DetailLn(GenBuf)
                        # Break while loop here 
                        if detailDone is True: 
                            break
                    #### end while(!detailDone) ####
                    
                    # Add individual totals
                    numAccts = len(TCostC)
                    for i in range(numAccts):
                        Ctot = TCostC[i] + TShippingC[i] + TDiscountC[i]
                        TAccTotalsC.append(Ctot)
                        ASP_GTotalC += Ctot 
                    # Insert Grand Total into upper lines
                   
                    print ASP_GTotalC
                    # Remove decimal component, add leading zeros
                    ASP_GTotalS = currency_to_str(ASP_GTotalC)
                    print ASP_GTotalS
                    
                    # Plug into template
                    ASP_000buf = insert_string(ASP_GTotalS, ASP_000buf, 135)
                    ASP_001buf = insert_string(ASP_GTotalS, ASP_001buf, 79)
                    # Write upper lines
                    outfile.write(ASP_000buf)
                    
                    AcctLineCntrI = 1
                    allCount = 0
                    for i in range(0, len(allMOCode)): 
                        allTotal = allCostC[i] + allShippingC[i] + allDiscountC[i]
                        ASP_002buf = ASPtempl[3] 
                        AcctLineCntrS = "%05d" % AcctLineCntrI
                        ASP_002buf = insert_string(AcctLineCntrS, ASP_002buf, 16)
                        ASP_002buf = insert_string("00001", ASP_002buf, 21)
                        MCAcctOut = allMOCode[i]
                        dashLoc = MCAcctOut.find("-")
                        MCOut = MCAcctOut[0:dashLoc]
                        AcctOut = MCAcctOut[dashLoc+1:]
                        
                        ASP_002buf = insert_string(AcctOut, ASP_002buf, 31)
                        ASP_002buf = insert_string(MCOut, ASP_002buf, 339)

                        ASP_002TotalS = currency_to_str(allTotal)
                        
                        if sys.argv[3] == "LSO":
                            AcctLineCntrI += 1
                            ASP_002buf = insert_string(ASP_002TotalS, ASP_002buf, 115)
                            ASP_001buf = insert_string(ASP_002TotalS, ASP_001buf, 79)
                            ASP_001buf = insert_string(AcctLineCntrS, ASP_001buf, 16)
                            
                            ASP_001buf = insert_string(NoteFields[i], ASP_001buf, 49);

                            ASP_001buf = ASP_001buf.rstrip()
                            ASP_001buf = ASP_001buf + "\r\n"
                            outfile.write(ASP_001buf)
                            
                            ASP_002buf = ASP_002buf.rstrip()
                            ASP_002buf = ASP_002buf + "\r\n"
                            outfile.write(ASP_002buf)
                    
                    if sys.argv[3] == "CLB":
                        # get set of unique MOCodes associated with each header line
                        MOCode_set = uniq(allMOCode)
                        ASP_001buf = insert_string(ASP_GTotalS, ASP_001buf, 79)
                        ASP_001buf = ASP_001buf.rstrip()
                        ASP_001buf = ASP_001buf + "\r\n"
                        outfile.write(ASP_001buf)
                        # Columns 22-27 for the 002 lines
                        DistribLineCntrI = 0
                        for i in range(0, len(TCostC)):
                            
                            MCAcctOut = MOCode_set[i]
                            dashLoc = MCAcctOut.find("-")
                            MCOut = MCAcctOut[0:dashLoc]
                            AcctOut = MCAcctOut[dashLoc+1:]
                            
                            DistribLineCntrI += 1
                            DistribLineCntrS = "%05d" % DistribLineCntrI
                            Ctot_tmp = TCostC[i] + TShippingC[i] + TDiscountC[i]
                            Ctot_str = currency_to_str(Ctot_tmp)
                            ASP_002buf = ASPtempl[3] 
                            ASP_002buf = insert_string(AcctLineCntrS, ASP_002buf, 16)
                            ASP_002buf = insert_string(DistribLineCntrS, ASP_002buf, 21)
                            ASP_002buf = insert_string(AcctOut, ASP_002buf, 31)
                            ASP_002buf = insert_string(MCOut, ASP_002buf, 339)
                            ASP_002buf = insert_string(Ctot_str, ASP_002buf, 115)
                            ASP_002buf = ASP_002buf.rstrip()
                            ASP_002buf = ASP_002buf + "\r\n" 
                            outfile.write(ASP_002buf)
                        
                        if done is True:
                            ASP_002buf = insert_string(lastDetail.DBASPacct, ASP_002buf, 31)
                            ASP_002buf = insert_string(lastDetail.DBMOcode, ASP_002buf, 339)
                        else:
                            ASP_002buf = insert_string(DetailObj.DBASPacct, ASP_002buf, 31)
                            ASP_002buf = insert_string(DetailObj.DBMOcode, ASP_002buf, 339) 
                    

                    allCount += 1
                    allTotal = 0
                    next
                    # End while (loop to process account detail lines)
                
                # Only one detail line:
                # VENNAME not found but done == True 
                else:
                    HdrObj = HeaderLn(GenBuf)
                    # Compute grand total
                    ASP_GTotalC = DetailObj.CostC + DetailObj.ShippingC + DetailObj.DiscountC
                    ASP_GTotalS = currency_to_str(ASP_GTotalC)
                    
                    # Plug into template
                    ASP_000buf = insert_string(ASP_GTotalS, ASP_000buf, 135)
                    ASP_000buf = ASP_000buf.rstrip()
                    ASP_000buf = ASP_000buf + "\r\n"
                    outfile.write(ASP_000buf)
                    
                    ASP_001buf = insert_string(ASP_GTotalS, ASP_001buf, 79)
                    ASP_001buf = ASP_001buf.rstrip()
                    ASP_001buf = ASP_001buf + "\r\n"    
                    outfile.write(ASP_001buf)
                    
                    # Get fresh template
                    ASP_002buf = ASPtempl[3]
                    ASP_002buf = insert_string("00001", ASP_002buf, 21)
                    ASP_002buf = insert_string(ASP_GTotalS, ASP_002buf, 115)
                    ASP_002buf = insert_string(DetailObj.DBASPacct, ASP_002buf, 31)
                    ASP_002buf = insert_string(DetailObj.DBMOcode, ASP_002buf, 339) 
                    ASP_002buf = ASP_002buf.rstrip()
                    ASP_002buf = ASP_002buf + "\r\n"
                    outfile.write(ASP_002buf)

                if done is True:
                    break


# Validate input args
validArgs()

# Get path to script 
pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(pathname)
ASPtempl_path = fullpath + "/ASPtempl.txt"

# Fill up & ASPTempl 
ASPtempl = loadTemplate(ASPtempl_path)

# Construct output filename
outFile = "MO_COLUM_ORG_UMAP0007.TXT"
outFile = insert_string(sys.argv[3], outFile, 9)
outFile_path = sys.argv[4] + outFile

# Process input file
read_inputFile(str(sys.argv[1]), outFile_path)
#print "Output filename: %s\n" % (outFile_path)

sys.exit()


