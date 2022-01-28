#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Library for heatzy devices
"""
import requests
import json
import pandas

class Connexion:
    API_URL = "http://euapi.gizwits.com/app"
    
    def __init__ (self, username, password):
        self.username = username
        self.password = password
        
        self.login()
        
    def login (self):
        headers = {'X-Gizwits-Application-Id': 'c70a66ff039d41b4a220e198b0fcc8b3',
                   'Content-Type': 'text/plain'
                   }
        
        if not isinstance(self.username, str) or not isinstance(self.password, str):
            raise TypeError("username and password must be str")
        
        payload = """{"username":" """ + self.username + """ ","password":" """ + self.password + """"}"""
        
        login_response = requests.request("POST", f'{Connexion.API_URL}/login', headers=headers, data=payload)
        login_response = dict(login_response.json())
        
        if 'error_message' in login_response.keys():
            raise Warning(f"{login_response['error_message']}")
            
        else:
            self.usr_token = login_response['token']
            
        self.bouded_device()
            
            
    def bouded_device (self):
        headers = {'X-Gizwits-Application-Id': 'c70a66ff039d41b4a220e198b0fcc8b3',
                   'X-Gizwits-User-token': self.usr_token
                   }
        payload = {}
        
        response = requests.request("GET", f'{self.API_URL}/bindings?limit=20&skip=0', headers=headers, data=payload)
        
        list_radiateur = []
        for device in response.json()['devices']:
            rad_dict = dict(device)
            
            temp_list =  [x.split('=') for x in rad_dict['remark'].split('|')]
            rad_dict['remark'] = {element[0]:element[1] for element in temp_list}
            radiateur = Radiateur(rad_dict)
            
            list_radiateur.append(radiateur)
            print(radiateur)
        
    def __str__(self):
        return f'User id {self.usr_token}'
    
class Radiateur:
    def __init__ (self, iterable):
        for key in iterable.keys():
            setattr(self, key, iterable[key])
            
    def state(self):
        
            
    def __str__ (self):
        return self.dev_alias
        
        
        
