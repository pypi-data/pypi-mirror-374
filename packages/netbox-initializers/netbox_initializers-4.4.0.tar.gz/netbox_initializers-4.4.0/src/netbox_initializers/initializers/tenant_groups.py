from tenancy.models import TenantGroup

from netbox_initializers.initializers.base import BaseInitializer, register_initializer


class TenantGroupInitializer(BaseInitializer):
    data_file_name = "tenant_groups.yml"

    def load_data(self):
        tenant_groups = self.load_yaml()
        if tenant_groups is None:
            return
        for params in tenant_groups:
            tags = params.pop("tags", None)
            matching_params, defaults = self.split_params(params)
            tenant_group, created = TenantGroup.objects.get_or_create(
                **matching_params, defaults=defaults
            )

            if created:
                print("🔳 Created Tenant Group", tenant_group.name)

            self.set_tags(tenant_group, tags)


register_initializer("tenant_groups", TenantGroupInitializer)
