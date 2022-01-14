#DISCLAIMER: Please note: This script is meant for demo purposes only. All tools/
# #scripts in this repo are released for use "AS IS" without any warranties of any kind,
# #including, but not limited to their installation, use, or performance. Any use of
#these scripts and tools is at your own risk. There is no guarantee that they have
# #been through thorough testing in a comparable environment and we are not responsible
# #for any damage or data loss incurred with their use. You are responsible for
# #reviewing and testing any scripts you run thoroughly before use in any non-testing
# #environment.

# usage python3 main.py -k <api key> -o <specific org name> -f csv or json


import meraki
import getopt, sys, csv, json
from pathlib import Path
import datetime




def main(argv):

    def getorg(arg_orgname):
        org_response = dashboard.organizations.getOrganizations()
        for org in org_response:
            if org['name'].lower() == arg_orgname.lower():
                orgid = org['id']
                # print(orgid)
                print("Org" + " " + orgid + " " + "found.")
                return(orgid)

            else:
                print("No Org found")

    #Function for creating output as CSV
    def output_csv(data, flag, filename, net_name):
        # Create and write the CSV file (Windows, linux, macos)
        if len(client_data) > 0:
            keys = data[0].keys()
            Path(flag).mkdir(parents=True, exist_ok=True)
            inpath = Path.cwd() / flag / filename
            # print(inpath)
            with inpath.open(mode='w+', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(client_data)
        return ('success')

    #Function for creating output as json
    def output_json(data, flag, filename, netname):
        if len(client_data) > 0:
            Path(flag).mkdir(parents=True, exist_ok=True)
            inpath = Path.cwd() / flag / filename
            with inpath.open('w') as jsonFile:
                json.dump(data, jsonFile, indent=4, sort_keys=True)
        return ('success')


    arg_apikey = None
    arg_orgname = None



    try:
        opts, args = getopt.getopt(argv, 'k:o:f:')
    except getopt.GetoptError:
        sys.exit(0)

    for opt, arg in opts:
        if opt == '-k':
            arg_apikey = arg
        elif opt == '-o':
            arg_orgname = arg
        elif opt == '-f':
            arg_filetype = arg


    #print(arg_apikey) #test point for correct apikey
    #print(arg_orgname) #test point for correct orgname
    #print(arg_netname) #test print for correct network name

    if arg_apikey is None or arg_orgname is None:
        print('Please specify the required values!')
        sys.exit(0)


    API_KEY = arg_apikey
    dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)

    time = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")


    # get orgid for specified org name by calling getorg function
    orgid = getorg(arg_orgname)


    # create iterable list of all networks and then create filtered categories
    networks = dashboard.organizations.getOrganizationNetworks(orgid, total_pages='all')

    # Build the Client Data Report
    # for each network retrieve the client list
    for i in range(0, len(networks)):
        if networks[i]['productTypes'] != ['systemsManager']:
            # print(i) # debug network response

            clients = dashboard.networks.getNetworkClients(networks[i]['id'], total_pages='all')
            # print(clients) # debug clients
            print("*******Generating Client Data Report*******")
            # Build the Client data into a nested dictionary
            try:
                client_data = []
                # print(clients)

                # populate the data storage object
                for client in clients:
                    # print(client)
                    client_data_df = {'ID': client['id'], 'Description': client['description'],
                                      'MAC': client['mac'],
                                      'User': client['user'], 'IP': client['ip'], 'manufacturer': client['manufacturer'], 
                                      'manufacturer': client['manufacturer'], 
                                      'OS': client['os'], 'VLAN': client['vlan'], 'Device': client['recentDevicename'] 'Device Serial': client['recentDeviceSerial']}

                    client_data.append(client_data_df)

                    #Set Variables and send to the CSV report function
                    data = client_data
                    flag = 'client_data'
                    filename = networks[i]['name'] + '_clients-' + str(time) + '.' + arg_filetype
                    net_name = networks[i]['name']

                    if arg_filetype == 'csv':
                        output = output_csv(data, flag, filename, net_name)
                    elif arg_filetype == 'json':
                        output = output_json(data, flag, filename, net_name)

                if output == 'success':
                    print("Client Report For" + " " + networks[i]['name'] + " " + "Created in /Client_data")
                else:
                    print("Client Report For" + " " + networks[i]['name'] + " " + "failed")

            except Exception as e:
                print(e)

    print("I am Done. Have a nice day!")

if __name__ == '__main__':
    main(sys.argv[1:])
