# VLAN APP

## Demo

https://www.youtube.com/watch?v=_Zi_ux3b5HE

## Summary


Network controller form managing VLANS.

**TESTED ONLY ON NEXUS**

The is implemented as a network controller and uses the following components:
- Data Models for VLANS, and devices
- vlan database helper class for interfacting with database
- Vlan Service Class for main functionality of the library
- Controller implemented in fastapi for exposing library functionality through API.
- CLI tool for



Managing updates in two places is difficult to maintain but this tries to allow
a flexible solution.  In the end rules should be put in place to handle sync issues
and give router vs database priority.

Through the use of the controller, all updates to vlans through teh tool
can be added to the database and then updated on the router.

The controller provides trigger endpoints, where events for configuration
changes on the router can trigger an API call to the controller to notify
of changes on the router that need to be synced.  This notification/trigger
is not implented at this time and the notification must be done manually after
a config change.

The controller exposes the following:

**check_sync** Tells whether or not db and router are in sync.

**sync_from** Updates the VLAN database to match the router.

**sync_to** Updates the router to match the database.

**merge** This is the process of merging or combining the vlans from the both
the router and the database.  In order for a merget to be allowed, the VLANs
existing on both the db and the router must match.  Any vlans on the router
that are not int he database will be added to the database.  Any vlans in
the db that are not in the router will be added on the router.

**can_merge** Is the state of the db and router in a state that it can be merged.

**merge_from_device** Add all the missing vlans from the router to the db.

**merge_to_device** add all the missing vlans from the db to the router.

**delete_vlan** delete the vlan from the db and the router.

**add_vlan** add a vlan to the db and router.

**update_vlan** update a vlan in the db and the router.

**get_device_vlans** get the vlans from teh router

**get_db_vlans** get the vlans from the db.


## Setup

The easiest way to run this is with a pip install.  While
in them ain project directory.

Instructions are for mac or linux.

```
# create venv
python3 -m venv env

#activate virtual env
. env/bin/activate

# upgrade pip
python -m pip install --upgrade pip

# install the application.
pip install .

# start the "controller" in one shell
# can access the API Swagger page at 127.0.0.1:8000/docs
vlan-controller

# use the vlan_cli
vlan-cli --help
vlan-cli dumprouter
vlan-cli dumpdb
vlan-cli add
vlan-cli del
vlan-cli update

```
## Requirements

The following ENV variables will be used for running the tool.
```
export DB_URI=$(pwd)/mydb.db
export MANAGED_HOST=172.16.30.54
export ROUTER_USR=cisco
export ROUTER_PSSWD=cisco
export DEVICE_TYPE=cisco_nxos
```

## tests

Unit tests can be run in the tests directory.

```
pytest tests
```
