import MySQLdb as mdb
import sys
from jabberbot import JabberBot,botcmd
import logging
from JointParser import cff


def utfizing_db(lst):
    '''used to turn sql row in list format into unicode string '''
    return reduce(lambda x,y : x+"|"+y , map(lambda x : unicode(x),lst ))


def connectNexecute(sqlin,args=None):
    '''
    connect and execute sql query , for averting use of keepalive querys
    '''
    try:
        connection = mdb.connect(MYSQLSERV, MYSQLUSER , MYSQLPASS, MYSQLDB,
            charset="utf8", use_unicode = True);
    except mdb.Error , e:
        print "Error %d, %s " % ( e.args[0] , e.args[1])
        sys.exit(1)
    finally:
        cursor = connection.cursor()
        if args:
            cursor.execute(sqlin, args )
        else:
            cursor.execute(sqlin)
        return_rows = cursor.fetchall()
        return reduce ( lambda x ,y : x+u"\n"+y , map( utfizing_db, return_rows  ) )

class MamaJabberBot(JabberBot):

    def __init__( self, jid, password, res = None):
        super( MamaJabberBot, self).__init__( jid, password, res)
        # create console handler
        chandler = logging.StreamHandler()
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # add formatter to handler
        chandler.setFormatter(formatter)
        # add handler to logger
        self.log.addHandler(chandler)
        # set level to INFO
        self.log.setLevel(logging.INFO)

        self.users = []
        self.message_queue = []
        self.thread_killed = False

    @botcmd
    def who(self,mess,args):
        """Tells you who is in hacklab in mama"""
        self.log.info(mess.getFrom().getStripped())
        return connectNexecute("""SELECT CONCAT("Prije ", MINUTE(TIMEDIFF(NOW(), MAX(entry.created_on))), " min: ", IFNULL(person.fullname, "Nepoznati")) FROM entry LEFT JOIN mac ON entry.mac = mac.mac LEFT JOIN person ON mac.person_id = person.id WHERE DATE_ADD(entry.created_on, INTERVAL 1 HOUR) >= NOW() GROUP BY person.id ORDER BY MINUTE(TIMEDIFF(NOW(), MAX(entry.created_on)));""")



if __name__=="__main__":
    cf =  cff.CfParser("bot2.cfg")
    options = cf.options
    username = options.jabuser
    password = options.jabpass
    MYSQLSERV= options.dbsrv
    MYSQLUSER= options.dbusr
    MYSQLPASS= options.dbpass
    MYSQLDB = options.dbdb

    bot = MamaJabberBot(username,password)
    bot.serve_forever()
