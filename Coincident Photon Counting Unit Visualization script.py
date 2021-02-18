# Justin Smethers
# Purdue Fort Wayne Physics
# Advised by Dr. Mark Masters

import serial
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import random as rand
import csv
import pandas as pd


'''
-----------TODO-------------
Break plotData up into several functions
Break script up into several classes
Get the script to run 'sta' more than once without crashing
'''

'''
This script interacts with the PSoC device in Dr. Masters' lab as part of the Coincident Photon Counting Unit. 
It's designed to take the data output by the PSoC and graph it, calculate the number of accidental coincident photons, 
and save the data to a csv file. Currently the 'sta' function can only be ran once without restarting the script.

If two channels are selected (eg A, B, AB) the script displays the number of accidental coincident photons as 'Noise'

There must be at least one channel selected, as well as one coincident channel (eg A, AB)
'''


#
# save_data
# save_data outputs the data collected to a csv file
# @params - value_list - list containing the data values collected from the PSoC
#           channel_list - list of string names of channels used
# @returns - none
def save_data(value_list, channel_list):
    # Append a row for the number of data points collected
    value_list.append(['Count'])
    count = 1
    for i in range(len(value_list[0])):
        value_list[len(value_list)-1].append(count)
        count += 1
    # Combine channel list and value list
    for i in range(len(channel_list)):
        value_list[i].insert(0, channel_list[i])
    # Write the lists to a csv file
    with open('last_saved_run.csv', 'w') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        for row in value_list:
            writer.writerow(row)
    # Transpose the csv so the data are in columns instead of rows
    pd.read_csv('last_saved_run.csv', header=None).T.to_csv('last_saved_run.csv', header=False, index=False)
    # Print success message to console
    print('Successfully saved data')


#
# set_channels
# Allows the channels to choose which channels are plotted in plot_data
# @params: list - string names of channels
# @returns: individual_channel_list - list of string names of individual channels to be used
#           coincident_channel_list - list of string names of coincident channels to be used
def set_channels(name_list):
    name_list = name_list.split(',')
    individual_channel_list = []
    coincident_channel_list = []
    chn_cmnd_list = []
    for name in name_list:
        if name.upper() == 'A':
            individual_channel_list.append('Channel A')
            chn_cmnd_list.append("CHN1000\r\n")
        elif name.upper() == 'B':
            individual_channel_list.append('Channel B')
            chn_cmnd_list.append("CHN0100\r\n")
        elif name.upper() == 'C':
            individual_channel_list.append('Channel C')
            chn_cmnd_list.append("CHN0010\r\n")
        elif name.upper() == 'D':
            individual_channel_list.append('Channel D')
            chn_cmnd_list.append("CHN0001\r\n")

        elif name.upper() == 'AB':
            coincident_channel_list.append('Channel AB')
            chn_cmnd_list.append("CHN1100\r\n")
        elif name.upper() == 'AC':
            coincident_channel_list.append('Channel AC')
            chn_cmnd_list.append("CHN1010\r\n")
        elif name.upper() == 'AD':
            coincident_channel_list.append('Channel AD')
            chn_cmnd_list.append("CHN1001\r\n")
        elif name.upper() == 'BC':
            coincident_channel_list.append('Channel BC')
            chn_cmnd_list.append("CHN0110\r\n")
        elif name.upper() == 'BD':
            coincident_channel_list.append('Channel BD')
            chn_cmnd_list.append("CHN0101\r\n")
        elif name.upper() == 'CD':
            coincident_channel_list.append('Channel CD')
            chn_cmnd_list.append("CHN0011\r\n")

        elif name.upper() == 'ABC':
            coincident_channel_list.append('Channel ABC')
            chn_cmnd_list.append("CHN1110\r\n")
        elif name.upper() == 'ABD':
            coincident_channel_list.append('Channel ABD')
            chn_cmnd_list.append("CHN1101\r\n")
        elif name.upper() == 'BCD':
            coincident_channel_list.append('Channel BCD')
            chn_cmnd_list.append("CHN0111\r\n")

        elif name.upper() == 'ABCD':
            coincident_channel_list.append('Channel ABCD')
            chn_cmnd_list.append("CHN1111\r\n")

    print('Individual channel list:', individual_channel_list)
    print('Coincident channel list:', coincident_channel_list)
    for i in range(len(chn_cmnd_list)):
        ser.write(str("CTR" + str(i) + "\r\n").encode())
        ser.write(chn_cmnd_list[i].encode())

    output = ser.readline().decode()
    while output != "":
        output = ser.readline().decode()

    return individual_channel_list, coincident_channel_list


