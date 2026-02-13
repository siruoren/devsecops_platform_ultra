import random

class MasterSlaveRouter:
    def db_for_read(self, model, **hints): return 'replica'
    def db_for_write(self, model, **hints): return 'default'
    def allow_relation(self, obj1, obj2, **hints): return True
    def allow_migrate(self, db, app_label, model_name=None, **hints): return db == 'default'

class ActiveActiveRouter:
    def db_for_read(self, model, **hints): return random.choice(['dc1_replica', 'dc2_replica'])
    def db_for_write(self, model, **hints): return ['dc1_master', 'dc2_master']
    def allow_relation(self, obj1, obj2, **hints): return True
    def allow_migrate(self, db, app_label, model_name=None, **hints): return True
