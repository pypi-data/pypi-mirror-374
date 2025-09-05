from typing import Tuple
from circuits.constants import CIRCUIT_TERMINATION_TERMINATION_TYPES
from circuits.models import Circuit, CircuitTermination
from dcim.models import (
    Cable,
    CableTermination,
    ConsolePort,
    ConsoleServerPort,
    FrontPort,
    Interface,
    PowerFeed,
    PowerOutlet,
    PowerPanel,
    PowerPort,
    RearPort,
)
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from netbox_initializers.initializers.base import BaseInitializer, register_initializer
from netbox_initializers.initializers.utils import get_scope_details

CONSOLE_PORT_TERMINATION = ContentType.objects.get_for_model(ConsolePort)
CONSOLE_SERVER_PORT_TERMINATION = ContentType.objects.get_for_model(ConsoleServerPort)
FRONT_PORT_TERMINATION = ContentType.objects.get_for_model(FrontPort)
REAR_PORT_TERMINATION = ContentType.objects.get_for_model(RearPort)
FRONT_AND_REAR = [FRONT_PORT_TERMINATION, REAR_PORT_TERMINATION]
POWER_PORT_TERMINATION = ContentType.objects.get_for_model(PowerPort)
POWER_OUTLET_TERMINATION = ContentType.objects.get_for_model(PowerOutlet)
POWER_FEED_TERMINATION = ContentType.objects.get_for_model(PowerFeed)
POWER_TERMINATIONS = [POWER_PORT_TERMINATION, POWER_OUTLET_TERMINATION, POWER_FEED_TERMINATION]

VIRTUAL_INTERFACES = ["bridge", "lag", "virtual"]


def get_termination_object(params: dict, side: str):
    klass = params.pop(f"termination_{side}_class")
    name = params.pop(f"termination_{side}_name", None)
    device = params.pop(f"termination_{side}_device", None)
    feed_params = params.pop(f"termination_{side}_feed", None)
    circuit_params = params.pop(f"termination_{side}_circuit", {})

    if name and device:
        termination = klass.objects.get(name=name, device__name=device)
        return termination
    elif feed_params:
        q = {
            "name": feed_params["power_panel"]["name"],
            "site__name": feed_params["power_panel"]["site"],
        }
        power_panel = PowerPanel.objects.get(**q)
        termination = PowerFeed.objects.get(name=feed_params["name"], power_panel=power_panel)
        return termination
    elif circuit_params:
        circuit = Circuit.objects.get(cid=circuit_params.pop("cid"))
        term_side = circuit_params.pop("term_side").upper()

        if scope := circuit_params.pop("scope", None):
            scope_type, scope_id = get_scope_details(scope, CIRCUIT_TERMINATION_TERMINATION_TYPES)
            circuit_params["termination_type"] = scope_type
            circuit_params["termination_id"] = scope_id
        else:
            raise ValueError(
                f"⚠️ Missing required parameter: 'scope'"
                f"for side {term_side} of circuit {circuit}"
            )

        termination, created = CircuitTermination.objects.get_or_create(
            circuit=circuit, term_side=term_side, defaults=circuit_params
        )
        if created:
            print(f"⚡ Created new CircuitTermination {termination}")

        return termination

    raise ValueError(
        f"⚠️ Missing parameters for termination_{side}. "
        "Need termination_{side}_name AND termination_{side}_device OR termination_{side}_circuit"
    )


def get_termination_class_by_name(port_class: str):
    if not port_class:
        return Interface

    return globals()[port_class]


def cable_in_cables(term_a: tuple, term_b: tuple) -> bool:
    """Check if cable exist for given terminations.
    Each tuple should consist termination object and termination type
    """

    try:
        cable_term_a = CableTermination.objects.get(
            Q(
                termination_id=term_a[0].id,
                termination_type=term_a[1],
            )
        )
        cable_term_b = CableTermination.objects.get(
            Q(
                termination_id=term_b[0].id,
                termination_type=term_b[1],
            )
        )
    except CableTermination.DoesNotExist:
        return False

    cable_a = Cable.objects.get(Q(terminations=cable_term_a))
    cable_b = Cable.objects.get(Q(terminations=cable_term_b))

    return cable_a.id == cable_b.id


