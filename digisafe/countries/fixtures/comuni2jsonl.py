#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

with open('gb_cities.csv') as f:
    lines = f.readlines()
    
newL = {}
for l in lines[1:]:
    print(l)
    l = l.replace('\n', "")
    pk, country, name, prov, sigla_prov = [x.replace('"', "") for x in l.split(";") ]
    newL[pk] = [country, name, prov, sigla_prov]
    print(newL[pk])

with open('gb_cities.jsonl', "w") as f:
    for k, v in newL.items():
        country, name, prov, sigla_prov = v
        f.write('{"pk": %s, "model": "countries.city","fields":{"country": %s, "name": "%s", "prov": "%s", "sigla_prov": "%s"}}\n'%(k, country, name,prov, sigla_prov))