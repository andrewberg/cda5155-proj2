""" andrew berg assignment 4 spring 2018 dr. whalley, python"""
""" run with "python dynamic_schedule.py < inputfile" """
""" programmed on oldiablo.cs.fsu.edu which is python 2.4 """

import sys

"""class for storing config information"""

class Config:

    def __init__(self, file_name):

        self.file_name = file_name # instance variable for file_name

        self.read_config()
        self.print_config()

    # function to read the config values from the given input file_name
    # and store these

    def read_config(self):

        i = 0

        for line in open(self.file_name):

            if ":" not in line:
                continue

            value = line.strip().split(":")[1].strip()

            if i is 0:
                self.num_eff_addr = value
            elif i is 1:
                self.num_fp_add = value
            elif i is 2:
                self.num_fp_mul = value
            elif i is 3:
                self.num_int = value
            elif i is 4:
                self.num_reorder = value
            elif i is 5:
                self.len_fp_add = value
            elif i is 6:
                self.len_fp_sub = value
            elif i is 7:
                self.len_fp_mul = value
            elif i is 8:
                self.len_fp_div = value

            i += 1

    # function to print the config values

    def print_config(self):

        print("Configuration")
        print("-------------")

        print("buffers:")

        print('%12s' % ('eff addr:',)),
        print(self.num_eff_addr)

        print('%12s' % ('fp adds:',)),
        print(self.num_fp_add)

        print('%12s' % ('fp muls:',)),
        print(self.num_fp_mul)

        print('%12s' % ('ints:',)),
        print(self.num_int)

        print('%12s' % ('reorder:',)),
        print(self.num_reorder)

        print("\nlatencies:")

        print('%10s' % ('fp add:',)),
        print(self.len_fp_add)

        print('%10s' % ('fp sub:',)),
        print(self.len_fp_sub)

        print('%10s' % ('fp mul:',)),
        print(self.len_fp_mul)

        print('%10s' % ('fp div:',)),
        print(self.len_fp_div)

"""class for storing the instructions of the given input"""

class Instructions:

    def __init__(self, config):
        self.data = list()  # list to store the instructions
        self.config = config # stores the config instance for continual use

        self.read_ins()

    # reads each ins and stores it in the proper type of instruction object
    # for use later

    def read_ins(self):
        for line in sys.stdin.readlines():
            value = line.strip().split()

            # data transfers loads

            if value[0] == "L.S" or value[0] == 'S.S':
                args = value[1].split(",")
                addr = args[1].split(":")[1]
                
                self.data.append(DataTransfer(value[0], 
                    args[0], addr, line.strip()))

            # data transfers for non floating point

            elif value[0] == "LW" or value[0] == "SW":
                args = value[1].split(",")
                addr = args[1].split(":")[1]
                
                self.data.append(DataTransfer(value[0], 
                    args[0], addr, line.strip()))

            # arithmetic for the floating point values

            elif (value[0] == "ADD.S" or
                value[0] == "SUB.S" or
                value[0] == "MUL.S" or
                value[0] == "DIV.S"):

                ins = value[0]
                args = value[1].split(",")
                
                cost = 0

                if value[0] == "ADD.S":
                    cost = self.config.len_fp_add
                elif value[0] == "SUB.S":
                    cost = self.config.len_fp_sub
                elif value[0] == "MUL.S":
                    cost = self.config.len_fp_mul
                elif value[0] == "DIV.S":
                    cost = self.config.len_fp_div

                self.data.append(FloatingPoint(ins, args[0],
                 args[1], args[2], cost, line.strip()))

            # stores the regular arithmetic int objects

            elif (value[0] == "DADD" or
                value[0] == "DSUB"):
                ins = value[0]
                args = value[1].split(",")

                self.data.append(Arithmetic(ins, args[0],
                    args[1], args[2], line.strip()))

            # stores the branch instruction

            elif (value[0] == "BEQ" or
                value[0] == "BNE"):
                ins = value[0]
                args = value[1].split(",")

                self.data.append(Arithmetic(ins, args[0],
                    args[1], args[2], line.strip()))

"""class for datatransfer object storage with given information"""

class DataTransfer:

    def __init__(self, ins, dest, addr, text):
        self.ins = ins
        self.dest = dest
        self.addr = addr
        self.cost = 1
        self.text = text

        self.issues_at = 0

        self.start_executing = 0
        self.end_executing = 0

        self.writes_result = 0
        self.commits = 0

        self.memory_read = 0

"""class for arithmetic object storage with given information from the 
    ins class"""

