'''
By: Amanda Trinh
CS 143B Winter 2019 - Project 1
Processes and Resource Management
Written in Python 3.6

When running using a new test file, please change the variable path
and input_file in the main method to the correct path/filename
'''


Running_Process = None  # will be a PCB
RL = None  # will be the ReadyList
preempt = None  # determines what will be outputted after error
All_PIDs = set() # set of all PID names
R1 = None
R2 = None
R3 = None
R4 = None


# Process Control Block
class PCB:
    def __init__(self, name, priority, parent):
        self.PID = name  # process name
        self.Priority = priority  # 0, 1, or 2 (Init, User, System)
        # Creation Tree
        self.Parent = parent  # will use the parent's PID name
        self.Children = []  # if the process has created any PCBs, linked list of each child's name

    def addChild(self, pid):
        # only callable from current running process & when instructed "cr"
        # adds the PID string name to Children
        self.Children.append(pid)


class ReadyList:
    def __init__(self, root_process):
        # root_process is the init
        self.System = []  # priority 2, highest
        self.User = []  # priority 1
        self.Init = [root_process]  # priority 0, root & should only ever have ONE process (the init)


class RCB:
    def __init__(self, rid, counter):
        self.RID = rid  # either R1, R2, R3 or R4
        self.Status_units = counter  # number of free units
        self.WaitingList = []  # list of blocked PCBs, hold tuples (PCB, units needed)
        # processes that tried to request some # of units but failed since the number of free units was not enough
        self.max_units = counter  # initial resource available
        self.Other_resources = []  # linked list, each PID = 1 unit is result of a successful request






def create(name, priority):
    new_process = PCB(name, priority, Running_Process.PID)
    All_PIDs.add(name) # add PID name to list of PID names in RL
    if priority == 2:
        RL.System.append(new_process)
    elif priority == 1:
        RL.User.append(new_process)
    # find the running process in RL (should definitely be there)
    # and add the new process's PID string name to running process's children list
    if RL.System:
        for process in RL.System:
            if process.PID == Running_Process.PID:
                process.addChild(name)
    if RL.User:
        for process in RL.User:
            if process.PID == Running_Process.PID:
                process.addChild(name)
    if RL.Init:
        for process in RL.Init:
            if process.PID == Running_Process.PID:
                process.addChild(name)
    scheduler()


def request(rid, n):
    global Running_Process
    global RL
    global preempt
    if Running_Process.PID == "init":
        preempt = "error"
    elif rid == "R1":
        global R1
        if R1.Status_units >= n and not R1.WaitingList:
            # if enough resources available
            R1.Status_units = R1.Status_units - n
            for i in range(n):
                R1.Other_resources.append(Running_Process.PID)
        elif (R1.Other_resources.count(Running_Process.PID) + n) <= R1.max_units:
            # if not enough resources now, but could be in the future
            # remove current process from ReadyList and insert it into the WaitingList
            if Running_Process in RL.System:
                RL.System.remove(Running_Process)
            if Running_Process in RL.User:
                RL.User.remove(Running_Process)
            if Running_Process in RL.Init:
                RL.Init.remove(Running_Process)
            R1.WaitingList.append((Running_Process, n))
        else:
            preempt = "error"
    elif rid == "R2":
        global R2
        if R2.Status_units >= n and not R2.WaitingList:
            R2.Status_units = R2.Status_units - n
            for i in range(n):
                R2.Other_resources.append(Running_Process.PID)
        elif (R2.Other_resources.count(Running_Process.PID) + n) <= R2.max_units:
            if Running_Process in RL.System:
                RL.System.remove(Running_Process)
            if Running_Process in RL.User:
                RL.User.remove(Running_Process)
            if Running_Process in RL.Init:
                RL.Init.remove(Running_Process)
            R2.WaitingList.append((Running_Process, n))
        else:
            preempt = "error"
    elif rid == "R3":
        global R3
        if R3.Status_units >= n and not R3.WaitingList:
            R3.Status_units = R3.Status_units - n
            for i in range(n):
                R3.Other_resources.append(Running_Process.PID)
        elif (R3.Other_resources.count(Running_Process.PID) + n) <= R3.max_units:
            if Running_Process in RL.System:
                RL.System.remove(Running_Process)
            if Running_Process in RL.User:
                RL.User.remove(Running_Process)
            if Running_Process in RL.Init:
                RL.Init.remove(Running_Process)
            R3.WaitingList.append((Running_Process, n))
        else:
            preempt = "error"
    elif rid == "R4":
        global R4
        if R4.Status_units >= n and not R4.WaitingList:
            R4.Status_units = R4.Status_units - n
            for i in range(n):
                R4.Other_resources.append(Running_Process.PID)
        elif (R4.Other_resources.count(Running_Process.PID) + n) <= R4.max_units:
            if Running_Process in RL.System:
                RL.System.remove(Running_Process)
            if Running_Process in RL.User:
                RL.User.remove(Running_Process)
            if Running_Process in RL.Init:
                RL.Init.remove(Running_Process)
            R4.WaitingList.append((Running_Process, n))
        else:
            preempt = "error"
    if preempt != "error":
        scheduler()


