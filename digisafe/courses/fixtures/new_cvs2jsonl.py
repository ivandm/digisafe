#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
filename = "new"
model = "courses.new"

with open(filename+'.csv') as f:
    lines = f.readlines()
    
with open(filename+'.jsonl', "w") as f:
    for l in lines[1:]:
        l = l.replace('\n', "")
        l = pk, course, theory, practice = [x.replace('"', "") for x in l.split(";") ]
        print(l)
        f.write('{"pk": %s, "model": "%s","fields":{"course": %s, "theory": "%s", "practice": "%s"}}\n'%(pk, model, course, theory, practice))