def check_termination_types(type_a, type_b) -> Tuple[bool, str]:
    if type_a in POWER_TERMINATIONS and type_b in POWER_TERMINATIONS:
        if type_a == type_b:
            return False, "Can't connect the same power terminations together"
        elif (
            type_a == POWER_OUTLET_TERMINATION
            and type_b == POWER_FEED_TERMINATION
            or type_a == POWER_FEED_TERMINATION
            and type_b == POWER_OUTLET_TERMINATION
        ):
            return False, "PowerOutlet can't be connected with PowerFeed"
    elif type_a in POWER_TERMINATIONS or type_b in POWER_TERMINATIONS:
        return False, "Can't mix power terminations with port terminations"
    elif type_a in FRONT_AND_REAR or type_b in FRONT_AND_REAR:
        return True, ""
    elif (
        type_a == CONSOLE_PORT_TERMINATION
        and type_b != CONSOLE_SERVER_PORT_TERMINATION
        or type_b == CONSOLE_PORT_TERMINATION
        and type_a != CONSOLE_SERVER_PORT_TERMINATION
    ):
        return False, "ConsolePorts can only be connected to ConsoleServerPorts or Front/Rear ports"
    return True, ""


def get_cable_name(termination_a: tuple, termination_b: tuple) -> str:
    """Returns name of a cable in format:
    device_a interface_a <---> interface_b device_b
    or for circuits:
    circuit_a termination_a <---> termination_b circuit_b
    """
    cable_name = []

    for is_side_b, termination in enumerate([termination_a, termination_b]):
        try:
            power_panel_id = getattr(termination[0], "power_panel_id", None)
            if power_panel_id:
                power_feed = PowerPanel.objects.get(id=power_panel_id)
                segment = [f"{power_feed}", f"{termination[0]}"]
            else:
                segment = [f"{termination[0].device}", f"{termination[0]}"]
        except AttributeError:
            segment = [f"{termination[0].circuit.cid}", f"{termination[0]}"]

        if is_side_b:
            segment.reverse()

        cable_name.append(" ".join(segment))

    return " <---> ".join(cable_name)


def check_interface_types(*args):
    for termination in args:
        try:
            if termination.type in VIRTUAL_INTERFACES:
                raise Exception(
                    f"⚠️ Virtual interfaces are not supported for cabling. "
                    f"Termination {termination.device} {termination} {termination.type}"
                )
        except AttributeError:
            # CircuitTermination doesn't have a type field
            pass


def check_terminations_are_free(*args):
    any_failed = False
    for termination in args:
        if termination.cable_id:
            any_failed = True
            print(
                f"⚠️ Termination {termination} is already occupied "
                f"with cable #{termination.cable_id}"
            )
    if any_failed:
        raise Exception("⚠️ At least one end of the cable is already occupied.")


class CableInitializer(BaseInitializer):
    data_file_name = "cables.yml"

    def load_data(self):
        cables = self.load_yaml()
        if cables is None:
            return
        for params in cables:
            tags = params.pop("tags", None)

            params["termination_a_class"] = get_termination_class_by_name(
                params.get("termination_a_class")
            )
            params["termination_b_class"] = get_termination_class_by_name(
                params.get("termination_b_class")
            )

            term_a = get_termination_object(params, side="a")
            term_b = get_termination_object(params, side="b")

            check_interface_types(term_a, term_b)

            term_a_ct = ContentType.objects.get_for_model(term_a)
            term_b_ct = ContentType.objects.get_for_model(term_b)

            types_ok, msg = check_termination_types(term_a_ct, term_b_ct)
            cable_name = get_cable_name((term_a, term_a_ct), (term_b, term_b_ct))

            if not types_ok:
                print(f"⚠️ Invalid termination types for {cable_name}. {msg}")
                continue

            if cable_in_cables((term_a, term_a_ct), (term_b, term_b_ct)):
                continue

            check_terminations_are_free(term_a, term_b)

            cable = Cable.objects.create(**params)

            params_a_term = {
                "termination_id": term_a.id,
                "termination_type": term_a_ct,
                "cable": cable,
                "cable_end": "A",
            }
            CableTermination.objects.create(**params_a_term)

            params_b_term = {
                "termination_id": term_b.id,
                "termination_type": term_b_ct,
                "cable": cable,
                "cable_end": "B",
            }
            CableTermination.objects.create(**params_b_term)

            print(f"🧷 Created cable {cable} {cable_name}")
            self.set_tags(cable, tags)


register_initializer("cables", CableInitializer)
