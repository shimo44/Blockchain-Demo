from hfc.fabric import ca_service


class HyperConnect:

    def __init__(self):
        pass

    def connect(self):
        cli = Client(net_profile="test/fixtures/network.json")

        print(cli.organizations)  # orgs in the network
        print(cli.peers)  # peers in the network
        print(cli.orderers)  # orderers in the network
        print(cli.CAs)  # ca nodes in the network, TODO

    def get_cli(self):
        cli = ca_service(target="https://127.0.0.1:7054")
        return cli


    def make_admin(self):
        cli = self.get_cli()

        adminEnrollment = cli.enroll("admin", "pass")
        secret = adminEnrollment.register("user1")

        user1Enrollment = cli.enroll("user1", secret)

        admin = user1Enrollment

        return admin, adminEnrollment


    def renroll(self):
        cli = self.get_cli()
        admin, admin_enrollment = self.make_admin()

        user1ReEnrollment = cli.reenroll(admin)

        RevokedCerts, CRL = admin_enrollment.revoke("user1")

