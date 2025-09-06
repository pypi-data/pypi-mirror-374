'''
the arg parser for cocup
'''
import argparse
import os
from argparse import RawTextHelpFormatter

def available_licenses():
    '''
    find available licenses for the parser
    '''
    package_dir = os.path.dirname(os.path.dirname(__file__))
    templates_dir = os.path.join(package_dir, 'templates/licenses')
    licenses = os.listdir(templates_dir)
    return licenses

def get_parser():
    '''
    create a parser object for cocup
    '''
    parser = argparse.ArgumentParser(
        "cocup",
        description="cocup: Thom's COokie CUtter for Python",
        epilog="Written by Dr. Thom Booth, 2025.",
        formatter_class=RawTextHelpFormatter
        )
    parser.add_argument(
      'project_name',
      type=str
    )
    parser.add_argument(
      'description',
      type=str
    )
    parser.add_argument(
      '-a', '--author',
      default='annonymous',
      type=str
    )
    parser.add_argument(
      '-e', '--email',
      default='example@email.com',
      type=str
    )
    parser.add_argument(
      '-r', '--requirements',
      default='[]',
      type=str
    )
    parser.add_argument(
      '-l', '--license',
      choices=available_licenses(),
      help=(
      "IMPORTANT: Always check the license before publishing!\n"
      "You are responsible for licensing your own software!"
      ),
      default='gpl3.txt',
      type=str
    )
    return parser

def parse_args():
    '''
    get the arguments from the console via the parser
    '''
    arg_parser = get_parser()
    args = arg_parser.parse_args()
    return args
