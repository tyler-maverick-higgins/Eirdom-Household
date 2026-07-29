# ADR-0003: Model Households and Household Membership

## Status

Accepted

## Date

2026-07-28

## Context

Eirdom Household needs a clear ownership and access boundary before additional household domains are implemented.

Future records such as rooms, assets, inventory items, maintenance schedules, tasks, documents, recipes, meal plans, and financial integrations must belong to a specific household. The application must also determine which users may view or manage those records.

A direct relationship between a user and a household is not sufficient because the relationship itself contains important information, including:

- The member's role
- When the membership began
- Whether the membership is active
- Who created or approved the membership
- Future household-specific permissions or preferences

The design must also support the possibility that:

- A user may belong to more than one household
- A household may have more than one owner
- A user account may exist before joining a household
- Household membership may later be created through invitations
- Authorization must prevent records from one household from being exposed to another

The household model will become the primary tenant boundary for Eirdom Household. This decision must therefore be made before implementing household-owned domain models or API authorization.

## Decision

Eirdom Household will represent households and users through an explicit membership model.

The core relationship will be:

```text
User
  └── HouseholdMembership
          └── Household
```

A user may belong to zero, one, or many households.

A household may contain one or many users.

The many-to-many relationship will be implemented through `HouseholdMembership` rather than a direct implicit many-to-many field.

## Domain Models

### Household

The `Household` model represents one independently managed household.

Initial fields should include:

- `id`
- `name`
- `slug`
- `created_at`
- `updated_at`

Recommended behavior:

- `name` is required.
- `slug` is unique and suitable for URLs and stable household identification.
- Creation and modification timestamps are maintained automatically.
- Future household-owned records will reference `Household` using a foreign key.

Example relationship:

```python
class Household(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### HouseholdMembership

The `HouseholdMembership` model represents a user's relationship to a household.

Initial fields should include:

- `id`
- `household`
- `user`
- `role`
- `is_active`
- `joined_at`
- `updated_at`

Recommended behavior:

- A user may have only one membership record per household.
- Membership roles are constrained to defined choices.
- Memberships may be deactivated without deleting historical relationships.
- Membership creation time is preserved.

Example relationship:

```python
class HouseholdMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMINISTRATOR = "administrator", "Administrator"
        MEMBER = "member", "Member"
        GUEST = "guest", "Guest"

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="household_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["household", "user"],
                name="unique_household_membership",
            ),
        ]
```

## Membership Roles

The initial roles will be:

| Role            | Purpose                                                                         |
| --------------- | ------------------------------------------------------------------------------- |
| `owner`         | Full control of the household, including membership and administrative settings |
| `administrator` | Broad household management without ownership semantics                          |
| `member`        | Normal household participation                                                  |
| `guest`         | Limited or temporary access                                                     |

The role model will begin as Django `TextChoices`.

A separate permission or role table will not be introduced in the first implementation.

## Ownership

A household may have more than one owner.

The database will not initially enforce that every household always has an owner because cross-row ownership guarantees are difficult to enforce cleanly with a basic database constraint.

Instead:

- Household creation must create an owner membership in the same application operation.
- Application services must prevent removal or demotion of the final active owner.
- Tests must cover final-owner protection.
- Administrative tools must clearly identify owners.

## User Accounts Without Households

A user account may exist without a household membership.

This supports:

- Invitations
- Account provisioning before household creation
- Administrative or integration accounts
- Future onboarding workflows

## Active Household Context

A user may belong to multiple households, but most requests will operate within one active household context.

The active household must be selected explicitly rather than inferred globally from the user account.

The exact API mechanism will be defined in a later ADR covering API conventions and authorization.

Regardless of transport mechanism, the application must verify that the requesting user has an active membership in the selected household.

## Household Data Isolation

Every household-owned model must include a required foreign key to `Household`, unless a documented exception applies.

Examples include:

```text
Room.household
Asset.household
InventoryItem.household
MaintenanceSchedule.household
Task.household
Recipe.household
```

Application queries must be scoped by both:

- The selected household
- The requesting user's active membership

Authorization tests must verify that a user cannot access another household's records.

## Application Structure

The models will be implemented in:

```text
backend/src/apps/households/
```

Expected initial structure:

```text
households/
├── migrations/
├── tests/
├── admin.py
├── apps.py
├── models.py
└── services.py
```

A service layer may be used for operations that require multiple related writes, such as:

- Creating a household and its first owner
- Adding a member
- Changing roles
- Deactivating a membership
- Preventing removal of the final owner

## Administrative Interface

Both models will be registered in Django Admin.

The admin interface should support:

- Viewing households
- Viewing household memberships
- Filtering memberships by household, role, and active status
- Searching by household name, username, and email
- Reviewing ownership relationships

## Testing Requirements

The initial implementation must include tests for:

- Creating a household
- Creating a household with an owner
- Adding a member
- Adding multiple users to one household
- Allowing one user to join multiple households
- Preventing duplicate memberships
- Assigning each supported role
- Defaulting new memberships to the expected role
- Deactivating a membership
- Protecting the final active owner
- Household and membership string representations
- Cascading membership deletion when a household is deleted
- Household isolation behavior

## Consequences

### Positive

- Household ownership is explicit throughout the application.
- One user can participate in multiple households.
- Membership-specific metadata and roles are supported.
- Future domains have a consistent tenant boundary.
- Multi-owner households are supported.
- Membership history can be retained through deactivation.
- The design supports future invitations and onboarding.
- Authorization rules can be centralized around household membership.

### Negative

- Every household-scoped query must include household filtering.
- Multi-household support adds complexity to user experience and authorization.
- Final-owner protection cannot be expressed fully through a simple database constraint.
- Role choices may eventually be too limited for granular permissions.
- More joins are required than with a direct foreign key from user to household.
- Administrative and service code must consistently enforce membership rules.

## Alternatives Considered

### One household foreign key directly on User

Rejected because it would prevent a user from belonging to multiple households and would not provide a place for membership-specific fields such as role and status.

### Implicit Django many-to-many relationship

Rejected because the relationship requires metadata, uniqueness constraints, role information, activation state, and future invitation support.

### Separate owner field on Household

Rejected because it would model only one owner cleanly and create two competing sources of truth between ownership and membership.

### Exactly one owner per household

Rejected because multiple adults may need equal control, and single ownership creates an avoidable continuity risk.

### Fully dynamic roles and permissions

Deferred because the initial requirements can be represented with a small set of role choices.

### Require every user to belong to a household

Rejected because accounts may need to exist before onboarding, invitation acceptance, or household creation.

## Validation

This decision will be considered implemented when:

- The `households` Django application exists.
- `Household` and `HouseholdMembership` models are implemented.
- The membership uniqueness constraint is applied.
- Household creation establishes an owner membership.
- Final-owner protection is implemented and tested.
- Models are registered in Django Admin.
- Migrations apply successfully.
- Ruff, pytest, and Django checks pass.

## Future Work

Separate ADRs or feature work should address:

- API household-context selection
- Authorization and permission enforcement
- Household invitations
- User onboarding
- Custom household roles
- Fine-grained permissions
- Household archival and deletion
- Household transfer and recovery
- Audit logging
- Soft deletion
- Cross-household administrative access
