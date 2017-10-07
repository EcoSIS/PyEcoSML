import sys
import yaml
from os import path, getcwd
import transform, run
import argparse

ECOSML_CONF_FILE = ['ecosml.yml', 'ecosis.yaml']

def main():
  # preparser, we need the transform arguments from this file before we know what to print in cli
  # options
  package_parser = argparse.ArgumentParser(description='EcoSML Python CLI', add_help=False)
  package_parser.add_argument('package', nargs='?', help='Path to PLSR package to use')
  package_parser.add_argument('--transform', '-t', action='store', help='Custom transform input spectra', required=False)
  package_args, unknown = package_parser.parse_known_args()

  # if a package was given, read in the EcoSML file
  config = None
  if package_args.package is not None:
    if not path.isabs(package_args.package):
      package_args.package = path.normpath(path.join(getcwd(), package_args.package))
    config = get_config(package_args.package)

  # Generate custom cli and actually fire off a 'for real' argparser
  args = get_custom_args(config, package_args.transform)

  # normalize some more paths
  if not path.isabs(args.spectra):
    args.spectra = path.normpath(path.join(getcwd(), args.spectra))
  if not path.isfile(args.spectra):
    print 'Input spectra file does not exist: %s' % args.spectra
    exit(1)

  if not path.isabs(args.output):
    args.output = path.normpath(path.join(getcwd(), args.output))
  if not path.exists(args.output):
    print 'Output directory does not exist: %s' % args.output
    exit(1)

  # run the desired transforms
  transform.run(config, args)
  # run main module
  run.run(config, args)

def get_custom_args(config, custom_transform_file):
  parser = argparse.ArgumentParser(description='EcoSML Python CLI', add_help=True)

  parser.add_argument('package', help='Path to PLSR package to use')
  parser.add_argument('--spectra', '-s', action='store', help='spectra input file', required=True)
  parser.add_argument('--transform', '-t', action='store', help='Custom transform for input spectra', required=False)
  parser.add_argument('--output', '-o', action='store', help='Output directory', required=True)

  if config is not None:
    if not custom_transform_file:
      for arg in config['transform']['arguments']:
        key = arg.keys()[0]
        parser.add_argument('--%s' % key, required=True)
    else:
      config['transform']['custom'] = True
      config['transform']['file'] = custom_transform_file
      if not path.isabs(config['transform']['file']):
        config['transform']['file'] = path.normpath(path.join(getcwd(), config['transform']['file']))

  return parser.parse_args()

# read in ecosis.yml file
# normalize paths
def get_config(packageDir):
  config_path = path.join(packageDir, ECOSML_CONF_FILE[0])
  if not path.isfile(config_path):
    config_path = path.join(packageDir, ECOSML_CONF_FILE[1])
    if not path.isfile(config_path):
      raise Exception('Package %s does not contain a config %s file' % (packageDir, ECOSML_CONF_FILE))

  with open(config_path, 'r') as stream:
    config = yaml.load(stream)

  config['root_path'] = packageDir

  normalizeConfigPath(packageDir, config, 'main', 'main', 'Package does not define a main class')
  # normalizeConfigPath(packageDir, config, 'coefficients', 'coefficients', 'Package does not define a coefficients files')

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