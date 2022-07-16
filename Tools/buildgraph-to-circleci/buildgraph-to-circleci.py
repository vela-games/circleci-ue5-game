#!/usr/bin/env python3

import json
import yaml
import argparse
import os
import sys
import importlib

from common import yaml_multiline_string_pipe, sanitize_job_name

# We create some arguments that we need to execute the script.
parser = argparse.ArgumentParser()
parser.add_argument("--json-graph", required=True, help="Path to Graph in JSON format")
parser.add_argument("--git-branch", default=os.getenv("CIRCLE_BRANCH", ""), help="Branch that triggered the pipeline")
parser.add_argument("--git-commit", default=os.getenv("CIRCLE_SHA1", ""), help="Commit that triggered the pipeline")
args = parser.parse_args()

if not args.git_branch or not args.git_commit:
  print("--git-branch and --git-commit are required. Or CIRCLE_BRANCH and CIRCLE_SHA1 variables should be defined")
  parser.print_help(sys.stderr)
  parser.exit(1)

graph = None

# Create an empty boilerplate object that we will fill with jobs for CircleCI
circleci_manifest = {
  'version': 2.1,
  'parameters': {
  },
  'jobs': {
  },
  'workflows': {
    'build-game': {
      'jobs': [
      ]
    }
  }
}

# Load the Exported JSON BuildGraph
with open(args.json_graph, "r") as stream:
    try:
        graph = json.load(stream)
    except Exception as exc:
        print(exc)

# Loop over the generated jobs
for group in graph["Groups"]:
  for node in group["Nodes"]:

    sanitized_name = sanitize_job_name(node['Name'])

    # The End node is an additional node that buildgraph creates that depends on all nodes being executing, there's no actual logic here to execute
    # so we check if we should skip.
    if "end" in sanitized_name:
      continue

    # Using reflection load the runner class defined in the 'Agent Type' field on BuildGraph
    Class = getattr(importlib.import_module("runners"), group['Agent Types'][0])
    runner = Class(args.git_branch)

    # Generate the job for this Node
    steps = runner.generate_steps(node['Name'])

    circleci_manifest['jobs'][sanitized_name] = {
      'shell': runner.shell,
      'machine': True,
      'working_directory': runner.working_directory,
      'resource_class': runner.resource_class,
      'environment': runner.environment,
      'steps': steps
    }

    job = {
      sanitized_name: {
      }
    }
    
    # Set the dependencies for each job
    if node["DependsOn"] != "":
      if not 'requires' in job[sanitized_name]:
        job[sanitized_name]['requires'] = []

      # The depdencies are in a semicolon-separated list.
      depends_on = [sanitize_job_name(d) for d in node["DependsOn"].split(";")]
      job[sanitized_name]['requires'].extend(depends_on)
    
    circleci_manifest['workflows']['build-game']['jobs'].append(job)

# Print the final YAML
yaml.add_representer(str, yaml_multiline_string_pipe)
yaml.representer.SafeRepresenter.add_representer(str, yaml_multiline_string_pipe)
print(yaml.dump(circleci_manifest))