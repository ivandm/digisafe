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

#cmd = 'python3 manage.py collectstatic -c --no-post-process --noinput'
#print(cmd)
#os.system(cmd)

#cmd = 'sudo chgrp -R assoclinic %s' % os.getcwd()
#print(cmd)
#os.system(cmd)

#cmd = 'sudo chmod -R 777 %s' % os.getcwd()
#print(cmd)
#os.system(cmd)

cmd = 'python3 manage.py migrate'
print(cmd)
os.system(cmd)

# cmd = 'python3 manage.py makemigrations --merge'
# cmd = 'python3 manage.py makemigrations'
# print(cmd)
# os.system(cmd)

#cmd = 'python3 manage.py migrate'
#print(cmd)
#os.system(cmd)

print("Sincronizzare il Services Plans Assoclinica")
cmd = 'plesk bin service_plan --update "Digisafe"'
print(cmd)
os.system(cmd)

#cmd = 'python3 manage.py  crontab add'
#print(cmd)
#os.system(cmd)

print("Fine aggiornamento")



