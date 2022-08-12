#!/usr/bin/python

import errno
import json
import os
import re
import yaml

GITHUB_REPOSITORY_URL = 'https://github.com/camunda/portainer-templates'
GITHUB_REPOSITORY_BRANCH = 'master'

# via http://pyyaml.org/ticket/64 and http://signal0.com/2013/02/06/disabling_aliases_in_pyyaml.html
class ListIndentingDumper(yaml.Dumper):
  def increase_indent(self, flow=False, indentless=False):
    return super(ListIndentingDumper, self).increase_indent(flow, False)

  def ignore_aliases(self, data):
    return True

def mkdir_p(path):
  try:
    os.makedirs(path)
  except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise

def get_folder(old_template):
  return re.sub('[^a-z0-9.-]', '-', old_template['image'].lower())

def get_image(old_template):
  if 'registry' in old_template:
    # Private registries can be used successfully in stack templates,
    # so convert from anonymousproxy which has to be used for container templates
    # TODO: eventually we can drop container templates successfully if stack templates work fine!
    if old_template['registry'] == 'registry.camunda.cloud/team-cambpm':
      if old_template['image'].startswith('camunda-ci-websphere:'): # or old_template['image'].startswith('camunda-ci-weblogic:'):
        return "registry.camunda.cloud/team-cambpm/%s-port" % old_template['image']
      else:
        return "registry.camunda.cloud/team-cambpm/%s" % old_template['image']
    else:
      return "%s/%s" % (old_template['registry'], old_template['image'])
  else:
    return old_template['image']

def generate_docker_stack(old_template, file):
  stack = {
    'version': '3',
    'services': {
      'main': {
        'image': str(get_image(old_template)),
        'restart': str(old_template['restart_policy']),
        'ports': [str(p) for p in old_template['ports']],
        'environment': [],
        'deploy': {
          'restart_policy': {
            'condition': str(old_template['restart_policy'])
          }
        }
      }
    }
  }
  if old_template['image'].startswith('camunda-ci-websphere:'):
    stack['services']['main']['environment'].append("WAS_ADMINHOST_PORT=9060")
    stack['services']['main']['environment'].append("WAS_DEFAULTHOST_PORT=9080")
  # if old_template['image'].startswith('camunda-ci-weblogic:'):
  #   stack['services']['main']['environment'] = [
  #     "WL_ADMINSERVER_PORT=7001"
  #   ]
  if 'command' in old_template:
    stack['services']['main']['command'] = str(old_template['command'])

  if 'env' in old_template:
    for entry in old_template['env']:
      # workaround for bug in the old templates where default parameter got assigned as the label
      if entry['name'] == 'TRANSACTION_ISOLATION_LEVEL':
        stack['services']['main']['environment'].append('TRANSACTION_ISOLATION_LEVEL=${TRANSACTION_ISOLATION_LEVEL:-REPEATABLE-READ}')
      else:
        stack['services']['main']['environment'].append('{0}=${{{0}}}'.format(entry['name']))

  # Docker Swarm Mode does not support privileged flag yet,
  # see: https://github.com/moby/moby/issues/24862
  # if old_template.has_key('privileged'):
  #   stack['services']['main']['privileged'] = old_template['privileged']

  yaml.dump(stack, file, Dumper=ListIndentingDumper, default_flow_style=False, explicit_start=True)

def fix_env_label(label):
  if not 'set' in label:
    return label
  else:
    value_set = label.pop('set')
    label['default'] = value_set
    label['preset'] = True
    return label

def generate_portainer_container_template(old_template):
  list_link = '{0}/blob/{1}/stack-templates.json'.format(GITHUB_REPOSITORY_URL, GITHUB_REPOSITORY_BRANCH)

  old_template['note'] = 'List: <a href="{0}">{0}</a>'.format(list_link)

  # fix env section for new set syntax
  if 'env' in old_template:
    old_template['env'] = [fix_env_label(label) for label in old_template['env']]

  return old_template

def generate_portainer_stack_template(old_template):
  folder = get_folder(old_template)

  list_link = '{0}/blob/{1}/stack-templates.json'.format(GITHUB_REPOSITORY_URL, GITHUB_REPOSITORY_BRANCH)
  source_link = '{0}/blob/{1}/stacks/{2}/docker-stack.yml'.format(GITHUB_REPOSITORY_URL, GITHUB_REPOSITORY_BRANCH, folder)

  template = {
    'type': 2,
    'title': old_template['title'],
    'description': old_template['description'],
    'note': 'List: <a href="{0}">{0}</a><br/>Source: <a href="{1}">{1}</a>'.format(list_link, source_link),
    'categories': old_template['categories'],
    'platform': old_template['platform'],
    'logo': old_template['logo'],
    'repository': {
      'url': GITHUB_REPOSITORY_URL,
      'stackfile': 'stacks/{0}/docker-stack.yml'.format(folder)
    }
  }

  # fix env section for new set syntax
  if 'env' in old_template:
    template['env'] = [fix_env_label(label) for label in old_template['env']]
    template['env'] = old_template['env']

  return template

if __name__ == '__main__':
  with open('templates.json', 'r') as f:
    old_templates = json.load(f)

  new_templates = []

  with open('new-stack-templates.json', 'r') as f:
    new_templates.extend(json.load(f))

  for old_template in old_templates:
    if ('privileged' in old_template) and old_template['privileged']:
      # Use container templates Docker Swarm Mode does not support privileged flag yet
      new_templates.append(generate_portainer_container_template(old_template))
    else:
      folder = get_folder(old_template)

      mkdir_p('stacks/%s' % folder)
      with open('stacks/%s/docker-stack.yml' % folder, 'w') as f:
        generate_docker_stack(old_template, f)

      new_templates.append(generate_portainer_stack_template(old_template))

  with open('stack-templates.json', 'w') as f:
    json.dump(new_templates, f, sort_keys=True, indent=2)
    f.write("\n")
