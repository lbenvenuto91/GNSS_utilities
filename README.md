# GNSS_utilities
 Serie di script utili per trattare file in ambito GNSS
 
 ## ismr_reader.py
 
 file per leggere i file ascii ricavati dai dati binari dei ricevitori Septentrio.
 I riceivitori Septentrio generano dei file binari con estensione .yy_ Tramite un l'applicativo sbf2ismr è possibile convertire tali file binari in file ascii.
 Lo script ismr_reader.py legge in automatico quei file ascii e ne plotta le grandezzeche vi sono salvate all'interno.
  
 ## compact3_teqc.py
 
 Tramite il sw teqc è possibile fare analisi di qualità di dati GNSS a partire da file RINEX. 
 L'output di teqc però è verboso e non visivo. In particolare il comando teqc +qc +plot file_rinex genera una serie di file di testo in formato compact3.
 Lo script compact3_teqc.py legge e plotta in automatico i file di testo prodotti da teqc. I plot vengono fatti satellite per satellite
 
 ## compact3_residual.py
 
 Script che confronta fra loro due file prodotti da teqc [provenienti da ricevitori diversi].
 Nello script viene innanzitutto compiuta la differenza tra le due quantità assicurandosi che siano riferite allo stesso istante temporale.
 Opzionalmente si può sottrarre la media delle differenze ottenute e plottare la quantità risultante