class Arithmetic:

    def __init__(self, ins, dest, arg1, arg2, text):
        self.ins = ins
        self.dest = dest
        self.arg1 = arg1
        self.arg2 = arg2
        self.cost = 1
        self.text = text

        self.issues_at = 0

        self.start_executing = 0
        self.end_executing = 0

        self.writes_result = 0
        self.commits = 0

        self.memory_read = 0

"""class for FloatingPoint object storage with given information from the 
    ins class"""

class FloatingPoint:
    def __init__(self, ins, dest, arg1, arg2, cost, text):
        self.ins = ins
        self.dest = dest
        self.arg1 = arg1
        self.arg2 = arg2
        self.cost = int(cost)
        self.text = text

        self.issues_at = 0

        self.start_executing = 0
        self.end_executing = 0

        self.writes_result = 0
        self.commits = 0

        self.memory_read = 0

"""station class for use in the stations class"""

class Station:
    def __init__(self, name, t):
        self.type = t
        self.name = name
        self.busy = "no"
        self.op = ""
        self.qj = ""
        self.qk = ""
        self.dest = ""

    def reset(self):
        self.busy = "no"
        self.op = ""
        self.qj = ""
        self.qk = ""
        self.dest = ""

    """str class to convert to a string for printing the station"""

    def __str__(self):
        return ("%s %-04s %-05s #%-02s #%-02s #%-02s" % 
            (self.name, self.busy, self.op, self.qj, self.qk,
                self.dest))

# implementation of the reservation station

class Stations:
    def __init__(self, config, status):
        self.stations = list() # list of stations 
        self.config = config # instance variable for storing config instance
        self.status = status # register status variable storage

        self.setup()

    # setup the stations with the right amount of each type of station

    def setup(self):

        for i in xrange(int(self.config.num_eff_addr)):
            self.stations.append(Station("effaddr" + str(i+1), "effaddr"))

        for i in xrange(int(self.config.num_fp_add)):
            self.stations.append(Station("fpadd  " + str(i+1), "fpadd"))

        for i in xrange(int(self.config.num_fp_mul)):
            self.stations.append(Station("fpmul  " + str(i+1), "fpmul"))

        for i in xrange(int(self.config.num_int)):
            self.stations.append(Station("int    " + str(i+1), "int"))

    # print the reservation stations

    def print_stations(self):
        print("\tReservation stations")
        print("--------------------------------")
        print("  Name   Busy  Op   Qj  Qk  Dest")
        print("-------- ---- ----- --- --- ----")

        for i in self.stations:
            print(i)

    # check the columns to check for dependencies

    def check_oj(self, reg, num_reg):
        # check if depedent on any destinations
        # if depedent on any destinations return True
        # else return False

        # need to check to make sure it is not finding
        # itself for something to wait on

        x = 0

        for i in self.stations:
            if i.dest != '':
                if self.status.renames[int(i.dest)] == reg and x != num_reg:
                    return True

            x+=1

        return False

    # returns True if spot is found, false if not in the reservation station

    def find_spot(self, ins):
        for x in xrange(len(self.stations)):
            
            i = self.stations[x]

            # if DADD or DSUB look for int
            if ins.ins == "DSUB" or ins.ins == "DADD":
                if i.busy == "no":
                    if i.type == "int":
                        # spot is found and its not busy
                        # add it in

                        # have to rename the registers

                        # check the registers if they are in the reservation
                        # station, if they are then we need to write to qj and qk

                        # set to busy

                        i.busy = "yes"

                        # add in op

                        i.op = ins.ins

                        # rename dest

                        dest = self.status.find_spot(ins.dest)

                        i.dest = dest

                        # go through the stations and see if any dependencies
                        # that need to be added to qj qk


                        rs = ins.arg1

                        if self.check_oj(rs,x):
                            i.qj = self.status.check_in(rs)

                        rt = ins.arg2

                        if self.check_oj(rt,x):
                            i.qk = self.status.check_in(rt)


                        return True, x
            elif ins.ins == "ADD.S" or ins.ins == "SUB.S":
                if i.busy == "no":
                    if i.type == "fpadd":
                        # spot is found and its not busy
                        # add it in

                        # have to rename the registers

                        # check the registers if they are in the reservation
                        # station, if they are then we need to write to qj and qk

                        # set to busy

                        i.busy = "yes"

                        # add in op

                        i.op = ins.ins

                        # rename dest

                        dest = self.status.find_spot(ins.dest)

                        i.dest = dest

                        # go through the stations and see if any dependencies
                        # that need to be added to qj qk


                        rs = ins.arg1

                        if self.check_oj(rs,x):
                            i.qj = self.status.check_in(rs)

                        rt = ins.arg2

                        if self.check_oj(rt,x):
                            i.qk = self.status.check_in(rt)


                        return True, x

            elif ins.ins == "MUL.S" or ins.ins == "DIV.S":
                if i.busy == "no":
                    if i.type == "fpmul":
                        # spot is found and its not busy
                        # add it in

                        # have to rename the registers

                        # check the registers if they are in the reservation
                        # station, if they are then we need to write to qj and qk

                        # set to busy

                        i.busy = "yes"

                        # add in op

                        i.op = ins.ins

                        # rename dest

                        dest = self.status.find_spot(ins.dest)

                        i.dest = dest

                        # go through the stations and see if any dependencies
                        # that need to be added to qj qk


                        rs = ins.arg1

                        if self.check_oj(rs,x):
                            i.qj = self.status.check_in(rs)

                        rt = ins.arg2

                        if self.check_oj(rt,x):
                            i.qk = self.status.check_in(rt)


                        return True, x

            elif (ins.ins == "L.S" or ins.ins == "S.S" or 
                ins.ins == "SW" or ins.ins == "LW"):
                if i.busy == "no":
                    if i.type == "effaddr":
                        # spot is found and its not busy
                        # add it in

                        # have to rename the registers

                        # check the registers if they are in the reservation
                        # station, if they are then we need to write to qj and qk

                        # set to busy

                        i.busy = "yes"

                        # add in op

                        i.op = ins.ins

                        # rename dest

                        dest = self.status.find_spot(ins.dest)

                        i.dest = dest

                        # go through the stations and see if any dependencies
                        # that need to be added to qj qk

                        if self.check_oj(i.dest,x):
                            i.qk = self.status.check_in(i.dest)


                        return True, x
            elif ins.ins == "BEQ" or ins.ins == "BNE":
                if i.busy == "no":
                    if i.type == "int":
                        # spot is found and its not busy
                        # add it in

                        # have to rename the registers

                        # check the registers if they are in the reservation
                        # station, if they are then we need to write to qj and qk

                        # set to busy

                        i.busy = "yes"

                        # add in op

                        i.op = ins.ins

                        # rename dest

                        # go through the stations and see if any dependencies
                        # that need to be added to qj qk


                        rs = ins.dest

                        if self.check_oj(rs,x):
                            i.qj = self.status.check_in(rs)

                        rt = ins.arg1

                        if self.check_oj(rt,x):
                            i.qk = self.status.check_in(rt)



                        return True, x          


        return False, -1

