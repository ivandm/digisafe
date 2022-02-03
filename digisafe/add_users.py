#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# dalla shell di django digitare
# exec(open('add_users.py').read())

from users.models import User, Anagrafica, Profile
from countries.models import Country, City

filename = "users"
with open(filename+'.csv') as f:
    lines = f.readlines()

for u in lines[1:]:
    u = u.replace('"',"").replace("\n","").split(";")
    pk,last_name,country,city,birthday,fiscal_code,director,administrator,trainer = u
    username = "".join(last_name.split(" ")).lower()
    print(username, end = '...')
    user, created = User.objects.get_or_create(username=username)
    user.last_name = last_name
    user.save()
    
    try:
        user.anagrafica.country = Country.objects.get(pk=country)
        user.anagrafica.city = City.objects.get(pk=city)
        user.anagrafica.birthday = birthday
        user.anagrafica.fiscal_code = fiscal_code
        user.save()
    except:
        a = Anagrafica(
            user=user,
            country = Country.objects.get(pk=country),
            city = City.objects.get(pk=city),
            birthday = birthday,
            fiscal_code = fiscal_code,
        )
        a.save()
    try:
        user.profile.director = director
        user.profile.administrator = administrator
        user.profile.trainer = trainer
        user.save()
    except:
        p = Profile(
            user=user,
            director = director,
            administrator = administrator,
            trainer = trainer,
        )
        p.save()
    print(" loaded.")
    