from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.management.base import BaseCommand, CommandError

from ligoauth.management.commands.update_user_accounts_from_ligo_ldap import LigoPeopleLdap, KagraPeopleLdap

UserModel = get_user_model()
LDAP_CLASSES = {l.name: l for l in (LigoPeopleLdap, KagraPeopleLdap,)}


def get_all_permissions():
    permissions = set()
    TmpSuperuser = get_user_model()(is_active=True, is_superuser=True)

    for backend in auth.get_backends():
        if hasattr(backend, "get_all_permissions"):
            permissions.update(backend.get_all_permissions(TmpSuperuser))

    sorted_list_of_permissions = sorted(list(permissions))

    return sorted_list_of_permissions


class Command(BaseCommand):
    help="Get updated user data from LIGO/gw-astronomy LDAP for a single account"

    def add_arguments(self, parser):
        parser.add_argument('username',
            help="albert.einstein username to update")
        parser.add_argument('-p', '--password', default="userpassword",
            help="Local user password")
        parser.add_argument('-s', '--superuser', action='store_true',
            default=False, help="Is superuser?")
        parser.add_argument('-q', '--quiet', action='store_true',
            default=False, help='Suppress output')

    def handle(self, *args, **options):

        verbose = not options['quiet']

        # Set up ldap connection
        ldap_connection = LDAP_CLASSES['ligo'](verbose=verbose)
        ldap_connection.initialize()

        # Perform query
        result_data = ldap_connection.perform_query()

        # Search required username in list
        username_list = [entry[1]['krbPrincipalName'][0].decode('utf-8') for entry in result_data]
        result_data = [result_data[ui] for ui in range(len(username_list)) if username_list[ui] == options['username']]

        # Check username exists
        if len(result_data) == 0:
            raise ValueError("No matches found for %s" % username)

        else:
            ldap_dn, ldap_result = result_data[0]

            # Set up user processor
            user_processor = ldap_connection.initialize_user_processor(ldap_dn,
                ldap_result, verbose=verbose, stdout=self.stdout)

            # Get or create user - if an error occurs, continue.
            # Details should already be written to the log.
            user_processor.extract_user_attributes()
            user_processor.get_or_create_user()

            # Update user based on LDAP information - this includes
            # attributes, group memberships, X509 certificates, etc.
            user_processor.update_user()
            user_processor.save_user()

            # If provided, update password
            user_processor.user.set_password(options['password'])
            user_processor.user.save()

            # If true, make superuser
            user_processor.user.is_superuser = options['superuser']
            #if options['superuser']:
            #    for perm_codename in get_all_permissions():
            #        perm = Permission.objects.get(codename=perm_codename)
            #        user_processor.user.user_permissions.add(perm)
            user_processor.user.save()
