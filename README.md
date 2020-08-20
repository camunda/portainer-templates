# Portainer Templates

There are two types of [Portainer](https://www.portainer.io/) templates:

- type `stack`: the new type that uses [Docker stack](https://docs.docker.com/engine/swarm/stack-deploy/) under the hood and is better to use on Portainer
- type `container`: the old type that can only start one container, **discouraged to use** except if the `stack` type is too limited (e.g. old DB2 and old MSSQL server containers need more priviliges that only the `container` type can provide)

## How to create a new `stack` type template

A `stack` type template consists of two things:

1. a YAML file in the [Docker stack](https://docs.docker.com/engine/swarm/stack-deploy/) format that contains definitions like which container(s) to start on which ports, by our convention always named `docker-stack.yml` (to avoid [confusion with Docker Compose](https://vsupalov.com/difference-docker-compose-and-docker-stack/))
2. an entry in the `new-stack-templates.json` that includes some metadata about the template and makes the Docker stack YAML file available in Portainer UI

To create a new one:

1. In the `stacks` directory create a new subdirectory with the name of your stack (please follow existing naming scheme) and create a new `docker-stack.yml` inside that subdirectory or duplicate an existing subdirectory and modify the included `docker-stack.yml` with different Docker image or ports etc.
2. Edit the file `new-stack-templates.json` to create or duplicate an entry and supply metadata as required, minimum is changed `title` and `description` fields (for Portainer UI) and the correct path in `stackfile` field!
3. Run `python3 generate-stack-templates.py` to regenerate the `stack-templates.json` which is the definitive file consumed by Portainer
4. Create a new branch (e.g. use JIRA issue number), check in all modified/new files e.g. via `git add .`
5. Push the new commit and open a [Pull Request](https://github.com/camunda/portainer-templates/pulls)
6. When the PR is merged it may take some minutes for the change to be available in Portainer UI (due to Github caching)

## How to modify an existing `stack` type template

1. Modify a `docker-stack.yml` or the file `new-stack-templates.json` as needed
2. Run `python3 generate-stack-templates.py` to regenerate the `stack-templates.json` which is the definitive file consumed by Portainer
3. Create a new branch (e.g. use JIRA issue number), check in all modified/new files e.g. via `git add .`
4. Push the new commit and open a [Pull Request](https://github.com/camunda/portainer-templates/pulls)
5. When the PR is merged it may take some minutes for the change to be available in Portainer UI (due to Github caching)
