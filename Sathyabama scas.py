from texttable import Texttable 
class staff:
    s={}
    def create(self):
        s1=int(input("Enter staff id"))
        if s1 in self.s:
            print("id already exisit")
        else:
            s2=input("Enter staff name")
            self.s[s1]=s2
            print("staff id add succecfully")
        
    def info(self):
        i1=int(input("Enter staff id:"))
        for i in self.s:
            if i==i1:
                print("staff detials")



class room(staff):
    p=[[None]*5]*6
    p1=[[None]*5]*6
    def __init__(self,no):
        self.no=no
    def period(self):
        print("Enter day ")
        d=int(input())
        for i in range(5):
            self.p[d][i]=input("Enter period {} staff :".format(i+1))
        for i in range(5):
            print(self.p[d][i])
        
    def table(self):
        t=Texttable()
        t.add_rows([["DAYs","Peroid 1","Peroid 2","Peroid 3","Peroid 4","Peroid 5 "],
        ["Monday",self.p[0][0],self.p[0][1],self.p[0][2],self.p[0][3],self.p[0][4]],
        ["Tuesday",self.p[1][0],self.p[1][1],self.p[1][2],self.p[1][3],self.p[1][4]],
        ["Wednesday",self.p[2][0],self.p[2][1],self.p[2][2],self.p[2][3],self.p[2][4]],
        ["Thuesday",self.p[3][0],self.p[3][1],self.p[3][2],self.p[3][3],self.p[3][4]],
        ["Friday",self.p[4][0],self.p[4][1],self.p[4][2],self.p[4][3],self.p[4][4]]])
        print(t.draw())
    def speriod(self):
        print("Enter day ")
        d=int(input())
        for i in range(5):
            self.p1[d][i]=input("Enter period {} Subject :".format(i+1))
        for i in range(5):
            print(self.p1[d][i])
    def stable(self):
        t2=Texttable()
        t2.add_rows([["DAYs","Peroid 1","Peroid 2","Peroid 3","Peroid 4","Peroid 5 "],
        ["Monday",self.p1[0][0],self.p1[0][1],self.p1[0][2],self.p1[0][3],self.p1[0][4]],
        ["Tuesday",self.p1[1][0],self.p1[1][1],self.p1[1][2],self.p1[1][3],self.p1[1][4]],
        ["Wednesday",self.p1[2][0],self.p1[2][1],self.p1[2][2],self.p1[2][3],self.p1[2][4]],
        ["Thuesday",self.p1[3][0],self.p1[3][1],self.p1[3][2],self.p1[3][3],self.p1[3][4]],
        ["Friday",self.p1[4][0],self.p1[4][1],self.p1[4][2],self.p1[4][3],self.p1[4][4]]])
        print(t2.draw())
        

print("""         1.Create staff id
         2.create class Staff-wise time table
         3.create class Subject-wise time table
         4.display class time table
         5.list free staff
         """)
while(True):
    c=int(input("Input choice:"))
    r=room(359)
    if c==1:
        r.create()
    elif c==2:
        r.period()
    elif c==3:
        r.speriod()
    elif c==4:
        r.table()
    elif c==5:
        r.stable()
    
