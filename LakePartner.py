import math

class LakePartnerStation:
    def __init__(self, Lake, Township, STN, SiteID, SiteDescription, Latitude, Longitude):
        self.Lake = Lake
        self.Township = Township
        self.STN = STN
        self.SiteID = SiteID
        self.SiteDescription = SiteDescription
        self.Latitude = Latitude
        self.Longitude = Longitude    
        self.secchiDepthDict = {}
        self.tpDict = []    
    def convertLatLngToUTM(self, lat, lng):
        if (lat < 0.0001):
            return "0\t0\t0"
        pi = 3.14159265358979; #PI
        a = 6378137; #equatorial radius for WGS 84
        k0 = 0.9996; #scale factor
        e = 0.081819191; #eccentricity
        e_2 = 0.006694380015894481; #e'2
        A0 = 6367449.146;
        B0 = 16038.42955;
        C0 = 16.83261333;
        D0 = 0.021984404;
        E0 = 0.000312705;

        zone = 31 + math.floor(lng / 6);
        lat_r = lat * pi / 180.0;
        t1 = math.sin(lat_r); # SIN(LAT)
        t2 = e * t1 * e * t1;
        t3 = math.cos(lat_r); # COS(LAT)
        t4 = math.tan(lat_r); # TAN(LAT)
        nu = a / (math.sqrt(1 - t2));
        S = A0 * lat_r - B0 * math.sin(2 * lat_r) + C0 * math.sin(4 * lat_r) - D0 * math.sin(6 * lat_r) + E0 * math.sin(8 * lat_r);
        k1 = S * k0;
        k2 = nu * t1 * t3 * k0 / 2.0;
        k3 = ((nu * t1 * t2 * t2 * t2) / 24) * (5 - t4 * t4 + 9 * e_2 * t3 * t3 + 4 * e_2 * e_2 * t3 * t3 * t3 * t3) * k0;
        k4 = nu * t3 * k0;
        k5 = t3 * t3 * t3 * (nu / 6) * (1 - t4 * t4 + e_2 * t3 * t3) * k0;

        #var lng_r = lng*pi/180.0;
        lng_zone_cm = 6 * zone - 183;
        d1 = (lng - lng_zone_cm) * pi / 180.0;
        d2 = d1 * d1;
        d3 = d2 * d1;
        d4 = d3 * d1;

        x = 500000 + (k4 * d1 + k5 * d3);
        rawy = (k1 + k2 * d2 + k3 * d4);
        y = rawy;
        if (y < 0): 
            y = y + 10000000;

        return str(int(zone)) + "\t" + str(x)  + "\t" + str(y);
    def strWithUTM(self):
        id = self.STN * 10000 + self.SiteID        
        return str(id) + "\t" + self.Lake + "\t" + self.Township + "\t" + str(self.STN) + "\t" + str(self.SiteID) + "\t" + self.SiteDescription + "\t" + str(self.Latitude) + "\t" +  str(self.Longitude)  + "\t" +  str(len(self.secchiDepthDict))  + "\t" +  str(len(self.tpDict))   + "\t" +  self.convertLatLngToUTM(self.Latitude, self.Longitude)
    def __str__(self):
        id = self.STN * 10000 + self.SiteID
        if len(self.secchiDepthDict) > 0:
            self.getSecchiDepthString()
        if len(self.tpDict) > 0:
            self.getTPString()
        return str(id) + "\t" + self.Lake + "\t" + self.Township + "\t" + str(self.STN) + "\t" + str(self.SiteID) + "\t" + self.SiteDescription + "\t" + str(self.Latitude) + "\t" +  str(self.Longitude)  + "\t" +  str(len(self.secchiDepthDict))  + "\t" +  str(len(self.tpDict))   + "\t" + 'http://www.downloads.ene.gov.on.ca/files/mapping/LakePartner/TP/TP_EN_' + str(id) + '.html'    + "\t" +  'http://www.downloads.ene.gov.on.ca/files/mapping/LakePartner/TP/TP_FR_' + str(id) + '.html'    + "\t" +  'http://www.downloads.ene.gov.on.ca/files/mapping/LakePartner/SECCHI/SECCHI_EN_' + str(id) + '.html'    + "\t" +  'http://www.downloads.ene.gov.on.ca/files/mapping/LakePartner/SECCHI/SECCHI_FR_' + str(id) + '.html' 
        #return self.getTPString()
    def getSecchiDepthTable(self):
        id = self.STN * 10000 + self.SiteID
        result = ""
        for key, value in self.secchiDepthDict.items():
            result = result + str(self.STN) + "\t" + str(self.SiteID) + "\t" + key + "\t" + value + "\t" + str(id) + "\n"
        return result
        
    def getSecchiDepthString(self):
        id = self.STN * 10000 + self.SiteID
        result = ""
        for key in sorted(self.secchiDepthDict.iterkeys()):
            value = self.secchiDepthDict[key]
            result = result + "{year:" + key + ", value: " + value + "},"
        #for key, value in self.secchiDepthDict.items():
        #    result = result + "{year:" + key + ", value: " + value + "},"
        result = "var dataArray = [" + result[:-1] + "];"        
        for lang in ["EN", "FR"]:
            text_file = open("template_" + lang + "_SECCHI.htm", "r")
            template = text_file.read()
            text_file.close()
            #template = template.replace("${ID}", str(id))
            template = template.replace('<script type="text/javascript" src="secchi_${ID}.js"></script>', '<script type="text/javascript">\n\t\t' + result + '\n\t</script>')
            template = template.replace("${LAKENAME}", self.Lake)
            template = template.replace("${STN}", str(self.STN))
            template = template.replace("${SITEID}", str(self.SiteID))
            template = template.replace("${SITEDESC}", self.SiteDescription)
            handle1 = open("SECCHI/SECCHI_" + lang + "_" + str(id) + ".html",'w+')
            handle1.write(template)
            handle1.close();        
        
    def addSecchiDepth (self, Year, SecchiDepth):
        if self.secchiDepthDict.has_key(Year):
            raise ValueError('The year %s has duplicated secchi depth %s and  %s in station %s.' % (Year, SecchiDepth, self.secchiDepthDict[Year], str(self.STN) + " - " + str(self.SiteID)))
        self.secchiDepthDict[Year] = SecchiDepth
    def convertDate(self, inputDate):
        #27-Jun-11
        items = inputDate.split("-")
        if (int(items[2]) > 50):
            print "Error\n"
        year = "20" + items[2]
        day = items[0]
        monthList = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"};
        month = monthList[items[1]]
        return year + "-" + month  + "-" + day
    def getTPString(self):
        id = self.STN * 10000 + self.SiteID
        result = ""
        for value in self.tpDict:
            items = value.split("\t")
            if(len(items[2])  > 0):
                result = result + "{date:'" + self.convertDate(items[0]) + "', tp1: " + items[1]  + ", tp2: " + items[2] + "},"
            else:
                result = result + "{date:'" + self.convertDate(items[0]) + "', tp1: " + items[1]  + "},"
        result = "var dataArray = [" + result[:-1] + "];"        
        for lang in ["EN", "FR"]:
            text_file = open("template_" + lang + "_TP.htm", "r")
            template = text_file.read()
            text_file.close()
            #template = template.replace("${ID}", str(id))
            template = template.replace('<script type="text/javascript" src="tp_${ID}.js"></script>', '<script type="text/javascript">\n\t\t' + result + '\n\t</script>')
            template = template.replace("${LAKENAME}", self.Lake)
            template = template.replace("${STN}", str(self.STN))
            template = template.replace("${SITEID}", str(self.SiteID))
            template = template.replace("${SITEDESC}", self.SiteDescription)
            handle1 = open("TP/TP_" + lang + "_" + str(id) + ".html",'w+')
            handle1.write(template)
            handle1.close();
    def addTP (self, date, tpValues):
        #if self.tpDict.has_key(date):
            #raise ValueError('The year %s has duplicated secchi depth %s and  %s in station %s.' % (date, tpValues, self.tpDict[date], str(self.STN) + " - " + str(self.SiteID)))
        #    print str(self.STN) + " - " + str(self.SiteID)  + " - " +  date
        #self.tpDict[date] = tpValues
        self.tpDict.append(date + "\t" + tpValues)
    def getTPTable(self):
        id = self.STN * 10000 + self.SiteID
        result = ""
        for value in self.tpDict:
            result = result + str(self.STN) + "\t" + str(self.SiteID) + "\t" + value + "\t" + str(id) + "\n"
        return result        
