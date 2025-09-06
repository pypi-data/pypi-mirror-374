import rich_click as click

from toy_glacier_project.core import make_glacier


@click.group()
def main():
    """
    Entry point for the toy_glacier_project CLI application.

    This function serves as the main Click group for all glacier-related commands.
    """
    pass


@main.command("accumulation-event")
@click.argument(
    "amount",
    type=int,
)
@click.option(
    "--name", default="defaultName", help="Name of the glacier created in this call."
)
@click.option(
    "--glacier-mass",
    default=100,
    help="Initial mass of glacier created in this call.",
)
def accumulation_event(
    amount: int,
    name: str,
    glacier_mass: int,
):
    """
    Create a glacier and apply an accumulation event.

    This command creates a glacier with the specified name and initial mass,
    then increases its mass by the specified accumulation amount.

    Parameters
    ----------
    amount : int
        The mass to add to the glacier.
    name : str
        The name assigned to the glacier.
    glacier_mass : int
        The initial mass of the glacier.
    """
    glacier = make_glacier(name=name, mass=glacier_mass)
    create_text = click.wrap_text(
        f"Glacier created with name: {name}, initial mass: {glacier_mass}."
    )
    click.echo(create_text)

    glacier.accumulate(accum_amount=amount)
    accum_text = click.wrap_text(f"Accumulation event: Mass is now {glacier.mass}.")
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
    """
    Create a glacier and apply an ablation event.

    This command creates a glacier with the specified name and initial mass,
    then decreases its mass by the specified ablation amount.

    Parameters
    ----------
    amount : int
        The mass to remove from the glacier.
    name : str
        The name assigned to the glacier.
    glacier_mass : int
        The initial mass of the glacier.
    """
    glacier = make_glacier(name=name, mass=glacier_mass)
    create_text = click.wrap_text(
        f"Glacier created with name: {name}, initial mass: {glacier_mass}."
    )
    click.echo(create_text)

    glacier.ablate(ablate_amount=amount)
    ablate_text = click.wrap_text(f"Ablation event: Mass is now {glacier.mass}.")
    click.echo(ablate_text)
