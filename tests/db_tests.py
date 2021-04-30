import pytest
from networkapp.util.db import VlanDatabaseHelper
import os

DBNAME_01="testdb.db"

@pytest.fixture(scope='class')
def project_dir(tmpdir_factory):
    my_tmpdir = tmpdir_factory.mktemp("dbdir")
    return my_tmpdir
    #shutil.rmtree(str(my_tmpdir))



class TestDB():


    def test_new_db_creation(self, project_dir):
        p = project_dir / DBNAME_01
        db_helper = VlanDatabaseHelper(db_name=p)
        assert db_helper.database_name == p
        assert db_helper is not None
        assert db_helper.vlan_table_exists() == True


    def test_db_loading(self, project_dir):
        p = project_dir / DBNAME_01
        db_helper = VlanDatabaseHelper(db_name=p)
        db_vlans = db_helper.get_all_vlans_from_db()
        #print(p)
        assert db_helper.vlan_table_exists() == True
        assert db_vlans.error == 0
        assert db_vlans.success == 1
        assert db_vlans.data is not None
        assert db_vlans.data == {}


    def test_vlan_addition(self, project_dir):
        p = project_dir / DBNAME_01

        db_helper = VlanDatabaseHelper(db_name=p)
        res = db_helper.add_vlan_to_db(vlan_id=2,vlan_name="test",description="test")
        assert res.success == 1

        db_vlan_result = db_helper.get_all_vlans_from_db()
        assert db_vlan_result.success == 1

        data = db_vlan_result.data
        assert len(data) == 1


    def test_vlan_already_exists(self, project_dir):
        p = project_dir / DBNAME_01

        db_helper = VlanDatabaseHelper(db_name=p)
        res = db_helper.add_vlan_to_db(vlan_id=2,vlan_name="test",description="test")
        assert res.success == 0

        db_vlan_result = db_helper.get_all_vlans_from_db()
        assert db_vlan_result.success == 1

        data = db_vlan_result.data
        assert len(data) == 1
        assert data[2].name == "test"


    def test_vlan_update(self, project_dir):
        p = project_dir / DBNAME_01

        db_helper = VlanDatabaseHelper(db_name=p)

        ud_result = db_helper.update_vlan_in_db(vlan_id=2, vlan_name="test2", description="asdf")
        assert ud_result.success == 1

        db_vlan_result = db_helper.get_all_vlans_from_db()
        assert db_vlan_result.success == 1

        data = db_vlan_result.data
        assert len(data) == 1
        assert data[2].name == "test2"
        assert data[2].description == "asdf"


    def test_vlan_clear(self, project_dir):
        p = project_dir / DBNAME_01
        db_helper = VlanDatabaseHelper(db_name=p)
        res = db_helper.clear_vlans_from_db()
        assert res.success == 1

        db_vlan_result = db_helper.get_all_vlans_from_db()
        assert db_vlan_result.success == 1

        data = db_vlan_result.data
        assert len(data) == 0