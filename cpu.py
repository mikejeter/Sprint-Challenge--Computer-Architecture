"""CPU functionality."""

import sys



class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""

        self.reg = [0] * 8 
        self.ram = [0] * 256
        self.PC = 0

        
        self.stack_pointer = 7

        
        self.reg[self.stack_pointer] = 0xf4

        # branch table
        self.branchtable = {}
        self.branchtable[0b01000111] = self.PRN
        self.branchtable[0b10000010] = self.LDI
        self.branchtable[0b10100010] = self.MUL
        self.branchtable[0b01000101] = self.PUSH
        self.branchtable[0b01000110] = self.POP
        self.branchtable[0b10100111] = self.CMP
        self.branchtable[0b01010100] = self.JMP
        self.branchtable[0b01010101] = self.JEQ
        self.branchtable[0b01010110] = self.JNE

        
        self.FL = [0] * 8

     
    def load(self, filename):
     """Load a program into memory."""

     params = sys.argv

     if len(params) != 2:
         print("usage: file.py filename")
         sys.exit(1)

     if len(params) == 2:
            try:
                with open(params[1]) as f:
                    address = 0
                    for line in f:
                        comment_split = line.split("#")
                        num = comment_split[0].strip()
                        if num == '':
                            continue
                        val = int("0b"+num, 2)
                        self.ram_write(address, val)
                        
                        address += 1

            except FileNotFoundError:   
                print("ERROR: File not found")
                sys.exit(2)

    
    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        if op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        if op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        if op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]

        if op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]: 
                self.FL[5] = 0
                self.FL[6] = 0
                self.FL[7] = 1
            elif self.reg[reg_a] < self.reg[reg_b]: 
                self.FL[5] = 1 
                self.FL[6] = 0
                self.FL[7] = 0
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.FL[5] = 0
                self.FL[6] = 1
        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')
        for i in range(8):
            print(" %02X" % self.reg[i], end='')
        print()

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def LDI(self):
        self.reg[self.ram_read(self.PC+1)] = self.ram_read(self.PC+2)
        self.PC += 3

    def PRN(self):
        print(self.reg[self.ram_read(self.PC+1)])
        self.PC += 2

    def MUL(self):
        self.reg[self.ram_read(
            self.PC+1)] = (self.reg[self.ram_read(self.PC+1)] * self.reg[self.ram_read(self.PC+2)]) # multipies values using alu
        self.PC += 3

    def PUSH(self):
        self.reg[self.stack_pointer] -= 1
        reg_num = self.ram[self.PC + 1]
        value = self.reg[reg_num]
        self.ram[self.reg[self.stack_pointer]] = value
        self.PC += 2

    def POP(self):
        value = self.ram[self.reg[self.stack_pointer]]
        reg_num = self.ram[self.PC + 1]
        self.reg[reg_num] = value
        self.reg[self.stack_pointer] += 1
        self.PC += 2

    # Sprint functions
    def CMP(self):
        self.alu("CMP", self.ram[self.PC+1], self.ram[self.PC+2])
        self.PC += 3

    def JMP(self):
        self.PC = self.reg[self.ram[self.PC + 1]]

    def JEQ(self):
        if self.FL[7] == 1:
            self.PC = self.reg[self.ram[self.PC + 1]]
        else:
            self.PC += 2 

    def JNE(self):
        if self.FL[7] == 0:
            self.PC = self.reg[self.ram[self.PC + 1]]
        else:
            self.PC += 2

    def run(self):
        """Run the CPU."""

        # opcode commands
        HLT = 0b00000001
        CALL = 0b01010000
        RET = 0b00010001

        running = True

        while running:
            command = self.ram_read(self.PC)
            if command == HLT:
                running = False
            elif command == CALL:
                return_address = self.PC + 2
                self.reg[self.stack_pointer] -= 1
                self.ram[self.reg[self.stack_pointer]] = return_address
                reg_num = self.ram[self.PC + 1] 
                self.PC = self.reg[reg_num]
            elif command == RET:
                self.PC = self.ram[self.reg[self.stack_pointer]]
                self.reg[self.stack_pointer] += 1
            else:
                self.branchtable[command]()
