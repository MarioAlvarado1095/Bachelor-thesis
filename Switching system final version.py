import seabreeze.spectrometers as sb
import numpy as np
import datetime
import matplotlib.pyplot as plt
import serial
import time



#This program consist in the union of the program that takes quick photos of the spectrometer with a program that inlights the sample with a monocromator.
#This program is meant to be used to Take spectroscopy measurements of a sample that can be photoswitched via a monocromator and take diferent transmition (and then absoption) spectrums

#Variables of the monocromator (Switching light parameters)
Initial_Wave_Lenght_Monocromator = 600
Final_Wave_Length_Monocromator = 600
Space_betweetn_Wave_Lenghts = 10
Monocromator_Wating_Time = 5  #Change this time in order to inlight the sample with shorter of longer periods of time *(Time is in seconds)
Factor_of_exponential_growth=2
Number_of_iterations=11


Return_Wave_Lenght_Switch = False #Set here "True" if you want to activate the return wavelength value or "False" if you want it inactive *(it makes that begore the proces of switching to a wavelength is starts, you start in an specific state acording to the value you choose here)
Return_Wave_Lenght = 365  #This is the value of the return wave lenght in nm
Return_Wave_Lenght_time=250


#Variables of the spectrometer
integration_time_micros = 14000 #Change this parameter to set the integration time in the spectrometer
Num_Photos_spectrometer = 10 # Select the number of meassurements needed in a round of the spectrometer. (this can be used for time averaging at the cost that the sample will be inlight longer by the dueterium lamp)




#this imports the comands of the monocromator
from monocromador import Monocromador
mono = Monocromador("COM6") #You can find this in the device maneger from windows

#This is the last parameter that is most likely you will need to modified in the code unless you really want to modify the program functions
arduino_port = "COM4"  #This is the port of your PC in which the arduino is conected. Once set for your PC is likely that it will not requiere any changes in the future (you can also find this in the device manager in windows)







#this part just tell the program if it has to go up or down in the change of wavelengths
Up_or_down_parameter=Final_Wave_Length_Monocromator-Initial_Wave_Lenght_Monocromator
if Up_or_down_parameter > 0:
    Final_Wave_Length_Monocromator+=1
    Space_betweetn_Wave_Lenghts=abs(Space_betweetn_Wave_Lenghts)
elif Up_or_down_parameter < 0:
    Final_Wave_Length_Monocromator-=1
    Space_betweetn_Wave_Lenghts=-abs(Space_betweetn_Wave_Lenghts)
else:
    Final_Wave_Length_Monocromator+=1
    Space_betweetn_Wave_Lenghts=abs(Space_betweetn_Wave_Lenghts)