def release(rid, n):
    global Running_Process
    global RL
    global preempt
    if Running_Process.PID == "init":
        preempt = "error"
    elif rid == "R1":
        global R1
        if n <= R1.Other_resources.count(Running_Process.PID):
            # able to release n units from RCB R1
            R1.Status_units = R1.Status_units + n
            i = 0
            while i < n:
                # release processes here
                R1.Other_resources.remove(Running_Process.PID)
                i += 1
            while R1.WaitingList and R1.WaitingList[0][1] <= R1.Status_units:
                first_in_WL = R1.WaitingList[0][0]
                units_requested = R1.WaitingList[0][1]
                R1.Status_units = R1.Status_units - units_requested
                for i in range(units_requested):
                    R1.Other_resources.append(first_in_WL.PID)
                R1.WaitingList.pop(0)
                if first_in_WL.Priority == 2:
                    RL.System.append(first_in_WL)
                elif first_in_WL.Priority == 1:
                    RL.User.append(first_in_WL)
        else:
            preempt = "error"
    elif rid == "R2":
        global R2
        if n <= R2.Other_resources.count(Running_Process.PID):
            R2.Status_units = R2.Status_units + n
            i = 0
            while i < n:
                R2.Other_resources.remove(Running_Process.PID)
                i += 1
            while R2.WaitingList and R2.WaitingList[0][1] <= R2.Status_units:
                first_in_WL = R2.WaitingList[0][0]
                units_requested = R2.WaitingList[0][1]
                R2.Status_units = R2.Status_units - units_requested
                for i in range(units_requested):
                    R2.Other_resources.append(first_in_WL.PID)
                R2.WaitingList.pop(0)
                if first_in_WL.Priority == 2:
                    RL.System.append(first_in_WL)
                elif first_in_WL.Priority == 1:
                    RL.User.append(first_in_WL)
        else:
            preempt = "error"
    elif rid == "R3":
        global R3
        if n <= R3.Other_resources.count(Running_Process.PID):
            R3.Status_units = R3.Status_units + n
            i = 0
            while i < n:
                R3.Other_resources.remove(Running_Process.PID)
                i += 1
            while R3.WaitingList and R3.WaitingList[0][1] <= R3.Status_units:
                first_in_WL = R3.WaitingList[0][0]
                units_requested = R3.WaitingList[0][1]
                R3.Status_units = R3.Status_units - units_requested
                for i in range(units_requested):
                    R3.Other_resources.append(first_in_WL.PID)
                R3.WaitingList.pop(0)
                if first_in_WL.Priority == 2:
                    RL.System.append(first_in_WL)
                elif first_in_WL.Priority == 1:
                    RL.User.append(first_in_WL)
        else:
            preempt = "error"
    elif rid == "R4":
        global R4
        if n <= R4.Other_resources.count(Running_Process.PID):
            R4.Status_units = R4.Status_units + n
            i = 0
            while i < n:
                R4.Other_resources.remove(Running_Process.PID)
                i += 1
            while R4.WaitingList and R4.WaitingList[0][1] <= R4.Status_units:
                first_in_WL = R4.WaitingList[0][0]
                units_requested = R4.WaitingList[0][1]
                R4.Status_units = R4.Status_units - units_requested
                for i in range(units_requested):
                    R4.Other_resources.append(first_in_WL.PID)
                R4.WaitingList.pop(0)
                if first_in_WL.Priority == 2:
                    RL.System.append(first_in_WL)
                elif first_in_WL.Priority == 1:
                    RL.User.append(first_in_WL)
        else:
            preempt = "error"
    if preempt != "error":
        scheduler()