#
# build_figure
# builds the window and figure in which the data is plotted. Called by plot_data
# @params: none
# @returns: fig - pyplot figure
#           incident - subplot for detected single photons
#           coincident - subplot for detected coincident photons
def build_figure():
    # Turn on Pyplot interactive mode. Pyplot won't work within a thread without it
    plt.ion()

    # Create the figure window
    fig = plt.figure(1)
    fig.suptitle('Single photon detection', fontsize=24)
    # Create a plot with 3 rows and 2 columns of subplots
    gridspec.GridSpec(3, 2)

    # Create plot for incident photon detections
    incident = plt.subplot2grid((3, 2), (0, 0), colspan=1, rowspan=2)
    incident.set_xlabel('Measurement number', fontsize=18)
    incident.set_ylabel('Detected single photons', fontsize=18)
    incident.tick_params(labelsize=16)
    incident.set_xlim(0, 50)
    incident.set_ylim(20, 80)
    incident.grid()

    # Create plot for coincidences and noise
    coincident = plt.subplot2grid((3, 2), (0, 1), colspan=1, rowspan=2)
    coincident.set_xlabel('Measurement number', fontsize=18)
    coincident.set_ylabel('Detected coincident photons', fontsize=18)
    coincident.tick_params(labelsize=16)
    coincident.set_xlim(0, 50)
    coincident.set_ylim(20, 80)
    coincident.grid()

    # Create a subplot to display the current number of counts on each plot
    legend = plt.subplot2grid((3, 2), (2, 0), colspan=2, rowspan=1)
    legend.tick_params(axis='both', which='both', bottom=False, left=False, labelbottom=False, labelleft=False)
    legend.axis('off')

    return fig, incident, coincident