#We do here a conditional that scans different values of the wavelenght output from the monocromator. Basically this will take a the values of wavelenght you put in the parameter before and will scantrough them untill it reaches the closer number to the final wave lenght uotput+1
for wavelength_mono in range(Initial_Wave_Lenght_Monocromator, Final_Wave_Length_Monocromator, Space_betweetn_Wave_Lenghts):
    
    
    if Return_Wave_Lenght_Switch:
       #This part takes thw wished wave lengt and send it to the monocromator via a ASCII message
        mono.store_wavelength(Return_Wave_Lenght)
        wavelength = mono.get_wavelength()
        time.sleep(4) #The monocromator takes time to change the wave lenght to the next value, this wating time is just so that the shutter does not open in a different wavelenght that the one we spected (this time can be shorter, but better to be safe than to be sorry)
        mono.set_shutter(True) #opens the monocromator shutter.
        time.sleep(Return_Wave_Lenght_time) #Here is the program just wating the time you have at the beginning of the program.
        mono.set_shutter(False) # Closes the monocromator shutter so that it does not appear in the spectrometer spectrum.
        
        # Here ends one ciclus of the process of the monocromator. The following part is just to take the "photos" of the spectra.     
        
        
        # Makes python talk with the arduino (don't touch it)
        ser = serial.Serial(arduino_port, 9600, timeout=1)
        # Wait for the Arduino to initialize *(This time is in seconds and has to be consider for the data analisys, in case it afects. basically, after the program starts, it takes about 2 seconds to start measuring. This time helps to sincronice everthing)
        time.sleep(2)
        # turn on the lamp via arduino
        ser.write(b'H')  # Turns the light on


        #Now here starts the part of the spectrometer
        #This comand looks for the spectrometer
        devices = sb.list_devices()

        spectrometer = sb.Spectrometer(devices[0])

        # This is to set the integration time in the monocromator (in microseconds) (also recomend to see first in the original program what the values below saturation are)
        
        spectrometer.integration_time_micros(integration_time_micros)

        
        #waiting time to compleatly open the deuterium lamp
        time.sleep(0.02)

        # Acumulates the measurements
        all_wavelengths = spectrometer.wavelengths()  # WL are the same for every meassurement of intensity (don't touch this)
        all_spectra = []

        for i in range(Num_Photos_spectrometer):
            spectrum = spectrometer.intensities()

            # Puts values in diferent colums 
            all_spectra.append(spectrum)

        # Puts the data in a CSV (Excel like programs)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"espectrum_{timestamp} Wavelenght {Return_Wave_Lenght} nm {Return_Wave_Lenght_time} sec.csv"

        # Saves the data in the CSV in colums
        np.savetxt(output_file, np.column_stack((all_wavelengths, np.column_stack(all_spectra))),
                delimiter=',', header='Wave Lenght,' + ','.join([f'Intensity_Measure{i+1} Wave_Lenght{wavelength_mono}' for i in range(Num_Photos_spectrometer)]), comments='')

        print(f"Data of {Num_Photos_spectrometer} Measurements were saved in {output_file}")
        
        #turn off the lamp via arduino
        ser.write(b'L')

        # Close the serial connection and the spectrometer 
        ser.close()
        spectrometer.close()
       
    




    #switching light
    mono.store_wavelength(wavelength_mono)
    wavelength = mono.get_wavelength()
    time.sleep(4) #The monocromator takes time to change the wave lenght to the next value, this wating time is just so that the shutter does not open in a different wavelenght which are not the one we spected (this time can be shorter, but better to be safe than to be sorry)
    
    
    current_time_value = Monocromator_Wating_Time #This is for calculating how long the monocromator slith will be open 
    total_time=Monocromator_Wating_Time #This is just for saving documents purpose
    for Iteration_number in range(Number_of_iterations+1):
        mono.set_shutter(True) #opens the monocromator shutter.
        if Iteration_number==0:
         time.sleep(current_time_value) #Here is the program just wating the time you have at the beginning of the program.
        else:
            time.sleep(current_time_value-total_time/Factor_of_exponential_growth)
        mono.set_shutter(False) # Closes the monocromator shutter so that it does not appear in the spectrometer spectrum.
        
        # Here ends one ciclus of the process of the monocromator. The following part is just to take the "photos" of the spectra.     
        
        
        # Makes python talk with the arduino (don't touch it)
        ser = serial.Serial(arduino_port, 9600, timeout=1)
        # Wait for the Arduino to initialize *(This time is in seconds and has to be consider for the data analisys, in case it afects. basically, after the program starts, it takes about 2 seconds to start measuring. This time helps to sincronice everthing)
        time.sleep(2)
        # turn on the lamp via arduino
        ser.write(b'H')  # Turns the light on


        #Now here starts the part of the spectrometer
        #This comand looks for the spectrometer
        devices = sb.list_devices()

    
        spectrometer = sb.Spectrometer(devices[0])

        # This is to set the integration time in the monocromator (in microseconds) (also recomend to see first in the original program what the values below saturation are)
        
        spectrometer.integration_time_micros(integration_time_micros)

        
        #waiting time to compleatly open the deuterium lamp
        time.sleep(0.02)

        # Acumulates the measurements
        all_wavelengths = spectrometer.wavelengths()  # WL are the same for every meassurement of intensity (don't touch this)
        all_spectra = []

        for i in range(Num_Photos_spectrometer):
            spectrum = spectrometer.intensities()

            # Puts values in diferent colums 
            all_spectra.append(spectrum)

        # Puts the data in a CSV (Excel like programs)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"espectrum_{timestamp} Wavelenght {wavelength_mono}nm {total_time} sec.csv"

        # Saves the data in the CSV in colums
        np.savetxt(output_file, np.column_stack((all_wavelengths, np.column_stack(all_spectra))),
                delimiter=',', header='Wave Lenght,' + ','.join([f'Intensity_Measure{i+1} Wave_Lenght{wavelength_mono}' for i in range(Num_Photos_spectrometer)]), comments='')

        print(f"Data of {Num_Photos_spectrometer} Measurements were saved in {output_file}")
        
        #turn off the lamp via arduino
        ser.write(b'L')

        # Close the serial connection and the spectrometer 
        ser.close()
        spectrometer.close()


        #modifies the values for the new iteration
        current_time_value *=Factor_of_exponential_growth
        total_time *=Factor_of_exponential_growth
        





