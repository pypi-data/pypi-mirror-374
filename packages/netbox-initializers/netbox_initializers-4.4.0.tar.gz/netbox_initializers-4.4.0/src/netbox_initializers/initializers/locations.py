from dcim.models import Location, Site

from netbox_initializers.initializers.base import BaseInitializer, register_initializer

OPTIONAL_ASSOCS = {"site": (Site, "name"), "parent": (Location, "name")}


class LocationInitializer(BaseInitializer):
    data_file_name = "locations.yml"

    def load_data(self):
        locations = self.load_yaml()
        if locations is None:
            return
        for params in locations:
            tags = params.pop("tags", None)

            for assoc, details in OPTIONAL_ASSOCS.items():
                if assoc in params:
                    model, field = details
                    query = {field: params.pop(assoc)}
                    params[assoc] = model.objects.get(**query)

            matching_params, defaults = self.split_params(params)
            location, created = Location.objects.get_or_create(**matching_params, defaults=defaults)

            if created:
                print("🎨 Created location", location.name)

            self.set_tags(location, tags)


register_initializer("locations", LocationInitializer)
