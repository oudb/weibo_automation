#! /usr/bin/python
# -*- coding: utf-8 -*-

from sina_claws import SinaClaws

claws = SinaClaws(level=1)
if claws.login():
    claws.work([u"2349836674"])
else:
    print "login fail"

