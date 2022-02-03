#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
filename = "feature"
model = "courses.feature"

with open(filename+'.csv') as f:
    lines = f.readlines()
    
with open(filename+'.jsonl', "w") as f:
    for l in lines[1:]:
        l = l.replace('\n', "")
        l = pk, course, title, desc, laws, notes = [x.replace('"', "") for x in l.split(";") ]
        print(l)
        f.write('{"pk": %s, "model": "%s","fields":{"course_id": %s, "title": "%s", "desc": "%s", "laws": "%s", "notes": "%s"}}\n'%(pk, model, course, title, desc, laws, notes))