#
# plot_data
# Function to plot the data until the stop command interrupt it. Target of the thread function. This function is a monster
# God help those who try to comprehend what's going on in it.
# @params: individual_channel_list / coincident_channel_list - lists containing string names of the channels to be used
# @returns: none
def plot_data(individual_channel_list, coincident_channel_list):
    # Print start message to the console
    print('starting plot data')

    # Send commands to the PSoC to turn of echo and execute the start function
    ser.write("ECO 0\r\n".encode())
    output = ser.readline().decode()
    while output != "":
        output = ser.readline().decode()
    # Write the start command to the data collection device
    ser.write("STA\r\n".encode())
    # Get the output from the data collection device
    output = ser.readline().decode()

    # Initialize variables to be used in plotting
    count = 1                 # Each data point is a single count
    plt_window_size = 50      # Choose the max number of points per plot with pltWindowSize
    count_list = [count]
    value_list = []
    complete_value_list = []
    color_list = ['r-', 'b-', 'g-', 'c-', 'y-', 'b-']

    # Call the build_figure function
    fig, incident, coincident = build_figure()

    # Initialize the plot of each of the selected channels
    for i in range(len(individual_channel_list)):
        value_list.append([1])
        complete_value_list.append([1])
        incident.plot(count_list, value_list[i], color_list[i], label=individual_channel_list[i], lw=2)
    for i in range(len(coincident_channel_list)):
        value_list.append([1])
        complete_value_list.append([1])
        coincident.plot(count_list, value_list[len(individual_channel_list)], color_list[i], label=coincident_channel_list[i], lw=2)

    # Add a noise plot if there's only one coincident photon channel
    if len(coincident_channel_list) == 1:
        coincident_channel_list += ['Noise']
        value_list.append([1])
        complete_value_list.append([1])
        coincident.plot(count_list, value_list[len(individual_channel_list)], color_list[1], label='Noise', lw=2)

    # Create legends for the plots
    incident.legend(loc=1, bbox_to_anchor=(.4, -.175), fontsize=15)
    coincident.legend(loc=1, bbox_to_anchor=(.45, -.185), fontsize=15)
    incident_caption = incident.text(0, -.65, '', transform=incident.transAxes, fontsize=15, bbox={'facecolor': 'white'}, style='oblique')
    coincident_caption = coincident.text(0, -.65, '', transform=coincident.transAxes, fontsize=15, bbox={'facecolor': 'white'}, style='oblique')

    # Continuously plot until the data collection device isn't outputting data (i.e. when the PSoC executes the stop command)
    while True:
        try:
            output_index = 0     # index of the list from output
            # Iterate through the values given by the data collection device
            for val in str(output).strip().split(', '):
                # Check if the value is zero, so that unused channels on the data collection device aren't plotted
                if val != 0 and output_index < len(individual_channel_list) + len(coincident_channel_list):
                        # If the desired window size has been reached
                        if count > plt_window_size:
                            # Remove the first value from each list
                            if output_index == 0:
                                count_list.pop(0)
                            value_list[output_index].pop(0)
                            incident.set_xlim(count - plt_window_size, count + 1)
                            coincident.set_xlim(count - plt_window_size, count + 1)

                            # Move caption
                            incident_caption.set_visible(False)
                            coincident_caption.set_visible(False)
                            incident_caption = incident.text(0, -.65, '', transform=incident.transAxes, fontsize=15, bbox={'facecolor': 'white'}, style='oblique')
                            coincident_caption = coincident.text(0, -.65, '', transform=coincident.transAxes, fontsize=15, bbox={'facecolor': 'white'}, style='oblique')

                        # Append the data from the data collection device to value_list
                        if coincident_channel_list[1] == 'Noise':
                            if output_index == len(individual_channel_list) + len(coincident_channel_list) - 1:
                                pulse_width = 1*10**-9
                                r1 = value_list[0][len(value_list[output_index]) - 1] * pulse_width
                                r2 = value_list[1][len(value_list[output_index]) - 1] * 2
                                noise_value = int(r1 * r2)
                                value_list[output_index].append(noise_value)
                                complete_value_list[output_index].append(noise_value)
                            else:
                                value_list[output_index].append(int(val))
                                complete_value_list[output_index].append(int(val))
                        else:
                            value_list[output_index].append(int(val))
                            complete_value_list[output_index].append(int(val))

                        # Update the incidents graph y-limit according to the max and min data values in the list
                        max_list = []
                        for i in range(len(individual_channel_list)):
                            max_list.append(max(value_list[i]))
                        incident.set_ylim(-((max(max_list) + 3000) * (1 / 60)), max(max_list) + 3000)
                        # Update the co-incidents graph y-limit
                        max_list = []
                        for i in range(len(coincident_channel_list)):
                            max_list.append(max(value_list[len(individual_channel_list) + i]))
                        coincident.set_ylim(-((max(max_list) + 30) * (1 / 60)), max(max_list) + 30)

                        # Increment output_index so the index of value_list increases
                        output_index += 1

            # Update the plot data
            for i in range(len(individual_channel_list)):
                incident.get_lines()[i].set_data(count_list, value_list[i])
            for i in range(len(coincident_channel_list)):
                coincident.get_lines()[i].set_data(count_list, value_list[len(individual_channel_list) + i])

            # Update the incident figure caption with current data
            caption_text = ''
            for i in range(len(individual_channel_list)):
                if i != 0:
                    caption_text += '\n'
                caption_text += individual_channel_list[i] + ': ' + str(value_list[i][len(value_list[i]) - 1])
            incident_caption.set_text(caption_text)
            # Update the coincident figure caption with current data
            caption_text = ''
            for i in range(len(coincident_channel_list)):
                if i != 0:
                    caption_text += '\n'
                caption_text += coincident_channel_list[i] + ': ' + str(value_list[len(individual_channel_list) + i][len(value_list[len(individual_channel_list) + i]) - 1])
            coincident_caption.set_text(caption_text)

            # Increment count and add the count to the list
            count += 1
            count_list.append(count)
            # Update the figure with the new data
            fig.canvas.draw()
            fig.canvas.flush_events()
            # Update output with the next line of data from the data collection device
            output = ser.readline().decode()

        except:
            save_data(complete_value_list, individual_channel_list + coincident_channel_list)
            break


