import numpy as np 
import requests
import json
import re
import time
import arrow
from ics import Calendar, Event
from bs4 import BeautifulSoup

c = Calendar()

def get_date(item):
    item_list=[]
    for element in item:
        item_list.append(element)
    return item_list[-1]
def get_string_list_containing_time(test_string_list):
    if len(test_string_list)<1:
        test_string_list=['None']
    count=0
    for item in test_string_list:
        am_index=item.find("am")
        pm_index=item.find("pm")
        # print(item[am_index-1])
        if item.find("function")!=-1:
            del test_string_list[count]
        if am_index!=-1 and pm_index==-1:
            if item[am_index-1].isdigit()==False:
                del test_string_list[count]
        if pm_index!=-1 and am_index==-1:
            if item[pm_index-1].isdigit()==False:
                del test_string_list[count]
        if test_string_list==[] or test_string_list=='None':
            test_string_list=['None']
        count=count+1
    return test_string_list
def split_time_strings(test_string_list):
    split_index=test_string_list[0].find("-")
    if split_index!=-1:
        if test_string_list[0].find("am")!=-1 and test_string_list[0].find("pm")!=-1:
            test_string_list.append(test_string_list[0][0:(split_index)])
            test_string_list.append(test_string_list[0][split_index:])
            # test_string_list.append('SpAn')
            test_string_list[0]='SpAn'
            return test_string_list
        elif test_string_list[0].find("am")!=-1 and test_string_list[0].find("pm")==-1:
            test_string_list.append(test_string_list[0][0:(split_index)])
            test_string_list.append(test_string_list[0][split_index:])
            # test_string_list.append('AM')
            test_string_list[0]='AM'
            return test_string_list
        elif test_string_list[0].find("am")==-1 and test_string_list[0].find("pm")!=-1:
            test_string_list.append(test_string_list[0][0:(split_index)])
            test_string_list.append(test_string_list[0][split_index:])
            # test_string_list.append('PM')
            test_string_list[0]='PM'
            return test_string_list
        else:
            print("no am or pm found but there is a -")
            return test_string_list
    else:
        test_string_list.append(test_string_list[0])
        test_string_list[0]='NO_SPLIT'
        return test_string_list

             
def get_time_string(test_string,amORpm):
    # print("test string: ", test_string, " and ", amORpm)
    index=test_string.find(amORpm)
    # print("index", index)
    return_string=test_string
    test_char=test_string[index-1]
    counter=2 
    while counter<7 and (test_char.isdigit() or test_char==':') and test_char.isspace()==False:
        # print("TEST CHAR: ", test_char)
        test_char=test_string[index-counter]
        counter=counter+1 
    counter=counter-1
    return_string=return_string[(index-counter):(index)]
    return_string=return_string.strip()
    # print("return: ", return_string)
    time_format='%I:%M%p'
    if return_string.find(":")==-1:
        return_string=return_string+":00"+amORpm
    else:
        return_string=return_string+amORpm
    # print("return: ", return_string)
    time_obj = time.strptime(return_string, time_format)
    # print("time object", time_obj)
    return_str= time.strftime('%H:%M:%S',time_obj)
    # print(return_str)
    return return_str

def get_time(href_item):
    start_time_string='None'
    end_time_string='None'
    time_URL="https://artsandscience.usask.ca"+href_item
    time_page=requests.get(time_URL)
    time_soup=BeautifulSoup(time_page.content,"lxml")
    # for tag in time_soup.body.find_all(attrs={"class":"col-md-7"}):
        # print(tag)
        # print(tag.h1)
        # print("and \n")
    time_section=time_soup.body.find_all(attrs={"class":"col-md-7"})[2]
    am_times=time_section.find_all(string=re.compile("am"))
    pm_times=time_section.find_all(string=re.compile("pm"))
    #some logic to try and deal with formatting
    am_times=get_string_list_containing_time(am_times)
    pm_times=get_string_list_containing_time(pm_times)
    am_times=split_time_strings(am_times)
    pm_times=split_time_strings(pm_times)
    if am_times[0]=='NO_SPLIT' and am_times[1]!='None':
        start_time_string=get_time_string(am_times[1],"am")
    if pm_times[0]=='NO_SPLIT' and pm_times[1]!='None':
        start_time_string=get_time_string(pm_times[1],"pm")
    if am_times[0]=='SpAn':
        start_time_string=get_time_string(am_times[1],"am")
        end_time_string=get_time_string(am_times[2],"pm")
    if am_times[0]=='AM':
        start_time_string=get_time_string(am_times[1],"am")
        end_time_string=get_time_string(am_times[2], "am")
    if pm_times[0]=='PM':
        start_time_string=get_time_string(pm_times[1],"pm")
        end_time_string=get_time_string(pm_times[2],"pm")
    # print("start time: ", start_time_string)
    # print("end time: ", end_time_string)
    return [start_time_string,end_time_string]

