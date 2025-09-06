'''
main routine for CoCuP
'''

from cocup.parser import parser
from cocup import builder

def main():
    '''
    main routine for cocup
    '''
    args = parser.parse_args()
    builder.scaffold(args.project_name)
    builder.setup(
      args.project_name, args.description, args.author, args.email, args.requirements
      )
    builder.gitignore()
    builder.readme(args.project_name, args.description)
    builder.licenses(args.license)
    builder.scripts(args)

if __name__ == "__main__":
    main()
