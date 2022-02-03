#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
filename = "courses"
model = "courses.courses"

with open(filename+'.csv') as f:
    lines = f.readlines()
    
with open(filename+'.jsonl', "w") as f:
    for l in lines[1:]:
        l = l.replace('\n', "")
        l = pk, code, country = [x.replace('"', "") for x in l.split(";") ]
        print(l)
        f.write('{"pk": %s, "model": "%s","fields":{"code": "%s"}}\n'%(pk, model, code))
