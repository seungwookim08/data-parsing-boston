import requests, bs4, os, csv, re, pandas
from csv import writer
import numpy as np

class DataParser:
  def __init__(self):
    self.file_name = 'parsed_result-demo.csv'
    self.kijiji_url =  'https://www.kijiji.ca/b-a-louer/ville-de-montreal/c30349001l1700281'

  def data_parse(self):
    with open(self.file_name, 'w+') as output_file:
      open_writer = writer(output_file, delimiter=',')
      open_writer.writerow(["Title", "Price", "Address", "Bathroom", "Room", "Furnished", "Pet Allowed"])
    res = requests.get(self.kijiji_url)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    number_of_elements = len(soup.select('div .info-container'))
    start = 0
    while start < 1000:
      for i in range(number_of_elements):
        try:
          titles = soup.select('div .info-container > .title > a')
          title = titles[i].getText()
          title = title.replace("\n", "")
          title = title.replace(",", " ") 
          title = re.sub(r'\s+', ' ', title)
          title = title.replace("\\\\", "\\") 
          title = title.strip()

          sublink = 'http://www.kijiji.ca' + titles[i].get('href')
          res = requests.get(sublink)
          subsoup = bs4.BeautifulSoup(res.text, "html.parser")  
          price = subsoup.select_one('span[class*="currentPrice"]').text
          price = price.replace(",", ".")
          price = re.sub(r'\s+', '', price)
          price = price.replace("$", "")
          price = price.strip()

          address = subsoup.select_one('span[itemprop="address"]').text
          address = address.replace(",", " ")
          address = re.sub(r'\s+', ' ', address)
          try:
            child_bathroom = subsoup.find(text=re.compile('Salles de bain')).parent
            bathroom = re.findall('\d+', child_bathroom.parent.select_one('dd').text)[0]
          except:
            bathroom = 'Unknown'
          try:
            child_room = subsoup.find(text=re.compile('Chambres')).parent
            room = child_room.parent.select_one('dd').text
          except:
            room = 'Unknown'
          try:
              child_furnished = subsoup.find(text=re.compile('Meublé')).parent
              furnished = child_furnished.parent.select_one('dd').text
          except:
              furnished = 'Unknown'

          try:
              child_animal = subsoup.find(text=re.compile('Animaux acceptés')).parent
              animal = child_animal.parent.select_one('dd').text
          except:
              animal = 'Unknown'
        except Exception as e:
          print(e)
        val_array = [title, price, address, bathroom, room, furnished, animal]
        for elem in val_array:
          elem = elem.strip()
        with open(self.file_name, "a", encoding='UTF-8') as output_file:
          csv_writer = writer(output_file, delimiter=',')
          csv_writer.writerow(val_array)
      nextpageLink = soup.select('a[title="Suivante"]')[0]
      url = 'http://www.kijiji.ca' + nextpageLink.get('href')
      res = requests.get(url)
      soup = bs4.BeautifulSoup(res.text, "html.parser")
    output_file.close()

  def csv_extractor(self):
    df = pandas.read_csv(self.file_name,delimiter=',')
    df = df[['Address','Price']]

    df['Postal Code'] = df['Address'].str.extract(r'([a-zA-Z][0-9][a-zA-Z])')
    df['Postal Code'] = df['Postal Code'].str.upper()
    df['Price'] = df['Price'].str.extract(r'(\d+\.\d{2})')
    df = df[['Postal Code','Price']]
    df.dropna(subset=['Postal Code'], inplace=True)
    df.dropna(subset=['Price'], inplace=True)
    df['Price'] = df['Price'].astype(float)

    df = df.groupby('Postal Code', as_index=False).mean()
    df = df[df['Price'] > 500]  
    df = df[df['Price'] < 3000]  

    df.to_csv(self.file_name.replace('.csv', '_price_by_postal.csv'), index=False)
    df.to_csv('./front-end/src/assets/parsed_result.csv', index=False)