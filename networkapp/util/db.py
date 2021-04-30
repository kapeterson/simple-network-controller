import sqlite3
import logging
import os
from networkapp.models.vlan import vlan
from networkapp.models.action_result import action_result

logger = logging.getLogger(__name__)

class VlanDatabaseHelper():

    def __init__(self, db_name):
        self.database_name = db_name

        if not self.db_file_exists(db_name):
            self.create_database()

        if not self.vlan_table_exists():
            self.create_vlan_table()
        else:
            logger.info("VLAN table already exists")


    def vlan_table_exists(self):

        conn = sqlite3.connect(self.database_name)
        cur = conn.cursor()
        cur.execute("SELECT name from sqlite_master where type='table' and name='VLANS'")
        rows = cur.fetchall()
        logger.info(f"Searching for vlans count = {len(rows)}")
        return len(rows) == 1

    def db_file_exists(self, db_path):
        """

        :param db_path:
        :return:
        """
        return os.path.isfile(self.database_name)


    def clear_vlans_from_db(self):
        try:
            conn = sqlite3.connect(self.database_name)
            cur = conn.cursor()
            op = cur.execute("DELETE FROM VLANS")
            logger.info(f"Clearning vlans row result = {op.rowcount}")
            conn.commit()
            vlan_map = {}

            return action_result(success=1, error=0)
            #return op.rowcount


        except Exception as err:
            logger.error(f"Error clearing vlans from db")
            logger.error(repr(err))
            return action_result(
                success=0,
                error=1,
                errormsg=repr(e)
            )

    def get_all_vlans_from_db(self):

        try:
            conn = sqlite3.connect(self.database_name)
            cur = conn.cursor()
            cur.execute("SELECT * FROM VLANS")
            rows = cur.fetchall()

            vlan_map = {}
            for row in rows:
                #import ipdb; ipdb.set_trace()
                vlan_map[row[0]] = vlan(id=row[0], name=row[1], description=row[2])


            #return vlan_map
            res = action_result(
                success=1,
                error=0,
            )
            res.data = vlan_map
            return res

        except Exception as err:
            logger.error(f"Error getting vlans from db")
            logger.error(repr(err))
            res = action_result(
                success=0,
                error=1,
                errmsg=repr(err)

            )
            return res

    def update_vlan_in_db(self, vlan_id=None, vlan_name=None, description=None):
        """

        :param db_name:
        :param vlan_id:
        :param name:
        :param description:
        :return:
        """
        update_sql = f"""UPDATE VLANS
        SET
        name = '{vlan_name}',
        description = '{description}'
        WHERE
        id = {vlan_id};

        """

        logger.info(f"Attempting to update vlan {vlan_id} in database")
        logger.info(update_sql)
        try:
            conn = sqlite3.connect(self.database_name)
            cur = conn.cursor()
            op = cur.execute(update_sql)
            impacted_rows = op.rowcount
            logger.info(f"Impacted rows in update for vlan {vlan_id} = {impacted_rows}")

            conn.commit()
            if impacted_rows != 1:
                logger.error("{impacted_rows} impacted by update")
                return action_result(success=0, error=1, errmsg=f"{impacted_rows} db rows impacted by update")
            elif impacted_rows == 1:
                return action_result(success=1, error=0)

        except Exception as err:
            logger.error(f"Error updating vlan {vlan_id}")
            logger.error(repr(err))
            return action_result(success=0, error=1, errmsg=repre(err))

    def delete_vlan_from_db(self, vlan_id=None) -> action_result:
        del_sql = f"DELETE FROM VLANS where id={vlan_id}"


        try:
            conn = sqlite3.connect(self.database_name)
            cur = conn.cursor()
            op = cur.execute(del_sql)
            impacted_rows = op.rowcount
            logger.info(f"Impacted rows in delete = {impacted_rows}")
            conn.commit()

            if impacted_rows == 0:
                logger.error("No rows impacted by delete")
                return action_result(error=1, success=0, errmsg=f"Received {op.rowcount} row results in addtition")

            else:
                return action_result(error=0, success=1)

        except Exception as err:
            logger.error(f"Error deleting vlan {vlan_id}")
            logger.error(repr(err))

            return action_result(error=1, success=0, errmsg=repr(e))

    def add_vlan_to_db(self, vlan_id=None, vlan_name=None, description=None) -> action_result:
        conn = sqlite3.connect(self.database_name)
        ins_vlan = f"""INSERT INTO VLANS ( 'id', 'name', 'description')
        VALUES ({vlan_id}, '{vlan_name}', '{description}')
        """

        try:
            logger.info(f"Adding vlan {vlan_id} to database")
            cur = conn.cursor()
            op = cur.execute(ins_vlan)
            logger.info(f"Rowcount {op.rowcount}")
            conn.commit()
            if op.rowcount == 1:
                return action_result(error=0, success=1)
            else:
                return action_result(error=1, success=0, errmsg=f"Received {op.rowcount} row results in addtition")

        except Exception as err:

            logger.error("Exception during insert")
            logger.error(repr(err))
            return action_result(error=1, success=0, errmsg=repr(err))


    def get_db_connection(db_name=None):
        """
        Get the connection to the database
        :param db_name:
        :return:
        """

    def create_database(self):
        """

        :param db_name:
        :return:
        """


        logger.info(f"Creating database {self.database_name}")
        self.create_vlan_table()


    def create_vlan_table(self):
        """

        :param db_name:
        :return:
        """

        vlan_table_sql = """
        CREATE TABLE IF NOT EXISTS VLANS (
        id integer UNIQUE,
        name text,
        description text
        )
        """

        logger.info("Creating VLAN table called if it does not exist")
        conn = sqlite3.connect(self.database_name)
        c = conn.cursor()
        c.execute(vlan_table_sql)
        conn.commit()
        #logger.info(dir(c))
        logger.info(f"{c.rowcount} Impacted ")
