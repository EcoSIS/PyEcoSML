import sys
import yaml
from os import path, getcwd
import transform
import argparse

ECOSML_CONF_FILE = 'ecosml.yml'

def main():
  parser = argparse.ArgumentParser(description='EcoSML Python CLI', add_help=False)
  args, unknown = get_base_args(parser)
  # package = sys.argv[1]

  if not path.isabs(args.package):
    args.package = path.normpath(path.join(getcwd(), args.package))
  if not path.isabs(args.spectra):
    args.spectra = path.normpath(path.join(getcwd(), args.spectra))

  
  config = get_config(args.package)
  custom_args = get_custom_args(config, parser)

  print getattr(custom_args, 'bands')

  # transform.run(config, args)

def get_base_args(parser):
  parser.add_argument('package', help='Path to PLSR package to use')
  parser.add_argument('--spectra', action='store', help='spectra input file', required=True)
  return parser.parse_known_args()

def get_custom_args(config, parser):
  parserc = argparse.ArgumentParser(parents=[parser])
  for arg in config['transform']['arguments']:
    key = arg.keys()[0]
    print key
    parserc.add_argument('--%s' % key, required=True)
  
  return parserc.parse_args()

def get_config(packageDir):
  config_path = path.join(packageDir, ECOSML_CONF_FILE)
  if not path.isfile(config_path):
    raise Exception('Package %s does not contain a config %s file' % (packageDir, ECOSML_CONF_FILE))

  with open(config_path, 'r') as stream:
    config = yaml.load(stream)

  config['root_path'] = packageDir

  normalizeConfigPath(packageDir, config, 'main', 'main', 'Package does not define a main class')
  normalizeConfigPath(packageDir, config, 'coefficients', 'coefficients', 'Package does not define a coefficients files')

  if 'transform' in config:
    normalizeConfigPath(packageDir, config['transform'], 'file', 'transform', 'Package does not define a transform class')
  
  if 'examples' in config:
    for key in config['examples']:
      example = config['examples'][key]
      if 'arguments' in example:
        example['arguments'] = {}
      
      example['arguments']['source_folder'] = path.join(packageDir, 'examples', 'source')
      example['arguments']['output_folder'] = path.join(packageDir, 'examples', 'output')

  return config

def normalizeConfigPath(packageDir, root, value, subpath, errormsg):
  if not value in root:
    raise Exception(errormsg)

  root[value] = path.join(packageDir, subpath, root[value])
  if not path.isfile(root[value]):
    raise Exception('%s defined in config is not found' % root[value])

if __name__ == "__main__":
    main()