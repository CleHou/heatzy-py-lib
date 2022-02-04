#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Library for heatzy devices
"""
import requests
import json
import pandas

class Connexion:
    API_URL = "https://euapi.gizwits.com/app"
    APP_ID = 'c70a66ff039d41b4a220e198b0fcc8b3'
    
    def __init__ (self, username, password):
        self.username = username
        self.password = password
        
        self.login()
        
        self.BindingManagement = BindingManagement(self.usr_token)
        self.DeviceMonitoring = DeviceMonitoring(self.usr_token)
        self.UserManagement = UserManagement(self.usr_token)
        
    def login (self):
        headers = {'X-Gizwits-Application-Id': self.APP_ID,
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
            
        
        
    def __str__(self):
        return f'User id {self.usr_token}'
    
class BindingManagement:
    def __init__ (self, usr_token):
        self.usr_token = usr_token  
        
        self.devices()
    
    def devices(self):
        headers = {'X-Gizwits-Application-Id': Connexion.APP_ID,
                   'X-Gizwits-User-token': self.usr_token
                   }
        path = f'{Connexion.API_URL}/bindings?limit=20&skip=0'
        payload = {}
        
        response = requests.request("GET", path, headers=headers, data=payload)
        
        self.devices_dict = {}
        self.devices_df = pandas.DataFrame(columns=['did', 'dev_alias', 'dev_label'])
        for device in response.json()['devices']:
            rad_dict = dict(device)
            
            temp_list =  [x.split('=') for x in rad_dict['remark'].split('|')]
            rad_dict['remark'] = {element[0]:element[1] for element in temp_list}
            
            self.devices_dict[rad_dict['did']] = rad_dict
            
            if len(rad_dict['dev_label']) > 0:
                for label in rad_dict['dev_label']:
                    self.devices_df.loc[len(self.devices_df)]=[rad_dict['did'], rad_dict['dev_alias'], label]
            else:
                self.devices_df.loc[len(self.devices_df)]=[rad_dict['did'], rad_dict['dev_alias'], '']
        
        self.devices_df = self.devices_df.set_index('did')
        
            
    def edit (self, device:str, remark={}, dev_alias='', dev_label=''):
        print(self.devices_df.reset_index())
        if device in self.devices_df.reset_index().values:
            did = self.get_did(device)
            
            headers = {'X-Gizwits-Application-Id': Connexion.APP_ID,
                       'X-Gizwits-User-token': self.usr_token,
                       'Content-Type': 'text/plain'
                       }
            path = f'{Connexion.API_URL}/bindings/{did}'
            payload = "{"
            for param, param_str in zip([dev_alias, dev_label], ['dev_alias', 'dev_label']):
                if param != '':
                    payload += "\"" + param_str + "\": \"" + param + "\", "
                    
            if remark != {}:
                if not isinstance(remark, dict):
                    raise Warning('remark parameter must be a dict')
                else:
                    former_remark = self.devices_dict[did]['remark']
                    
                    for key in remark.keys():
                        former_remark[key] = remark[key]
                        
                    former_remark.pop('test')
                        
                    remark_str = ""
                    for key in former_remark.keys():
                        remark_str += f"{key.strip()}={former_remark[key].strip()}|"
                    remark_str = remark_str[:-1]
                    
                    payload += "\"" + "remark" + "\": \"" + remark_str + "\", "
                    
            payload = payload[:-2]
            payload += "}"
            
            if payload == "}":
                raise Warning('No information were sent')
                
            else:
                response = requests.request("PUT", path, headers=headers, data=payload)
                json_rep = response.json()
                
                print(f"Information of device {device} was succesfully change")
                
                self.devices()    
            
        else:
            raise Warning(f"Device {device} doesn't match any devices. device param must be a device id, alias or one of the device label")
            
        return json_rep
    
    def delete (self, device):
        if device in self.devices_df.reset_index().values:
            did = self.get_did(device)
            
            headers = {'X-Gizwits-Application-Id': Connexion.APP_ID,
                       'X-Gizwits-User-token': self.usr_token,
                       'Content-Type': 'text/plain'
                       }
            path = f'{Connexion.API_URL}/bindings'
            payload = "{\"devices\": [{\"did\":\"" + did + "\"}]}"
            
            response = requests.request("DELETE", path, headers=headers, data=payload)
            json_rep = response.json()
            
        else:
            raise Warning(f"Device {device} doesn't match any devices. device param must be a device id, alias or one of the device label")
         
        return json_rep
    
    def get_did (self, device):
        for col in self.devices_df.columns:
            if device in self.devices_df[col].values:
                df = self.devices_df.reset_index().set_index(col)
                return df.loc[device, 'did']
        else:
            return device
        
    def __str__ (self):
        return repr(self.devices_df)
    
    def device_param(self, device):
        if device in self.devices_df.reset_index().values:
            did = self.get_did(device)
            print(json.dumps(self.devices_dict[did], indent=2))
            
        
    
class DeviceMonitoring:
    def __init__ (self, usr_token):
        self.usr_token = usr_token
    
class UserManagement:
    def __init__ (self, usr_token):
        self.usr_token = usr_token
    
class Radiateur:
    def __init__ (self, iterable):
        for key in iterable.keys():
            setattr(self, key, iterable[key])
            
    def state(self):
        pass
            
    def __str__ (self):
        return self.dev_alias
        
        
        
