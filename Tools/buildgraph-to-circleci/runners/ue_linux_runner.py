from .runner import Runner

class UELinuxRunner(Runner):
  def __init__(self, branch_name):
    Runner.__init__(self)
    self.branch_name = branch_name
    self.env_prefix = '$'
    self.env_assignment_prefix = 'export '
    self.environment = {
      'UE_SharedDataCachePath': '/data_fsx/SharedDDCUE5Test'
    }
    self.resource_class = 'vela-games/linux-runner-ue5'
    self.run_uat_subpath = '/Engine/Build/BatchFiles/RunUAT.sh'
    self.shell = '/usr/bin/env bash'
    self.shared_storage_volume = '/data_fsx/'
    self.ue_path = '/home/ubuntu/UnrealEngine'
    self.working_directory = f'/home/ubuntu/workspace/{branch_name.replace("/","-").replace("_", "-").lower()}'

  def patch_buildgraph(self):
    return f'{self.self_patch_buildgraph()} || true'
  
  def mount_shared_storage(self):
    return 'echo "Linux already mounted"'

  def create_dir(self, directory):
    return f"mkdir -p {directory}"
  
  def pre_cleanup(self):
    return """rm -rf *.zip
    rm -rf /home/ubuntu/UnrealEngine/Engine/Saved/BuildGraph/
    rm -rf $CIRCLE_WORKING_DIRECTORY/Engine/Saved/*
    rm -rf $CIRCLE_WORKING_DIRECTORY/dist
    """