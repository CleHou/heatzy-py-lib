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
        
        self.BM = BindingManagement(self.usr_token)
        self.devices_dict = self.BM.devices_dict
        self.devices_df = self.BM.devices_df
        
    def status (self, device):
        if device in self.devices_df.reset_index().values:
            did = self.BM. get_did(device)
            
            headers = {'X-Gizwits-Application-Id': Connexion.APP_ID,
                       'X-Gizwits-User-token': self.usr_token,
                       }
            path = f'{Connexion.API_URL}/devdata/{did}/latest'
            
            response = requests.request("GET", path, headers=headers)
            json_rep = response.json()
            
        else:
            raise Warning(f"Device {device} doesn't match any devices. device param must be a device id, alias or one of the device label")
        
        df_shed = self.status_to_schedule(json_rep)
        
        print(json_rep.keys())
        
        self.time_week = json_rep['attr']['time_week']
        self.mode = json_rep['attr']['mode']
        self.lock_switch = json_rep['attr']['lock_switch']
        self.timer_switch = json_rep['attr']['timer_switch']
        self.boost_switch = json_rep['attr']['boost_switch']
        self.boost_time = json_rep['attr']['boost_time']
        self.derog_mode = json_rep['attr']['derog_mode']
        self.derog_time = json_rep['attr']['derog_time']
        
        return json_rep, df_shed
    
    def status_to_schedule (self, json_rep):
        matching_table = {'00': 'cft', '01':'eco', '10':'fro', '11':'off'}
        self.df_schedule  = pandas.DataFrame(index=pandas.date_range(start='2022-01-03 00:00', end='2022-01-10 00:00', freq='30min'),columns=['status'])
        for day in range(1, 8):
            for block in range(0, 13):
                if f'p{day}_data{block}' in json_rep['attr'].keys():
                    mode = str(bin(json_rep['attr'][f'p{day}_data{block}']).replace("0b", "")).zfill(8)
                    #print(f'p{day}_data{block}', mode)
                    
                    day_0 = self.df_schedule.index[0] + pandas.to_timedelta(f'{day-1} days')
                    
                    for k, l in zip([0.5, 1, 1.5, 2], range(0,8,2)):
                        date_time = day_0 + pandas.to_timedelta(f'{2*block - k} hours')
                        status = mode[l:l+2]
                        
                        self.df_schedule.loc[date_time] = matching_table[status]
                        
                        #print(f'p{day}_data{block}', date_time)
        self.df_schedule.loc[:,'day'] = self.df_schedule.index
        self.df_schedule.loc[:,'time'] = self.df_schedule.index
        self.df_schedule['day'] = self.df_schedule['day'].apply(lambda x: x.strftime('%a'))
        self.df_schedule['time'] = self.df_schedule['time'].apply(lambda x: x.strftime('%H:%M'))
        
        self.df_schedule = self.df_schedule.dropna().pivot(index='time', columns='day', values='status')
        self.df_schedule = self.df_schedule[['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']]
        
        return self.df_schedule
                    
                    
        
        
        
        
    
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
        
        
        
