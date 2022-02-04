#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from heatzypy import heatzypy

load_dotenv()

manager = heatzypy.Connexion(os.environ.get('username'), os.environ.get('password'))
print(manager)

A = manager.BindingManagement
print(A)
rep = A.edit('3Xt9llkUMckRdeaZ3mNRlb', remark={'test':'test'})
A.device_param('Salon')
print(rep)