def process_event_name(name_string, event_filter_status):
    return_filter='None'
    if name_string.find("thesis")!=-1:
        return_filter='Def'
    if name_string.find("Seminar")!=-1:
        return_filter='990'
    print(return_filter)
    return return_filter
# class biology_event:
#     def __init__(self, name, url, event_start_date, event_start_time=None, event_end_date=None, event_end_time=None, event_duration=None):
#         self.name = name
#         self.url= url
#         self.event_start_time = event_start_time
#         self.event_start_date= event_start_date
#         self.event_end_date=event_end_date
#         self.event_end_time=event_end_time
#         self.even_duration=event_duration
#     def add_to_cal(self, e,c):
#         e.name=self.name
#         # date and time for begin must be in the form '2014-01-01 00:00:00'
#         if event_start_time!=None:
#             event_start_date_and_time=event_start_date+" "+ event_start_time
#         else:
#             event_start_date_and_time=event_start_date+" 00:00:00"
#         e.begin=event_start_date_and_time
#         if event_duration!=None:
#             if event_end_time != None and event_end_date != None:
#                 event_end_date_and_time=event_end_date+" "+event_end_time
#             else: 
#                 event_end_date_and_time=event_start_date+" "+event_end_time
#             e.end=event_end_date_and_time
#         else:
#             e.duration=event_duration
#         c.events.add(e)
#         c.events



def process_date(date_string):
    date_format = '%b %d, %Y'
    date_obj = time.strptime(date_string, date_format)
    date_str= time.strftime('%Y-%m-%d',date_obj)
    # print(date_str)
    return date_str
