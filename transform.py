import importlib, sys, re
from os import path
from pandas import read_csv

def run(ecosml_config, args):
  sys.path.append(ecosml_config['root_path']+'/transform')
  
  modulename = re.sub(r'\.py$', '', path.basename(ecosml_config['transform']['file']), flags=re.IGNORECASE)

  spectra = read_csv(args.spectra)

  transform_module = importlib.import_module(modulename)
  transform_module.transform(spectra)