def destroy(pid):
    global RL
    global R1
    global R2
    global R3
    global R4
    processes = set() # set of all PCB pid names to be destroyed
    running_children = set()
    # search for process in the Ready List
    if RL.System:
        for r in RL.System:
            if r.PID == pid:
                processes.add(r.PID) # add process that was initially instructed to destroy
                if r.Children:
                    processes = processes.union(find_children(r.Children)) # pass in children's PIDs
            if r.PID == Running_Process.PID:
                running_children.add(r.PID)
                if r.Children:
                    running_children = running_children.union(find_children(r.Children)) # pass in children's PIDs
    if RL.User:
        for r in RL.User:
            if r.PID == pid:
                processes.add(r.PID)
                if r.Children:
                    processes = processes.union(find_children(r.Children))
            if r.PID == Running_Process.PID:
                running_children.add(r.PID)
                if r.Children:
                    running_children = running_children.union(find_children(r.Children)) # pass in children's PIDs
    # if not in RL, search for process in the Waiting List
    if R1.WaitingList:
        for PCB_tuple in R1.WaitingList:
            if PCB_tuple[0].PID == pid:
                processes.add(PCB_tuple[0].PID)
                if PCB_tuple[0].Children:
                    processes = processes.union(find_children(PCB_tuple[0].Children))
            if PCB_tuple[0].PID == Running_Process.PID:
                running_children.add(PCB_tuple[0].PID)
                if PCB_tuple[0].Children:
                    running_children = running_children.union(find_children(PCB_tuple[0].Children))
    if R2.WaitingList:
        for PCB_tuple in R2.WaitingList:
            if PCB_tuple[0].PID == pid:
                processes.add(PCB_tuple[0].PID)
                if PCB_tuple[0].Children:
                    processes = processes.union(find_children(PCB_tuple[0].Children))
            if PCB_tuple[0].PID == Running_Process.PID:
                running_children.add(PCB_tuple[0].PID)
                if PCB_tuple[0].Children:
                    running_children = running_children.union(find_children(PCB_tuple[0].Children))
    if R3.WaitingList:
        for PCB_tuple in R3.WaitingList:
            if PCB_tuple[0].PID == pid:
                processes.add(PCB_tuple[0].PID)
                if PCB_tuple[0].Children:
                    processes = processes.union(find_children(PCB_tuple[0].Children))
            if PCB_tuple[0].PID == Running_Process.PID:
                running_children.add(PCB_tuple[0].PID)
                if PCB_tuple[0].Children:
                    running_children = running_children.union(find_children(PCB_tuple[0].Children))
    if R4.WaitingList:
        for PCB_tuple in R4.WaitingList:
            if PCB_tuple[0].PID == pid:
                processes.add(PCB_tuple[0].PID)
                if PCB_tuple[0].Children:
                    processes = processes.union(find_children(PCB_tuple[0].Children))
            if PCB_tuple[0].PID == Running_Process.PID:
                running_children.add(PCB_tuple[0].PID)
                if PCB_tuple[0].Children:
                    running_children = running_children.union(find_children(PCB_tuple[0].Children))

    if pid not in running_children and Running_Process.PID != "init":
        global preempt
        preempt = "error"
    else:
        # remove every process from the RL or WL
        for pname in processes:
            if RL.System:
                for r in RL.System:
                    if r.PID == pname:
                        RL.System.remove(r)
            if RL.User:
                for r in RL.User:
                    if r.PID == pname:
                        RL.User.remove(r)
            # if not in RL, search for process in the Waiting List and remove
            if R1.WaitingList:
                for PCB_tuple in R1.WaitingList:
                    if PCB_tuple[0].PID == pname:
                        R1.WaitingList.remove(PCB_tuple)
            if R2.WaitingList:
                for PCB_tuple in R2.WaitingList:
                    if PCB_tuple[0].PID == pname:
                        R2.WaitingList.remove(PCB_tuple)
            if R3.WaitingList:
                for PCB_tuple in R3.WaitingList:
                    if PCB_tuple[0].PID == pname:
                        R3.WaitingList.remove(PCB_tuple)
            if R4.WaitingList:
                for PCB_tuple in R4.WaitingList:
                    if PCB_tuple[0].PID == pname:
                        R4.WaitingList.remove(PCB_tuple)

        for pname in processes:
            if pname in R1.Other_resources:
                # release process's units
                while pname in R1.Other_resources:
                    R1.Other_resources.remove(pname)
                    R1.Status_units = R1.Status_units + 1
                while R1.WaitingList and R1.WaitingList[0][1] <= R1.Status_units:
                    first_in_WL = R1.WaitingList[0][0]
                    units_requested = R1.WaitingList[0][1]
                    R1.Status_units = R1.Status_units - units_requested
                    for i in range(units_requested):
                        R1.Other_resources.append(first_in_WL.PID)
                    R1.WaitingList.pop(0)
                    if first_in_WL.Priority == 2:
                        RL.System.append(first_in_WL)
                    elif first_in_WL.Priority == 1:
                        RL.User.append(first_in_WL)
            if pname in R2.Other_resources:
                # release process's units
                while pname in R2.Other_resources:
                    R2.Other_resources.remove(pname)
                    R2.Status_units = R2.Status_units + 1
                while R2.WaitingList and R2.WaitingList[0][1] <= R2.Status_units:
                    first_in_WL = R2.WaitingList[0][0]
                    units_requested = R2.WaitingList[0][1]
                    R2.Status_units = R2.Status_units - units_requested
                    for i in range(units_requested):
                        R2.Other_resources.append(first_in_WL.PID)
                    R2.WaitingList.pop(0)
                    if first_in_WL.Priority == 2:
                        RL.System.append(first_in_WL)
                    elif first_in_WL.Priority == 1:
                        RL.User.append(first_in_WL)
            if pname in R3.Other_resources:
                # release process's units
                while pname in R3.Other_resources:
                    R3.Other_resources.remove(pname)
                    R3.Status_units = R3.Status_units + 1
                while R3.WaitingList and R3.WaitingList[0][1] <= R3.Status_units:
                    first_in_WL = R3.WaitingList[0][0]
                    units_requested = R3.WaitingList[0][1]
                    R3.Status_units = R3.Status_units - units_requested
                    for i in range(units_requested):
                        R3.Other_resources.append(first_in_WL.PID)
                    R3.WaitingList.pop(0)
                    if first_in_WL.Priority == 2:
                        RL.System.append(first_in_WL)
                    elif first_in_WL.Priority == 1:
                        RL.User.append(first_in_WL)
            if pname in R4.Other_resources:
                # release process's units
                while pname in R4.Other_resources:
                    R4.Other_resources.remove(pname)
                    R4.Status_units = R4.Status_units + 1
                while R4.WaitingList and R4.WaitingList[0][1] <= R4.Status_units:
                    first_in_WL = R4.WaitingList[0][0]
                    units_requested = R4.WaitingList[0][1]
                    R4.Status_units = R4.Status_units - units_requested
                    for i in range(units_requested):
                        R4.Other_resources.append(first_in_WL.PID)
                    R4.WaitingList.pop(0)
                    if first_in_WL.Priority == 2:
                        RL.System.append(first_in_WL)
                    elif first_in_WL.Priority == 1:
                        RL.User.append(first_in_WL)

        # update All_PIDs by removing all the destroyed processes names
        global All_PIDs
        All_PIDs.difference_update(processes)
        scheduler()

