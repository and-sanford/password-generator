#!/usr/bin/env python
from datetime import datetime
from time import sleep
import os.path
import psutil
import random
import csv
import sys
import os

'''
This program creates a pseudorandom password, based on current:

* Time (microseconds)
* Memory usage (bytes)
* Virtual memory swap stats
* CPU stats
* DISK stats
* Battery level


This password generator is created for educational purposes and should not be used in real-world environments.
I recommend using an actual, secure password manager (e.g., LastPass, 1Password) or another proven app.

You are free to share, use, adapt, etc. this file in any way.

--- Future Plans ---
* Allow user to specify password length
* Add non-numeric characters to password
* Use this as a seed generator for encrypting files (e.g., AES) - for personal use, not real-world environments

Copyright (c) Andrew Sanford 2018.
'''

########################
### START OF PROGRAM ###
########################

'''
-------------------------------------------------------------------------
--- OBTAIN PSUEORANDOM NUMBERS BASED ON COMPUTER'S CURRENT PROPERTIES ---
-------------------------------------------------------------------------
'''
psuedo_numbers = []

now = datetime.now()
MICROSECONDS = now.microsecond
psuedo_numbers.append(MICROSECONDS)

process = psutil.Process(os.getpid())
MEMORY_USAGE = process.memory_info().rss
psuedo_numbers.append(MEMORY_USAGE)

mem = psutil.swap_memory()
VIRTUAL_MEMORY_USAGE =  mem.total
VIRTUAL_MEMORY_PERCENT = int(round(mem.percent))
psuedo_numbers.extend((VIRTUAL_MEMORY_USAGE, VIRTUAL_MEMORY_PERCENT))

cpu = psutil.cpu_stats()
CPU_INTERRUPTS = cpu.interrupts
CPU_SOFT_INTERRUPTS = cpu.soft_interrupts
CPU_CTX_SWITCHES = cpu.ctx_switches
CPU_SYSCALLS = cpu.syscalls
psuedo_numbers.extend((CPU_INTERRUPTS, CPU_SOFT_INTERRUPTS, CPU_CTX_SWITCHES, CPU_SYSCALLS))

disk = psutil.disk_usage('/')
DISK_TOTAL = disk.total
DISK_USAGE = disk.used
DISK_FREE = disk.free
DISK_USAGE = int(round(disk.percent,0))
psuedo_numbers.extend((DISK_TOTAL, DISK_USAGE, DISK_FREE, DISK_USAGE))

battery = psutil.sensors_battery()
CHARGE_PERCENT = battery.percent
psuedo_numbers.append(CHARGE_PERCENT)

###############################
### END OF GLOBAL VARIABLES ###
###############################


'''
--------------------------
--- START OF FUNCTIONS ---
--------------------------


Ensure no numbers == 0
If a number < 1:
    Replace with pseudorandom int
'''
def check_numbers(list1):
    for position, value in enumerate(list1):
        if value < 1:
            print position, " | ", list1[position]
            list1[position] = random.randint(1,10000000000000000)
    return list1
    

'''
Performing some math to create passwords of various lengths and compositions.   
'''
def math_on_self(psrn):
    # get rid random number of digits at the end && multiply by itself
    str_psrn = str(psrn)
    str_psrn = str_psrn[:-random.randint(1,random.randint(2,30))]
    
    firstpart, secondpart = str_psrn[:len(str_psrn)/2], str_psrn[len(str_psrn)/2:]
    int_firstpart = int(firstpart)
    int_secondpart = int(secondpart)
    
    rand_num = random.randint(0,4)
    if rand_num == 0:
        psrn = int_firstpart * int_secondpart
        
    elif rand_num == 1:
        psrn = int_firstpart ^ int_secondpart
        
    elif rand_num == 2:
        psrn *= int_firstpart % int_secondpart
       
    elif rand_num == 3:
        psrn *= (int_firstpart * int_secondpart)
        
    elif rand_num == 4:
        psrn = (psrn % int_firstpart) * psrn^(psrn % int_secondpart)
                 
    else:
        pass
    
    return psrn


