#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Gter copyleft 2019
#Lorenzo Benvenuto

#from datetime import datetime, date
import datetime
import matplotlib.pyplot as plt
import sys,os
import numpy as np
import time
import sqlite3
import datetime
import compact3_teqc
import matplotlib.dates as mdates

class ReadFromDB:
    def __init__(self,dbname='./RINEX_OBS.db',table='test_rinex_ridotto'):
            
        self.dbname=dbname
        self.table=table
    def __str__(self):
        return("database = {}\ntabella = {}".format(self.dbname,self.table))
        
    def allTrackedSatellites (self):
        '''this method returns an array with the SatID of all tracked satellites'''
        conn=sqlite3.connect(self.dbname)
        s=conn.cursor()
        s.execute("SELECT sat_id from {} group by sat_id".format(self.table))
        a=s.fetchall()
        s.close()
        conn.close()
        return a
    
    def categories(self):
        '''this method return all the field name in the selected table
            In particular it returns an array of touples: each tuoples has the following structure
            ('field_name','TYPE')
        '''
        conn=sqlite3.connect(self.dbname)
        s=conn.cursor()
        s.execute("PRAGMA table_info({})".format(self.table))
        a=s.fetchall()
        conn.close()
        b=[]
        for i in range(len(a)):
            j=(a[i][1],a[i][2])
            b.append(j)
        return b


    def readAllData4Sat(self,grandezza,satID,freq):
        conn=sqlite3.connect(self.dbname)
        c=conn.cursor()
        c.execute("SELECT epoca,gpst, {0}_{1} FROM {2} WHERE sat_ID=\'{3}\'".format(grandezza, freq,self.table, satID))
        data=c.fetchall()
        c.close()
        conn.close()
        data=str_to_datetime(data) #in questo modo tutti i secondi elementi delle varie tuple sono oggetti di tipo datetime
        data = add_missing_epochs(data,"one")
        return data

    def readAllData4SatnoFreq(self,grandezza,satID):
        conn=sqlite3.connect(self.dbname)
        c=conn.cursor()
        c.execute("SELECT epoca,gpst, {0} FROM {1} WHERE sat_ID=\'{2}\'".format(grandezza,self.table, satID))
        data=c.fetchall()
        c.close()
        conn.close()
        data=str_to_datetime(data) #in questo modo tutti i secondi elementi delle varie tuple sono oggetti di tipo datetime
        data = add_missing_epochs(data,"one")
        return data

    def readFracSec(self):
        conn=sqlite3.connect(self.dbname)
        c=conn.cursor()
        c.execute("SELECT epoca,gpst,frazione_secondo FROM {} ".format(self.table))
        data=c.fetchall()
        c.close()
        conn.close()
        data=str_to_datetime(data) #in questo modo tutti i secondi elementi delle varie tuple sono oggetti di tipo datetime
        return data


    def readAllData(self,satID,srnfilter,snrthreshold,freq):
        n_obs=8
        conn=sqlite3.connect(self.dbname)
        c=conn.cursor()
        c.execute("SELECT epoca,gpst,frazione_secondo,Epoch_flag,Pseudorange_f1,LLI_PR_f1,SSI_PR_f1,CarrierPhase_f1,LLI_CP_f1,SSI_CP_f1,Doppler_f1,LLI_DP_f1,SSI_DP_f1,SNR_f1,LLI_SNR_f1,SSI_SNR_f1,\
            Pseudorange_f2,LLI_PR_f2,SSI_PR_f2,CarrierPhase_f2,LLI_CP_f2,SSI_CP_f2,Doppler_f2,LLI_DP_f2,SSI_DP_f2,SNR_f2,LLI_SNR_f2,SSI_SNR_f2,\
            Pseudorange_f3,LLI_PR_f3,SSI_PR_f3,CarrierPhase_f3,LLI_CP_f3,SSI_CP_f3,Doppler_f3,LLI_DP_f3,SSI_DP_f3,SNR_f3,LLI_SNR_f3,SSI_SNR_f3 FROM {0} WHERE sat_ID='{1}'".format(self.table, satID))
        data=c.fetchall()
        c.close()
        conn.close()


        if srnfilter==True:
            data=SNR_filter(data,freq,snrthreshold)
            data=str_to_datetime(data) #in questo modo tutti i secondi elementi delle varie tuple sono oggetti di tipo datetime
            data = add_missing_epochs(data,"all")
        else:
            data=str_to_datetime(data) #in questo modo tutti i secondi elementi delle varie tuple sono oggetti di tipo datetime
            data = add_missing_epochs(data,"all")
        return data       

    def decodifica(self,cnst_letter):
        conn=sqlite3.connect(self.dbname)
        c=conn.cursor()
        c.execute("SELECT * from {}_decodifica WHERE constellation = '{}'".format(self.table, cnst_letter))
        data=c.fetchall()
        c.close()
        conn.close()
        return data
