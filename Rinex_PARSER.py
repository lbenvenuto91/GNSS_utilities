#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Gter copyleft 2019
#Lorenzo Benvenuto



from datetime import datetime, date, timedelta
import time
from progressbar import ProgressBar
from tqdm import tqdm
import sqlite3
import mmap
import sys,os
import numpy
#import dateutil.parser as dparser


def get_num_lines(dir, file):
    lines = 0
    with open(dir + file) as handler:
    
        for i, line in  enumerate(handler):
                #Check for a Timestamp lable
                if '> ' in line:
                    lines+=1
   
    return lines


def readObsAndroid(dir, file, table_name):
    
    '''
    Function to read obs from a RINEX file (generated with GEO++ RINEX Logger app)
    returns a list of query which must be used to upload the data to a sqlite DB
    the list contains also the field code_minus_phase: this parameter is calculated within this function.

    '''
    lambda_l1= 0.1905 #lunghezza d'onda portante L1 [m]
    lambda_l5= 0.2548  #lunghezza d'onda portante L5 [m]
    #df = pd.DataFrame()
    #Grab header
    costellazioni=[]
    query=[]
    query_decod=[]
    header = ''
    observation_type={}
    total_iter=get_num_lines(dir,file)
    print('\n\t*** READING DATA ***\n')
    with open(dir + file) as handler:
        for i,line in enumerate(handler):

            if line.startswith('G') and line[74:79]=='TYPES':

                costellazioni.append('G')
                tipo_osservazioni=[]
                a=7
                b=10
                for i in range(int(line[4:6])):
                    tipo_osservazioni.append(line[a:b])
                    a+=4
                    b+=4
                observation_type['G']=tipo_osservazioni

            elif line.startswith('R ')and line[74:79]=='TYPES':
                costellazioni.append('R')
                tipo_osservazioni=[]
                a=7
                b=10
                for i in range(int(line[4:6])):
                    tipo_osservazioni.append(line[a:b])
                    a+=4
                    b+=4
                observation_type['R']=tipo_osservazioni
            elif line.startswith('E')and line[74:79]=='TYPES':
                costellazioni.append('E')
                tipo_osservazioni=[]
                a=7
                b=10
                for i in range(int(line[4:6])):
                    tipo_osservazioni.append(line[a:b])
                    a+=4
                    b+=4
                observation_type['E']=tipo_osservazioni
            elif line.startswith('C')and line[74:79]=='TYPES':
                costellazioni.append('C')
                tipo_osservazioni=[]
                a=7
                b=10
                for i in range(int(line[4:6])):
                    tipo_osservazioni.append(line[a:b])
                    a+=4
                    b+=4
                observation_type['C']=tipo_osservazioni
            elif line.startswith('J')and line[74:79]=='TYPES':
                costellazioni.append('J')
                tipo_osservazioni=[]
                a=7
                b=10
                for i in range(int(line[4:6])):
                    tipo_osservazioni.append(line[a:b])
                    a+=4
                    b+=4
                observation_type['J']=tipo_osservazioni

            header += line
            total_iter+=1 #serve per barra di stato
            
            if 'END OF HEADER' in line:
                break
    #print(observation_type)                
    for c in costellazioni:
        
        a = len(observation_type[c])
        while a < 12:
            observation_type[c].append('-')
            a+=1
        
        elem_query="INSERT INTO {}_decodifica VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(table_name,c,observation_type[c][0],observation_type[c][1],observation_type[c][2],observation_type[c][3],observation_type[c][4],observation_type[c][5],observation_type[c][6],observation_type[c][7],observation_type[c][8],observation_type[c][9],observation_type[c][10],observation_type[c][11])
        
        query_decod.append(elem_query)

        

    #Grab Data
    #print(total_iter)
    epoch=0

    #print('ciao sono qui')
    with open(dir + file) as handler:
        
        for i, line in  enumerate(tqdm(handler, total=total_iter)):
            #Check for a Timestamp lable
            if '> ' in line:
                epoch +=1 
                epoch_flag=line[31]
                #print(epoch_flag)
                year=line[2:6]
                months=line[7:9]
                day=line[10:12]
                hour=line[13:15]
                minute=line[16:18]
                second=line[19:29]
                satNum=line[32:35]
                               
                #f int(epoch_flag)<2: #epoch_flag>2 significa Special event (vedere appendice A14 RINEX 3.03)
                try:
                    clock_offset=line[40:55]
                except:
                    clock_offset=' '
                              
                secondi=second.split('.')[0]
                frac_sec=int(second.split('.')[1])/10**7
                #print(secondi,frac_sec)
                #print(year, months, day, hour, minute, second, epoch_flag, satNum, clock_offset)
                index=datetime(int(year), int(months), int(day), int(hour), int(minute), int(secondi))
                #print(index)
                index+=timedelta(seconds=frac_sec)
                #print(index)
                
                for j in range(int(satNum)):
                    #just save the data as a string for now
                    satData = handler.readline()
                    satId = satData[0:3]
                    
                    #fix the names
                    if satId[1]==' ':
                        a=satId.split()
                        satId='{}0{}'.format(a[0],a[1])

                    #first frequency
                    try:
                        psr_1 = float(satData[3:17])
                    except:
                        psr_1 = 0.0
                    
                    try:
                        lli_psr_1 = int(satData[17])
                    except:
                        lli_psr_1= 0.0

                    try:
                        ssi_psr_1 = int(satData[18])
                    except:
                        ssi_psr_1 = 0.0

                    try:
                        phs_1 = float(satData[19:33])
                    except:
                        phs_1 = 0.0
                    
                    try:
                        lli_phs_1 = int(satData[33])
                    except:
                        lli_phs_1=0.0

                    try:
                        ssi_phs_1 = int(satData[34])
                    except:
                        ssi_phs_1 = 0.0

                    try:              
                        dop_1 = float(satData[35:49])
                    except:
                        dop_1 = 0.0

                    try:
                        lli_dop_1 = int(satData[49])
                    except:
                        lli_dop_1 = 0.0

                    try:
                        ssi_dop_1 = int(satData[50])
                    except:
                        ssi_dop_1 = 0.0

                    try:
                        snr_1 = float(satData[51:65])
                    except:
                        snr_1 = 0.0
                    
                    try:
                        lli_snr_1 = int(satData[65])
                    except:
                        lli_snr_1 = 0.0
                    
                    try:
                        ssi_snr_1 = int(satData[66])
                    except:
                        ssi_snr_1 = 0.0
                    
                    #second frequency
                    try:
                        try:
                            psr_2 = float(satData[67:81])
                        except:
                            psr_2 = 0.0
                        
                        try:
                            lli_psr_2 = int(satData[81])
                        except:
                            lli_psr_2= 0.0

                        try:
                            ssi_psr_2 = int(satData[82])
                        except:
                            ssi_psr_2 = 0.0

                        try:
                            phs_2 = float(satData[83:97])
                        except:
                            phs_2 = 0.0
                        
                        try:
                            lli_phs_2 = int(satData[97])
                        except:
                            lli_phs_2=0.0

                        try:
                            ssi_phs_2 = int(satData[98])
                        except:
                            ssi_phs_2 = 0.0

                        try:              
                            dop_2 = float(satData[99:113])
                        except:
                            dop_2 = 0.0

                        try:
                            lli_dop_2 = int(satData[113])
                        except:
                            lli_dop_2 = 0.0

                        try:
                            ssi_dop_2 = int(satData[114])
                        except:
                            ssi_dop_2 = 0.0

                        try:
                            snr_2 = float(satData[115:129])
                        except:
                            snr_2 = 0.0
                        
                        try:
                            lli_snr_2 = int(satData[129])
                        except:
                            lli_snr_2 = 0.0
                        
                        try:
                            ssi_snr_2 = int(satData[130])
                        except:
                            ssi_snr_2 = 0.0
                    
                    except:
                        psr_2 = 0.0
                        lli_psr_2 = 0.0
                        ssi_psr_2 = 0.0
                        phs_2 = 0.0
                        lli_phs_2 = 0.0
                        ssi_phs_2 = 0.0
                        dop_2 = 0.0
                        lli_dop_2 = 0.0
                        ssi_dop_2 = 0.0
                        snr_2 = 0.0
                        lli_snr_2 = 0.0
                        ssi_snr_2 = 0.0    

                    #third frequency
                    try:
                        try:
                            psr_3 = float(satData[131:145])
                        except:
                            psr_3 = 0.0
                        
                        try:
                            lli_psr_3 = int(satData[145])
                        except:
                            lli_psr_3= 0.0

                        try:
                            ssi_psr_3 = int(satData[146])
                        except:
                            ssi_psr_3 = 0.0

                        try:
                            phs_3 = float(satData[147:161])
                        except:
                            phs_3 = 0.0
                        
                        try:
                            lli_phs_3 = int(satData[161])
                        except:
                            lli_phs_3=0.0

                        try:
                            ssi_phs_3 = int(satData[162])
                        except:
                            ssi_phs_3 = 0.0

                        try:              
                            dop_3 = float(satData[163:177])
                        except:
                            dop_3 = 0.0

                        try:
                            lli_dop_3 = int(satData[177])
                        except:
                            lli_dop_3 = 0.0

                        try:
                            ssi_dop_3 = int(satData[178])
                        except:
                            ssi_dop_3 = 0.0

                        try:
                            snr_3 = float(satData[179:193])
                        except:
                            snr_3 = 0.0
                        
                        try:
                            lli_snr_3 = int(satData[193])
                        except:
                            lli_snr_3 = 0.0
                        
                        try:
                            ssi_snr_3 = int(satData[194])
                        except:
                            ssi_snr_3 = 0.0
                    
                    except:
                        psr_3 = 0.0
                        lli_psr_3 = 0.0
                        ssi_psr_3 = 0.0
                        phs_3 = 0.0
                        lli_phs_3 = 0.0
                        ssi_phs_3 = 0.0
                        dop_3 = 0.0
                        lli_dop_3 = 0.0
                        ssi_dop_3 = 0.0
                        snr_3 = 0.0
                        lli_snr_3 = 0.0
                        ssi_snr_3 = 0.0                                     

                    
                    #print(psr_1,lli_psr_1, ssi_psr_1,phs_1,lli_phs_1,ssi_phs_1,dop_1,lli_dop_1,ssi_dop_1,snr_1,lli_snr_1,ssi_snr_1)
                    
                                       
                    #Fix the names
                    
            
                    c="INSERT INTO {} VALUES ({},'{}','{}',{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{})".format(table_name,epoch,satId,index,frac_sec,epoch_flag,psr_1,lli_psr_1,ssi_psr_1,phs_1,lli_phs_1,ssi_phs_1,dop_1,lli_dop_1,ssi_dop_1,snr_1,lli_snr_1,ssi_snr_1,psr_2,lli_psr_2,ssi_psr_2,phs_2,lli_phs_2,ssi_phs_2,dop_2,lli_dop_2,ssi_dop_2,snr_2,lli_snr_2,ssi_snr_2,psr_3,lli_psr_3,ssi_psr_3,phs_3,lli_phs_3,ssi_phs_3,dop_3,lli_dop_3,ssi_dop_3,snr_3,lli_snr_3,ssi_snr_3)
                    query.append(c)
                
            else:
                continue

    return header, query_decod, query