class LakePartner:
    def __init__(self, secchiDepthFile, tpFile):
        self.LakePartnerStations = {}
        import fileinput
        i = 0
        for line in fileinput.input(secchiDepthFile):
            i = i + 1
            if i < 3:
                continue
            items = line.strip().split("\t")
            STN = int(items[2])
            SiteID = int(items[3])
            id = STN * 10000 + SiteID
            if self.LakePartnerStations.has_key(id):
                self.LakePartnerStations[id].addSecchiDepth(items[7], items[8])
            else:
                Lake = items[0]
                Township = items[1]
                SiteDescription = items[4]
                Latitude = self.parseDegree(items[5])
                Longitude = -self.parseDegree(items[6])
                if Longitude > -70 or id == 47140002:
                    Latitude = 0
                    Longitude = 0
                station = LakePartnerStation(Lake, Township, STN, SiteID, SiteDescription, Latitude, Longitude)
                #if id == 71680001:
                #    print station.strWithUTM()
                station.addSecchiDepth(items[7], items[8])
                self.LakePartnerStations[id] = station
        i = 0
        for line in fileinput.input(tpFile):                
            i = i + 1
            if i < 9:
                continue
            #print line
            items = line.strip().split("\t")
            STN = int(items[2])
            SiteID = int(items[3])
            id = STN * 10000 + SiteID
            if self.LakePartnerStations.has_key(id):
                self.LakePartnerStations[id].addTP(items[7], items[8] + "\t" + items[9])
            else:
                Lake = items[0]
                Township = items[1]
                SiteDescription = items[4]
                Latitude = self.parseDegree(items[5])
                Longitude = -self.parseDegree(items[6])
                if Longitude > -70:
                    Latitude = 0
                    Longitude = 0
                station = LakePartnerStation(Lake, Township, STN, SiteID, SiteDescription, Latitude, Longitude)
                station.addTP(items[7], items[8] + "\t" + items[9])
                self.LakePartnerStations[id] = station        
            #print items
    def parseDegree(self, ddmmss):
        if len(ddmmss.strip()) == 0:
            return 0
        d = int(ddmmss[:2])
        m = int(ddmmss[2:4])
        s = int(ddmmss[4:])
        return d + m/60.0 + s/3600.0
    def strWithUTM(self):
        result = "ID\tLAKENAME\tTOWNSHIP\tSTN\tSITEID\tSITEDESC\tLATITUDE\tLONGITUDE\tSE_COUNT\tPH_COUNT\tZONE\tEASTING\tNORTHING\n"
        for key, value in self.LakePartnerStations.items():
            result = result + value.strWithUTM() + "\n"
        return result
    
    def __str__(self):
        result = "ID\tLAKENAME\tTOWNSHIP\tSTN\tSITEID\tSITEDESC\tLATITUDE\tLONGITUDE\tSE_COUNT\tPH_COUNT\tTP_URL_EN\tTP_URL_FR\tSE_URL_EN\tSE_URL_FR\n"
        for key, value in self.LakePartnerStations.items():
            result = result + str(value) + "\n"
        return result
    def getTable(self):
        handle1 = open("secchiDepth1.txt",'w+')
        result = "STN\tSITEID\tYEAR_\tSECCI\tID\n"
        for key, value in self.LakePartnerStations.items():
            result = result + value.getSecchiDepthTable()
        handle1.write(result)
        handle1.close();
        handle1 = open("TP1.txt",'w+')
        result = "STN\tSITEID\tDATE_\tTP1\tTP2\tID\n"
        for key, value in self.LakePartnerStations.items():
            result = result + value.getTPTable()
        handle1.write(result)
        handle1.close();
            
        return result
        
if __name__ == "__main__":
    stations = LakePartner('SecchiDepth.txt', 'TP.txt')
    handle1 = open("1.txt",'w+')
    handle1.write(str(stations))
    handle1.close();
    stations.getTable();
    #os.system("1.py")
    