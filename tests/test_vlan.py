from networkapp.models.vlan import vlan

def test_vlan_instantiation():
    this_vlan = vlan(id=1, name="vlanone", description="default vlan")
    assert this_vlan.id == 1
    assert this_vlan.name == "vlanone"
    assert this_vlan.description == "default vlan"

def test_no_desc():
    this_vlan = vlan(id=1, name="vlanone")
    assert this_vlan.id == 1
    assert this_vlan.name == "vlanone"
    assert this_vlan.description == None