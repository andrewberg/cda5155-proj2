""" andrew berg assignment 4 spring 2018 dr. whalley, python"""

import sys

class Config:

	def __init__(self, file_name):

		self.file_name = file_name

		self.read_config()
		self.print_config()

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

class Instructions:

	def __init__(self, config):
		self.data = list()
		self.config = config

		self.read_ins()

	def read_ins(self):
		for line in sys.stdin.readlines():
			value = line.strip().split()

			#print(value)

			if value[0] == "L.S" or value[0] == 'S.S':
				args = value[1].split(",")
				addr = args[1].split(":")[1]
				
				self.data.append(DataTransfer(value[0], 
					args[0], addr, line.strip()))
			elif value[0] == "LW" or value[0] == "SW":
				args = value[1].split(",")
				addr = args[1].split(":")[1]
				
				self.data.append(DataTransfer(value[0], 
					args[0], addr, line.strip()))
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

			elif (value[0] == "DADD" or
				value[0] == "DSUB"):
				ins = value[0]
				args = value[1].split(",")

				self.data.append(Arithmetic(ins, args[0],
					args[1], args[2], line.strip()))

			elif (value[0] == "BEQ" or
				value[0] == "BNE"):
				ins = value[0]
				args = value[1].split(",")

				self.data.append(Arithmetic(ins, args[0],
					args[1], args[2], line.strip()))
			
			#self.data.append(dum)

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

	def __str__(self):
		return ("%s %-04s %-05s #%-02s #%-02s #%-02s" % 
			(self.name, self.busy, self.op, self.qj, self.qk,
				self.dest))

class Stations:
	def __init__(self, config, status):
		self.stations = list()
		self.config = config
		self.status = status

		self.setup()

		#self.print_stations()

	def setup(self):

		for i in xrange(int(self.config.num_eff_addr)):
			self.stations.append(Station("effaddr" + str(i+1), "effaddr"))

		for i in xrange(int(self.config.num_fp_add)):
			self.stations.append(Station("fpadd  " + str(i+1), "fpadd"))

		for i in xrange(int(self.config.num_fp_mul)):
			self.stations.append(Station("fpmul  " + str(i+1), "fpmul"))

		for i in xrange(int(self.config.num_int)):
			self.stations.append(Station("int    " + str(i+1), "int"))

	def print_stations(self):
		print("\tReservation stations")
		print("--------------------------------")
		print("  Name   Busy  Op   Qj  Qk  Dest")
		print("-------- ---- ----- --- --- ----")

		for i in self.stations:
			print(i)

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
					#print(i.dest),
					#print(self.status.renames[int(i.dest)])
					return True

			x+=1
		return False

	def add_spot(self, ins, station):
		station.busy = "yes"

		# need to find if any of the registers are in register status already

	# returns True if spot is found, false if not

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

						#dest = self.status.find_spot(ins.arg2)

						#i.dest = dest

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



class RegisterStatus:
	def __init__(self):
		self.renames = list()

		for i in xrange(0, 50):
			self.renames.append(-1)

	def find_spot(self, reg):
		x = 0
		
		for i in self.renames:
			if i == -1:
				self.renames[x] = reg
				return x

			x+=1

	def remove_spot(self, reg):
		x=0

		for i in self.renames:
			if i == reg:
				self.renames[x] = -1
				break

			x+=1

	def check_in(self, reg):
		x=0

		for i in self.renames:
			if i == reg:
				return (x)
			x+=1

		return False

	def find_it(self, reg):

		for i in self.renames:
			print(i)

	def print_status(self):
		print("register status")
		print("---------------")

		x = 0

		for i in self.renames:
			if i != - 1:
				print(i+"=#"+str(x)),

			x+=1

		print("")

class ReorderEntry:

	def __init__(self, num):
		self.num = num
		self.busy = "no"
		self.ins = ""
		self.status = ""
		self.dest = ""
		self.cycles_left = -1
		self.obj = ""
		self.res = ""

	def __str__(self):
		return (("%5d %-04s %-021s %-011s %-011s"
			% (self.num, self.busy, self.ins, self.status, self.dest)))

class ReorderBuffer:

	def __init__(self, config):
		self.config = config
		self.entries = list()

		for i in xrange(int(self.config.num_reorder)):
			self.entries.append(ReorderEntry(i+1))

		#self.print_buffer()

	def print_buffer(self):
		print("                     Reorder buffer")
		print("--------------------------------------------------------")
		print("Entry Busy      Instruction         State    Destination")
		print("----- ---- --------------------- ----------- -----------")

		for i in self.entries:
			print(i)

	def is_open(self):
		for i in self.entries:
			if i.busy == "no":
				return True

		return False

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



