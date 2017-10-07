import importlib, sys, re
from os import path
from pandas import read_csv

def run(ecosml_config, args):

  print 'Running main module for package'
  sys.path.append(path.join(ecosml_config['root_path'], 'main'))
  modulename = re.sub(r'\.py$', '', path.basename(ecosml_config['main']), flags=re.IGNORECASE)

  # read in spectra
  normalized_spectra = read_csv(ecosml_config['transform']['results'])

  # import transform module
  main_module = importlib.import_module(modulename)
  # run module transform fn
  outputDF = main_module.run(normalized_spectra, path.join(ecosml_config['root_path'], 'coefficients'))

  # save output
  resultsFile = path.join(args.output, 'ecosml_results.csv')
  outputDF.to_csv(resultsFile, index=False)