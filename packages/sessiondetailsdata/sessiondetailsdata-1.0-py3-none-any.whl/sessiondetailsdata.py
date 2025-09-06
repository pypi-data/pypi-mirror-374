
a='''pip install session_log_scrapping

from  session_log_scrapping import Session_log_scrapping
import datetime

filename=input('provide the session log name')
a=Session_log_scrapping(filename)

time=a.sessionduration()

file_txt=filename+'.txt'
file=open(file_txt,'w')
duration='the mapping task ran in '+str(time)+' mins'
file.write(duration+'\n')
file.write('\n')
file.write('\n')

lookupthreads=a.lookupthreads()
file.write('the following are the lookup threads we have'+'\n')
for i in lookupthreads:
  time=datetime.datetime.strptime(a.readerduration(i)[1],'%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(a.readerduration(i)[0],'%Y-%m-%d %H:%M:%S')
  details=i+' '+a.lookupname(i)+' with starttime '+a.readerduration(i)[0]+' and endtime '+a.readerduration(i)[1]+' has a duration of '+str(time)
  file.write(details+'\n')
  #print(details)
  file.write('\n')
  file.write('\n')
file.write('\n')
file.write('\n')
file.write('\n')

uncached_lookups=set(a.uncached_lookups())
file.write('the following are the lookup threads without caches'+'\n')
for i in uncached_lookups:
  #print(i)
  file.write(i+'\n')
  #print(details)
  file.write('\n')
  file.write('\n')
file.write('\n')
file.write('\n')
file.write('\n')


readerthreads=a.readerthreads()
file.write('the following are the reader threads we have'+'\n')
for i in readerthreads:
  time=datetime.datetime.strptime(a.readerduration(i)[1],'%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(a.readerduration(i)[0],'%Y-%m-%d %H:%M:%S')
  details=i+' '+a.readername(i)+' with starttime '+a.readerduration(i)[0]+' and endtime '+a.readerduration(i)[1]+' has a duration of '+str(time)
  file.write(details+'\n')
  file.write('\n')
file.write('\n')
file.write('\n')
file.write('\n')

writerthreads=a.writerthreads()
file.write('the following are the writer thread names we have'+'\n')
for i in writerthreads:
  time=datetime.datetime.strptime(a.writerduration(i)[1],'%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(a.writerduration(i)[0],'%Y-%m-%d %H:%M:%S')
  name_details=i+' name is '+a.writertable(i)+' with start time '+a.writerduration(i)[0]+' and end time '+a.writerduration(i)[1]+' with duration '+str(time)
  file.write(name_details+'\n')
  file.write('\n')
  #print(name_details)
file.write('\n')
file.write('\n')
file.write('\n')

file.write('the following are the SQL queries for sources we have'+'\n')
for i in readerthreads:
  query=' '.join(a.sourcequery(i))
  query=i+' : '+query
  file.write(query+'\n')
  file.write('\n')
  #print(query)
file.write('\n')
file.write('\n')

file.write('the following are the SQL queries for lookups we have'+'\n')
for i in lookupthreads:
  query=' '.join(a.lookupquery(i))
  query=i+' : '+query
  file.write(query+'\n')
  file.write('\n')
file.write('\n')
file.write('\n')

file.write('the following are the SQL queries for lookups for uncached'+'\n')
for i in uncached_lookups:
  query=i+':'+a.uncached_lookups_queries(i)
  file.write(query+'\n')
  file.write('\n')
file.write('\n')
file.write('\n')

print('the details of the log are present in the newly created file :',file_txt)'''



