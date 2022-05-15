import os

#cmd = 'python3 manage.py  crontab remove'
#print(cmd)
#os.system(cmd)

# print("Preservo settings_config.py") #file fra gli ignored del git
# os.rename('clinica/settings_config.py', 'clinica/settings_config_.py')

cmd = 'git add *'
print(cmd)
os.system(cmd)

cmd = 'git stash'
print(cmd)
os.system(cmd)

cmd = 'git pull'
print(cmd)
os.system(cmd)

# print("Ripristino settings_config.py")
# os.remove("clinica/settings_config.py")
# os.rename('clinica/settings_config_.py', 'clinica/settings_config.py')

cmd = 'python3 pip install -r digisafe/requirements.txt'
print(cmd)
os.system(cmd)

cmd = 'python3 digisafe/manage.py collectstatic -c --no-post-process --noinput'
print(cmd)
os.system(cmd)

import shutil

from distutils.dir_util import copy_tree
from digisafe.digisafe.settings import STATIC_ROOT
shutil.copy2("digisafe/static/theme.scss", str(STATIC_ROOT))
for src in ["css/", 'js/', "fonts/", "imgs/", "bootstrap-5.1.3-dist/", "leaflet/"]:
    copy_tree("digisafe/static/"+src, str(STATIC_ROOT)+"/"+src)
    print("digisafe/static/"+src, str(STATIC_ROOT)+"/"+src)

cmd = 'python3 digisafe/manage.py compress --force'
print(cmd)
os.system(cmd)


#cmd = 'sudo chgrp -R assoclinic %s' % os.getcwd()
#print(cmd)
#os.system(cmd)

cmd = 'sudo chmod -R 777 %s' % os.getcwd()
print(cmd)
os.system(cmd)

cmd = 'python3 digisafe/manage.py migrate'
print(cmd)
os.system(cmd)

# cmd = 'python3 manage.py makemigrations --merge'
# cmd = 'python3 manage.py makemigrations'
# print(cmd)
# os.system(cmd)

#cmd = 'python3 manage.py migrate'
#print(cmd)
#os.system(cmd)

cmd = 'django-admin compilemessages'
print(cmd)
os.system(cmd)

print("Sincronizzare il Services Plans Assoclinica")
cmd = 'plesk bin service_plan --update "Digisafe"'
print(cmd)
os.system(cmd)

#cmd = 'python3 manage.py  crontab add'
#print(cmd)
#os.system(cmd)

print("Fine aggiornamento")



