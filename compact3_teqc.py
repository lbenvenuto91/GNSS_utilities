import sys, os
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt


#with open (r'C:\Users\gterg\Documenti\test4\RINEX\ublox_neom8t\rinex_211\SC6000980.ele','r') as elefile:

def creaElemento(start_time,sec,millisec,valore):
    
    if 'S' in valore:
        
        valore=valore[:-1]
        element=(start_time+timedelta(seconds=int(sec),milliseconds=int(millisec)),float(valore),'S')
        element_cycle=(start_time+timedelta(seconds=int(sec),milliseconds=int(millisec)),float(valore),'S')
        #print(element)
        #dati.append(element)
    else:
        element=(start_time+timedelta(seconds=int(sec),milliseconds=int(millisec)),float(valore),'O')
        element_cycle=(start_time+timedelta(seconds=int(sec),milliseconds=int(millisec)),np.nan,'O')
        #print(element)
        #dati.append(element)
    return element,element_cycle


def readCompact3(filename,satellite,csv_out):
    '''function to read compact3 file generated by tecq
        - .ele for elevation
        - .azi for azimuth
        - .m12 for multipath
        ....

        The funcion returns a list of tuples [(utctime_1,value_2,cyclesplip),(utctime_2,value_2)....(utctime_n,value_n)
        
        If csv_out=True the function returns also a csv file with epoch,utc_time,value 
        '''
    with open (filename,'r') as elefile:
        totlines=elefile.readlines()
    #print(totlines)
    data=totlines[1].split()

    year=data[1]
    month=data[2]
    day=data[3]
    hour=data[4]
    minute=data[5]
    second=data[6]
    secondi=second.split('.')[0]
    millisec=second.split('.')[1]

    #print(year,month,day,hour,minute,type(second))
    start_time=datetime(int(year),int(month),int(day),int(hour),int(minute),int(secondi),int(millisec))

    #print(start_time)
    dati=[]
    dati_cycle=[]
    dati_noheader=totlines[2:]

    sat_presente=False

    for i in range(0,len(dati_noheader),2):
        if satellite in dati_noheader[i].split():
            sat_presente=True
            #trovo indice del satellite nella lista
            sat_index=dati_noheader[i].split()[2:].index(satellite)       
            #print(sat_index) #indice del satellite desiderato: nella lista tolgo i primi due elementi 
            
            #aggiorno la lista dei tempi con il relativo istante temporale.
            sec=dati_noheader[i].split()[0].split('.')[0]
            millisec=dati_noheader[i].split()[0].split('.')[1]
            valore=dati_noheader[i+1].split()[sat_index]
            element,element_cycle=creaElemento(start_time,sec,millisec,valore)           
            #aggiorno la lista con i valori di elevazione da plottare
            dati.append(element)
            dati_cycle.append(element_cycle)
        else:
            if sat_presente and dati_noheader[i].split()[1]=='-1':
                #satellite presente

                #aggiorno la lista dei tempi con il relativo istante temporale.
                sec=dati_noheader[i].split()[0].split('.')[0]
                millisec=dati_noheader[i].split()[0].split('.')[1]
                valore=dati_noheader[i+1].split()[sat_index]
                element,element_cycle=creaElemento(start_time,sec,millisec,valore)
                dati.append(element)
                dati_cycle.append(element_cycle)
            else:
                #satellite non presente
                sat_presente=False
                #aggiorno la lista dei tempi con il relativo istante temporale.
                sec=dati_noheader[i].split()[0].split('.')[0]
                millisec=dati_noheader[i].split()[0].split('.')[1]
                
                #aggiorno la lista con i valori di elevazione da plottare inserendo valore nullo
                element=(start_time+timedelta(seconds=int(sec),milliseconds=int(millisec)),np.nan)
                
                dati.append(element)
                dati_cycle.append(element)
    
    if csv_out:
        with open('logfile_{}.csv'.format(satellite),'w') as textfile:
            for i in range(len(dati)):
                textfile.write('{},{},{}\n'.format(i,dati[i][0].strftime("%Y/%m/%d %H:%M:%S"),dati[i][0]))


    
    return dati,dati_cycle



def main():

    from to_plot_teqc import grandezza

    path=os.path.dirname(os.path.realpath(__file__))

    satelliti=['G01','G02','G03','G04','G05','G06','G07','G08','G09','G10','G11','G12','G13','G14','G15','G16','G17','G18','G19','G20','G21','G22','G23','G25','G26','G29','G28','G30','G31','G32']

    sat='G02'

    compact3filename='PRU1305_union_15secondi'

    to_plot='MP1' #scegliere tra le chiavi del dizionario grandezza

    '''
    print(grandezza.keys()) #per vedere tutte le possibili grandezze da plottare
    for i in grandezza.keys():  #ciclo su tutte le grandezze
        print(i)
    sys.exit()

    '''


    d12,d12_c=readCompact3('{}//files/compact3/{}.{}'.format(path,compact3filename,grandezza[to_plot][1]),sat,False)
    ricevitore='PPTE'
    elevation=readCompact3('{}/files/compact3/{}.ele'.format(path,compact3filename),sat,False)
    '''
    d12,d12_c=readCompact3('{}\\RINEX_PRU1_CALIBA\\dati15secondi_nuovo\\PRU1305_union_15secondi.m12'.format(path),sat,False)
    ricevitore='PRU1'
    elevation=readCompact3('{}\\RINEX_PRU1_CALIBA\\dati15secondi_nuovo\\PRU1305_union_15secondi.ele'.format(path),sat,False)
    '''

    asse_x= [d12[i][0] for i in range(len(d12))]
    asse_y= [d12[i][1] for i in range(len(d12))]
    asse1_x=[d12_c[i][0] for i in range(len(d12_c))]
    asse1_y= [d12_c[i][1] for i in range(len(d12_c))]
    xele=[elevation[0][i][0] for i in range(len(elevation[0]))]
    ele=[elevation[0][i][1] for i in range(len(elevation[0]))]

    print(asse_x==asse1_x)
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    plt.plot(asse_x,asse_y,label='{}'.format(grandezza[to_plot][0]))
    plt.plot(asse1_x,asse1_y,'r*',label='cycle splip')
    #plt.plot(asse_x,asse_y,label=grandezza)
    plt.xlim(datetime(2011, 11, 1, 2, 0, 0),datetime(2011, 11, 1, 3, 5, 0))
    #plt.ylim(-3,4)
    plt.legend()
    #ax.plot(asse1_x, asse1_y)
    # format your data to desired format. Here I chose YYYY-MM-DD but you can set it to whatever you want.
    import matplotlib.dates as mdates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()
    plt.xlabel('time')
    plt.ylabel('{} {}'.format(grandezza[to_plot][0],grandezza[to_plot][2]))
    plt.title('Receiver {0}; Satellite {1}'.format(ricevitore,sat))


    ax2 = ax1.twinx()
    plt.plot(xele,ele,'C1',label='elevation')
    plt.ylabel('elevation')
    plt.ylim(0,90)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    #plt.legend()
    #plt.savefig('C:\\Users\\gterg\\Documents\\Dati_Stazioni_co-locate_Caliba_brasiliana_Alessio_Lorenzo\\coppia_ppte\\immagine_{}_{}.png'.format(sat,grandezza))
    plt.show()

if __name__ == "__main__":
    main()