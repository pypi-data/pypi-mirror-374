from tenancy.models import ContactRole

from netbox_initializers.initializers.base import BaseInitializer, register_initializer


class ContactRoleInitializer(BaseInitializer):
    data_file_name = "contact_roles.yml"

    def load_data(self):
        contact_roles = self.load_yaml()
        if contact_roles is None:
            return
        for params in contact_roles:
            custom_field_data = self.pop_custom_fields(params)
            tags = params.pop("tags", None)

            matching_params, defaults = self.split_params(params)
            contact_role, created = ContactRole.objects.get_or_create(
                **matching_params, defaults=defaults
            )

            if created:
                print("🔳 Created Contact Role", contact_role.name)

            self.set_custom_fields_values(contact_role, custom_field_data)
            self.set_tags(contact_role, tags)


register_initializer("contact_roles", ContactRoleInitializer)
