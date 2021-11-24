#!/usr/bin/env python
""" Plot RPM traces obtained during DIBH breast RT treatments 
Longer description!!

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__authors__ = ["Philippa Patterson", "Elena Vasina", "Joerg Lehmann"]
__contact__ = "philippa.patterson@newcastle.edu.au"
__copyright__ = "Copyright 2021, The Univeristy of Newcastle and Calvary Mater Newcastle"
__credits__ = ["Philippa Patterson", "Elena Vasina", "Joerg Lehmann"]
__date__ = "2021/11/24"
__deprecated__ = False
__email__ =  "philippa.patterson@newcastle.edu.au"
__license__ = "GPL"
__maintainer__ = "Philippa Patterson"
__status__ = "Prototype"
__version__ = "0.0.2"

#import required Python modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from tkinter.filedialog import askopenfilenames

#open file explorer and ask user to select input RPM files
file_list = askopenfilenames()

#iterate plotting procedure for all input RPM files
for i in file_list:
    #write status to command line
    sys.stdout.write('Reading RPM file %s \n' %i)
    sys.stdout.flush()
    
    #read RPM file and extract header information
    rpm_head = pd.read_csv(i,delimiter=';',nrows=9,header=None)
    crc = rpm_head.iloc[1,0]
    version = rpm_head.iloc[2,0]
    data_layout = rpm_head.iloc[3,0]
    patient_ID = rpm_head.iloc[4,0]
    date = rpm_head.iloc[5,0]
    tot_study_time = rpm_head.iloc[6,0]
    samp_per_sec = rpm_head.iloc[7,0]
    scale_fact = rpm_head.iloc[8,0]
    
    #read RPM file and extract data
    rpm_data = pd.read_csv(i,delimiter=',',skiprows=10,header=None)
    amplitude = np.array(rpm_data.iloc[:,0])
    phase = np.array(rpm_data.iloc[:,1])
    timestamp = np.array(rpm_data.iloc[:,2])
    validflag = np.array(rpm_data.iloc[:,3])
    ttlin = np.array(rpm_data.iloc[:,4])
    mark = np.array(rpm_data.iloc[:,5])
    ttlout = np.array(rpm_data.iloc[:,6])
    
    #write status to command line
    sys.stdout.write('Plotting RPM trace and beam on/off \n')
    sys.stdout.flush()
    
    #plot RPM trace and beam on/off for entire fraction
    plt.figure(figsize=(10,5));
    plt.plot(timestamp,np.abs(amplitude),color='teal',label='RPM trace') #plot absolute values of amplitude
    plt.fill(timestamp,ttlout*np.abs(amplitude),facecolor="lightblue",label='Beam ON') #scale binary beam on/off to corresponding RPM amplitude
    plt.ylim(np.min(np.abs(amplitude))); #centre y-axis on RPM trace
    plt.xlabel('Timestamp');
    plt.ylabel('Amplitude');
    plt.legend();
    plt.title('RPM trace %s' %i);
    plt.text(1,0.2,'\n'+crc+'\n \n'+version+'\n \n'+data_layout+'\n \n'+patient_ID+
             '\n \n'+date+'\n \n'+tot_study_time+'\n \n'+samp_per_sec+'\n \n'+
             scale_fact, transform=plt.gcf().transFigure); #include RPM file header next to trace
    plt.savefig('RPM_'+patient_ID[11:20]+'_'+date[5:15]+'.png',bbox_inches="tight")
    
    #calculate number of samples per second
    samples_per_sec = 25
    three_sec = samples_per_sec*3 #to plot 3 seconds either side of beam 
    
    #determine indexes where beam is turned on and off
    beamon_idxs = np.where(np.diff(ttlout) == 1)[0] #
    beamoff_idxs = np.where(np.diff(ttlout) == -1)[0] + 1 #+1 since last index in range not included
    
    #create empty arrays of beam on RPM data for future use
    beams_amplitude = []
    beams_timestamp = []
    
    #write status to command line
    sys.stdout.write('Plotting RPM trace for individual beams \n')
    sys.stdout.flush()
    
    #plot RPM trace for each individual beam
    if ttlout[-1] == 1: #if the beam is on when last RPM recording is taken
        beamoff_idxs = np.append(beamoff_idxs, ttlout.size-1) #add the index of last data point to array which holds indexes of when beam turns off
     
    if beamon_idxs.size == 1: #if the beam is only on once in the fraction
        fig, ax = plt.subplots(1, figsize=(10,5)) #set up figure
        beam_on = beamon_idxs[0] #index where beam is turned on
        beam_off = beamoff_idxs[0] #index where beam is turned off
        base_time = timestamp[beam_on] #set axis label so beam starts at time 0
        ax.scatter(timestamp[(beam_on-three_sec):(beam_off+three_sec)]-base_time, 
                   np.abs(amplitude[(beam_on-three_sec):(beam_off+three_sec)]),
                   s=50, color='teal', marker='.') #plot RPM data with three seconds either side of beam on/off
        ax.axvline(timestamp[beam_on]-base_time) #mark where beam turns on
        ax.axvline(timestamp[beam_off]-base_time) #mark where beam turns off
        ax.set_xlabel('Relative Timestamp')
        ax.set_ylabel('Amplitude')
        ax.text(0.85, 0.8, 'Beam 1', transform=ax.transAxes, fontsize = 16) #annotate beam number on plot
        plt.savefig('RPM_'+patient_ID[11:20]+'_'+date[5:15]+'_beamON.png')
        
    else: #if there are multiple beams in this data
        fig, axes = plt.subplots(beamon_idxs.size, figsize = (10,15)) #set up separate plots for each beam
        for n in range(axes.size): #iterate through each beam
            #fill arrays of beam on RPM data
            beams_amplitude.append(amplitude[beamon_idxs[n]:beamoff_idxs[n]])
            beams_timestamp.append(timestamp[beamon_idxs[n]:beamoff_idxs[n]])
            
            ax = np.ndarray.flatten(axes)[n] #set up axis for this figure
            beam_on = beamon_idxs[n] #indexes where beam is turned on
            beam_off = beamoff_idxs[n] #indexes where beam is turned off
            base_time = timestamp[beam_on] #set axis label so beam starts at time 0
            ax.scatter(timestamp[(beam_on-three_sec):(beam_off+three_sec)]-base_time, 
                       np.abs(amplitude[(beam_on-three_sec):(beam_off+three_sec)]),
                        s=50, color='teal', marker='.') #plot RPM data with three seconds either side of beam on/off
            ax.axvline(timestamp[beam_on]-base_time) #mark where beam turns on
            ax.axvline(timestamp[beam_off]-base_time) #mark where beam turns off
            ax.set_xlabel('Relative Timestamp')
            ax.set_ylabel('Amplitude')
            ax.text(0.85, 0.8, 'Beam '+str(n + 1), transform=ax.transAxes, fontsize=16) #annotate beam numbers on plots
            plt.savefig('RPM_'+patient_ID[11:20]+'_'+date[5:15]+'_beamON.png') 
    
    #create dataframe for RPM data for the entire fraction
    rpm_export_df = pd.DataFrame({'amplitude': amplitude,
                             'phase': phase,
                             'timestamp': timestamp,
                             'validflag': validflag,
                             'ttlin': ttlin,
                             'mark': mark,
                             'ttlout': ttlout})
     
    #write status to command line
    sys.stdout.write('Writing data and plots to excel \n')
    sys.stdout.flush()
    
    #write dataframes and plot images to excel
    writer = pd.ExcelWriter('RPM_'+patient_ID[11:20]+'_'+date[5:15]+'.xlsx', engine='xlsxwriter')
    rpm_export_df.to_excel(writer,index=False, sheet_name='Sheet1')
    worksheet1 = writer.sheets['Sheet1']
    worksheet1.insert_image('H2','RPM_'+patient_ID[11:20]+'_'+date[5:15]+'.png') 
    worksheet1.insert_image('H26','RPM_'+patient_ID[11:20]+'_'+date[5:15]+'_beamON.png')
    #save the excel
    writer.save()
    
#write status to command line
sys.stdout.write('All done! \n')
sys.stdout.flush()