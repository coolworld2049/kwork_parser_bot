from prisma.models import KworkAccount


KworkAccount.create_partial(
    "KworkAccount", exclude_relational_fields=True
)
