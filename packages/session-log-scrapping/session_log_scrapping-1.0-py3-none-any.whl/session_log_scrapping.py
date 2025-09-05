#Om Namo Parvati Pataye Hara Hara Mahadev Shambo Shankara
import datetime
class Session_log_scrapping:

  def __init__(self,filename):
    a=open(filename,'r')
    self.file_data=a.read()

  def sessionduration(self):
    for i in self.file_data.split('\n'):
      if 'Beginning the prepare phase for the session' in i:
        start_time_str=' '.join((i.split()[1:3]))[1:-1]
      if 'Session' in i and 'completed at' in i:
        end_time_str=' '.join((i.split()[2:4]))[1:-1]
    start_time=datetime.datetime.strptime(start_time_str[:19],'%Y-%m-%d %H:%M:%S')
    end_time=datetime.datetime.strptime(end_time_str[:19],'%Y-%m-%d %H:%M:%S')
    time_diff=(end_time-start_time).total_seconds()/60
    return time_diff

  def lookupthreads(self):
    lookups=[]
    for i in self.file_data.split('\n'):
      if 'Reader run started' in i and 'LKPDP' in i:
        lookups.append(i.split(':')[0])
    return lookups

  def readerthreads(self):
    readers=[]
    for i in self.file_data.split('\n'):
      if 'Reader run started' in i and 'READER' in i[:6]:
        readers.append(i.split('>')[0])
    return readers

  def writerthreads(self):
    writers=[]
    for i in self.file_data.split('\n'):
      if 'Writer run started' in i and 'WRITER' in i[:6]:
        writers.append(i.split('>')[0])
    return writers

  def readername(self,name):
    for i in self.file_data.split('\n'):
      if 'SQ Instance' in i and name in i:
        return i.split('SQ Instance [')[1].split(']')[0]

  def lookupname(self,name):
    for i in self.file_data.split('\n'):
      if 'DBG_21' in i and name in i and 'Lookup Transformation' in i:
        return i.split('Lookup Transformation [')[1].split(']')[0]

  def readerduration(self,name):
    start_time=''
    end_time=''
    for i in self.file_data.split('\n'):
      if 'Reader run started' in i and name in i:
        start_time=' '.join(i.split()[2:4])[1:-5]
      if 'Reader run completed' in i and name in i:
        end_time=' '.join(i.split()[2:4])[1:-5]
    return [start_time,end_time]

  def writerduration(self,name):
    start_time=''
    end_time=''
    for i in self.file_data.split('\n'):
      if 'Writer run started' in i and name in i:
        start_time=' '.join(i.split()[2:4])[1:-5]
      if 'Writer run completed' in i and name in i:
        end_time=' '.join(i.split()[2:4])[1:-5]
    return [start_time,end_time]

  def sourcequery(self,name):
    count=0
    query_lines=[]
    for i in self.file_data.split('\n'):
      if 'SQ Instance' in i and name in i:
        query_lines.append(i.split('SQL Query [')[1])
        if ']' not in i[-1]:
          for j in self.file_data.split('\n')[count+1:]:
            if ']' not in j[-1]:
              query_lines.append(j)
            else:
              query_lines.append(j)
              break

      count=count+1
    return query_lines

  def lookupquery(self,name):
    count=0
    query_lines=[]
    for i in self.file_data.split('\n'):
      if 'DBG_21' in i and name in i and 'Lookup Transformation' in i:
        query_lines.append(i.split(':')[4])
        #print(i)
        if ']' not in i[-1]:
          for j in self.file_data.split('\n')[count+1:]:
            if len(j)>1:
              if ']' not in j[-1]:
                query_lines.append(j)
              else:
                query_lines.append(j)
                break
            else:
              break

      count=count+1
    return query_lines

  def uncached_lookups(self):
    lookups_list=[]
    for i in self.file_data.split('\n'):
      if 'Non-cached Lookup SQL:' in i:
        lookups_list.append(i.split('Non-cached Lookup SQL:')[0].split()[-1][:-1])
    return lookups_list

  def uncached_lookups_queries(self,lookup_name):
    query_lines=[]
    count=0
    for i in self.file_data.split('\n'):
      if 'Non-cached Lookup SQL:' in i and lookup_name in i:
        query_lines.append(i.split('Non-cached Lookup SQL:')[-1])

    return ' '.join(query_lines)

  def writertable(self,name):
    for i in self.file_data.split('\n'):
      if 'Start loading table' in i and name in i:
        return i.split()[7]