def readObsRINEX_v3_03(dir, file, table_name):
    
    '''
    Function to read obs from a RINEX file (generated with GEO++ RINEX Logger app)
    returns a list of query which must be used to upload the data to a sqlite DB
    the list contains also the field code_minus_phase: this parameter is calculated within this function.

    '''
    lambda_l1= 0.1905 #lunghezza d'onda portante L1 [m]
    lambda_l5= 0.2548  #lunghezza d'onda portante L5 [m]
    #df = pd.DataFrame()
    #Grab header
    query=[]
    header = ''
    total_iter=get_num_lines(dir,file)
    
    with open(dir + file) as handler:
        for i,line in enumerate(handler):
            header += line
            total_iter+=1 #serve per barra di stato
            if 'END OF HEADER' in line:
                break
    
    #Grab Data
    #print(total_iter)
    epoch=0
    #print('ciao sono qui')
    with open(dir + file) as handler:
        
        for i, line in  enumerate(tqdm(handler, total=total_iter)):
            #Check for a Timestamp lable
            if '> ' in line:
                epoch +=1 
                #Grab Timestamp
                links = line.split()
                #print(links)
                index = datetime.strptime(' '.join(links[1:7]), '%Y %m %d %H %M %S.%f0')
           
                #Identify number of satellites
                satNum = int(links[8])
                #print(satNum)
                #For every sat
                
                for j in range(satNum):
                    #just save the data as a string for now
                    satData = handler.readline()
                                      
                    
                    #satelliti GPS GLONASS Galielo e BeiDou               
                                            
                    try:
                        C1=float(satData[5:19])
                #          print("c1", C1)
                    except:
                        C1=0.0
                #          print("c1", C1)
                    
                    try:
                        L1=float(satData[19:34])
                #         print("L1", L1)
                    except:
                        L1=0.0
                #        print("L1", L1)

                    try:
                        D1=float(satData[38:51])
                    #       print("d1", D1)
                    except:
                        D1=0.0
                    #      print("d1", D1)
                    
                    try:
                        C_N0_L1=float(satData[58:67])
                    #     print("c/n0_l1",C_N0_L1)
                    except:
                        C_N0_L1=0.0
                    #    print("c/n0_l1", C_N0_L1)
                    #print("\n")
                
                    try:
                        
                        try:
                            C5=float(satData[68:82])
                        #       print("c5", C5)
                        except:
                            C5=0.0
                        #      print("c5", C5)
                        
                        try:
                            L5=float(satData[83:98])
                        #     print("l5", L5)
                        except:
                            L5=0.0
                        #    print("l5", 0.0)
                        
                        try:
                            D5=float(satData[102:117])
                            #   print("d5", float(satData[102:117]))
                        except:
                            D5=0.0
                            #  print("d5", D5)
                        
                        try:
                            C_N0_L5=float(satData[121:130])
                            # print("c/n0_l5", C_N0_L5)
                        except:
                            C_N0_L5=0.0
                            #print("c/n0_l5", C_N0_L5)
                        #print("\n")
                    except:
                        C5=0.0
                        #print("c5",C5)
                        L5=0.0
                        #print("l5", L5)
                        D5=0.0
                        #print("d5", D5)
                        C_N0_L5=0.0
                        #print("c/n0_l5",C_N0_L5)
                        #print("\n")

                    #code-phase

                    if C1 != 0.0 and L1!= 0.0:
                        cd_phs_l1=C1-L1*lambda_l1
                    else:
                        cd_phs_l1=0.0
                    
                    if C5 != 0.0 and L5!= 0.0:
                        cd_phs_l5=C5-L5*lambda_l5
                    else:
                        cd_phs_l5=0.0
                    
                    
                    
                    #Fix the names
                    
                    satdId = satData.replace("G ", "G0").split()[0]
                    
                    
                    #print(satdId)
                    #Make a dummy dataframe

                    c="INSERT INTO {} VALUES ({},'{}','{}',{},{},{},{},{},{},{},{},{},{})".format(table_name, epoch,index,satdId,C1,L1,D1,C_N0_L1,cd_phs_l1,C5,L5,D5,C_N0_L5,cd_phs_l5)
                    #print(c)
                    query.append(c)
            else:
                continue

    return header, query