ml='''from sentence_transformers import SentenceTransformer, util
import torch
from sourcepatterndata import SourcePatternData
import os

def removingtimestamp(text):
  text_list=text.split()
  text_val=[]
  for i in text_list:
    if (len(i)==11 and i[0]=='[' and i[-1]!=']') or (len(i)==13 and i[0]!='['and i[-1]==']'):
      pass
    else:
      text_val.append(i)
  return ' '.join(text_val)

error_raw_data=SourcePatternData.source_data()

check_model= SentenceTransformer('all-MiniLM-L6-v2')

error_clean_data={}
for i,j in error_raw_data.items():
  timestampremovaldata= [removingtimestamp(k) for k in j]
  error_clean_data[i]=check_model.encode(timestampremovaldata,convert_to_tensor=True)

def finding_suitable_solution(text):
  text1=removingtimestamp(text)
  print(text1)
  converted_data=check_model.encode(text1,convert_to_tensor=True)
  score=0
  class_val=''
  for key,val in error_clean_data.items():
    cosine_similarity_val=util.cos_sim(converted_data,val)
    score_val=torch.max(cosine_similarity_val).item()
    #print(score_val,class_val)
    if score_val>score:
      score=score_val
      class_val=key
  return score,class_val

filename=input("insert file here")
a=open(filename,'r')
file=a.read()
error_data_text=[]
patterns=SourcePatternData.patterns_data()
for i in file.split('\n'):
  if ('Error' in i or 'error' in i or 'ERROR' in i) and (patterns[0] not in i and patterns[1] not in i and patterns[2] not in i and patterns[3] not in i and patterns[4] not in i and patterns[5] not in i and patterns[6] not in i and patterns[7] not in i and patterns[8] not in i and patterns[9] not in i and patterns[10] not in i and patterns[11] not in i and patterns[12] not in i and patterns[13] not in i and patterns[14] not in i and patterns[15] not in i):
    error_data_text.append(i)
error_text=' '.join(error_data_text)
#print(error_text)
score_val,class_val=finding_suitable_solution(error_text)

if class_val=='DTM ERROR FOR COLUMNS' and score_val>0.9:
  print("it is ",score_val*100," sure it is because",class_val,"check the column datatypes and precisions in the lookup/join condition")
else:
  print(score_val*100,' percent sure it is due to',class_val )'''