'''
def readFromDB(grandezza):    
    print(db_name)
    tabella='test_rinex_ridotto'
    conn=sqlite3.connect(db_name)
    s=conn.cursor()
    
    s.execute("SELECT sat_id from {} group by sat_id".format(tabella))
    temp_sat_id = s.fetchall()


    satID = input('inserire l\'ID del satellite:\n {} \n >>> '.format(temp_sat_id))
    freq = input('inserire la frequenza desiderata: \n >>> ')

    c=conn.cursor()
    c.execute("SELECT epoca,gpst, {0}_{1} FROM {2} WHERE sat_ID=\'{3}\'".format(grandezza, freq,tabella, satID))
    data=c.fetchall()
    
    c.close()
    #conn.commit()
    conn.close()
    #print(data)
      
    return data, satID, freq 

'''
def replace_data_in_tuple(tpl,dt):
    lst = list(tpl)
    lst[1] = dt
    t=tuple(lst)
    return t

def str_to_datetime(lista):
    for i in range(len(lista)):
        a=lista[i][1]
        #aggiungo i decimi di secondo che potrebbero esserci come no
        if not '.' in a:
            a += '.0'
        istante_attuale = datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S.%f')
        lista[i]=replace_data_in_tuple(lista[i],istante_attuale)
    return lista

def add_missing_epochs(data,n_obs):
    data_completo =[]
    #print(range(data[-1][0]))
    #print(data[-1][0])

    #istante_attuale = datetime.datetime.strptime(data[0][1], '%Y-%m-%d %H:%M:%S')
    i=0
    while i < len(data):
        #print(i)
        #print(data[i][0],data[i+1][0],data[i][0]+1==data[i+1][0])

        if i < (len(data)-1):

            if data[i][0]+1==data[i+1][0]:
                
                data_completo.append(data[i])
            else:
                
                data_completo.append(data[i])
                #calcolo epoche mancanti
                epc_manc = data[i+1][0] - data[i][0]
                #aggiungo valore 0.0 della grandezza richiesta per le epoche mancanti
                cont = data[i][0] #definisco un contatore
                #istante_attuale = datetime.datetime.strptime(data[i][1], '%Y-%m-%d %H:%M:%S')
                
                for j in range(epc_manc-1):
                    cont+=1
                    if n_obs == "all":
                        new_elem = (cont,data[i][1]+datetime.timedelta(0,j+1),0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0)
                    elif n_obs == "one":
                        new_elem = (cont,data[i][1]+datetime.timedelta(0,j+1),0.0)
                    else:
                        print("error in adding missing epochs")
                    
                    #print(new_elem)
                    
                    data_completo.append(new_elem)
        else:
            
            
            data_completo.append(data[i])
        i+=1
        
    

    #data.sort()
    #print(data)


    return data_completo


def SNR_filter(data,freq, soglia):
    data_fitered=[]
    if freq=='f1':
        #snr l1 in posizione 5 nell array
        for i in data:
            if i[13] >= soglia:
                data_fitered.append(i)
            else:
                continue                  
    elif freq=='f2':
        #snr l5 in posizione 10 nell array
        for i in data:
            if i[25] >= soglia:
                data_fitered.append(i)
            else:
                continue
    elif freq=='f3':
        #snr l5 in posizione 10 nell array
        for i in data:
            if i[37] >= soglia:
                data_fitered.append(i)
            else:
                continue        
    elif freq=='l2':
        #snr l2 bisogna vedere in che posizione metterlo
        pass
    else:
        print('SNR filter error: freq must be l1, l2 or l5')
        sys.exit()
    
    return data_fitered
    


def plotFromDB(data, grandezza, freq, satID,cartella_output):
    '''funzione che fa cose'''

    to_plot=[]
    epochs = []


    for i in range(len(data)):
        
        epochs.append(data[i][0])
        to_plot.append(data[i][2])
    
    to_plot_temp=np.array(to_plot)
    to_plot_final = np.where(to_plot_temp==0.0, np.nan, to_plot_temp) #rimpiazzo tutti gli 0 con NotANumber in modo che vengano esclusi dal plot
    #print(to_plot_final)
    plt.plot(epochs,to_plot_final)
    plt.title("{} {} {}".format(grandezza, satID, freq))
    plt.ylabel("{}".format(grandezza))
    plt.xlabel("No. of epochs")
    plt.savefig('{0}/{1}_sat_{2}_freq_{3}.png'.format(cartella_output,grandezza,satID, freq))
    #plt.figure()
    plt.show(block=False)
    #plt.pause(0.5)
    plt.close()

