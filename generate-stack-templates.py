#!/usr/bin/python

import errno
import json
import os
import re
import yaml

GITHUB_REPOSITORY_URL = 'https://github.com/camunda-ci/portainer-templates'
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
  if old_template.has_key('registry'):
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
        'deploy': {
          'restart_policy': {
            'condition': str(old_template['restart_policy'])
          }
        }
      }
    }
  }
  if old_template.has_key('command'):
    stack['services']['main']['command'] = str(old_template['command'])
  if old_template.has_key('privileged'):
    stack['services']['main']['privileged'] = old_template['privileged']
  yaml.dump(stack, file, Dumper=ListIndentingDumper, default_flow_style=False, explicit_start=True)

def fix_env_label(label):
  if not label.has_key('set'):
    return label
  else:
    value_set = label.pop('set')
    label['select'] = [{'text': value, 'value': value} for value in value_set.split(',')]
    label['select'][0]['default'] = True
    return label

def generate_portainer_template(old_template):
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

  # fix env section for new select syntax
  if old_template.has_key('env'):
    template['env'] = [fix_env_label(label) for label in old_template['env']]

  return template

if __name__ == '__main__':
  with open('templates.json', 'r') as f:
    old_templates = json.load(f)

  new_templates = []

  for old_template in old_templates:
    folder = get_folder(old_template)

    mkdir_p('stacks/%s' % folder)
    with open('stacks/%s/docker-stack.yml' % folder, 'w') as f:
      generate_docker_stack(old_template, f)

    new_templates.append(generate_portainer_template(old_template))

  with open('stack-templates.json', 'w') as f:
    json.dump(new_templates, f, sort_keys=True, indent=2)
