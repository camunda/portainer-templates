# Portainer Templates

## How to create a new stack 

1. in `stacks`, duplicate the entry you want to duplicate, then make modifications like docker image etc. 
2. Edit the file `new-stack-templates.json`, copy & paste an old entry and make the modifications as required.
3. run `python3 generate-stack-templates.py` and cross your fingers - this will regenerate `stack-templates.json`
4. `git add .` all modified/new files to the index 
5. commit and push to a new branch and file a Pull Request