def plotBothFreqFromDB(data, grandezza, satID):
    '''funzione che fa cose'''
       
    #per app GEO++ commentare negli altri casi e usare
    #frequenze=['f1','f2']

    if satID.startswith('E'):
        pf=int(input('[0] C1B \n[1] C1C? \n>> '))
        if pf == 0:
            frequenze=['f1', 'f3']
        elif pf == 1:
            frequenze=['f2', 'f3']
        else:
            print('inserire 0 o 1')
    else:
        frequenze=['f1', 'f2']
    
    to_plot = []
    epochs = []

    for i in frequenze:
        dati=data.readAllData4Sat(grandezza,satID,'{}'.format(i))
        epoche=[]
        grndToPlot=[]
        for j in range(len(dati)):
            epoche.append(dati[j][0])
            grndToPlot.append(dati[j][2])
        grndToPlot_temp=np.array(grndToPlot)
        grndToPlot_final=np.where(grndToPlot_temp==0.0, np.nan, grndToPlot_temp) #rimpiazzo tutti gli 0 con NotANumber in modo che vengano esclusi dal plot
    
        #print(np.isnan(grndToPlot_final).all())
        epochs.append(epoche)
        to_plot.append(grndToPlot_final)        

    
    
    
    plt.plot(epochs[0],to_plot[0],label='{}'.format(associaLabel(data,satID,grandezza,frequenze[0])))
    plt.plot(epochs[1],to_plot[1],label='{}'.format(associaLabel(data,satID,grandezza,frequenze[1])))

    plt.title("{} {}".format(grandezza, satID))
    plt.ylabel("{}".format(grandezza))
    plt.xlabel("No. of epochs")
    #plt.savefig('{0}/{1}_sat_{2}_freq_{3}.png'.format(cartella_output,grandezza,satID, freq))
    #plt.figure()
    plt.legend()
    plt.show()
    #plt.pause(0.5)
    #plt.close()

def plotDelta(data,grandezza, freq, satID):

    i = data[0][0] #prima epoca di osservazione del satellite selezionato
    Delta=[] 

    for p in range(len(data)):
        
        try:

            if data[p+1][0] == data[p][0]+1:
                
                if data[p+1][1] != 0.0 and data[p][1] != 0.0:
                    delta = (data[p+1][0], data[p+1][1]-data[p][1])
                    Delta.append(delta)
                    #print(data[p][0],data[p+1][0],'posso calcolare mdp')
                else:
                    delta = (data[p+1][0], np.nan)
                    Delta.append(delta)

            else:
                delta = (data[p+1][0], np.nan)
                Delta.append(delta)
                #print(data[p][0],data[p+1][0],'NON posso calcolare mdp')    
        except:
            print('ultimo valore')    
        
    epoche=[]
    delta_values=[]
     
    for i in range(len(Delta)):
        
        epoche.append(Delta[i][0])
        delta_values.append(Delta[i][1])

    plt.plot(epoche,delta_values)

   # plt.xticks(np.arange(0, 1000, step=100))
    plt.title("Delta {} for sat {}, freq {}".format(grandezza,satID, freq))
    plt.ylabel("delta ")
    plt.xlabel("No. of epochs")
    #plt.savefig('./OUTPUT_PLOTS/mdp_sat_{}_freq_{}.png'.format(satellite, frequenza))
    plt.show()


