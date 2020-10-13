#!/bin/python
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta , date
import re

def get_soup(url):
    '''
    Get the html soup
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def remove_extra_chars(ds): 
    '''
    Input string 

    Remove pesky st,th,rd,nd from dates

    return string
    '''                                            
    return re.sub(r'(\d)(st|nd|rd|th)', r'\1', ds)

def try_parsing_date(text):
    
    # add more formats as oddbox decide
    for fmt in ("%d%b%Y", "%d%B%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

def get_date_page(soup, day_of_week, baseurl):
    '''
    Input 
        : soup <BeautifulSoup object>
        : day_of_week <int> 0 = Monday
    
    Hack the website.

    '''
    # Hope this doesn't change!
    job_elems = soup.find_all(class_="BlogList-item-title")
    
    for job_elem in job_elems:
        text = (job_elem.text)
        url = job_elem['href'].split('/')[2]
        text  = remove_extra_chars(text)
        text = (text.split('-')[1].replace(' ',''))
        
        last_box_day = try_parsing_date(text)

        first_box_day = last_box_day - timedelta(days=6)
        
        d = date.today()
        if d.weekday() == day_of_week:
            d += timedelta(7)
        else:
            while d.weekday() != day_of_week:
                d += timedelta(1)
        
        if first_box_day.date() < d <= last_box_day.date():
            return d, baseurl + '/' + url

def find_box(soup, box_type, box_size):
    boxes = []
    # let's hope strong formatting doesn't change 
    for elem2 in soup.findAll("strong", text=box_size+":"):
        boxes.append([elem2.next.next.text])
    
    fruit_veg_box = boxes[0][0]
    fruit_veg_box = fruit_veg_box.replace('*', '') 

    try:
        veg_box = boxes[1][0]
        veg_box = veg_box.replace('*', '')
    except IndexError:
        return fruit_veg_box
    
    if box_type == "Fruit And Veg":
        return re.sub("[\(\[].*?[\)\]]", "", fruit_veg_box)
    
    if box_type == "Veg":
        return re.sub("[\(\[].*?[\)\]]", "", veg_box)
    
def main(box_type, box_size, delivery_day = datetime.now().weekday()):
    '''
    Input  
        box_type:
            Fruit and Veg
            Veg
            Fruit Booster
        box_size:
            Large
            Medium 
            Small
        delivery_day:
            Default Current day (so next week)
    '''
    baseurl = 'https://www.oddbox.co.uk/box-contents'
    soup = get_soup(baseurl)

    date, mainpage = get_date_page(soup, delivery_day, baseurl)
    soup2 = get_soup(mainpage)

    return find_box(soup2, box_type.title() , box_size.title())

print (main("fruit and veg", "large"))