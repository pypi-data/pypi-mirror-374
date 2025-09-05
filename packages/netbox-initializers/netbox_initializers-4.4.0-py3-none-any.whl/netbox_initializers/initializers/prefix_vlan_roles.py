from ipam.models import Role

from netbox_initializers.initializers.base import BaseInitializer, register_initializer


class RoleInitializer(BaseInitializer):
    data_file_name = "prefix_vlan_roles.yml"

    def load_data(self):
        roles = self.load_yaml()
        if roles is None:
            return
        for params in roles:
            tags = params.pop("tags", None)
            matching_params, defaults = self.split_params(params)
            role, created = Role.objects.get_or_create(**matching_params, defaults=defaults)

            if created:
                print("⛹️‍ Created Prefix/VLAN Role", role.name)

            self.set_tags(role, tags)


register_initializer("prefix_vlan_roles", RoleInitializer)
