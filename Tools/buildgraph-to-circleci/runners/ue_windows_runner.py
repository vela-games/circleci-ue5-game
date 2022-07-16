from .runner import Runner

class UEWindowsRunner(Runner):
  def __init__(self, branch_name):
    Runner.__init__(self)
    self.branch_name = branch_name
    self.env_prefix = '$Env:'
    self.env_assignment_prefix = '$Env:'
    self.environment = {
      'UE-SharedDataCachePath': 'Z:\\SharedDDCUE5Test'
    }
    self.resource_class = 'vela-games/windows-runner-ue5'
    self.run_uat_subpath = '\\Engine\\Build\\BatchFiles\\RunUAT.bat'
    self.shell = 'powershell.exe'
    self.shared_storage_volume = 'Z:\\'
    self.ue_path = 'C:\\UnrealEngine'
    self.working_directory = f'C:\\workspace\\{branch_name.replace("/","-").replace("_", "-").lower()}'
  
  def patch_buildgraph(self):
    return f"""{self.self_patch_buildgraph()}
    [Environment]::Exit(0)
    """

  def mount_shared_storage(self):
    return "C:\\mount_fsx.ps1"

  def create_dir(self, directory):
    return f"New-Item -ItemType 'directory' -Path \"{directory}\" -Force -ErrorAction SilentlyContinue"
  
  def pre_cleanup(self):
    return """Remove-Item -Force *.zip -ErrorAction SilentlyContinue
    Remove-Item -Force -Recurse \"C:\\UnrealEngine\\Engine\\Saved\\BuildGraph\\\" -ErrorAction SilentlyContinue
    Remove-Item -Force -Recurse \"$Env:CIRCLE_WORKING_DIRECTORY\\Engine\\Saved\\*\" -ErrorAction SilentlyContinue
    Remove-Item -Force -Recurse \"$Env:CIRCLE_WORKING_DIRECTORY\\dist\\\" -ErrorAction SilentlyContinue
    [Environment]::Exit(0)
    """