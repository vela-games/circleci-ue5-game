from common import sanitize_job_name

class Runner:
  def __init__(self):
    self.resource_class = ''
    self.run_uat_subpath = ''
    self.env_prefix = ''
    self.env_assignment_prefix = ''
    self.shell = ''
    self.environment = {}
    self.ue_path = ''
    self.working_directory = ''
    self.shared_storage_volume = ''
    self.branch_name = ''

  def mount_shared_storage(self):
    raise NotImplementedError("Runners have to implement this")

  def create_dir(self, directory):
    raise NotImplementedError("Runners have to implement this")
  
  def pre_cleanup(self):
    raise NotImplementedError("Runners have to implement this")
  
  def self_patch_buildgraph(self):
    return f"git -C {self.ue_path} apply {self.env_prefix}CIRCLE_WORKING_DIRECTORY/Tools/BuildGraph.patch"
  
  def patch_buildgraph(self):
    self.self_patch_buildgraph()

  def generate_steps(self, job_name):
    return self.generate_buildgraph_steps(job_name)

  def generate_buildgraph_steps(self, job_name):
    sanitized_job_name = sanitize_job_name(job_name)
    filesafe_branch_name = self.branch_name.replace("/", "_")
    
    steps = [
      "checkout",
      {
        'run': {
          'name': 'Mount Shared Storage (FSx)',
          'command': self.mount_shared_storage()
        }
      },
      {
        'run': {
          'name': "Create shared directory for workflow",
          'command': f"""{self.create_dir(f"{self.shared_storage_volume}{filesafe_branch_name}/{self.env_prefix}CIRCLE_SHA1")}
          """
        }
      },
      {
        'run': {
          'name': "Cleanup old build",
          'command': self.pre_cleanup()
        }
      },
      {
        'run': {
          'name': "Apply BuildGraph patch",
          'command': self.patch_buildgraph()
        }
      },
      {
        'run': {
          'name': job_name,
          'command': f"""
            {self.env_assignment_prefix}BUILD_GRAPH_ALLOW_MUTATION=\"true\"
            {self.env_assignment_prefix}uebp_UATMutexNoWait=\"1\"
            {self.env_assignment_prefix}uebp_LOCAL_ROOT=\"{self.ue_path}\"
            {self.env_assignment_prefix}BUILD_GRAPH_PROJECT_ROOT=\"{self.env_prefix}CIRCLE_WORKING_DIRECTORY\"

            {self.ue_path}{self.run_uat_subpath} BuildGraph -Script=\"{self.env_prefix}CIRCLE_WORKING_DIRECTORY/Tools/BuildGraph.xml\" -SingleNode=\"{job_name}\" -set:ProjectRoot=\"{self.env_prefix}CIRCLE_WORKING_DIRECTORY\" -set:UProjectPath=\"{self.env_prefix}CIRCLE_WORKING_DIRECTORY/FirstPersonGame.uproject\" -set:StageDirectory=\"{self.env_prefix}CIRCLE_WORKING_DIRECTORY/dist\" -SharedStorageDir=\"{self.shared_storage_volume}{filesafe_branch_name}/{self.env_prefix}CIRCLE_SHA1\" -NoP4 -WriteToSharedStorage -BuildMachine
          """
        }
      }
    ]

    pak_steps = []

    if "pak" in sanitized_job_name:
      suffix = ""
      if "win64" in sanitized_job_name:
        suffix = "_win64"
      elif "linux" in sanitized_job_name:
        suffix = "_linux"

      pak_steps.extend([
        {
          'store_artifacts': {
            'path': f'dist{suffix}.zip'
          }
        }
      ])
    
    steps.extend(pak_steps)
    return steps
