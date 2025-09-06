'''
builder module for cocup.
This module contains functions for building the architechture of the new package
'''

import os
import shutil
from datetime import date

def create_script_from_template(template_path, dest_path, context):
    """
    template_path: path to template file
    dest_path: output path for new script
    context: dict with placeholder replacements, e.g., {"project_name": "cocup"}
    """
    with open(template_path) as file:
        content = file.read()

    for key, value in context.items():
        content = content.replace(f"{{{key}}}", value)

    with open(dest_path, "w") as file:
        file.write(content)

def scripts(args):
    '''
    build scripts from templates
    '''
    templates_path = os.path.join(os.path.dirname(__file__), 'templates')
    #build main
    create_script_from_template(
        os.path.join(templates_path, 'python/main.py'),
        os.path.join(args.project_name, 'main.py'),
        {
            "project_name": args.project_name
        }
    )
    #build parser
    create_script_from_template(
        os.path.join(templates_path, 'python/parser.py'),
        os.path.join(args.project_name, 'parser/parser.py'),
        {
            "project_name": args.project_name,
            "description": args.description,
            "author": args.author,
            "year": str(date.today().year)
        }
    )
    #build errors()
    create_script_from_template(
        os.path.join(templates_path, 'python/errors.py'),
        os.path.join(args.project_name, 'utils/errors.py'),
        {
            "project_name": args.project_name,
            "capitalised_project_name" : args.project_name.capitalize()
            #capitalised for class name
        }
    )

    #build.logging()

def gitignore():
    '''
    copy the gitignore from the templates/misc dir
    '''
    source_path = os.path.join(os.path.dirname(__file__), 'templates/misc/gitignore')
    dest_path = os.path.join(os.getcwd(), ".gitignore")
    shutil.copyfile(source_path, dest_path)

def licenses(license_path: str) -> None:
    '''
    copy a license from the license_templates directory to the new project
        argumets:
            license_path: the name of the license file from the parser
        returns:
            None
    '''
    source_path = os.path.join(os.path.dirname(__file__), 'templates/licenses', license_path)
    dest_path = os.path.join(os.getcwd(), "LICENSE")
    shutil.copyfile(source_path, dest_path)

def readme(project_name, description):
    '''
    add README.md to directory
        arguments:
            project name: the name of the package
            descriptiom: the packages description
    '''
    writelines = [
        f'#{project_name}: {description}',
        '##Description',
        description,
        '\n'
        '##Installation',
        'WIP',
        '\n'
        '##Usage',
        'WIP',
        '\n'
        '##Citation',
        'TBC'
    ]
    with open('README.md', "w") as file:
        for line in writelines:
            file.write(line + "\n")

def setup(project_name, description, author, email, requirements):
    '''
    add setup.py to the directory
        arguments:
        returns:
            None
    '''
    template_path = os.path.join(os.path.dirname(__file__), 'templates/python/setup.py')
    requirements_str = ',\n'.join(["'" + req + "'" for req in requirements.split(',')])
    print(requirements_str)
    create_script_from_template(
        template_path,
        'setup.py',
        {
            "project_name": project_name,
            "description": description,
            "author": author,
            "email": email,
            "requirements":  requirements_str
        }
    )


def scaffold(project_name: str) -> None:
    '''
    makes the directories for the new package
        arguments:
            project_name: the name for the new project
        returns:
            None
    '''
    print(f'make scaffold for {project_name}')
    project_dirs = [
        project_name,
        f"{project_name}/parser",
        f"{project_name}/utils",
        f"{project_name}/tests",
        "example_data/example_in",
        "example_data/example_out"
    ]

    project_files = [
        f"{project_name}/__init__.py",
        f"{project_name}/__main__.py",
        f"{project_name}/parser/__init__.py",
        f"{project_name}/utils/__init__.py",
    ]

    for directory in project_dirs:
        path = os.path.join(directory)
        os.makedirs(path)

    for file in project_files:
        open(file, 'a').close()
