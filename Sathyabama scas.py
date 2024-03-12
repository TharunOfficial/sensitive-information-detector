class staff:
    s=[]
    sn=[]
    def create(self):
        s1=int(input("Enter staff id"))
        if s1 in s:
            print("id already exisit")
        else:
            self.s.append(s1)
            print("staff id add succecfully")
        s2=input("Enter staff name")
        self.sn.append(s2)
        
    def info(self):
        i1=int(input("Enter staff if:"))
        for i in s:
            if i==i1:
                print("staff detials")



class room:
    p=[None]*5
    def __init__(self,no):
        self.no=no
    def period(self):
        for i in range(len(self.p)):
            self.p[i]=input("Enter period {} staff :".format(i+1))
    def table(self):
        for i in range(len(self.P)):
            print("period {} staff:")
        pass

print("""         1.Create staff id
         2.create class time table
         3.display class time table
         4.list free staff
         """)
while(True):
    c=int(input("Input choice:"))
