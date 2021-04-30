"""
uvicorn api:app --reload --log-level info --log-config logconfig.yaml
"""
from fastapi import FastAPI
import os
import json
import logging
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

from networkapp.netservice import VlanService
from networkapp.models.switch import cisco_switch
from networkapp.models.vlan import vlan
from networkapp.util.db import VlanDatabaseHelper

from networkapp.api.logconfig import log_config as logcfg

logging.config.dictConfig(logcfg)


app = FastAPI(
    title="Vlan Controller",
    description="Simple Vlan Controller",
    version="0.00",
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DB_URI=os.getenv("DB_URI",None)

class Vlan(BaseModel):
    id: int
    name: str
    description: str

class VlanList(BaseModel):
    vlans: Optional[List] = []



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

@app.post("/trigger/device_vlan_add", tags=['trigger'])
def trigger_device_vlan_add_update(vobj: Vlan):
    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    return vservice.merge_from_device(device_obj=sw, vlans=[vobj.id])

@app.post("/trigger/device_vlan_delete", tags=['trigger'])
def trigger_device_vlan_delete(vobj : Vlan):
    db_helper = VlanDatabaseHelper(db_name=DB_URI)
    del_result = db_helper.delete_vlan_from_db(vlan_id=vobj.id)

    return del_result

@app.delete("/vlan/{vlan_id}", tags=['config'])
def del_vlan(vlan_id:int):
    logger.info(f"Received del vlan {vlan_id} in api")

    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    del_result = vservice.del_vlan(vlan_id=vlan_id, device_obj=sw)
    return del_result

@app.put("/vlan/{vlanid}", tags=['config'])
def update_vlan(v: Vlan, vlanid):
    logger.info(f"Updating vlan {vlanid} in api")
    this_vlan = vlan(id=v.id, name=v.name, description=v.description)


    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    update_result = vservice.update_vlan(vlan_obj=this_vlan, device_obj=sw)
    return update_result

@app.post("/vlan/{vlanid}", tags=['config'])
def add_vlan(v: Vlan, vlanid):
    logger.info(f"adding vlan {vlanid} through api")
    this_vlan = vlan(id=v.id, name=v.name, description=v.description)


    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    add_result = vservice.add_vlan(vlan_obj=this_vlan, device_obj=sw)
    return add_result

@app.get("/sync_from_device", tags=['config'])
def sync_from_device():

    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    sync_result = vservice.sync_from(device_obj=sw)
    return sync_result

@app.get("/sync_to_device", tags=['config'])
def sync_from_device():

    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    sync_result = vservice.sync_to(device_obj=sw)
    return sync_result

@app.post("/merge_to_device", tags=['config'])
def merge_go(vlans: VlanList):

    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    merge_reult = vservice.merge_to_device(device_obj=sw, vlans=vlans.vlans)
    return merge_reult

@app.post("/merge_from_device", tags=['config'])
def merge_from(vlans: VlanList):

    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    merge_reult = vservice.merge_from_device(device_obj=sw, vlans=vlans.vlans)
    return merge_reult

@app.get("/merge", tags=['config'])
def merge():

    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    merge_reult = vservice.merge(device_obj=sw)
    return merge_reult

@app.get("/can_merge", tags=['oper'])
def can_merge():
    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())
    can_merge_result = vservice.can_merge(device_obj=sw)
    return can_merge_result

@app.get("/get_device_vlans", tags=['oper'])
def device_vlans():
    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())

    device_vlans_result = vservice.get_vlans_from_device(device_obj=sw)
    if device_vlans_result.success == 0:
        return device_vlans_result

    vlans = []


    device_vlans = device_vlans_result.data

    for vlanid, vlan_obj in device_vlans.items():
        logger.info(vlanid)
        vlans.append(vlan_obj.toJSON())

    logger.info(json.dumps(vlans))
    device_vlans_result.data = vlans

    return device_vlans_result

@app.get("/get_db_vlans", tags=['oper'])
def db_vlans():

    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())

    db_vlan_result = vservice.get_vlans_from_db(device_obj=sw)
    vlans = []

    db_vlans = db_vlan_result.data

    # jsonify the data

    for vlanid, vlan_obj in db_vlans.items():
        logger.info(vlanid)
        vlans.append(vlan_obj.toJSON())

    logger.info(json.dumps(vlans))
    return db_vlan_result

@app.get("/check_sync", tags=['oper'])
def check_sync():

    vservice = VlanService(db_name=DB_URI)
    sw = cisco_switch(**get_params_from_env())

    sync = vservice.check_sync(device_obj=sw)

    return sync

def run():
    uvicorn.run("networkapp.api.api:app", host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    run()