"""class for storing the register renames for register status needs"""

class RegisterStatus:
    def __init__(self):
        self.renames = list() # storage container for the renames

        for i in xrange(0, 50):
            self.renames.append(-1)

    # finds a spot to rename a new register

    def find_spot(self, reg):
        x = 0
        
        for i in self.renames:
            if i == -1:
                self.renames[x] = reg
                return x

            x+=1

    # removes a given register from the register status

    def remove_spot(self, reg):
        x = 0

        for i in self.renames:
            if i == reg:
                self.renames[x] = -1
                break

            x+=1

    # check if a given register has been renamed

    def check_in(self, reg):
        x=0

        for i in self.renames:
            if i == reg:
                return (x)
            x+=1

        return False

    # prints the status of the register renames

    def print_status(self):
        print("register status")
        print("---------------")

        x = 0

        for i in self.renames:
            if i != - 1:
                print(i+"=#"+str(x)),

            x+=1

        print("")

"""utility class for the reorder buffer implementation"""

class ReorderEntry:

    def __init__(self, num):
        self.num = num # num of the reorder buffer
        self.busy = "no" #variable to check if it busy
        self.ins = "" # operation of the instruction
        self.status = "" # status for the reorder buffer display
        self.dest = "" # destination register buffer
        self.cycles_left = -1 # cycles_left for executing
        self.obj = "" # whole instruction object for printing
        self.res = "" # reservation station assigned to reorder buffer

    # string class for printing the string

    def __str__(self):
        return (("%5d %-04s %-021s %-011s %-011s"
            % (self.num, self.busy, self.ins, self.status, self.dest)))


"""implementation of the reorder buffer"""

