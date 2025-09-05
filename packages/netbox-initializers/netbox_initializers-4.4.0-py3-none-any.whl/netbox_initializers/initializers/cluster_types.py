from virtualization.models import ClusterType

from netbox_initializers.initializers.base import BaseInitializer, register_initializer


class ClusterTypesInitializer(BaseInitializer):
    data_file_name = "cluster_types.yml"

    def load_data(self):
        cluster_types = self.load_yaml()
        if cluster_types is None:
            return
        for params in cluster_types:
            tags = params.pop("tags", None)
            matching_params, defaults = self.split_params(params)
            cluster_type, created = ClusterType.objects.get_or_create(
                **matching_params, defaults=defaults
            )

            if created:
                print("🧰 Created Cluster Type", cluster_type.name)
            self.set_tags(cluster_type, tags)


register_initializer("cluster_types", ClusterTypesInitializer)
