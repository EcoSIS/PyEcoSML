import importlib, sys, re
from os import path
from pandas import read_csv

def run(ecosml_config, args):
  if 'custom' in ecosml_config['transform']:
      print 'Using custom tranform module: %s' % ecosml_config['transform']['file']
      sys.path.append(path.dirname(ecosml_config['transform']['file']))
      modulename = re.sub(r'\.py$', '', path.basename(ecosml_config['transform']['file']), flags=re.IGNORECASE)
  else:
      print 'Running base transform for package'
      sys.path.append(path.join(ecosml_config['root_path'], 'transform'))
      modulename = re.sub(r'\.py$', '', path.basename(ecosml_config['transform']['file']), flags=re.IGNORECASE)

  # read in spectra
  spectra = read_csv(args.spectra)

  # import transform module
  transform_module = importlib.import_module(modulename)
  # run module transform fn
  outputDF = transform_module.transform(spectra, args)

  # save output
  transformFile = path.join(args.output, 'ecosml_transform_spectra.csv')
  ecosml_config['transform']['results'] = transformFile
  outputDF.to_csv(transformFile, index=False)