class session_details():
  a='''pip install session_log_scrapping

from  session_log_scrapping import Session_log_scrapping
import datetime

filename=input('provide the session log name')
a=Session_log_scrapping(filename)

time=a.sessionduration()

file_txt=filename+'.txt'
file=open(file_txt,'w')
duration='the mapping task ran in '+str(time)+' mins'
file.write(duration+'\n')
file.write('\n')
file.write('\n')

lookupthreads=a.lookupthreads()
file.write('the following are the lookup threads we have'+'\n')
for i in lookupthreads:
  time=datetime.datetime.strptime(a.readerduration(i)[1],'%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(a.readerduration(i)[0],'%Y-%m-%d %H:%M:%S')
  details=i+' '+a.lookupname(i)+' with starttime '+a.readerduration(i)[0]+' and endtime '+a.readerduration(i)[1]+' has a duration of '+str(time)
  file.write(details+'\n')
  #print(details)
  file.write('\n')
  file.write('\n')
file.write('\n')
file.write('\n')
file.write('\n')

uncached_lookups=set(a.uncached_lookups())
file.write('the following are the lookup threads without caches'+'\n')
for i in uncached_lookups:
  #print(i)
  file.write(i+'\n')
  #print(details)
  file.write('\n')
  file.write('\n')
file.write('\n')
file.write('\n')
file.write('\n')


readerthreads=a.readerthreads()
file.write('the following are the reader threads we have'+'\n')
for i in readerthreads:
  time=datetime.datetime.strptime(a.readerduration(i)[1],'%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(a.readerduration(i)[0],'%Y-%m-%d %H:%M:%S')
  details=i+' '+a.readername(i)+' with starttime '+a.readerduration(i)[0]+' and endtime '+a.readerduration(i)[1]+' has a duration of '+str(time)
  file.write(details+'\n')
  file.write('\n')
file.write('\n')
file.write('\n')
file.write('\n')

writerthreads=a.writerthreads()
file.write('the following are the writer thread names we have'+'\n')
for i in writerthreads:
  time=datetime.datetime.strptime(a.writerduration(i)[1],'%Y-%m-%d %H:%M:%S')-datetime.datetime.strptime(a.writerduration(i)[0],'%Y-%m-%d %H:%M:%S')
  name_details=i+' name is '+a.writertable(i)+' with start time '+a.writerduration(i)[0]+' and end time '+a.writerduration(i)[1]+' with duration '+str(time)
  file.write(name_details+'\n')
  file.write('\n')
  #print(name_details)
file.write('\n')
file.write('\n')
file.write('\n')

file.write('the following are the SQL queries for sources we have'+'\n')
for i in readerthreads:
  query=' '.join(a.sourcequery(i))
  query=i+' : '+query
  file.write(query+'\n')
  file.write('\n')
  #print(query)
file.write('\n')
file.write('\n')

file.write('the following are the SQL queries for lookups we have'+'\n')
for i in lookupthreads:
  query=' '.join(a.lookupquery(i))
  query=i+' : '+query
  file.write(query+'\n')
  file.write('\n')
file.write('\n')
file.write('\n')

file.write('the following are the SQL queries for lookups for uncached'+'\n')
for i in uncached_lookups:
  query=i+':'+a.uncached_lookups_queries(i)
  file.write(query+'\n')
  file.write('\n')
file.write('\n')
file.write('\n')

print('the details of the log are present in the newly created file :',file_txt)'''


  ml='''from sentence_transformers import SentenceTransformer, util
import torch
from sourcepatterndata import SourcePatternData
import os

def removingtimestamp(text):
  text_list=text.split()
  text_val=[]
  for i in text_list:
    if (len(i)==11 and i[0]=='[' and i[-1]!=']') or (len(i)==13 and i[0]!='['and i[-1]==']'):
      pass
    else:
      text_val.append(i)
  return ' '.join(text_val)

error_raw_data=SourcePatternData.source_data()

check_model= SentenceTransformer('all-MiniLM-L6-v2')

error_clean_data={}
for i,j in error_raw_data.items():
  timestampremovaldata= [removingtimestamp(k) for k in j]
  error_clean_data[i]=check_model.encode(timestampremovaldata,convert_to_tensor=True)

def finding_suitable_solution(text):
  text1=removingtimestamp(text)
  print(text1)
  converted_data=check_model.encode(text1,convert_to_tensor=True)
  score=0
  class_val=''
  for key,val in error_clean_data.items():
    cosine_similarity_val=util.cos_sim(converted_data,val)
    score_val=torch.max(cosine_similarity_val).item()
    #print(score_val,class_val)
    if score_val>score:
      score=score_val
      class_val=key
  return score,class_val

filename=input("insert file here")
a=open(filename,'r')
file=a.read()
error_data_text=[]
patterns=SourcePatternData.patterns_data()
for i in file.split('\n'):
  if ('Error' in i or 'error' in i or 'ERROR' in i) and (patterns[0] not in i and patterns[1] not in i and patterns[2] not in i and patterns[3] not in i and patterns[4] not in i and patterns[5] not in i and patterns[6] not in i and patterns[7] not in i and patterns[8] not in i and patterns[9] not in i and patterns[10] not in i and patterns[11] not in i and patterns[12] not in i and patterns[13] not in i and patterns[14] not in i and patterns[15] not in i):
    error_data_text.append(i)
error_text=' '.join(error_data_text)
#print(error_text)
score_val,class_val=finding_suitable_solution(error_text)

if class_val=='DTM ERROR FOR COLUMNS' and score_val>0.9:
  print("it is ",score_val*100," sure it is because",class_val,"check the column datatypes and precisions in the lookup/join condition")
else:
  print(score_val*100,' percent sure it is due to',class_val )'''

  def code_val(self):
    return a
  def ml_code(self):
    return ml