class ReorderBuffer:

    def __init__(self, config):
        self.config = config # config instance for setting up proper amount
        self.entries = list() # container for storing the entries

        for i in xrange(int(self.config.num_reorder)):
            self.entries.append(ReorderEntry(i+1))

    # prints the buffer out for display

    def print_buffer(self):
        print("                     Reorder buffer")
        print("--------------------------------------------------------")
        print("Entry Busy      Instruction         State    Destination")
        print("----- ---- --------------------- ----------- -----------")

        for i in self.entries:
            print(i)

    # returns True if a spot is open but if spot is not open then returns False

    def is_open(self):
        for i in self.entries:
            if i.busy == "no":
                return True

        return False

    # setups the new spot for an issued instruction

    def add_open(self, ins, num):
        for i in self.entries:
            if i.busy == "no":
                i.busy = "yes"
                i.ins = ins.text
                i.status = "issued"
                if ins.ins != "BNE" and ins.ins != "BEQ":
                    i.dest = ins.dest
                i.cycles_left = ins.cost
                i.obj = ins
                i.res = num

                return True

        return False

"""implementation of the Tomasulo algorithm for dynamic scheduling"""

class Pipeline:

    def __init__(self, ins, buff, stations, status):
        self.ins = ins # instruction storage container
        self.buff = buff # reorder buffer for scheduling
        self.stations = stations # reservation stations
        self.status = status # register status renames

        self.v = False # DECIDES WHETHER SHOULD SHOW INFORMATION

        self.write_queue = list() # ensures only one thing is written at a time

        self.commit_queue = list() # for committing in order

        self.reset_list = list() # reset list for the load and store

        self.read_queue = list() # ensures only one thing is read at a time

        self.cycle = 1

        # all the delays

        self.reservation_delays = 0
        self.reorder_delays = 0
        self.data_conflicts = 0
        self.true_dependence = 0

        self.do_tomasulo()

    # issue instruction in reorder buffer if there is space

    def issue_instruction(self, ins, num):
        self.buff.add_open(ins, num)

    # check if everything is committed

    def check_commited(self):
        for i in self.buff.entries:
            if i.busy == "yes":
                return True

        return False

    # starts executing from the issued stage

    def start_executing(self):
        for i in self.buff.entries:
            if i.status == "issued":
                
                # check if it has any direct dependencies
                
                # check stations for rs or rt requiring something to finish
                # executing (i.e. qk or qj is one of the destinations)

                station = self.stations.stations[i.res]

                i.obj.start_executing = self.cycle

                if station.qj == "" and station.qk == "":
                    i.status = "executing"
                    i.cycles_left = i.cycles_left - 1
                else:
                    self.true_dependence += 1

    # changes from the finish executed from executing to executed

    def finish_executing(self):
        for i in self.buff.entries:
            if i.status == "executing":
                if i.cycles_left == 0:
                    i.status = "executed"

                    i.obj.finish_executing = self.cycle

                    if (i.obj.ins == "S.S" or i.obj.ins == "SW"
                        or i.obj.ins == "BEQ" or i.obj.ins == "BNE"):
                        self.commit_queue.append(i)
                    
                        # need to setup so that on next cycle after being
                        # executed it will reset the reservation station
                    
                    elif i.obj.ins == "L.S" or i.obj.ins == "LW":
                        self.read_queue.append(i)
                    else:
                        self.write_queue.append(i)

    # read stage of the pipeline

    def read_stage(self):
        if len(self.read_queue) > 0:
            self.read_queue.sort(key= lambda x: x.obj.issues_at)
            val = self.read_queue.pop(0)
            val.status = "memread"
            val.obj.memory_read = self.cycle

            self.write_queue.append(val)

    # get the destination register from the reservation station,
    # go through the whole reservation station table and rest
    # lines that have that in their qj and qk

    def write_stage(self):
        if len(self.write_queue) > 0:
            self.write_queue.sort(key= lambda x: x.obj.issues_at)
            # get the destination register from the reservation station,
            # go through the whole reservation station table and rest
            # lines that have that in their qj and qk

            val = self.write_queue.pop(0)

            val.status = "wroteresult"

            val.obj.writes_result = self.cycle

            dest = self.status.check_in(val.dest)

            self.reset_list.append(dest)

            station = self.stations.stations[val.res]

            station.reset()

            self.commit_queue.append(val)

    # checks if any ins earlier has not committed yet
    # if it hasn't then wait
    # go through buffer and see if this is the earliest issued
    # if not then don't allow to commit

    # essentially needs to check if it is earliest ins issued currently
    # if not, then don't commit

    def commit_in_order(self, ins):

        ins_issued = ins.obj.issues_at

        for i in self.buff.entries:
            if i.busy == "yes": 
                if i.obj.issues_at < ins.obj.issues_at:
                    # need earliest to be in the first spot so sort based on issue
                    # at time
                    return False

        return True

    # commit stage of the commit stage

    def commit_result(self):
        if len(self.commit_queue) > 0:
            self.commit_queue.sort(key= lambda x: x.obj.issues_at)
            if self.commit_in_order(self.commit_queue[0]):
                val = self.commit_queue.pop(0)

                val.status = "committed"

                val.busy = "no"

                val.obj.commits = self.cycle

                # moving removing of the destinations to the qj and qk to
                # wroteresult

                self.status.remove_spot(val.dest)

    def still_executing(self):
        for i in self.buff.entries:
            if i.status == "executing":
                i.cycles_left -= 1

    def resets_for_waiting(self):
        for dest in self.reset_list:
            for i in self.stations.stations:
                        if i.qj == dest:
                            i.qj = ""
                        if i.qk == dest:
                            i.qk = ""

    def reset_res_store(self):
        for i in self.buff.entries:
            if i.busy == "yes":
                if (i.obj.ins == "S.S" or i.obj.ins == "SW" or
                i.obj.ins == "BEQ" or i.obj.ins == "BNE"):
                    if i.status == "executed":
                        dest = self.status.check_in(i.dest)

                        station = self.stations.stations[i.res]

                        station.reset() 

    # do the actual pipeline

    def do_tomasulo(self):

        stack = list(self.ins.data)

        first_ins = True

        # allows for keep executing until done

        while self.check_commited() or first_ins:

            first_ins = False

            self.resets_for_waiting()

            self.reset_res_store()

            self.still_executing()

            # commits result to the CDB

            self.commit_result()

            # start wrote_resuult stage start

            self.write_stage()

            self.read_stage()

            # check issued if they can start executing
            # if issued can start executing and it takes one cycle to execute
            # change directly to executed else turn to executing

            self.start_executing()

            # check cyclces left and change executing to executed if 0

            self.finish_executing()

            if len(stack) > 0:
                i = stack[0]
            
                # issue if available spots

                if (self.buff.is_open()):
                    res, num = self.stations.find_spot(i)
                    if res:
                        # station is open
                        # buffer spot is open
                        # issue instruction

                        # once done executing remove from th

                        self.issue_instruction(i, num)
                        stack.pop(0)
                        i.issues_at = self.cycle
                    else:
                        self.reservation_delays += 1
                else:
                    self.reorder_delays += 1

            # if this set to True prints the data in every cycle

            if self.v:
                print("\nCycle: " + str(self.cycle))
                print("")
                self.stations.print_stations()
                print("")
                self.buff.print_buffer()
                print("")
                self.status.print_status()

            self.cycle+=1


