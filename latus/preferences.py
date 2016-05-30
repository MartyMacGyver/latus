
import os
import datetime

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative

import latus.util
import latus.const
import latus.logger

Base = sqlalchemy.ext.declarative.declarative_base()

class PreferencesTable(Base):
    __tablename__ = 'preferences'

    key = sqlalchemy.Column(sqlalchemy.String(), primary_key=True)
    value = sqlalchemy.Column(sqlalchemy.String())
    datetime = sqlalchemy.Column(sqlalchemy.DateTime())


class Preferences:

    PREFERENCES_FILE = 'preferences' + latus.const.DB_EXTENSION

    def __init__(self, latus_appdata_folder, init=False):

        self.__id_string = 'nodeid'
        self.__key_string = 'cryptokey'
        self.__most_recent_key_folder_string = 'keyfolder'
        self.__cloud_root_string = 'cloudroot'
        self.__latus_folder_string = 'latusfolder'
        self.__verbose_string = 'verbose'

        if not os.path.exists(latus_appdata_folder):
            latus.util.make_dirs(latus_appdata_folder)
        self._db_path = os.path.abspath(os.path.join(latus_appdata_folder, self.PREFERENCES_FILE))
        sqlite_path = 'sqlite:///' + self._db_path
        self.__db_engine = sqlalchemy.create_engine(sqlite_path)  # , echo=True)
        if init:
            self.init()
        Base.metadata.create_all(self.__db_engine)
        self.__Session = sqlalchemy.orm.sessionmaker(bind=self.__db_engine)

    def __pref_set(self, key, value):
        latus.logger.log.debug('pref_set : %s to %s' % (str(key), str(value)))
        session = self.__Session()
        pref_table = PreferencesTable(key=key, value=value, datetime=datetime.datetime.utcnow())
        q = session.query(PreferencesTable).filter_by(key=key).first()
        if q:
            session.delete(q)
        session.add(pref_table)
        session.commit()
        session.close()

    def __pref_get(self, key):
        latus.logger.log.debug('pref_get : %s' % str(key))
        session = self.__Session()
        row = session.query(PreferencesTable).filter_by(key=key).first()
        if row:
            value = row.value
        else:
            value = None
        session.close()
        latus.logger.log.debug('pref_get : %s' % str(value))
        return value

    def set_crypto_key(self, key):
        self.__pref_set(self.__key_string, key)

    def get_crypto_key(self):
        return self.__pref_get(self.__key_string)

    def set_cloud_root(self, folder):
        self.__pref_set(self.__cloud_root_string, os.path.abspath(folder))

    def get_cloud_root(self):
        return self.__pref_get(self.__cloud_root_string)

    def set_latus_folder(self, folder):
        self.__pref_set(self.__latus_folder_string, os.path.abspath(folder))

    def get_latus_folder(self):
        return self.__pref_get(self.__latus_folder_string)

    def set_verbose(self, value):
        self.__pref_set(self.__verbose_string, str(value))

    def get_verbose(self):
        return bool(self.__pref_get(self.__verbose_string))

    def set_key_folder(self, folder):
        self.__pref_set(self.__most_recent_key_folder_string, folder)

    def get_key_folder(self):
        return self.__pref_get(self.__most_recent_key_folder_string)

    def set_node_id(self, new_node_id):
        self.__pref_set(self.__id_string, new_node_id)

    def get_node_id(self):
        return self.__pref_get(self.__id_string)

    def get_db_path(self):
        return self._db_path

    def init(self):
        Base.metadata.drop_all(self.__db_engine)
        Base.metadata.create_all(self.__db_engine)

    def folders_are_set(self):
        return self.get_cloud_root() is not None and self.get_latus_folder() is not None