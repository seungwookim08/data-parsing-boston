from data_parse import *

if __name__ == '__main__':
  parse = DataParser()
  # parse.data_parse() # Only use when we want to parse a data again (Takes very long time)
  parse.csv_extractor()