from ipam.models import RIR

from netbox_initializers.initializers.base import BaseInitializer, register_initializer


class RIRInitializer(BaseInitializer):
    data_file_name = "rirs.yml"

    def load_data(self):
        rirs = self.load_yaml()
        if rirs is None:
            return

        for params in rirs:
            tags = params.pop("tags", None)
            matching_params, defaults = self.split_params(params)
            rir, created = RIR.objects.get_or_create(**matching_params, defaults=defaults)

            if created:
                print("🗺️ Created RIR", rir.name)

            self.set_tags(rir, tags)


register_initializer("rirs", RIRInitializer)
