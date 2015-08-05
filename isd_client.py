from ftplib import FTP
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import os.path
import gzip

def stations_between(low_lat,high_lat):
    cached = True
    if cached:
        f = open("data/isd-history.csv", "r")
        reader = csv.reader(f)
    else:
        ftp = FTP('ftp.ncdc.noaa.gov')
        ftp.login()

        data = []
        def handle_binary(more_data):
            data.append(more_data)

        resp = ftp.retrbinary("RETR pub/data/noaa/isd-history.csv", callback=handle_binary)
        data = "".join(data)
        ftp.quit()
        reader = csv.reader(data.split('\n'), delimiter=',')
        


    stations = []
    first = 0
    for row in reader:
        if first > 0:      
            if (len(row[6]) > 0) and (len(row[7]) > 0): #  and row[6] != '""':
                if (abs(float(row[6])) + abs(float(row[7]))) != 0:
                    if (low_lat <= float(row[6])) and (float(row[6]) <= high_lat):
                        # stations.append([row[2],row[6],row[7]])
                        stations.append(row)
        else:
            first += 1

    if cached:
        f.close()

    sorted_stations = sorted(stations, key=lambda self: self[7])

    for row in sorted_stations:
        print row
    
    return sorted_stations

# # stations = stations_between(-.1,.1)
def look_up_station(station):
    ftp = FTP('ftp.ncdc.noaa.gov')
    ftp.login()
    
    for year in range(int(station[9][0:4]),int(station[10][0:4])):
        print "trying {0}".format(year)
        ftp.cwd("pub/data/noaa/{0}".format(year))
        file_list = ftp.nlst()
        filename = "{0}-{1}-{2}.gz".format(station[0], station[1], year)
        if filename in file_list:
            file = open("data/{0}".format(filename), "wb")
            ftp.retrbinary("RETR {0}".format(filename), file.write)
            file.close()
        ftp.cwd("../../../..")
    ftp.quit()

# stations = stations_between(-1,1)
# look_up_station(stations[0])

def get_data_from_row(row):
    dt = datetime(int(row[15:19]),int(row[19:21]),int(row[21:23]), int(row[23:25]), int(row[25:27]))
    return dt, (float(row[87:92]) / 10)    

def get_data_from_file(filename):
    dts = []
    Ts = []
    
    f = gzip.open("data/" + filename + ".gz","rb")
    file_content = f.read()
    f.close()
    rows = file_content.split("\n")
    
    for row in rows:
        if len(row) > 0:
            dt, T = get_data_from_row(row)
                
            if T < 100:
                dts.append(dt)
                Ts.append(T)
    
    return dts, Ts

# row = "0075619310999991973022321004+00383+006717FM-12+0009FPST V0201801N00461090001CN0120001N9+02601+02401101131ADDAY111999GA1011+005109089GA2041+090009009GF105991031081004501001021MW1051"

def plot_data_from_station(station,start_year,end_year,T_min=-30,T_max=40):
    rows = (end_year-start_year)+1
    # plt.figure("{0}-{1}".format(station[0],station[1]),(16,9))
    plt.figure(1,(16,9))
    for i in range(rows):
        plt.subplot(rows * 1e2 + 10 + i + 1)
        dts, Ts = get_data_from_file("{0}-{1}-{2}".format(station[0], station[1], start_year + i))
        plt.plot_date(dts, Ts, linestyle="-", marker=None)
        plt.plot_date([datetime(start_year+i,1,1),datetime(start_year+i,12,31)],[100,100],"ko")
        plt.ylim(T_min,T_max)
        plt.ylabel("T (C)")
    plt.subplots_adjust(left=.05,right=.95,top=.95,hspace=.25)
    plt.suptitle("{0} ({1}, {2})".format(station[2],station[6],station[7]))
    # plt.show()

plt.ion()
stations = stations_between(-1,1)
plot_data_from_station(stations[1],2009,2014)

stations = stations_between(74,76)
plot_data_from_station(stations[0],2009,2014)
# plot_data_from_station(stations[1],2009,2014)
