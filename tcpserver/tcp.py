import SocketServer
from SocketServer import StreamRequestHandler as SRH
import socket,traceback
import datetime
import MySQLdb
host = '192.168.1.110'
port = 9999
addr = (host,port)
class Servers(SRH):
    def handle(self):
        conn = MySQLdb.connect(host='localhost',port = 3306,user='root',passwd='telecom660786',db ='smart_home',)
        insertstr1=format('insert into smart_control (mac) values ("%s") on duplicate key update status=1')
        insertstr2=format('insert into smart_control (mac) values ("%s") on duplicate key update status=5')
        insertstr3=format('insert into smart_control (mac) values ("%s") on duplicate key update online_time="%s"')
        selecttstr=format('select status,type from smart_control where mac="%s"')
        insertstr5=format('insert into smart_control (mac) values ("%s") on duplicate key update status=0')
        print ('got connection from ' , self.client_address)
        self.mac=''
        self.request.settimeout(5)
        while True:
            try:
                self.data = self.request.recv(1024)
                if self.data==None or len(self.data)<17 or self.mac=='                 ':
                    aa=insertstr2 % (self.mac)
                    cur=conn.cursor()
                    cur.execute(aa)
                    conn.commit()
                    cur.close()
                    print('connection close')
                    break;
                if self.data[:3]=='add':
                    self.mac=self.data[3:20]
                    if self.mac == None or len(self.mac)<17 or self.mac=='                 ':
                        break
                    aa=insertstr1 % (self.data[3:20])
                    cur=conn.cursor()
                    cur.execute(aa)
                    conn.commit()
                    cur.close()
                if self.data[:3]=='hrt':
                    now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.mac=self.data[3:20]
                    if self.mac == None or len(self.mac)<17 or self.mac=='                 ':
                        break
                    aa=insertstr3 % (self.mac,now)
                    cur=conn.cursor()
                    cur.execute(aa)
                    conn.commit()
                    cur.close()
                if self.data[:3] == 'sen':
                    self.mac=self.data[3:20]
                    if self.mac == None or len(self.mac)<17 or self.mac=='                 ':
                        break
                    aa=insertstr1 % (self.mac)
                    cur=conn.cursor()
                    cur.execute(aa)
                    conn.commit()
                    cur.close()
                if self.data[:3] == 'non':
                    self.mac=self.data[3:20]
                    if self.mac == None or len(self.mac)<17 or self.mac=='                 ':
                        break
                    aa=insertstr5 % (self.mac)
                    cur=conn.cursor()
                    cur.execute(aa)
                    conn.commit()
                    cur.close()
                if self.data[:3] == 'sen' or self.data[:3] == 'hrt' or self.data[:3] == 'non':
                    aa=selecttstr % (self.mac)
                    cur=conn.cursor()
                    count=cur.execute(aa)
                    result=cur.fetchone()
                    sts=result[0]
                    res=result[1]
                    cur.close()
                    self.connection.sendall('%s%s\n' % (res,sts))
            except socket.timeout:
                print ('socket timeout')
                print ('connection is close....')
                if len(self.mac)==17 and self.mac != '                 ':
                    aa=insertstr2 % (self.mac)
                    cur=conn.cursor()
                    cur.execute(aa)
                    conn.commit()
                    cur.close()
                break
            except:
                traceback.print_exc()
                break;
        self.connection.close()
if __name__ == '__main__':
    print ('server is running....')
    SocketServer.TCPServer.allow_reuse_address=True
    server = SocketServer.ThreadingTCPServer(addr,Servers)
    server.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.serve_forever()

