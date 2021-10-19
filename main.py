#DISCLAIMER: Please note: This script is meant for demo purposes only. All tools/
# #scripts in this repo are released for use "AS IS" without any warranties of any kind,
# #including, but not limited to their installation, use, or performance. Any use of
#these scripts and tools is at your own risk. There is no guarantee that they have
# #been through thorough testing in a comparable environment and we are not responsible
# #for any damage or data loss incurred with their use. You are responsible for
# #reviewing and testing any scripts you run thoroughly before use in any non-testing
# #environment.

# usage python3 main.py -k <api key> -o <specific org name>


import meraki
import getopt, csv, os, sys, time
from pathlib import Path
import datetime


def main(argv):


    arg_apikey = None
    arg_orgname = None

    try:
        opts, args = getopt.getopt(argv, 'k:o:')
    except getopt.GetoptError:
        sys.exit(0)

    for opt, arg in opts:
        if opt == '-k':
            arg_apikey = arg
        elif opt == '-o':
            arg_orgname = arg




    #print(arg_apikey) #test point for correct apikey
    #print(arg_orgname) #test point for correct orgname
    #print(arg_netname) #test print for correct network name


    if arg_apikey is None or arg_orgname is None:
        print('Please specify the required values!')
        sys.exit(0)


    # set needed vlaues from env_vars
    m_headers = {'X-Cisco-Meraki-API-Key': arg_apikey}
    m_baseUrl = 'https://api.meraki.com/api/v1'

    API_KEY = arg_apikey
    dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)

    time = datetime.datetime.now()

    # get orgid for specified org name
    org_response = dashboard.organizations.getOrganizations()

    for org in org_response:
        if org['name'].lower() == arg_orgname.lower():
            orgid = org['id']
            #print(orgid)
            print("Org" + " " + orgid + " " + "found.")
        else:
            print("Exception: This Org does not match:" + ' ' + orgid + ' ' + 'Is not the orginization specified!')

    # create iterable list of all networks and then create filtered categories
    networks = dashboard.organizations.getOrganizationNetworks(orgid, total_pages='all')

    #for each network retrieve the client list
    for i in range(0, len(networks)):
        if networks[i]['productTypes'] != ['systemsManager']:
            #print(i) # debug network response

            clients = dashboard.networks.getNetworkClients(networks[i]['id'], total_pages='all')
            #print(clients) # debug clients

            try:
                client_data = []
                #print(clients)

                # populate the data storage object
                for client in clients:
                    #print(client)
                    client_data_df = {'ID': client['id'], 'Description': client['description'], 'MAC': client['mac'],
                            'User': client['user'], 'IP': client['ip'], 'VLAN': client['vlan'], 'manufacturer': client['manufacturer'],
                            'OS': client['os']}

                    client_data.append(client_data_df)


                # Create and write the CSV file
                if len(client_data) > 0:
                    keys = client_data[0].keys()
                    filename = networks[i]['name'] + '_clients-' + str(time) + '.csv'
                    inpath = Path(filename)
                    print(inpath)
                    with inpath.open('w+', newline='') as output_file:
                            dict_writer = csv.DictWriter(output_file, keys)
                            dict_writer.writeheader()
                            dict_writer.writerows(client_data)

                    print("Client Report For" + " " + networks[i]['name'] + " " + "Created")
                #time.sleep(2)

            #except:
                #print("An Exception has Occurred")
            except Exception as e: print(e)






    print("I am Done. Have a nice day!")

if __name__ == '__main__':
    main(sys.argv[1:])