class PipelineResults:

    def __init__(self, ins, reo, res, data, true):

        self.ins = ins

        self.reo = reo # number of reorder buffer delays
        self.res = res # number of reservation buffer delays
        self.data = data # number of data memory delays
        self.true = true # number of true dependence delays

        self.setup_header()

        self.print_results()

        self.print_delays()

    # setup header for printing results

    def setup_header(self):
        print("\n\n                    Pipeline Simulation")
        print("-----------------------------------------------------------")
        print("                                      Memory Writes")
        print("     Instruction      Issues Executes  Read  Result Commits")
        print("--------------------- ------ -------- ------ ------ -------")

    # print results of, self explanatory really

    def print_results(self):
        for i in ins.data:
            if i.ins == "L.S" or i.ins == "LW":
                print("%-021s %6s %03s -%03s %06s %06s %07s" % 
                    (i.text, 
                        i.issues_at, 
                        i.start_executing, 
                        i.finish_executing,
                        i.memory_read, 
                        i.writes_result, 
                        i.commits))
            
            elif (i.ins == "S.S" or i.ins == "SW" 
                or i.ins == "BNE" or i.ins == "BEQ"):
                    print("%-021s %6s %03s -%03s               %07s" % 
                    (i.text, 
                        i.issues_at, 
                        i.start_executing, 
                        i.finish_executing,
                        i.commits))
            else:
                print("%-021s %6s %03s -%03s        %06s %07s" % 
                    (i.text, 
                        i.issues_at, 
                        i.start_executing, 
                        i.finish_executing,
                        i.writes_result, 
                        i.commits))

    # prints the different delay statistics

    def print_delays(self):
        print("\n\nDelays")
        print("------")
        print("reorder buffer delays:"),
        print(self.reo)
        print("reservation station delays:"),
        print(self.res)
        print("data memory conflict delays:"),
        print(self.data)
        print("true dependence delays:"),
        print(self.true)


if __name__ == "__main__":
    
    config = Config("config.txt")

    status = RegisterStatus()

    ins = Instructions(config)

    res = Stations(config, status)

    buff = ReorderBuffer(config)

    pipe = Pipeline(ins, buff, res, status)

    results = PipelineResults(ins, pipe.reorder_delays, 
        pipe.reservation_delays,pipe.data_conflicts, pipe.true_dependence)