def twoScalePlot(data, grandezza, freq, satID,cartella_output):

    #print(data)
    to_plot1= []
    epochs= []
    for i in range(len(data)):
        
        epochs.append(data[i][0])
        to_plot1.append(data[i][2])

    to_plot_temp=np.array(to_plot1)
    to_plot_final= np.where(to_plot_temp==0.0, np.nan, to_plot_temp) 

    
    #calcolo il delta

    i = data[0][0] #prima epoca di osservazione del satellite selezionato
    Delta=[] 
    p=0
    while p < len(data):
        
        if p == 0:
            #print('sono all\' inizio')
            delta=(data[p][0],data[p][1],np.nan)
            Delta.append(delta)
        else:
            if data[p-1][0] == data[p][0]-1:
                
                if data[p][2] != 0.0 and data[p-1][2] != 0.0:
                    delta = (data[p][0], data[p][1], data[p][2]-data[p-1][2])
                    Delta.append(delta)
                    #print(data[p][0],data[p+1][0],'posso calcolare mdp')
                else:
                    delta = (data[p][0],data[p][1], np.nan)
                    Delta.append(delta)

            else:
                delta = (data[p][0],data[p][1], np.nan)
                Delta.append(delta)
                #print(data[p][0],data[p+1][0],'NON posso calcolare mdp')    
        p+=1
        
    epoche=[]
    delta_values=[]
     
    for i in range(len(Delta)):
        #print(MDP[i][1])
        epoche.append(Delta[i][0])
        delta_values.append(Delta[i][2])
    
    #delta_values.append(np.nan) #aggiungo un valore nullo alla fine in modo che i vettori abbiano la stessa dimensione
    #epoche.append(np.nan)

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('No. of epochs')
    ax1.set_ylabel('{}'.format(grandezza), color=color)
    ax1.plot(epoche, to_plot_final, color=color)
    ax1.tick_params(axis='y', labelcolor=color)


    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Delta {}'.format(grandezza), color=color)  # we already handled the x-label with ax1
    ax2.plot(epoche, delta_values, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title("Plot for sat. {} freq. {}".format(satID, freq))
    plt.savefig('{0}/two_scale_plot_sat_{1}_freq_{2}.png'.format(cartella_output,satID, freq))
    plt.show(block=False)
    plt.pause(0.5)
    plt.close()



def plotAllData(dati, grandezza, freq):
    '''Function to plot all data and save the all the pictures in a folder'''
    print(dati)
    #creo cartella output
    ora=datetime.datetime.now()
    print("{}_{}_{}".format(ora.strftime("%Y"),ora.strftime("%m"),ora.strftime("%d")))
    nome_cartella = "plot_{}_{}_{}_{}".format(grandezza,ora.strftime("%Y"),ora.strftime("%m"),ora.strftime("%d"))
    if not os.path.exists('./OUTPUT_PLOTS/{}'.format(nome_cartella)):
        os.makedirs('./OUTPUT_PLOTS/{}'.format(nome_cartella))
    
    satelliti = dati.allTrackedSatellites()
    for i in range(len(satelliti)):
        sat=satelliti[i][0]
        print(sat)
        osservazioni=dati.readAllData4Sat('{}'.format(grandezza),'{}'.format(sat),'{}'.format(freq))
        #print (osservazioni)
        plotFromDB(osservazioni,'{}'.format(grandezza),'{}'.format(freq),'{}'.format(sat),'./OUTPUT_PLOTS/{}'.format(nome_cartella) )
        twoScalePlot(osservazioni,'{}'.format(grandezza),'{}'.format(freq),'{}'.format(sat),'./OUTPUT_PLOTS/{}'.format(nome_cartella))





def plotSNRFrom2tables(tab1,tab2,freq):


    if freq=='f1': #la posizione 5 si riferisce all SNR l1, laposizione 10 si riferisce all SNR l5
        frq=13
    elif freq=='f2':
        frq=25
    elif freq=='f3':
        frq=37
       
    dati_satelliti=[]
    dati_satelliti_cnst=[]
    dati_1 = ReadFromDB('/home/lorenzo/dati_GNSS','{}'.format(tab1))
    dati_2 = ReadFromDB('/home/lorenzo/dati_GNSS','{}'.format(tab2))
    print(dati_2.allTrackedSatellites())
    sat=input("scegli satellite >")
    
    data_to_plot=[]

    data_to_plot.append(['xiaomi mi8',dati_1.readAllData('{}'.format(sat),False,35,freq)])
    data_to_plot.append(['stonex sc 600',dati_2.readAllData('{}'.format(sat),False,35,freq)])
    print(data_to_plot[0])
    lista_dati_plot=[]
    for i in data_to_plot:
        elemento=[]

        ascisse=[]
        ordinate=[]
        for j in range(len(i[1])):
            ascisse.append(i[1][j][0])
            ordinate.append(i[1][j][frq]) 
        elemento.append(ascisse)
        ordinate_temp=np.array(ordinate)
        ordinate_final=np.where(ordinate_temp==0.0, np.nan, ordinate_temp)#rimpiazzo tutti gli 0 con NotANumber in modo che vengano esclusi dal plot
        elemento.append(ordinate_final)
        elemento.append(i[0])
        lista_dati_plot.append(elemento)
        
    for i in range(len(lista_dati_plot)):
        if np.isnan(lista_dati_plot[i][1]).all(): #se la grandezza contiene tutti elementi nulli (np.nan)
            plt.plot(lista_dati_plot[i][0],lista_dati_plot[i][1])
        else:
            plt.plot(lista_dati_plot[i][0],lista_dati_plot[i][1],label="{}".format(lista_dati_plot[i][2]))

    
    const_title='GPS'


    plt.title("Satellite {}, frequenza l1".format(sat))
    plt.xlabel("No. of epochs")
    plt.ylabel("C/N0 [dB-Hz]")
    plt.ylim(bottom=0)
    plt.legend(loc='best', fontsize='small',ncol=15,mode='expand')
    
    #for label in plt.legend():
    #    label.set_fontsize(11)
    
    plt.show()





############### NUOVI PLOT ###############
def associaLabel(data,satID,grandezza,frequenza):

    dati_decodifica=data.decodifica(satID[0])
   
    if grandezza=='Pseudorange':
        indexg=1
    elif grandezza=='CarrierPhase':
        indexg=2
    elif grandezza=='Doppler':
        indexg=3
    elif grandezza=='SNR':
        indexg=4
    else:
        indexg=0
    
    if frequenza=='f1':
        indexf=0
    elif frequenza=='f2':
        indexf=4
    elif frequenza=='f3':
        indexf=8
    
    index_tot=indexg+indexf

    return(dati_decodifica[0][index_tot])

def plotGrandezza(data, grandezza, freq, satID,teqc_plot):
    '''funzione che stampa per un specifico satellite, una grandezza tra:

       - pseudorange
       - carrierphase
       - doppler
       - SNR
        
        Con l'opzione teqc_plot settata a True si produce anche il grafico 
        per il satellite selezionato di una grandezza ricavata da teqc +qc
        Le grandezze possono essere

        - elevazione
        - azimuth
        - multipath
        - iono
        ....
        NOTA: per le opzioni del grafico di teqc bisogna agire nella funzione, 
        non sono automatiche
       '''
    
    dati=data.readAllData4Sat(grandezza,satID,freq)
    
    if teqc_plot:
        
        to_plot=[]
        epochs = []

        for i in range(len(dati)):
            
            epochs.append(dati[i][1])
            to_plot.append(dati[i][2])
        to_plot_temp=np.array(to_plot)
        to_plot_final = np.where(to_plot_temp==0.0, np.nan, to_plot_temp) #rimpiazzo tutti gli 0 con NotANumber in modo che vengano esclusi dal plot
        
        #calcolo statistiche
        j=to_plot_final[~np.isnan(to_plot_final)]
        etichetta='avg= {}\nvar={}\nstd= {}\nmin= {}\nmax= {}'.format(round(j.mean(),2),round(j.var(),2),round(j.std(),2),round(j.min(),2),round(j.max(),2))
    
        fig, (ax1, ax2) = plt.subplots(nrows=2)
        plt.subplots_adjust(hspace=0.5)
        ax1.plot(epochs,to_plot_final,label=etichetta)
        ax1.set_title("{} {} {}".format(grandezza, satID, freq))
        ax1.set_xlabel('UTC time')
        ax1.set_ylabel("{}".format(grandezza))
        leg = ax1.legend()
        ax1.legend(loc='best')


        teqc_quantity= compact3_teqc.readCompact3('/home/lorenzo/test4/RINEX/xiaomi_mi8/rinex_211/XIAOM0980_teSt.m15',satID,False)
        asse_x= [teqc_quantity[i][0] for i in range(len(teqc_quantity))]
        asse_y= [teqc_quantity[i][1] for i in range(len(teqc_quantity))]
        ax2.plot(asse_x,asse_y)
        ax2.set_title("Multipath f 1-5 Satellite {}".format(satID))
        ax2.set_xlabel('UTC time')

        plt.show()
    
    
    
    else:

        to_plot=[]
        epochs = []


        for i in range(len(dati)):
            
            epochs.append(dati[i][1])
            to_plot.append(dati[i][2])
        
        to_plot_temp=np.array(to_plot)
        to_plot_final = np.where(to_plot_temp==0.0, np.nan, to_plot_temp) #rimpiazzo tutti gli 0 con NotANumber in modo che vengano esclusi dal plot
        
        #calcolo statistiche
        j=to_plot_final[~np.isnan(to_plot_final)]
        etichetta='avg= {}\nvar={}\nstd= {}\nmin= {}\nmax= {}'.format(round(j.mean(),2),round(j.var(),2),round(j.std(),2),round(j.min(),2),round(j.max(),2))
        
        
        #print(to_plot_final)
        plt.plot(epochs,to_plot_final,label=etichetta)
        plt.title("{} {} {}".format(grandezza, satID, freq))
        plt.ylabel("{}".format(grandezza))
        plt.xlabel("UTC Time")
        #plt.savefig('{0}/{1}_sat_{2}_freq_{3}.png'.format(cartella_output,grandezza,satID, freq))
        plt.legend()
        name='/home/lorenzo/test4/analisi_segnale/SNR/stonex_sc600/{}/SNR_{}_{}.png'.format(satID[0],satID,freq)
        #plt.savefig(name,dpi=500)
        plt.show()
        #plt.pause(0.5)
        #plt.close()


def plotFrazioneSecondo(data,satID):
    '''funzione che fa cose'''
    dati=data.readAllData4SatnoFreq('frazione_secondo',satID)
    
    #sys.exit()
    
    to_plot=[]
    epochs = []


    for i in range(len(dati)):
        
        epochs.append(dati[i][1])
        to_plot.append(dati[i][2])
    
    to_plot_temp=np.array(to_plot)
    #to_plot_final = np.where(to_plot_temp==0.0, np.nan, to_plot_temp) #rimpiazzo tutti gli 0 con NotANumber in modo che vengano esclusi dal plot
    print(to_plot_temp)
    plt.plot(epochs,to_plot_temp)
    plt.title("Frazione secondo {}".format(satID))
    plt.ylabel("Frazione secodno")
    plt.xlabel("Datetime")
    #plt.savefig('{0}/{1}_sat_{2}_freq_{3}.png'.format(cartella_output,grandezza,satID, freq))
    #plt.figure()
    plt.show()
    #plt.pause(0.5)
    #plt.close()




def plotOBSFrom3tables(osserv,sat,tab1,tab2,tab3,freq,stats,teqc=False):

    osservabili=['PR','CP','DP','SNR']
    
    if osserv not in osservabili:
        print('choose between [PR, CP, DP, SNR]')
    
    PR=4
    CP=7
    DP=10
    SNR=13

    
    if freq=='f1': #la posizione 5 si riferisce all SNR l1, laposizione 10 si riferisce all SNR l5
        if osserv=='PR':
            osserv_position=PR
        elif osserv=='CP':
            osserv_position=CP
        elif osserv=='DP':
            osserv_position=DP
        elif osserv_position=='SNR':
            osserv_position==SNR
    elif freq=='f2':
        if osserv=='PR':
            osserv_position=PR+12
        elif osserv=='CP':
            osserv_position=CP+12
        elif osserv=='DP':
            osserv_position=DP+12
        elif osserv_position=='SNR':
            osserv_position==SNR+12
        
    elif freq=='f3':
        if osserv=='PR':
            osserv_position=PR+24
        elif osserv=='CP':
            osserv_position=CP+24
        elif osserv=='DP':
            osserv_position=DP+24
        elif osserv_position=='SNR':
            osserv_position==SNR+24    
       
    dati_satelliti=[]
    dati_satelliti_cnst=[]
    dati_1 = ReadFromDB('/home/lorenzo/dati_GNSS','{}'.format(tab1))
    dati_2 = ReadFromDB('/home/lorenzo/dati_GNSS','{}'.format(tab2))
    dati_3 = ReadFromDB('/home/lorenzo/dati_GNSS','{}'.format(tab3))

    
    data_to_plot=[]

    data_to_plot.append(['xiaomi mi8',dati_1.readAllData('{}'.format(sat),False,35,freq)])
    data_to_plot.append(['ublox neo m8t',dati_2.readAllData('{}'.format(sat),False,35,freq)])
    data_to_plot.append(['stonex sc600',dati_3.readAllData('{}'.format(sat),False,35,freq)])

    
    lista_dati_plot=[]
    for i in data_to_plot:
        elemento=[]

        ascisse=[]
        ordinate=[]
        for j in range(len(i[1])):
            ascisse.append(i[1][j][1])
            ordinate.append(i[1][j][osserv_position]) 
        elemento.append(ascisse)
        ordinate_temp=np.array(ordinate)
        ordinate_final=np.where(ordinate_temp==0.0, np.nan, ordinate_temp)#rimpiazzo tutti gli 0 con NotANumber in modo che vengano esclusi dal plot
        elemento.append(ordinate_final)
        elemento.append(i[0])
        lista_dati_plot.append(elemento)
    avg=[]
    var=[]
    std=[]   

    if teqc:
        fig, (ax1, ax2) = plt.subplots(nrows=2)
        plt.subplots_adjust(hspace=0.5)
        for i in range(len(lista_dati_plot)):
            if np.isnan(lista_dati_plot[i][1]).all(): #se la grandezza contiene tutti elementi nulli (np.nan)
                ax1.plot(lista_dati_plot[i][0],lista_dati_plot[i][1])
            else:
                ax1.plot(lista_dati_plot[i][0],lista_dati_plot[i][1],label="{}".format(lista_dati_plot[i][2]))
            
            j=lista_dati_plot[i][1][~np.isnan(lista_dati_plot[i][1])]
            etichetta='avg= {}\nvar={}\nstd= {}\nmin= {}\nmax= {}\n'.format(round(j.mean(),2),round(j.var(),2),round(j.std(),2),round(j.min(),2),round(j.max(),2))
            avg.append(round(j.mean(),2))
            var.append(round(j.var(),2))
            std.append(round(j.std(),2))
        print(avg,var,std)
        const_title='GPS'
        
        ax1.set_title("Satellite {}, frequenza l1".format(sat))
        ax1.set_xlabel('UTC time')
        ax1.set_ylabel('SNR [dB-Hz')
        leg = ax1.legend()
        ax1.legend(loc='best', fontsize='small',ncol=15,mode='expand')


        '''
        plt.title("Satellite {}, frequenza l1".format(sat))
        plt.xlabel("UTC time")
        plt.ylabel("C/N0 [dB-Hz]")
        plt.ylim(bottom=0)
        plt.legend(loc='best', fontsize='small',ncol=15,mode='expand')
        '''
        elevation= compact3_teqc.readCompact3('/home/lorenzo/test4/RINEX/ublox_neom8t/rinex_211/UBLX0980.ele',sat,False)
        asse_x= [elevation[i][0] for i in range(len(elevation))]
        asse_y= [elevation[i][1] for i in range(len(elevation))]
        ax2.plot(asse_x,asse_y)
        ax2.set_title("Elevazione Satellite {}".format(sat))
        ax2.set_xlabel('UTC time')
    else:
        for i in range(len(lista_dati_plot)):
            if np.isnan(lista_dati_plot[i][1]).all(): #se la grandezza contiene tutti elementi nulli (np.nan)
                plt.plot(lista_dati_plot[i][0],lista_dati_plot[i][1])
            else:
                plt.plot(lista_dati_plot[i][0],lista_dati_plot[i][1],label="{}".format(lista_dati_plot[i][2]))
            
            j=lista_dati_plot[i][1][~np.isnan(lista_dati_plot[i][1])]
            etichetta='avg= {}\nvar={}\nstd= {}\nmin= {}\nmax= {}\n'.format(round(j.mean(),2),round(j.var(),2),round(j.std(),2),round(j.min(),2),round(j.max(),2))
            avg.append(round(j.mean(),2))
            var.append(round(j.var(),2))
            std.append(round(j.std(),2))
        #print(avg,var,std)
        const_title='GPS'
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.title("Satellite {}, frequenza l1".format(sat))
        plt.xlabel('UTC time')
        #plt.xticks(rotation=45)
        plt.ylabel('Pseudorange [m]')
        plt.legend(loc='best', fontsize='small',ncol=15,mode='expand')





    if stats:
        plt.figure()
        
        labels = ['stonex sc600', 'ublox neo m8t', 'xiaomi mi8']
        fig, (ax1, ax2, ax3) = plt.subplots(nrows=3)
        #plt.figure(1,figsize=(1.36, 15.48),dpi=100)
        plt.subplots_adjust(hspace=1)
        xticks = [1,1.2,1.4] # ci serve per posizionare le barre e anche le label
        ax1.bar(xticks,avg, color=['tab:blue','tab:orange','tab:green'], width=0.1, align="center")
        ax1.set_title("Media")
        ax1.set_xticklabels(labels)  # verranno posizionate dove sono gli xticks
        ax1.set_xticks(xticks)
        ax1.set_ylabel('media SNR')


        xticks = [1,1.2,1.4] # ci serve per posizionare le barre e anche le label

        ax2.bar(xticks,var, color=['tab:blue','tab:orange','tab:green'], width=0.1, align="center")
        ax2.set_title("Varianza")
        ax2.set_xticklabels(labels)  # verranno posizionate dove sono gli xticks
        ax2.set_xticks(xticks)
        ax2.set_ylabel('var SNR')
        
        ax3.bar(xticks,std, color=['tab:blue','tab:orange','tab:green'], width=0.1, align="center")
        ax3.set_title("Deviazione Standard")
        ax3.set_xticklabels(labels)  # verranno posizionate dove sono gli xticks
        ax3.set_xticks(xticks)
        ax3.set_ylabel('std SNR')
        plt.show()
    else:
        plt.show()
        


def twoSizePlot(data, grandezza1, freq, grandezza2, satID):

    dati1=data.readAllData4Sat(grandezza1,satID,freq)
   
    dati1_decodifica=data.decodifica(satID[0])
    #print(dati1_decodifica[0][1])
    to_plot1= []
    epochs1= []
    for i in range(len(dati1)):
        
        epochs1.append(dati1[i][1])
        to_plot1.append(dati1[i][2])

    to_plot_temp1=np.array(to_plot1)
    to_plot_final1= np.where(to_plot_temp1==0.0, np.nan, to_plot_temp1) 
    if grandezza2=='frazione_secondo':
        dati2=data.readFracSec()
    else:
        dati2=data.readAllData4SatnoFreq(grandezza2,satID)
    
    to_plot2= []
    epochs2= []
    for i in range(len(dati2)):
        
        epochs2.append(dati2[i][1])
        to_plot2.append(dati2[i][2])

    to_plot_temp2=np.array(to_plot2)
    #to_plot_final2= np.where(to_plot_temp==0.0, np.nan, to_plot_temp) 
    
    
    #delta_values.append(np.nan) #aggiungo un valore nullo alla fine in modo che i vettori abbiano la stessa dimensione
    #epoche.append(np.nan)

    fig, ax1 = plt.subplots()

    color = 'tab:red'
    ax1.set_xlabel('UTC time')
    ax1.set_ylabel('{}'.format(grandezza1), color=color)
    ax1.plot(epochs1, to_plot_final1, color=color)
    ax1.tick_params(axis='y', labelcolor=color)


    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('{}'.format(grandezza2), color=color)  # we already handled the x-label with ax1
    ax2.plot(epochs2, to_plot_temp2, color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.title("Plot for sat. {} freq. {}".format(satID, freq))
    #plt.savefig('{0}/two_scale_plot_sat_{1}_freq_{2}.png'.format(cartella_output,satID, freq))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.show()
    #plt.pause(0.5)
    #plt.close()

def plotSNRAllSat(datiDB, costellazione, frequenza):
    
    if frequenza=='f1': #la posizione 5 si riferisce all SNR l1, laposizione 10 si riferisce all SNR l5
        frq=13
    elif frequenza=='f2':
        frq=25
    elif frequenza=='f3':
        frq=37
    
    dati_satelliti=[]
    dati_satelliti_cnst=[]


    for i in datiDB.allTrackedSatellites():
       dati_satelliti.append(i[0])
    
    for i in dati_satelliti:
        if i.startswith('{}'.format(costellazione)):
           dati_satelliti_cnst.append(i)
        else:
            continue

    data_to_plot=[]
    for i in dati_satelliti_cnst:

            data_to_plot.append([i,datiDB.readAllData('{}'.format(i),False,35,frequenza)])
   #print(data_to_plot)
    lista_dati_plot=[]
    for i in data_to_plot:

        elemento=[]
        
        ascisse=[]
        ordinate=[]
        j=0
        while j <len(i[1]):
            ascisse.append(i[1][j][1])
            ordinate.append(i[1][j][frq]) 
            #print(j)
            j+=1
        elemento.append(ascisse)
        ordinate_temp=np.array(ordinate)
        ordinate_final=np.where(ordinate_temp==0.0, np.nan, ordinate_temp)#rimpiazzo tutti gli 0 con NotANumber in modo che vengano esclusi dal plot
        elemento.append(ordinate_final)
        elemento.append(i[0])
        lista_dati_plot.append(elemento)
    
    # calcolo statistiche TEST

    media=[]
    var=[]
    std=[]
    minimo=[]
    massimo=[]

    fig, ax = plt.subplots()

    for i in range(len(lista_dati_plot)):
        j=lista_dati_plot[i][1][~np.isnan(lista_dati_plot[i][1])]
        etichetta='{}'.format(lista_dati_plot[i][2])

        if np.isnan(lista_dati_plot[i][1]).all(): #se la grandezza contiene tutti elementi nulli (np.nan)
            ax.plot(lista_dati_plot[i][0],lista_dati_plot[i][1])
        else:
            ax.plot(lista_dati_plot[i][0],lista_dati_plot[i][1],label=etichetta)
            media.append(j.mean())
            var.append(j.var())
            std.append(j.std())
            minimo.append(j.min())
            massimo.append(j.max())

    #creo una matrice contente le statistiche
    stats=np.array([media,var,std,minimo,massimo])
    media_all=stats[0].mean() #media delle medie
    min_all=stats[3].min() #minimo dei minimi
    max_all=stats[4].max() #massimo dei massimi
    
    textstr='media= {}\nmax= {}\nmin= {}'.format(round(media_all,2),round(max_all,2),round(min_all,2))
    print(textstr)
    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # place a text box in upper left in axes coords
    ax.text(0.05, 0.25, textstr, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props)

    const_title=''
    if costellazione=='G':
        const_title+='GPS'
    elif costellazione=='E':
        const_title+='Galileo'
    elif costellazione=='R':
        const_title+='GLONASS'
    elif costellazione=='C':
        const_title+='BeiDou'
    else:
        const_title+='all'

    if const_title=='Galileo':
        if frequenza=='f1' or frequenza=='f2':
            frqtlt='E1'
        elif frequenza=='f3':
            frqtlt='E5'
    else:
        if frequenza=='f1':
            frqtlt='L1'
        elif frequenza=='f2':
            frqtlt='L5'

    plt.title("Xiaomi mi8 Satelliti {}, frequenza {}".format(const_title,frqtlt))
    plt.xlabel("UTC time")
    plt.ylabel("C/N0 [dB-Hz]")
    plt.ylim(bottom=0)
    plt.legend(loc='best', fontsize='small',ncol=15,mode='expand')
    
    #for label in plt.legend():
    #    label.set_fontsize(11)
    #name='/home/lorenzo/Documenti/test3/secondo_test/analisi_segnale/multipath_indotto/posizione5/mp_ind_posiz5_Galileo-E1.png'
    #plt.savefig(name,dpi=500)
    #plt.figure(figsize=(3.841, 7.195), dpi=100)
    plt.show()

        




#main
def main():

    frequenza='f1'
    #dati = ReadFromDB() #posso istanziare una nuova istanza con diverso db e tabella
    #dati_mi8_geopp = ReadFromDB('/home/lorenzo/dati_GNSS','test_foss4g_xiaomi')
    #print(dati_mi8_geopp.allTrackedSatellites())
    #ati_new=ReadFromDB('/home/lorenzo/dati_GNSS','GEOPP_mi8_new')
    #print(dati_new.allTrackedSatellites())
    dati_test = ReadFromDB('/home/lorenzo/dati_GNSS','xiaomi_mi8_098')
    costellazione='R' #(G=GPS, E=galileo, R=GLONASS, C=BeiDou)
    #plotSNRAllSat(dati_test,costellazione,frequenza)
    #plotGrandezza(dati_test,'Pseudorange','f1','R09',False)
    '''
    for i in dati_test.allTrackedSatellites():
        try:
            plotGrandezza(dati_test,'SNR','f1',i[0])
        except Exception as e:
            print(e)
        try:
            plotGrandezza(dati_test,'SNR','f2',i[0])
        except Exception as e:
            print(e)
        try:
            plotGrandezza(dati_test,'SNR','f3',i[0])
        except Exception as e:
            print(e)
        '''         
           
    #plotFrazioneSecondo(dati_test3,'G20')
    #plot SNR
    
    twoSizePlot(dati_test,'Pseudorange','f1','frazione_secondo','G18')
        

    #plotBothFreqFromDB(dati_mi8_geopp,'SNR','G26')
    #plotSNRFrom2tables('xiaomi_mi8_098','stonex_sc600_098','f1')

    osservabili=['PR','CP','DP','SNR'] #pseudorange carrierphase doppler C/N0
    commonGPS=['G2','G12','G16','G18','G20','G21','G25','G26','G29','G31']

    #for i in commonGPS:
        #plotOBSFrom3tables('PR','{}'.format(i),'xiaomi_mi8_098','ublox_neom8t_098','stonex_sc600_098','f1',False)



  

    
    


if __name__=="__main__":
    main()