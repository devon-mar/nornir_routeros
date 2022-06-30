from typing import Dict, Optional

from jinja2 import Template
from nornir.core.task import Result, Task

from nornir_routeros.plugins.connections import CONNECTION_NAME


def routeros_config_item(
    task: Task,
    path: str,
    where: Dict[str, str],
    properties: Optional[Dict[str, str]] = None,
    add_if_missing=False,
) -> Result:
    """
    Configures an item.
    Property values can be templated using jinja2. Use ``host`` to access ``task.host``.

    Args:
        path: The path to where the item should be. Example: /ip/firewall/filter to configure firewall filters.
        where: Dictionary of properties and values to find the item.
        properties: Desired properties of the item. If ``None``, then any items matching ``where`` will be **removed**.
        add_if_missing: If an item matching the criteria in ``where`` doesn't exist then one will be created.

    Returns:
        Result: A ``Result`` with ``result`` set to the item after any changes.

    Examples:

            Ensure the router hostname is set to the inventory name::

                nr.run(
                    task=routeros_config_item,
                    path="/system/identity",
                    where={},
                    properties={
                        "name": "{{ host.name }}"
                    }
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
                    }
                )
    """

    api = task.host.get_connection(CONNECTION_NAME, task.nornir.config)

    resource = api.get_resource(path)
    get_results = resource.get(**where)
    dry_run = task.is_dry_run()

    changed = False
    diff = ""

    if properties is None:
        if len(get_results) > 0:
            changed = True
            for i in get_results:
                if not dry_run:
                    resource.remove(id=i["id"])
                diff += f"-{i}"

        return Result(host=task.host, changed=changed, diff=diff, result=get_results)

    # Holds the properties of the item
    desired_props = {}
    for k, v in properties.items():
        # Render the value using jinja2
        template = Template(str(v))
        rendered_val = template.render(host=task.host.dict())
        if rendered_val:
            desired_props[k] = rendered_val
        else:
            raise ValueError(f"Jinja2 rendered a empty value for property {k}")

    if len(get_results) == 0 and add_if_missing:
        if dry_run:
            result = None
        else:
            result = resource.add(**desired_props)
        return Result(host=task.host, changed=True, result=result)
    elif len(get_results) == 1:
        # Check the properties of the current item
        current_props = get_results[0]
        for k, v in desired_props.items():
            # Allow properties such as comments that
            # don't show if not set to be set.
            current_val = current_props.get(k, "")
            if current_val != desired_props[k]:
                changed = True
                set_params = {k: v}
                # Some resources don't use ID
                if "id" in current_props:
                    set_params["id"] = current_props["id"]

                diff += f"-{k}={current_props.get(k, '')}\n+{k}={v}\n"

                if not dry_run:
                    resource.set(**set_params)
    else:
        raise ValueError(
            f"{len(get_results)}>1 items were found using {where}. Consider revising `where`."
        )

    return Result(
        host=task.host, changed=changed, diff=diff, result=resource.get(**where)
    )
