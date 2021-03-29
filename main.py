import requests
import pandas as pd
import yaml
import datetime

time = datetime.datetime.now()

with open(r'./env_vars.yml') as file:
    vars = yaml.load(file, Loader=yaml.FullLoader)

m_headers = {'X-Cisco-Meraki-API-Key': vars['meraki_dash']['meraki_apikey']}
m_baseUrl = vars['meraki_dash']['m_baseUrl']

#get orginization #
org_response = requests.request("GET", f'{m_baseUrl}/organizations/', headers=m_headers)
org = org_response.json()

#uncomment to test return value
#print(org[0]["id"])

#create iterable list of all networks and then create filtered categories
net_response = requests.request("GET", f'{m_baseUrl}/organizations/{org[0]["id"]}/networks/', headers=m_headers)
if 'json' in net_response.headers.get('Content-Type'):
    networks = net_response.json()
    print(networks)
else:
    print('Response content is not in JSON format.')


for network in (network for network in networks if network['productTypes'] != 'systemsManager'):
    client_req = requests.get(f'{m_baseUrl}/networks/{network["id"]}/clients?timespan=86400&perPage=1000', headers = m_headers)
    try:
       if 'json' in client_req.headers.get('Content-Type'):
           clients = client_req.json()

           client_data = {'Network' : [],  'Description' : [], 'MAC' : [], 'User' : [], 'IP' : [], 'Vlan' : [], 'Manufacturer' : [],
                          'OS' : [], }

           # populate the data storage object
           for client in clients:
               client_data['Network'].append(network['name'])
               client_data['Description'].append(client['description'])
               client_data['MAC'].append(client['mac'])
               client_data['User'].append(client['user'])
               client_data['IP'].append(client['ip'])
               client_data['Vlan'].append(client['vlan'])
               client_data['Manufacturer'].append(client['manufacturer'])
               client_data['OS'].append(client['os'])

               # Build switch port dataframe
               client_df = pd.DataFrame(data=client_data)

               # Write dataframe to csv
               client_df.to_csv(path_or_buf=network['name'] + '_clients-' + str(time) + '.csv', index=False)

               print(f'The client information has been stored in {network["name"]}_clients.csv')

       else:
           print('Response content is not in JSON format.')

    except:
        print("An Exception has Occurred")
