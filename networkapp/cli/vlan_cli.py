#from networkapp.util.db import add_vlan_to_db, delete_vlan_from_db, update_vlan_in_db, get_all_vlans_from_db
from networkapp.util.db import VlanDatabaseHelper
from networkapp.netservice import VlanService

import argparse
import logging
import os

from networkapp.models.switch import cisco_switch
from networkapp.models.vlan import vlan

DB_NAME=os.getenv("DB_URI",None)
FORMAT = '%(asctime)-15s %(levelname)s %(module)s %(message)s'
logging.basicConfig(format=FORMAT, level="INFO")
logger = logging.getLogger(__name__)


def get_params_from_env():

    hostname = os.getenv("MANAGED_HOST", None)
    usr = os.getenv("ROUTER_USR")
    psswd = os.getenv("ROUTER_PSSWD")
    device_type = os.getenv("DEVICE_TYPE")

    return {
        "hostname" : hostname,
        "user" : usr,
        "psswd" : psswd,
        "device_type" : device_type
    }


def populate_parser(parser):
    main_subparser = parser.add_subparsers(dest="cmd")
    main_subparser.required = True

    addvlan_parser = main_subparser.add_parser("add", help="add vlan")
    addvlan_parser.add_argument("--vlanid", "-v", type=int, required=True)
    addvlan_parser.add_argument("--name", "-n", required=True)
    addvlan_parser.add_argument("--description", "-d", required=True)

    addvlan_parser = main_subparser.add_parser("update", help="update vlan")
    addvlan_parser.add_argument("--vlanid", "-v", type=int, required=True)
    addvlan_parser.add_argument("--name", "-n", required=True)
    addvlan_parser.add_argument("--description", "-d", required=True)

    deletevlan_parser = main_subparser.add_parser("del", help="delete vlan")
    deletevlan_parser.add_argument("--vlanid", "-v", type=int, required=True)

    merge_parser = main_subparser.add_parser("merge", help="merge the devices")

    dumpdb_parser = main_subparser.add_parser("dumpdb", help="dump db vlan")
    dumprouter_parser = main_subparser.add_parser("dumprouter", help="sync to device")

    sync_parser = main_subparser.add_parser("checksync", help="check sync")
    sync_from_parser = main_subparser.add_parser("syncfrom", help="sync from device")
    sync_to_parser = main_subparser.add_parser("syncto", help="sync to device")
    sync_to_parser = main_subparser.add_parser("canmerge", help="sync to device")

def main():
    this_parser = argparse.ArgumentParser()
    populate_parser(this_parser)
    args = this_parser.parse_args()

    vservice = VlanService(db_name=DB_NAME)

    device_params = get_params_from_env()
    sw = cisco_switch(**device_params)


    if args.cmd is not None:
        cmd = args.cmd

        if cmd == "add":
            #add_vlan(args)
            tvlan = vlan(id=args.vlanid, name=args.name, description=args.description)
            vservice.add_vlan(vlan_obj=tvlan, device_obj=sw)

        elif cmd == "del":
            #del_vlan(args)
            vservice.del_vlan(vlan_id=args.vlanid, device_obj=sw)

        elif cmd == "dumpdb":
            vservice.dump_db(device_obj=sw)

        elif cmd == "checksync":
            sync = vservice.check_sync(device_obj=sw)

            print(f"In Sync = {sync.data}")
        elif cmd == "syncfrom":


            vservice.sync_from(device_obj=sw,)
        elif cmd == "syncto":
            vservice.sync_to(device_obj=sw)
        elif cmd == "dumprouter":
            vlan_result = vservice.get_vlans_from_device(device_obj=sw)
            if vlan_result.success:
                for id, vlanobj in vlan_result.data.items():
                    print(vlanobj.id, vlanobj.name)
            else:
                print(f"Error getting vlans from device: {vlan_result.errmsg}")

        elif cmd == "canmerge":

            mergeable_result = vservice.can_merge(device_obj=sw)
            print(f"Can merge == {mergeable_result.data}")

        elif cmd == "update":
            tvlan = vlan(id=args.vlanid, name=args.name, description=args.description)
            vservice.update_vlan(vlan_obj=tvlan, device_obj=sw)
        elif cmd == "merge":
            mresult = vservice.merge(device_obj=sw)
            print(f"Successful merge = {mresult.success}, {mresult.error}, {mresult.errmsg}")

if __name__ == "__main__":
    main()
