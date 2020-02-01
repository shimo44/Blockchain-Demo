from hfc.fabric_ca.caservice import ca_service
from resources.hyper_connect import HyperConnect


class User:
    def __init__(self):
        self.cacli = HyperConnect()

    def new_identity(self):
        identity_service = self.cacli.newIdentityService()

        admin = self.cacli.enroll("admin", "pass")
        admin = identity_service.create(admin, "shimo")

        res = identity_service.getOne('shimo', admin)
        res = identity_service.getAll(admin) # get all users
        res = identity_service.update('shimo', admin, maxEnrollments=3, affiliation='.', enrollmentSecret='bar') # update user foo
        res = identity_service.delete('shimo', admin) # delete user foo

