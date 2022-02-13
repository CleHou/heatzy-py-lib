#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from heatzypy import heatzypy

load_dotenv()

manager = heatzypy.Connexion(os.environ.get('username'), os.environ.get('password'))
print(manager)

"""
A = manager.BindingManagement
print(A)
#rep = A.edit('Salon', remark={'test':'Appartement'})
#rep = A.edit('Chambre', remark={'groupname':'Appartement'})
#rep = A.delete('test')
"""

B = manager.DeviceMonitoring
rep,df = B.status('Salon')
print(B.df_schedule)