# Open serial port for reading/writing
ser = serial.Serial()
ser.port = "/dev/ttyACM0"
ser.timeout = 1
ser.open()

# Print help menu and turn echo on
ser.write("ECO 1\r\n".encode())
output = ser.readline().decode()
while output != "":
    output = ser.readline().decode()

# Wait for user input - for use in outputting multiple commands to the control device
print("\nType 'sta' to start plotting")
print("Type 'hlp' for list of commands")
entry = input("\nEnter command, or q to quit: ")

while entry != "q":
    # Code to run if user inputs "sta" to start
    if entry.upper().startswith("STA"):
        print('\n------------------------------------------------------------------------------------------')
        print('WARNING: file "last_saved_run.csv" will be overwritten unless it has been moved or renamed')
        print('------------------------------------------------------------------------------------------\n')
        # Create a flag to kill plot_data thread when the stop command is entered
        stop_thread = False

        # Allow user to enter channels to collect data from
        chosen_channels = input('Enter channels to be used: (eg \'A,B,C,ABC\')\n')
        individual_channel_list, coincident_channel_list = set_channels(chosen_channels)

        # Create a new thread. Runs the plot_data function until stop command is entered
        thread1 = threading.Thread(target=plot_data, args=(individual_channel_list, coincident_channel_list))
        thread1.start()
        while True:
            # Main thread waits in this loop
            print('\nType STP to exit')
            entry = input()
            if entry.upper() == "STP":
                print('\n')
                # Wait for plot_data function to terminate and kill the thread
                ser.write('STP\r\n'.encode())
                print('Killing thread...')
                time.sleep(3)
                lag_counter = 0
                is_lagging = False
                output = ser.readline().decode()
                while output != "":
                    print(output)
                    lag_counter += 1
                    output = ser.readline().decode()
                
                if lag_counter >= 5:
                    is_lagging = True
                if is_lagging:
                    print('\n---------------------------------------------------------------------------------')
                    print("WARNING the graph was more than 5 points behind. The graph / program was lagging")
                    print('---------------------------------------------------------------------------------\n')
                    
                stop_thread = True
                if thread1.is_alive():
                    print('Failed to kill thread')
                else:
                    print('Successfully killed thread')
                # Clear the figure, close it, and turn off Pyplot interactive mode
                #plt.clf()
                #plt.close()
                plt.ioff()
                break
    elif entry.upper().startswith("HLP"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("SCN"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("CHN"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("CTR"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("LSC"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("LVL"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("DAC"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("COL"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("WIN"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("ECO"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("MAXDV"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    elif entry.upper().startswith("MINDV"):
        ser.write((entry + '\r\n').encode())
        output = ser.readline().decode()
        while output != "":
            print(output)
            output = ser.readline().decode()
    else:
        print("Invalid command in this context")

    entry = input("\nEnter command, or q to quit: ")
print("Quitting...")
