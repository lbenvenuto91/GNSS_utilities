import sys, os
#from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import math  
import numpy as np



def SVID(sat):
    '''
    Function to return SVID according to this rules:

    1 - 37 : PRN number of a GPS satellite
    38 - 61 : slot number of a GLONASS satellite with an offset of 37
    71 - 106 : PRN number of a GALILEO satellite with an offset of 70
    120 - 138 : PRN number of an SBAS satellite
    '''

    constellation=sat[0]
    sat_number=int(sat[1:])
    if constellation=='G':
        if sat_number>=1 and sat_number <= 37:
            return sat_number
        else:
            print('invalid satellite')
            return None
    elif constellation=='R':
        if sat_number>=1 and sat_number <= 24:
            return sat_number+37
        else:
            print('invalid satellite')
            return None
        
    elif constellation=='S':
        if sat_number>=120 and sat_number <= 138:
            return sat_number
        else:
            print('invalid satellite')
            return None

        
    elif constellation=='E':
        if sat_number>=1 and sat_number <= 36:
            return sat_number+70
        else:
            print('invalid satellite')
            return None

        
        return sat_number


def weeksecondstoutc(gpsweek,gpsseconds,leapseconds):
    import datetime, calendar
    datetimeformat = "%Y-%m-%d %H:%M:%S"
    epoch = datetime.datetime.strptime("1980-01-06 00:00:00",datetimeformat)
    return epoch + datetime.timedelta(days=(gpsweek*7),seconds=(gpsseconds+leapseconds))


def readismr(ismrfile,sat,index):


    with open (ismrfile,'r') as ismr:
        totlines=ismr.readlines()

    
    parsed_data=[]
    for i in totlines:
        if int(i.split(',')[2])==sat:
            #print(int(i.split(',')[0]),int(i.split(',')[1]),int(i.split(',')[2]))
            parsed_data.append((weeksecondstoutc(int(i.split(',')[0]),int(i.split(',')[1]),0),float(i.split(',')[index-1])))
        else:
            continue
    return parsed_data

def thermalNoiseCorr(s4raw,ismrfile,sat,index):
    '''
    page 19 of ismr manual
    '''
    diz_s4={}
    for i in s4raw:
        diz_s4[i[0]]=i[1]**2

    correction=readismr(ismrfile,SVID(sat),index+1)
    therm_corr=[]
    for j in correction:
        if j[0] in diz_s4:
            #print(diz_s4[j[0]],j[1]**2, diz_s4[j[0]]-j[1]**2,math.sqrt(diz_s4[j[0]]-j[1]**2))
            diff=diz_s4[j[0]]-j[1]**2
            if diff>=0:
                therm_corr.append((j[0],math.sqrt(diff)))
            elif diff <0:
                therm_corr.append((j[0],0))
       
        else:
            therm_corr.append((j[0],np.nan))
    return therm_corr       
    
            


def main():
    '''
    Quantities in ismr file
    1: WN, GPS Week Number
    2: TOW, GPS Time of Week (seconds)
    3: SVID
    4: Value of the RxState field of the ReceiverStatus SBF block
    5: Azimuth (degrees)
    6: Elevation (degrees)
    7: Average L1 C/N0 over the last minute (dB-Hz)
    8: Total S4 on L1 (dimensionless)
    9: Correction to total S4 on L1 (thermal noise component only) (dimensionless)
    10: Phi01 on L1,  1-second phase sigma (radians)
    11: Phi03 on L1,  3-second phase sigma (radians)
    12: Phi10 on L1, 10-second phase sigma (radians)
    13: Phi30 on L1, 30-second phase sigma (radians)
    14: Phi60 on L1, 60-second phase sigma (radians)
    15: AvgCCD on L1, average of code/carrier divergence (meters)
    16: SigmaCCD on L1, standard deviation of code/carrier divergence (meters)
    17: TEC at TOW - 45 seconds (TECU)
    18: dTEC from TOW - 60s to TOW - 45s (TECU)
    19: TEC at TOW - 30 seconds (TECU)
    20: dTEC from TOW - 45s to TOW - 30s (TECU)
    21: TEC at TOW - 15 seconds (TECU)
    22: dTEC from TOW - 30s to TOW - 15s (TECU)
    23: TEC at TOW (TECU)
    24: dTEC from TOW - 15s to TOW (TECU)
    25: L1 lock time (seconds)
    26: Reserved, currently set to 0
    27: L2 lock time (seconds)
    28: Averaged C/N0 of second frequency used for the TEC computation (dB-Hz)
    29: SI Index on L1 (dimensionless)
    30: SI Index on L1 (dB)
    31: p on L1, spectral slope of detrended phase in the 0.1 to 25Hz range (dimensionless)
    32: Average C/N0 on L2 (GPS/GLO) or E5a (GAL) over the last minute (dB-Hz)
    33: Total S4 on L2 (GPS/GLO) or E5a (GAL) (dimensionless)
    34: Correction to total S4 on L2 (GPS/GLO) or E5a (GAL) (thermal noise component only) (dimensionless)
    35: Phi01 on L2 (GPS/GLO) or E5a (GAL),  1-second phase sigma (radians)
    36: Phi03 on L2 (GPS/GLO) or E5a (GAL),  3-second phase sigma (radians)
    37: Phi10 on L2 (GPS/GLO) or E5a (GAL), 10-second phase sigma (radians)
    38: Phi30 on L2 (GPS/GLO) or E5a (GAL), 30-second phase sigma (radians)
    39: Phi60 on L2 (GPS/GLO) or E5a (GAL), 60-second phase sigma (radians)
    40: AvgCCD on L2 (GPS/GLO) or E5a (GAL), average of code/carrier divergence (meters)
    41: SigmaCCD on L2 (GPS/GLO) or E5a (GAL), standard deviation of code/carrier divergence (meters)
    42: Lock time of L2 (GPS/GLO) or E5a (GAL) (seconds)
    43: SI Index on L2 (GPS/GLO) or E5a (GAL) (dimensionless)
    44: SI Index on L2 (GPS/GLO) or E5a (GAL), numerator only (dB)
    45: p on L2 (GPS/GLO) or E5a (GAL), phase spectral slope in the 0.1 to 25Hz range (dimensionless)
        
    '''
    script_path=os.path.dirname(os.path.realpath(__file__))
    print(script_path)

    ismr_index={}
    with open ('{}/manuals/indici_ismr.txt'.format(script_path),'r') as ismr_idx:
        for line in ismr_idx.readlines():
            ismr_index[int(line.split(':')[0])]=line.split(':')[1]
    print(ismr_index[8])




    ismrfile='{}/files/ismr/PRU1305C.11_.ismr'.format(script_path)
    sat='G02'

    index=33

    values=readismr(ismrfile,SVID(sat),index)

    if index==8 or index==33:
        thermCorr=int(input('Apply Thermal Correction to S4?\nyes: 1\nno: 0\n>>> '))
        if thermCorr==1:
            values=thermalNoiseCorr(values,ismrfile,sat,index)
        elif thermCorr==0:
            pass
        else:
            print('not applying thermal correction to S4')
            pass


    asse_x= [values[i][0] for i in range(len(values))]
    asse_y= [values[i][1] for i in range(len(values))]

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    plt.plot(asse_x,asse_y)
    import matplotlib.dates as mdates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()
    plt.xlabel('time')
    plt.ylabel('{}'.format(ismr_index[index]))
    plt.title('sat {}'.format(sat))

    plt.show()

if __name__ == "__main__":
    main()