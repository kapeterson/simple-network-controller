import os
import logging
from typing import Optional, List
import sys
import pathlib


from networkapp.util.template import render_vlan_config
from networkapp.util.driver import get_device_driver
from networkapp.models.vlan import vlan
from networkapp.models.action_result import action_result
from networkapp.util.db import VlanDatabaseHelper


logger = logging.getLogger(__name__)

class NetworkService():

    def __init__(self, db_name):
        self.database_name = db_name


class VlanService(NetworkService):

    def __init__(self, db_name):
        super(VlanService, self).__init__(db_name=db_name)


    def can_merge(self, device_obj=None):
        """
        In order to merge properly without configuring priority:

        1. all vlans that are on both devices must be equal with id/name

        :return:
        """

        logging.info("can merge called")
        device_vlan_result = self.get_vlans_from_device(device_obj=device_obj)
        db_vlan_result = self.get_vlans_from_db(device_obj=device_obj)

        device_vlans = device_vlan_result.data
        db_vlans = db_vlan_result.data

        mergeable = True
        for vlan_id in device_vlans.keys():
            if vlan_id in db_vlans:
                tvlan = device_vlans[vlan_id]
                eq = tvlan == db_vlans[vlan_id]
                if not eq:
                    logger.info(f"Vlan {vlan_id} is in both checking equality = {eq}")
                    mergeable = False

        if not mergeable:

            return action_result(
                error=1,
                success=0,
                errmsg="Devices not mergeable"
            )


        res = action_result(success=1, error=0)
        res.data = { "can_merge" : mergeable}
        return res

    def merge(self, device_obj=None):
        """
        Do a merge between db and device

        :param device_obj:
        :return:
        """
        logging.info("merge called")
        canmerge_result = self.can_merge(device_obj=device_obj)

        if not canmerge_result.success or not canmerge_result.data['can_merge']:
            return action_result(success=0, error=1, errmsg="Device cannot be merged")

        merge1_result = self.merge_to_device(device_obj=device_obj)
        if merge1_result.success != 1:
            return merge1_result

        merge2_result = self.merge_from_device(device_obj=device_obj)
        return merge2_result

    def merge_from_device(self, device_obj, vlans:Optional[List]=None):
        """

        merge the vlans from the device into the database
        :param device_obj:
        :return:
        """
        logging.info("merge from device called")
        # now get list of vlans that are missing from the db.
        device_vlan_result = self.get_vlans_from_device(device_obj=device_obj)

        db_helper = VlanDatabaseHelper(db_name=self.database_name)
        db_vlan_result = db_helper.get_all_vlans_from_db()

        device_vlans = device_vlan_result.data
        db_vlans = db_vlan_result.data

        missing_from_db= []
        merge_vlans = []

        if vlans and len(vlans) > 0:
            for vid, vobj in device_vlans.items():
                if vid in vlans:
                    merge_vlans.append(vobj)

        else:
            merge_vlans = [ vobj for _, vobj in device_vlans.items() ]

        for vobj in merge_vlans:
            if vobj.id not in db_vlans.keys():
                logger.info(f"Flagging vlan {vobj.id} to be merged to db")
                missing_from_db.append(vlan(id=vobj.id, name=vobj.name,
                                                description=vobj.description))

        if len(missing_from_db) == 0:
            logger.info("No vlans to merge from device to db")
            return action_result(success=1, error=0)


        for vlan_obj in missing_from_db:
            logger.info("Adding vlan {vlan_obj.id} to db for merge")
            db_helper.add_vlan_to_db(vlan_id=vlan_obj.id, vlan_name=vlan_obj.name, description=vlan_obj.description)


        return action_result(success=1, error=0)

    def merge_to_device(self, device_obj, vlans:Optional[List]=None):
        """
        Get a list of vlans that are in the device but not in the router.
        Then render the template and add them to the router
        :param device_obj:
        :return:
        """

        logging.info("merge to device called")
        # now get list of vlans that are missing from the device.
        device_vlan_result = self.get_vlans_from_device(device_obj=device_obj)

        db_helper = VlanDatabaseHelper(db_name=self.database_name)
        db_vlan_result = db_helper.get_all_vlans_from_db()

        db_vlans = db_vlan_result.data
        device_vlans = device_vlan_result.data

        missing_from_device = []

        merge_vlans = []

        if vlans and len(vlans) > 0:

            for vid, vobj in db_vlans.items():
                if vid in vlans:
                    merge_vlans.append(vobj)
        else:

            for vid, vobj in db_vlans.items():
                if vid not in device_vlans.keys():
                    merge_vlans.append(vobj)

        #import ipdb; ipdb.set_trace()
        if len(merge_vlans) == 0:
            logger.info("No vlans to merge from db to device")
            return action_result(success=1, error=0)

        cfg = render_vlan_config(vlans_to_add=merge_vlans)
        cfg_set = cfg.split("\n")

        conn = get_device_driver(host_name=device_obj.hostname,
                                 username=device_obj.user,
                                 psswd=device_obj.psswd,
                                 device_type=device_obj.platform)

        op = conn.send_config_set(cfg_set)
        logger.debug(op)

        result = action_result(success=1, error=0)
        return result


    def add_vlan(self, vlan_obj:vlan=None, device_obj=None):
        """
        add a vlan to the db and then to the device
        :param input_args:
        :return:
        """
        in_sync_result = self.check_sync(device_obj=device_obj)
        logger.info(in_sync_result.data)
        if in_sync_result.error or not in_sync_result.data['synced']:
            res = action_result(success=0, error=1, errmsg=f"Device not in sync for vlan add")

        in_sync = in_sync_result.data['synced']

        logger.info(f"Device in sync = {in_sync}")

        if in_sync:
            vlanid = vlan_obj.id
            name = vlan_obj.name
            desc = vlan_obj.description
            logger.info(f"Adding vlan {vlanid} to the database")

            # add it to the database
            db_helper = VlanDatabaseHelper(db_name=self.database_name)
            add_result = db_helper.add_vlan_to_db(vlan_id=vlanid,
                                                          vlan_name=name,
                                                          description=desc)

            if not add_result.success:
                return add_result

            # now update the template
            logger.info(f"Updating device with new vlan {vlanid}")
            cfg = render_vlan_config(vlans_to_add=[{'id': vlanid, 'name': name}])
            cfg_set = cfg.split("\n")

            conn = get_device_driver(host_name=device_obj.hostname,
                                     username=device_obj.user,
                                     psswd=device_obj.psswd,
                                     device_type=device_obj.platform)

            op = conn.send_config_set(cfg_set)
            logger.debug(op)

            result = action_result(success=1, error=0)
            result.data = op
            return result

        else:
            logger.error("Device is not in sync with database")
            return action_result(error=1, success=0, errmsg="Device out of sync with db.")


    def get_vlans_from_db(self, device_obj=None):
        """
        Get the vlans from the database.

        :param self:
        :param device_obj:
        :return:
        """
        logger.info(f"Getting vlans from {self.database_name}")
        db_helper = VlanDatabaseHelper(db_name=self.database_name)
        intended_vlan_result = db_helper.get_all_vlans_from_db()

        return intended_vlan_result




    def get_vlans_from_device(self, device_obj=None):
        """
        Get the vlans from the device
        :param self:
        :param device_obj:
        :return:
        """
        logger.info("Getting vlans from device")
        vlan_command_dict = {
            "cisco_nxos": {
                "cmd": "show vlan",
                "textfsm_template": "textfsm_templates/cisco_nxos_show_vlan.textfsm"
            },
            "cisco_ios"  :{
                "cmd" : "show vlans",
                "textfsm_template" : "textfsm_templates/cisco_ios_show_vlan.textfsm"
            }
        }

        try:



            conn = get_device_driver(host_name=device_obj.hostname,
                                     username=device_obj.user,
                                     psswd=device_obj.psswd,
                                     device_type=device_obj.platform)


            cmd_detail = vlan_command_dict[device_obj.platform]
            cmd = cmd_detail['cmd']
            templ = cmd_detail['textfsm_template']

            c_path = os.path.dirname(os.path.abspath(sys.modules[self.__module__].__file__))
            pth = pathlib.Path(c_path)
            newpath = pth / templ
            logger.info(f"Current path = {c_path}")
            op = conn.send_command(cmd, use_textfsm=True,
                                   textfsm_template=newpath)
            logging.info(op)
            # hack.  the nxos is parsed as a dict instead of a list if thre
            # is only 1 vlan
            if isinstance(op,dict):
                op = [op]

            logger.info(op)
            configured_vlans = {}

            for vlandict in op:
                if isinstance(vlandict, dict):
                    configured_vlans[int(vlandict['vlan_id'])] = vlan(id=int(vlandict['vlan_id']), name=vlandict['name'])


            res = action_result(
                success=1,
                error=0,

            )
            res.data = configured_vlans
            return res

        except Exception as err:
            logger.error(f"Excpetion getting vlans from device: {repr(err)}")
            return action_result(
                success=0,
                error=1,
                errmsg=repr(err)
            )
    def del_vlan(self, vlan_id:int=None, device_obj=None):

        """
        Delete the vlan from the db and the device.

        :param self:
        :param vlan_id:
        :param device_obj:
        :return:
        """

        logger.info(f"Attempting to delete vlan {vlan_id}")

        # validate vlan is in the database
        db_vlans_result = self.get_vlans_from_db(device_obj=device_obj)
        db_vlans = db_vlans_result.data

        logger.info(db_vlans.keys())
        if vlan_id not in db_vlans.keys():
            logger.error(f"Vlan {vlan_id} type: {type(vlan_id)} is not in databse.  cannot delete")
            return  action_result(success=0, error=1, errmsg=f"Vlan {vlan_id} can't be deleted it doesn't exist")

        synced_result = self.check_sync(device_obj=device_obj)

        if not synced_result.success or not synced_result.data['synced']:
            logger.error(f"Device out of sync.")
            return action_result(success=0, error=1, errmsg="Devices not in sync during delete vlan")


        logger.info(f"Deleting vlan {vlan_id} to database")
        db_helper = VlanDatabaseHelper(db_name=self.database_name)
        del_result = db_helper.delete_vlan_from_db(vlan_id=vlan_id)

        if not del_result.success:
            logger.error(f"Unable to delete vlan {vlan_id} from database")
            return del_result

        # now delete from the device
        cfg = render_vlan_config(vlans_to_delete=[vlan_id])
        cfg_set = cfg.split("\n")
        conn = get_device_driver(host_name=device_obj.hostname,
                                 username=device_obj.user,
                                 psswd=device_obj.psswd,
                                 device_type=device_obj.platform)

        op = conn.send_config_set(cfg_set)
        logger.debug(op)
        return action_result(success=1, error=0)


    def sync_to(self, device_obj=None):
        """"
        Sync the database vlans to the device.  They will match after this
        """
        # get the vlans from the device
        configured_vlans_result = self.get_vlans_from_device(device_obj=device_obj)

        # now delete the vlans from database
        db_helper = VlanDatabaseHelper(db_name=self.database_name)
        intended_vlan_result = db_helper.get_all_vlans_from_db()

        configured_vlans = configured_vlans_result.data
        intended_vlans  = intended_vlan_result.data

        # get a list of vlans to delete
        vlans_to_delete = []
        for vlanid in configured_vlans.keys():
            if vlanid not in intended_vlans:
                logger.info("Adding vlan {vlanid} to delete list")
                vlans_to_delete.append(vlanid)

        vlans_to_add = []
        for vlanid, vlan_obj in intended_vlans.items():
            if vlanid not in configured_vlans or vlan_obj != configured_vlans[vlanid]:
                logger.info(f"Adding vlan {vlanid} to the add list on the device")
                vlans_to_add.append({
                    "id": vlanid,
                    "name": vlan_obj.name
                }
                )

        cfg = render_vlan_config(vlans_to_delete=vlans_to_delete, vlans_to_add=vlans_to_add)
        print(cfg)
        hostname = os.getenv("MANAGED_HOST", None)
        usr = os.getenv("ROUTER_USR")
        psswd = os.getenv("ROUTER_PSSWD")
        device_type = os.getenv("DEVICE_TYPE")

        conn = get_device_driver(host_name=device_obj.hostname, username=device_obj.user,
                                 psswd=device_obj.psswd, device_type=device_obj.platform)
        op = conn.send_config_set(cfg.split("\n"))
        print(op)
        res = action_result(success=1, error=0)
        return res

    def sync_from(self, device_obj):
        """
        Sync the device vlans to the database.  they will match after this.
        :return:
        """

        # get the vlans from the device
        configured_result = self.get_vlans_from_device(device_obj=device_obj)

        # now delete the vlans from database
        db_helper = VlanDatabaseHelper(db_name=self.database_name)
        deleted_count = db_helper.clear_vlans_from_db()

        configured_vlans = configured_result.data
        #import ipdb; ipdb.set_trace()

        sync_vlans = [vlanobj for _, vlanobj in configured_vlans.items() ]

        all_pass = True
        # now add the vlans to db
        for vlanobj in sync_vlans:
            logger.info(type(vlanobj))
            logger.info(f"Adding {vlanobj.id} to database")
            res = db_helper.add_vlan_to_db(vlan_id=vlanobj.id, vlan_name=vlanobj.name, description="")
            if res.success == 0:
                all_pass = False

        if all_pass:
            return action_result(success=1, error=0)

        return action_result(success=0, errmsg=1)


    def dump_db(self, device_obj=None):
        """
        Dump all
        :param self:
        :param device_obj:
        :return:
        """
        logger.info(f"Dumping vlans from db {self.database_name}")
        db_helper = VlanDatabaseHelper(db_name=self.database_name)

        db_result = db_helper.get_all_vlans_from_db()
        if db_result.success == 0:
            return db_result

        logger.info(f"{len(db_result.data)} vlans from database")
        rows = db_result.data

        for k, v in rows.items():
            print(v.toJSON())

        return db_result

    def update_vlan(self, vlan_obj=None, device_obj=None):

        vlan_id = vlan_obj.id

        logger.info("Updating vlan {vlan_obj.id} on {device_obj.hostname}")




        # validate vlan is in the database
        db_vlan_result = self.get_vlans_from_db(device_obj=device_obj)
        db_vlans = db_vlan_result.data

        logger.info(db_vlans.keys())
        if vlan_id not in db_vlans:
            logger.error(f"Vlan {vlan_id} is not in databse.  cannot update")
            return action_result(success=0, error=1, errmsg=f"Vlan {vlan_id} can't be updated it doesn't exist")

        synced_result = self.check_sync(device_obj=device_obj)


        if not synced_result.success or not synced_result.data['synced']:
            logger.error(f"Device out of sync.")
            return action_result(success=0, error=1, errmsg="Devices not in sync during update")

        logger.info(f"Updating vlan {vlan_id} in database")
        db_helper = VlanDatabaseHelper(db_name=self.database_name)
        update_result = db_helper.update_vlan_in_db(vlan_id=vlan_id,
                                                 vlan_name=vlan_obj.name,
                                                 description=vlan_obj.description)

        if update_result.success == 0:

            logger.error(f"Failure updating vlan {vlan_id}")
            return update_result

        else:
            logger.info("updating vlan in router")

            vlans_to_add=[
                vlan_obj
            ]


        cfg = render_vlan_config(vlans_to_delete=[], vlans_to_add=vlans_to_add)
        cfg_set = cfg.split("\n")

        try:
            conn = get_device_driver(host_name=device_obj.hostname,
                                     username=device_obj.user,
                                     psswd=device_obj.psswd,
                                     device_type=device_obj.platform)

            op = conn.send_config_set(cfg_set)
            logger.debug(op)
            return action_result(success=1, error=0)

        except Exception as err:
            logger.error(f"Error updating vlan on device")
            return action_result(success=0, error=1, errmsg=repr(err))


    def check_sync(self, device_obj=None):
        hostname = os.getenv("MANAGED_HOST", None)
        logger.info("Checking sync")

        vlan_result = self.get_vlans_from_device(device_obj=device_obj)
        configured_vlans = vlan_result.data
        logger.info(f"Read vlans {configured_vlans} from device {hostname}")
        db_helper = VlanDatabaseHelper(db_name=self.database_name)

        if vlan_result.error == 1:
            logger.error("Error in check_sync getting vlans from device")
            return vlan_result

        db_vlan_result = db_helper.get_all_vlans_from_db()
        if db_vlan_result.success == 0:
            logger.info("Unsuccessful getting all vlans from db in check_sync")
            db_vlan_result.data['synced'] = False
            return db_vlan_result

        intended_vlan_rows = db_vlan_result.data

        synced = True
        for vlanid, vlanobj in configured_vlans.items():
            if int(vlanid) not in intended_vlan_rows:
                logger.info(f"VLAN {vlanid} is in the router but not database")
                synced = False
            else:
                db_vlan = intended_vlan_rows[vlanid]
                if db_vlan != vlanobj:
                    synced = False
                    logger.info(f"Vlans {vlanid} not equal")

        for vlanid, vlanobj in intended_vlan_rows.items():
            if vlanid not in configured_vlans:
                logger.info(f"Vlan {vlanid} missing on router")
                synced = False
            else:
                cfg_vlan = configured_vlans[vlanid]
                if cfg_vlan != vlanobj:
                    synced = False
                    logger.info(f"Vlans not equal for vlan {vlanid}")

        res = action_result(error=0,success=int(synced))
        res.data = {'synced': synced}
        logger.info(f"Sync = {synced}")
        return res


    def run(self):
        logger.info("Running the vlan service")