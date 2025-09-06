'''
this is the main routine for {project_name}
'''
import logging
from {project_name}.parser import parser

def initialize_logging() -> None:
    '''Set up and configure logging.
        Arguments: None
        Returns: None'''
    logging_level = logging.DEBUG
    logging.basicConfig(
        #filename='getphylo.log',
        level=logging_level,
        format='[%(asctime)s] %(levelname)-10s: %(message)s',
        datefmt='%H:%M:%S')
    logging.info("Running getphylo version 1.0.0.")

def main():
    '''
    main routine for {project_name}
    '''
    args = parser.parse_args()
    logging.getLogger().setLevel(args.logging)

if __name__ == "__main__":
    main()
