from typing import Optional

from jinja2 import Template
from nornir.core.task import Result, Task

from nornir_routeros.plugins.connections import CONNECTION_NAME


def routeros_config_item(
    task: Task,
    path: str,
    where: dict[str, str],
    properties: Optional[dict[str, str]],
    set_properties: Optional[dict[str, str]] = None,
    add_if_missing: bool = False,
    template_property_values: bool = False,
) -> Result:
    """
    Configures an item.
    Property values can be templated using jinja2. Use ``host`` to access ``task.host``.

    Args:
        path: The path to where the item should be. Example: /ip/firewall/filter to configure firewall filters.
        where: Dictionary of properties and values to find the item.
        properties: Desired properties of the item. If ``None``, then any items matching ``where`` will be **removed**.
        set_properties: Sometimes the value used in add/set doesn't match what is showed in print. Values here will be
          override those used in ``properties`` when creating/updating an item.
        add_if_missing: If an item matching the criteria in ``where`` doesn't exist then one will be created.
        template_property_values: Use Jinja2 for property values.

    Returns:
        Result: A ``Result`` with ``result`` set to the item after any changes.
          If dry_run and add_if_missing is True or no item was removed, None will be returned.

    Examples:

            Ensure the router hostname is set to the inventory name::

                nr.run(
                    task=routeros_config_item,
                    path="/system/identity",
                    where={},
                    properties={
                        "name": "{{ host.name }}"
                    },
                )

            Ensure the ``www`` service is disabled::

                nr.run(
                    task=routeros_config_item,
                    path="/ip/service",
                    where={
                        "name": "www"
                    },
                    properties={
                        "disabled": "true"
                    },
                )

            Ensure a script is configured::

                nr.run(
                    task=routeros_config_item,
                    path="/system/script",
                    where={
                        "name": "test"
                    },
                    properties={
                        "name": "test"
                        "source": ':log info "hello"\\r\\n:log info "world"\\r\\n'
                    },
                    # To preserve \\r\\n line endings make sure templating is off:
                    template_property_values=False,
                )
    """

    api = task.host.get_connection(CONNECTION_NAME, task.nornir.config)

    resource = api.get_resource(path)
    get_results = resource.get(**where)
    dry_run = task.is_dry_run()
    set_properties = set_properties or {}

    diff_lines = []

    result = None

    if properties is None:
        if len(get_results) > 1:
            raise ValueError(
                f"Expected 1 item, received {len(get_results)}: {get_results}"
            )
        elif len(get_results) == 1:
            item = get_results[0]
            diff_lines.append(f"-{item}")
            if dry_run is False:
                resource.remove(id=item["id"])
            result = item

        return Result(
            host=task.host,
            changed=len(diff_lines) > 0,
            diff="\n".join(diff_lines),
            result=result,
        )

    # Holds the properties of the item
    desired_props = {}
    set_props = {}
    if template_property_values:
        for k, v in properties.items():
            # Render the value using jinja2
            template = Template(str(v))
            rendered_val = template.render(host=task.host.dict())
            if rendered_val:
                desired_props[k] = rendered_val
            else:
                raise ValueError(f"Jinja2 rendered a empty value for property {k}")

            if k in set_properties:
                sp = set_properties[k]
                template = Template(str(sp))
                rendered_val = template.render(host=task.host.dict())
                if rendered_val:
                    set_props[k] = rendered_val
                else:
                    raise ValueError(
                        f"Jinja2 rendered a empty value for set property {k}"
                    )
            else:
                set_props[k] = rendered_val
    else:
        desired_props = properties
        set_props = desired_props.copy()
        set_props.update(set_properties)

    if len(get_results) == 0 and add_if_missing is True:
        if dry_run is True:
            result = None
        else:
            resource.add(**set_props)
            item = resource.get(**where)
            if len(item) != 1:
                raise ValueError(f"Expected 1 item, received {len(item)}: {item}")
            result = item[0]

        return Result(host=task.host, changed=True, result=result)
    elif len(get_results) == 1:
        # Check the properties of the current item
        current_props = get_results[0]

        set_params = {}
        # Some resources don't use ID
        if "id" in current_props:
            set_params["id"] = current_props["id"]
        do_set = False

        for k, v in desired_props.items():
            # Allow properties such as comments that
            # don't show if not set to be set.
            current_val = current_props.get(k, "")

            if current_val != desired_props[k]:
                if k in set_properties:
                    v = set_properties[k]
                diff_lines.append(f"-{k}={current_props.get(k, '')}")
                diff_lines.append(f"+{k}={set_props[k]}")

                set_params[k] = set_props[k]
                do_set = True

        if do_set is True and dry_run is False:
            resource.set(**set_params)
            item = resource.get(**where)
            if len(item) != 1:
                raise ValueError(f"Expected 1 item, received {len(item)}: {item}")
            result = item[0]
        else:
            result = get_results[0]
    else:
        raise ValueError(f"Expected 1 item, received {len(get_results)}: {get_results}")

    return Result(
        host=task.host,
        changed=len(diff_lines) > 0,
        diff="\n".join(diff_lines),
        result=result,
    )