'''
Pseudorandom number generator (prng)
'''
def prng(list1):
    # psrn = pseudorandom number
    
    # 1. Find largest value in list
    temp_list = list1
    largest = max(temp_list)
    temp_list.remove(largest)
    
    # 2. Get second largest value in list
    # different way to do this, kind of cool: 
    # temp_list = [value for value in list1 if value != largest]
    second_largest = max(temp_list)
    temp_list.remove(second_largest)
    
    #3. Multiply two largest numbers by a third, psrn
    psrn = largest * second_largest * random.randint(1, 100000000000000000000000000000000000000000000000000000000000000000000000000)
    
    ''' 4. Let's have some math fun :) '''
    # multiply psrn by each item
    for item in list1:
        psrn *= item
    
    for item in temp_list:
        psrn *= item
    
    # do some moduular arithmetic 
    temp_list2 = [CPU_SOFT_INTERRUPTS, MICROSECONDS]
    temp_list2 = check_numbers(temp_list2)
    
    mod_number = temp_list2[0] % temp_list2[1]
    psrn *= mod_number^(psrn % temp_list2[0]) #this results in numbers ending in several 0s

    # multiply by parts of itself
    for _ in range(random.randint(1,random.randint(1,10))):
        psrn = math_on_self(psrn)
    
    # mod the number again
    mod_num = psrn % random.randint(1,100000000000)
    psrn = psrn^mod_num
    for item in list1:
        psrn *= item
    
    # mod the number again
    mod_num = (psrn % random.randint(1,100000000000))
    psrn *= mod_num
    
    # ensure there are no 0s at the end
    for item in temp_list:
        psrn += item

    # multiply by parts of itself several times
    for _ in range(random.randint(1,random.randint(1,10))):
        psrn = math_on_self(psrn)               
        
    # multiply by some of the pseudorandom numbers
    psrn = psrn * CPU_INTERRUPTS * CHARGE_PERCENT * MICROSECONDS * CPU_SOFT_INTERRUPTS
        
    # get psrn length
    psrn_length = len(str(psrn))
    
    # return psrn and length 
    return psrn, psrn_length


'''
Generate a pseudorandom number (psrn)
'''
def generate_psrn():
    number_list = check_numbers(psuedo_numbers)
    # psrn = pseudo-random number
    psrn, psrn_length = prng(number_list)
    
    return psrn, psrn_length
    

'''
Write to CSV file (for analysis)
'''
def add_to_csv(psrn, psrn_length):
    input_info = str(psrn_length) + ", " + str(psrn)
    file_to_edit = "analyze-pw-generator.csv"
    # first, check if CSV file exists
    #  if not, add to CSV
    if os.path.isfile("analyze-pw-generator.csv") is False:
        with open('analyze-pw-generator.csv', 'wb') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['Length', 'PSRN'])

    with open('analyze-pw-generator.csv','a') as newFile:
        newFileWriter = csv.writer(newFile)
        newFileWriter.writerow([psrn_length,psrn])


'''
Prints slowly on one line.
Utilized to print dots '. . .'
'''
def print_slowly(text, i):
    for _ in range(i):
        print text,
        sys.stdout.flush()
        sleep(1)

########################
### END OF FUNCTIONS ###
########################   
    

'''
-----------------------
----- MAIN PROGRAM ----  
-----------------------  
'''
psrn, psrn_length = generate_psrn()

print 'Generating password',
print_slowly('.', 5)
print "\n--- PSRN --- \n", psrn
print "\n--- PSRN Length --- \n", psrn_length, "characters"

add_to_csv(psrn, psrn_length)
print "\nAdded password & password length to a CSV file ('analyze-pw-generator.csv')"
print "*We advise against using this password in real-world scenarios*\n"
print "(c) Andrew Sanford 2018\n"