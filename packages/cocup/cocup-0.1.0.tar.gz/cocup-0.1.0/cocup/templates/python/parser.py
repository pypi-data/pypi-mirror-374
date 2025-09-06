'''
parser for {project_name}
'''
import argparse
import logging
from argparse import RawTextHelpFormatter

def get_parser():
    '''
    create a parser object for {project_name}
    '''
    parser = argparse.ArgumentParser(
        "{project_name}",
        description="{project_name}: {description}",
        epilog="Written by {author}, {year}.",
        formatter_class=RawTextHelpFormatter
        )
    parser.add_argument(
      'example_argument',
      type=str,
      default='example',
      help=('an example positional parameter')
    )
    parser.add_argument(
      '-e', '--example2',
      type=str,
      default='example',
      help=('an example of an optional paramater')
    )
    return parser
def get_config_parser(arg_parser):
    '''
    Create an argument group for basic config details.
        Arguments:
            arg_parser: the basic argument parser
        Returns:
            arg_parser: the argument parser with arguments added
    '''
    config_parser = arg_parser.add_argument_group(
            'basic configuration', 'basic configuration of {project_name}'
            )
    config_parser.add_argument(
        '-l',
        '--logging',
        default='ERROR',
        choices=[
            logging.getLevelName(level) for level in [
               logging.DEBUG, logging.ERROR, logging.INFO, logging.WARNING
               ]
            ],
        help='set the logging level\n'
        '(default: %(default)s)'
    )
    return arg_parser
  

def parse_args():
  '''
  get the arguments from the console via the parser
  '''
  arg_parser = get_parser()
  get_config_parser(arg_parser)
  args = arg_parser.parse_args()
  return args
