import platform
import urllib.request
import os
import sys
import tarfile
import stat
import shutil
from github import Github
import yaml

class Database(object):

    NOT_A_MODEL = ["physiboss-models", "physiboss-models.github.io", "adminbot", ".github"]
    def __init__(self):
        self._github = Github(per_page=100)
        self._organisation = self._github.get_organization("PhysiBoSS-Models")
        self._models = self._list_models()
        self._models_versions = self._list_versions()
        
        self._current_model_yaml = None
        self._current_model_info = None
    
    def _list_models(self):
        repos = self._organisation.get_repos()
        i=0
        page = repos.get_page(i)
        r = page
        while len(page) == 100:
            i += 1
            page = repos.get_page(i)
            r += page
            
        return {repo.name:repo for repo in r if repo.name not in self.NOT_A_MODEL}        

    def _list_versions(self):
        vs = {}
        
        for label, model in self._models.items():
            releases = model.get_releases()
            i=0
            page = releases.get_page(i)
            v = [(release.tag_name, release) for release in page]
            while len(page) == 100:
                i += 1
                page = releases.get_page(i)
                v += [(release.tag_name, release) for release in page]
            vs.update({label: v})
        return vs
        
    def _load_current_model_info(self):
        if self._current_model_yaml is not None and os.path.exists(self._current_model_yaml):
            with open(self._current_model_yaml) as yaml_file: 
                self._current_model_info = yaml.load(yaml_file, Loader=yaml.Loader)
    def all(self):
        return list(self._models.keys())

    def search(self, name):
        return [model for model in self._models.keys() if name in model]

    def versions(self, model):
        if model in self._models.keys():
            return [version[0] for version in self._models_versions[model]]

    def current_model_info(self):
        return self._current_model_info
        
    def download_model(self, model, path, version=None, backup=False):
        self._current_model_yaml = None
        self._current_model_info = None
        
        url = self._get_model_url(model, version)
        filename = url.split("/")[-1]
        my_file = os.path.join(path, filename)

        urllib.request.urlretrieve(url, my_file, download_cb)
        
        if backup:
            # print('> Creating backup of XML settings, Makefile, main.cpp')
            if os.path.exists("Makefile"):
                shutil.copyfile("Makefile", "Makefile-backup")
            if os.path.exists("main.cpp"):
                shutil.copyfile("main.cpp", "main-backup.cpp")
            if os.path.exists(os.path.join("config", "PhysiCell_settings.xml")):
                shutil.copyfile(os.path.join("config", "PhysiCell_settings.xml"), os.path.join("PhysiCell_settings-backup.xml"))
        old_path = os.getcwd()       
        os.chdir(path)
        # print('> Uncompressing the model')
        
        try:
            tar = tarfile.open(filename)
            tar.extractall()
            binary_name = [names for names in tar.getnames() if not names.endswith(".dll")][0]
            tar.close()
            os.remove(filename)
        
        except:
            print('! Error untarring the file')
            exit(1)
        
        st = os.stat(binary_name)
        os.chmod(binary_name, st.st_mode | stat.S_IEXEC)
        os.chdir(old_path)
        
        self._current_model_yaml = os.path.join(path, "model.yml")
        self._load_current_model_info()
        
    def _get_model_url(self, model, version=None):
        repo = self._models[model]
        if version is None:
            release = self._models_versions[model][0][1]
        else:
            release = [model_release for model_version, model_release in self._models_versions[model] if version == model_version][0]
        assets = [asset.browser_download_url for asset in release.assets]
    
        os_type = platform.system()
        suffix = None
        if os_type.lower() == 'darwin':
            suffix = "-macos.tar.gz"
        elif os_type.lower().startswith("win") or os_type.lower().startswith("msys_nt") or os_type.lower().startswith("mingw64_nt"):
            suffix = "-win.tar.gz"
        elif os_type.lower().startswith("linux"):
            suffix = "-linux.tar.gz"
        else:
            raise Exception("Your operating system seems to be unsupported. Please create an new issue at https://github.com/PhysiBoSS/PhysiBoSS/issues/ ")
    
        assets_os = [asset for asset in assets if asset.endswith(suffix)]
        if len(assets_os) == 0:
            raise Exception("Your operating system is not handled by this model.")
        elif len(assets_os) > 1:
            raise Exception("There are multiple versions of this model ??")

        return assets_os[0]    
    

def download_cb(blocknum, blocksize, totalsize):
    readsofar = blocknum * blocksize
    if totalsize > 0:
        percent = readsofar * 1e2 / totalsize
        s = "\r%5.1f%% %*d / %d" % (percent, len(str(totalsize)), readsofar, totalsize)
    