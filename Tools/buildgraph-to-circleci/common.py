def yaml_multiline_string_pipe(dumper, data):
  text_list = [line.lstrip().rstrip() for line in data.splitlines()]
  fixed_data = "\n".join(text_list)
  if len(text_list) > 1:
      return dumper.represent_scalar('tag:yaml.org,2002:str', fixed_data, style="|")
  return dumper.represent_scalar('tag:yaml.org,2002:str', fixed_data)

def sanitize_job_name(name):
  return name.replace(' ', '-').lower()