def writeDataToDB(db_name,table_name,query, query_decod):
    print('\n\t*** UPLOADING DATA TO DB*** \n')
    conn=sqlite3.connect(db_name)
    c=conn.cursor()

    dropTableStatement = "DROP TABLE IF EXISTS {}".format(table_name)

    c.execute(dropTableStatement)
    c.execute("CREATE TABLE {}(epoca INTEGER, sat_id TEXT, gpst DATE, frazione_secondo REAL, Epoch_flag INTEGER, Pseudorange_f1 REAL, LLI_PR_f1 INTEGER, SSI_PR_f1 INTEGER, CarrierPhase_f1 REAL, LLI_CP_f1 INTEGER, SSI_CP_f1 INTEGER, Doppler_f1 REAL, LLI_DP_f1 INTEGER, SSI_DP_f1 INTEGER, SNR_f1 REAL, LLI_SNR_f1 INTEGER, SSI_SNR_f1 INTEGER, Pseudorange_f2 REAL, LLI_PR_f2 INTEGER, SSI_PR_f2 INTEGER, CarrierPhase_f2 REAL, LLI_CP_f2 INTEGER, SSI_CP_f2 INTEGER, Doppler_f2 REAL, LLI_DP_f2 INTEGER, SSI_DP_f2 INTEGER, SNR_f2 REAL, LLI_SNR_f2 INTEGER, SSI_SNR_f2 INTEGER, Pseudorange_f3 REAL, LLI_PR_f3 INTEGER, SSI_PR_f3 INTEGER, CarrierPhase_f3 REAL, LLI_CP_f3 INTEGER, SSI_CP_f3 INTEGER, Doppler_f3 REAL, LLI_DP_f3 INTEGER, SSI_DP_f3 INTEGER, SNR_f3 REAL, LLI_SNR_f3 INTEGER, SSI_SNR_f3 INTEGER,   PRIMARY KEY (gpst, sat_id))".format(table_name))
    
    for i in tqdm(query):
        #print(i)
        #time.sleep(1)
        c.execute(i)

    dropTableStatement = "DROP TABLE IF EXISTS {}_decodifica".format(table_name)

    c.execute(dropTableStatement)

    c.execute("CREATE TABLE {}_decodifica (Constellation TEXT, Pseudorange_f1 TEXT, CarrierPhase_f1 TEXT, Doppler_f1 TEXT, SNR_f1 TEXT, Pseudorange_f2 TEXT, CarrierPhase_f2 TEXT, Doppler_f2 TEXT, SNR_f2 TEXT, Pseudorange_f3 TEXT, CarrierPhase_f3 TEXT, Doppler_f3 TEXT, SNR_f3 TEXT)".format(table_name))
    for j in query_decod:
            
            #time.sleep(1)
            c.execute(j)

    c.close()
    conn.commit()
    conn.close()



def main():
    path=os.path.dirname(os.path.realpath(__file__))
    directory ="{}/files/rinex/".format(path) #add your own path or if you want to test the script use ./Android_RINEX_data/
    rinex ="test_rinex_ridotto.19o" #put your own rinex file, or if you want to test the script put test_rinex_ridotto.19o
    database='{}/dati_GNSS'.format(path) #ATTENTION: DO NOT PUT THE DB IN A SAMBA FOLDER: otherwise it not gonna work
    tabella='test_rinex_ridotto'
    header, query_decod, query = readObsAndroid (directory,rinex,tabella)    
    #header, query = readObsRINEX_v3_03(directory, rinex,tabella)
    
    #print(type(header))

    writeDataToDB(database, tabella, query, query_decod)

if __name__=="__main__":
    main()