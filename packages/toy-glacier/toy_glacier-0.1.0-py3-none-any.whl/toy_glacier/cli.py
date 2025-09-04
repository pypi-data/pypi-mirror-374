import click

from toy_glacier.domain import make_glacier


@click.group()
def main():
    pass


# @main.command("create-glacier")
# @click.option(
#    "--name", default="myglacier", help="Assign a name to the glacier being created."
# )
# @click.option(
#    "--glacier-mass",
#    default=100,
#    help="NOT using for now. Assign a quantity to represent mass of glacier",
# )
# this is kind of redundant w/ fn in domain.py, not sure where to put/how to
# split this logic
# def create_glacier(name: str, glacier_mass: int):
#    glacier = make_glacier(name=name, glacier_mass=glacier_mass)
#    text = click.wrap_text(
#        f"Created a glacier, {name}, with mass {glacier.mass} (kg m^-3)."
#    )
#    click.echo(text)


# @main.command('remove-glacier')
# @click.option(
#    '--name',
#    help= 'Name of the glacier you want to remove from system'
# )
# def remove_glacier(ctx,
#                   name:str):
#    ctx.obj.pop(name)


@main.command("accumulation-event")
@click.argument(
    "amount",
    type=int,
    # help = "Select an amount that refers to the quantity of the accumulation event (kg/m3)")
)
@click.option(
    "--name", default="defaultName", help="Name of the glacier created in this call."
)
@click.option(
    "--glacier-mass", default=100, help="Initial mass of glacier created in this call."
)
def accumulation_event(
    amount: int,
    name: str,
    glacier_mass: int,
):
    glacier = make_glacier(name=name, glacier_mass=glacier_mass)
    create_text = click.wrap_text(
        f"Glacier created with name: {name}, initial mass: {glacier_mass} (kg/m3)."
    )
    click.echo(create_text)

    glacier.accumulate(accum_amount=amount)
    accum_text = click.wrap_text(
        f"Accumulation event: Mass is now {glacier.mass} (kg/m3)."
    )
    click.echo(accum_text)


@main.command("ablation-event")
@click.argument("amount", type=int)
@click.option(
    "--name", default="defaultName", help="Name of glacier created in this call."
)
@click.option(
    "--glacier-mass",
    default=100,
    help="Initial mass of a glacier created in this call.",
)
def ablation_event(amount: int, name: str, glacier_mass: int):
    glacier = make_glacier(name=name, glacier_mass=glacier_mass)
    create_text = click.wrap_text(
        f"Glacier created with name: {name}, initial mass: {glacier_mass} (kg/m3)."
    )
    click.echo(create_text)

    glacier.ablate(ablate_amount=amount)
    ablate_text = click.wrap_text(f"Ablation event: Mass is now {glacier.mass} (kg/m3)")
    click.echo(ablate_text)