# NOTE: make sure you remove the process from RL or WL
#       AND remove the name from list of PIDs too


def find_children(childrens_to_destroy):
    global RL
    global R1
    global R2
    global R3
    global R4
    processes = set()
    for child in childrens_to_destroy:
        processes.add(child) # add the child's PID
        # find Child in RL or WL
        if RL.System:
            for r in RL.System:
                if r.PID == child:
                    processes.add(r.PID)  # add process that was initially instructed to destroy
                    if r.Children:
                        processes = processes.union(find_children(r.Children))  # pass in children's PIDs
        if RL.User:
            for r in RL.User:
                if r.PID == child:
                    processes.add(r.PID)
                    if r.Children:
                        processes = processes.union(find_children(r.Children))
        # if not in RL, search for process in the Waiting List
        if R1.WaitingList:
            for PCB_tuple in R1.WaitingList:
                if PCB_tuple[0].PID == child:
                    processes.add(PCB_tuple[0].PID)
                    if PCB_tuple[0].Children:
                        processes = processes.union(find_children(PCB_tuple[0].Children))
        if R2.WaitingList:
            for PCB_tuple in R2.WaitingList:
                if PCB_tuple[0].PID == child:
                    processes.add(PCB_tuple[0].PID)
                    if PCB_tuple[0].Children:
                        processes = processes.union(find_children(PCB_tuple[0].Children))
        if R3.WaitingList:
            for PCB_tuple in R3.WaitingList:
                if PCB_tuple[0].PID == child:
                    processes.add(PCB_tuple[0].PID)
                    if PCB_tuple[0].Children:
                        processes = processes.union(find_children(PCB_tuple[0].Children))
        if R4.WaitingList:
            for PCB_tuple in R4.WaitingList:
                if PCB_tuple[0].PID == child:
                    processes.add(PCB_tuple[0].PID)
                    if PCB_tuple[0].Children:
                        processes = processes.union(find_children(PCB_tuple[0].Children))
    return processes # list of all children processes to be destroy