year_list=['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
def get_all_events(soup):
    results=soup.find_all("h2")
    # print(results)
    # print("For the first result:\n")
    # todays_events=results[0]
    # ongoing_events=results[1]
    # upcoming_events=results[2]

    # all_p=all_events.find_all("p")
    # print(todays_events.parent.prettify())
    # print("Parents: \n")
    # print(ongoing_events.parent)
    # print("SIBLINGS: \n")
    # print(upcoming_events.next_child)
    # print("THE DIVS: ")
    data_soup=soup.find_all(attrs={"class": "col-md-8"})
    i=0
    for tag in soup.find_all(attrs={"class": "col-md-8"}):
        i=i+1
        print(i," element : ")
        event_filter_status='None'
        start_date='None'
        end_date='None'
        event_name=tag.h3.string
        event_page=tag.a['href']
        event_URL="https://artsandscience.usask.ca"+str(event_page)
        print("Event: ", event_name)
        # print(tag.a['href'])
        event_time=get_time(event_page)
        # for element in tag.small:
            # print(element)
        # print(get_date(tag.small))
        date_string=str(get_date(tag.small))
        date_string=date_string.lstrip()
        print(date_string)
        start_date=date_string
        if date_string.find("-")!=-1:
            start=0
            end=0
            date=date_string
            year_end=date_string[-6:]
            # print("Year end: ", year_end)
            str_index_start_dig1=date[int(date.find("-"))-2]
            str_index_start_dig2=date[int(date.find("-"))-1]
            str_index_end_dig1=date[int(date.find("-"))+1]
            str_index_end_dig2=date[int(date.find("-"))+2]
            if(str_index_start_dig1.isspace()):
                start=int(str_index_start_dig2)
            else:
                start=int(str_index_start_dig1+str_index_start_dig2)
            if(str_index_end_dig2.isspace()):
                end=int(str_index_end_dig1)
                end_date=date[0:4]+str(end)+year_end
            elif str_index_end_dig1.isalpha():
                possible_date=date[str_index_end_dig1:str_index_end_dig1+6]
                for i in range(len(year_list)):
                    if(possible_date.find(year_list[i])!=-1):
                        end_date=possible_date+year_end
            elif str_index_end_dig1.isdigit():
                end=int(str_index_end_dig1)
                end_date=date[0:4]+str(end)+year_end
                if str_index_end_dig2.isdigit():
                    end=int(str_index_end_dig1+str_index_end_dig2)
                    end_date=date[0:4]+str(end)+year_end
            else:
                end='None'
                print("Weird formatting found!")
            start_date=date[0:4]+str(start)+year_end
        print(start_date,", ",end_date)
        start_date=process_date(start_date)
        if end_date!='None':
            end_date=process_date(end_date)
        print("event time: ", event_time)
        print("start_date: ", start_date)
        print("end_date: ", end_date)
        e = Event()
        event_filter_status=process_event_name(event_name,event_filter_status)
        if event_time[0]=='None':
            if end_date!='None':
                start=start_date+" 09:00:00"
                end = end_date+ " 17:00:00"
                make_event_two_dates(e,c,event_name,event_URL,start,end)
            else:
                if event_filter_status!='None':
                    if event_filter_status=='990':
                        start=start_date+' 11:45:00'
                        duration=1
                        make_event_duration(e,c,event_name,event_URL,start,duration)
                else:
                    start=start_date+" 09:00:00"
                    end = start_date+ " 17:00:00"
                    make_event_two_dates(e,c,event_name,event_URL,start,end)
        else:
            if end_date=='None':
                if event_time[1]!='None':
                    start=start_date+" "+event_time[0]
                    end = start_date+" "+event_time[1]
                    make_event_two_dates(e,c,event_name,event_URL,start,end)
                else:
                    if event_filter_status!='None':
                        if event_filter_status=='990':
                            start=start_date+" "+event_time[0]
                            duration=1
                            make_event_duration(e,c,event_name,event_URL,start,duration)
                        elif event_filter_status=='Def':
                            start=start_date+" "+event_time[0]
                            duration=3
                            make_event_duration(e,c,event_name,event_URL,start,duration)
                        else:
                            print("BAD EVENT FILTER!!")
                            start=start_date+" 09:00:00"
                            duration=1
                            make_event_duration(e,c,event_name,event_URL,start,duration)
                    else:
                        start=start_date+" 09:00:00"
                        duration=1
                        make_event_duration(e,c,event_name,event_URL,start,duration)
            else:
                if event_time[1]!='None':
                    start=start_date+" "+event_time[0]
                    end=end_date+" "+event_time[1]
                    make_event_two_dates(e,c,event_name,event_URL,start,end)
                else:
                    start=start_date+" "+event_time[0]
                    end=end_date+" 17:00:00"
                    make_event_two_dates(e,c,event_name,event_URL,start,end)

def make_event_two_dates(ev,cal,name,url,start,end):
    start=arrow.get(start, 'YYYY-MM-DD HH:mm:ss')
    start.replace(tzinfo='Canada/Saskatchewan')
    end=arrow.get(end, 'YYYY-MM-DD HH:mm:ss')
    end.replace(tzinfo='Canada/Saskatchewan')
    print(start)
    ev.name=name
    ev.begin=start
    ev.end=end
    ev.last_modified=arrow.now('Canada/Saskatchewan')
    ev.url=url
    cal.events.add(ev)
    print("Name: ",name,"Start: ",start,"End: ", end)
def make_event_duration(ev,cal,name,url,start,duration):
    start=arrow.get(start, 'YYYY-MM-DD HH:mm:ss')
    start.replace(tzinfo='Canada/Saskatchewan')
    ending={"hours":duration}
    ev.name=name
    ev.begin=start
    ev.duration=ending
    ev.last_modified=arrow.now('Canada/Saskatchewan')
    ev.url=url
    cal.events.add(ev)
    print("Duration", duration)
    # print(cal.events)
def generate_update_cal(old_file,new_file):       
    old_cal = open(old_file, "rt")
    new_cal = open(new_file, "rt")
    add_cal = open("cal_updates.ics",'wt')
    for line1 in new_cal:
        for line2 in old_cal:
            if line1.strip("\n")!=line2:
                add_cal.write(line1)
    old_cal.close()
    new_cal.close()
    add_cal.close()

# #close input and output files
#     calendrier.close()
#     cal.close()
def get_events_from_many_months():
    URL_start="https://artsandscience.usask.ca/biology/news/events.php"
    URL_list=['','?d=2024-01-01','?d=2024-02-01', '?d=2024-03-01', '?d=2024-04-01', '?d=2024-05-01', '?d=2024-06-01', '?d=2024-07-01']
    for url in range(len(URL_list)):
        URL=URL_start+URL_list[url]
        print(url)
        page=requests.get(URL)
        # print(page.text)

        soup= BeautifulSoup(page.content,"lxml")
        # print(soup.prettify)
        # print(data_soup)
        i=0
        get_all_events(soup)
def make_cal(cal):
    cal.events
    with open('utc_notimezone_cal.ics','w') as f:
        f.writelines(c.serialize_iter())
    cal.serialize()
    #input file to fix the fucking time zones
    calendrier = open("utc_notimezone_cal.ics", "rt")
    #output file to write the result to
    cal = open("bio_cal_v2.ics", "wt")
    #for each line in the input file
    for line in calendrier:
            cal.write(line.replace('Z', ''))
    calendrier.close()
    cal.close()
def main():
    get_events_from_many_months()
    print(c.events)
    make_cal(c)
if __name__ == "__main__":
    main()
