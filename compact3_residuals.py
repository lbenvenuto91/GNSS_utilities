import sys, os
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from compact3_teqc import readCompact3, creaElemento

#with open (r'C:\Users\gterg\Documenti\test4\RINEX\ublox_neom8t\rinex_211\SC6000980.ele','r') as elefile:

def residuals(ric1,ric2,rm_mean):
    diz_ric1={}
    for i in ric1:
        diz_ric1[i[0]]=i[1]
    residui=[]
    for j in ric2:
        if j[0] in diz_ric1:
            #print(j, diz_ric1[j[0]], j[1]-diz_ric1[j[0]])
            residui.append((j[0], j[1]-diz_ric1[j[0]]))
        else:
            continue
    if rm_mean:
        #values=[i[1] for i in residui]
        
        media=np.nanmean([i[1] for i in residui])
        residui_last=[(j[0],j[1]-media) for j in residui]
        #print(residui_last)
        #ys.exit()
    else:
        residui_last=residui
    return residui_last

#print(diz_ric1)

def main():
    from to_plot_teqc import grandezza

    path=os.path.dirname(os.path.realpath(__file__))

    satelliti=['G01','G02','G03','G04','G05','G06','G07','G08','G09','G10','G11','G12','G13','G14','G15','G16','G17','G18','G19','G20','G21','G22','G23','G25','G26','G29','G28','G30','G31','G32']
    #elevation= readCompact3('/home/lorenzo/test4/RINEX/ublox_neom8t/rinex_211/UBLX0980.ele','G31',False)

    #for sat in satelliti:
    

    to_plot='ION'  #scegliere tra le chiavi del dizionario grandezza

    sat='G31'
    
    sorgente1='ppte3051'
    sorgente2='PRU1305_union_15secondi'

    f1,f1_c=readCompact3('{}//files/compact3/{}.{}'.format(path,sorgente1,grandezza[to_plot][1]),sat,False)
    #ricevitore='PPTE'



    f2,f2_c=readCompact3('{}//files/compact3/{}.{}'.format(path,sorgente2,grandezza[to_plot][1]),sat,False)

    
    differenze=residuals(f1,f2,True)


    asse_x= [differenze[i][0] for i in range(len(differenze))]
    asse_y= [differenze[i][1] for i in range(len(differenze))]
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    plt.plot(asse_x,asse_y)
    plt.xlabel('time')
    plt.ylabel('residuals')
    plt.ylim(-0.5,0.5)
    plt.title('{} residuals for sat {}'.format(grandezza[to_plot][0], sat))
    import matplotlib.dates as mdates
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # rotate and align the tick labels so they look better
    fig.autofmt_xdate()

    plt.show()


if __name__ == "__main__":
    main()