class Pipeline:

	def __init__(self, ins, buff, stations, status):
		self.ins = ins
		self.buff = buff
		self.stations = stations
		self.status = status

		self.v = False

		self.write_queue = list()

		self.commit_queue = list()

		self.reset_list = list()

		self.read_queue = list()

		self.cycle = 1

		self.reservation_delays = 0
		self.reorder_delays = 0
		self.data_conflicts = 0
		self.true_dependence = 0

		self.do_tomasulo()

	def issue_instruction(self, ins, num):
		self.buff.add_open(ins, num)

	def check_commited(self):
		for i in self.buff.entries:
			if i.busy == "yes":
				return True

		return False

	def check_ready(self, ins):
		for i in self.buff.entries:
			# need to check everything but it self
			pass

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


	def finish_executing(self):
		for i in self.buff.entries:
			if i.status == "executing":
				if i.cycles_left == 0:
					i.status = "executed"

					i.obj.finish_executing = self.cycle

					if (i.obj.ins == "S.S" or i.obj.ins == "SW"
						or i.obj.ins == "BEQ" or i.obj.ins == "BNE"):
						self.commit_queue.append(i)
						#i.status = "committed"
						# need to setup so that on next cycle after being
						# executed it will reset the reservation station
					elif i.obj.ins == "L.S" or i.obj.ins == "LW":
						self.read_queue.append(i)
					else:
						self.write_queue.append(i)


					# this may not work correctly in some rare circumtances
					# TODO: fix that possibly?

	def read_stage(self):
		if len(self.read_queue) > 0:
			self.read_queue.sort(key= lambda x: x.obj.issues_at)
			val = self.read_queue.pop(0)
			val.status = "memread"
			val.obj.memory_read = self.cycle

			self.write_queue.append(val)

	def write_stage(self):
		if len(self.write_queue) > 0:
			self.write_queue.sort(key= lambda x: x.obj.issues_at)
			# get the destination register from the reservation station,
			# go through the whole reservation station table and rest
			# lines that have that in their qj and qk

			# TODO: NEED TO ONLY ALLOW ONE THING TO WRITE AT A TIME
			# AND IN ORDER

			val = self.write_queue.pop(0)

			val.status = "wroteresult"

			val.obj.writes_result = self.cycle

			dest = self.status.check_in(val.dest)

			self.reset_list.append(dest)

			station = self.stations.stations[val.res]

			station.reset()

			self.commit_queue.append(val)

	def commit_in_order(self, ins):
		# checks if any ins earlier has not committed yet
		# if it hasn't then wait
		# go through buffer and see if this is the earliest issued
		# if not then don't allow to commit

		# essentially needs to check if it is earliest ins issued currently
		# if not, then don't commit

		ins_issued = ins.obj.issues_at

		for i in self.buff.entries:
			if i.busy == "yes":	
				if i.obj.issues_at < ins.obj.issues_at:
					# need earliest to be in the first spot so sort based on issue
					# at time
					return False

		return True

			

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


	def do_tomasulo(self):


		stack = list(self.ins.data)

		first_ins = True

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

				#print(i.text)
			
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

		self.reo = reo
		self.res = res
		self.data = data
		self.true = true

		self.setup_header()

		self.print_results()

		self.print_delays()

	def setup_header(self):
		print("\n\n                    Pipeline Simulation")
		print("-----------------------------------------------------------")
		print("                                      Memory Writes")
		print("     Instruction      Issues Executes  Read  Result Commits")
		print("--------------------- ------ -------- ------ ------ -------")

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


	def print_delays(self):
		print("\n\nDelays")
		print("------")
		print("reorder buffer delays:"),
		print(self.reo)
		print("reservation station delays:"),
		print(self.res)
		print("data memory conflict delays:"),
		print(self.data)
		### TODO PROBABLY WHEN YOU CAN ONLY COMMIT ONE THING AT A TIME
		print("true dependence delays:"),
		print(self.true)


if __name__ == "__main__":
	
	config = Config("config.txt")

	status = RegisterStatus()

	ins = Instructions(config)

	res = Stations(config, status)

	buff = ReorderBuffer(config)

	pipe = Pipeline(ins, buff, res, status)

	results = PipelineResults(ins, pipe.reorder_delays, pipe.reservation_delays,
		pipe.data_conflicts, pipe.true_dependence)

	