def scheduler():
    # will edit the preempt aka output
    global RL
    global Running_Process
    global preempt
    if RL.System:
        Running_Process = RL.System[0]
    elif RL.User:
        Running_Process = RL.User[0]
    else:
        Running_Process = RL.Init[0]
    preempt = Running_Process.PID


def timeout():
    global Running_Process
    global RL
    if Running_Process in RL.System:
        RL.System.remove(Running_Process)
        RL.System.append(Running_Process)
    if Running_Process in RL.User:
        RL.User.remove(Running_Process)
        RL.User.append(Running_Process)
    if Running_Process in RL.Init:
        RL.Init.remove(Running_Process)
        RL.Init.append(Running_Process)
    scheduler()





if __name__ == '__main__':
    '''
    Change path & file names down below / HERE
    '''
    #path = "/Volumes/UNTITLED/"
    path = "/Users/Amanda/Desktop/"

    outpath = path + "30647913.txt"
    outfile = open(outpath, "w")
    input_file = path + "testGR-sample.txt"

    commands = ["init", "cr", "de", "req", "rel", "to"]
    with open(input_file) as file:
        # initial startup
        RL = ReadyList(PCB("init", 0, None)) # begins a new ReadyList with root as a process
        All_PIDs.add("init")
        Running_Process = RL.Init[0]  # current running process is init
        preempt = Running_Process.PID
        R1 = RCB("R1", 1)
        R2 = RCB("R2", 2)
        R3 = RCB("R3", 3)
        R4 = RCB("R4", 4)
        outfile.write(preempt)
        preempt = None

        for line in file:
            parseline = line.split()
            if len(parseline) == 0:
                parseline = ["init"]
                if preempt == "init":
                    preempt = None
            if parseline[0] in commands:
                # so far valid command, continue
                if parseline[0] == "init" and len(parseline) == 1:
                    if preempt == "init" and len(All_PIDs) == 1:
                        pass
                    else:
                        # Re-initialize everything
                        RL = ReadyList(PCB("init", 0, None))  # begins a new ReadyList with root as a process
                        All_PIDs.clear()
                        All_PIDs.add("init")
                        Running_Process = RL.Init[0]  # current running process is init
                        preempt = Running_Process.PID
                        R1 = RCB("R1", 1)
                        R2 = RCB("R2", 2)
                        R3 = RCB("R3", 3)
                        R4 = RCB("R4", 4)
                        outfile.write("\n" + preempt)
                elif parseline[0] == "cr" and len(parseline) == 3 and len(parseline[1]) == 1:
                    if parseline[1] in All_PIDs:
                        preempt = "error"
                    elif parseline[2] == "2":
                        create(parseline[1], 2)
                    elif parseline[2] == "1":
                        create(parseline[1], 1)
                    else:
                        preempt = "error"
                    outfile.write(" " + preempt)
                elif parseline[0] == "de":
                    if len(parseline) == 2:
                        if parseline[1] == "init" or parseline[1] not in All_PIDs:
                            preempt = "error"
                        else:
                            destroy(parseline[1])
                    else:
                        preempt = "error"
                    outfile.write(" " + preempt)
                elif parseline[0] == "req" and len(parseline) == 3:
                    preempt = None
                    if Running_Process.PID == "init":
                        preempt = "error"
                    elif parseline[1] in ["R1","R2","R3","R4"] and parseline[2] in ["1","2","3","4"]:
                        request(parseline[1], int(parseline[2]))
                    outfile.write(" " + preempt)
                elif parseline[0] == "rel" and len(parseline) == 3:
                    if Running_Process.PID == "init":
                        preempt = "error"
                    elif parseline[1] in ["R1","R2","R3","R4"] and parseline[2] in ["1","2","3","4"]:
                        release(parseline[1], int(parseline[2]))
                    outfile.write(" " + preempt)
                elif parseline[0] == "to" and len(parseline) == 1:
                    timeout()
                    outfile.write(" " + preempt)
            else:
                preempt = "error"
                outfile.write(" " + preempt)

    outfile.close()
