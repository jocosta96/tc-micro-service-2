# Gateways package
# Usually, Gateway, is a combination of some sort of Repository (JPA, etc.)
# is responsible for working with the low-level persistence entities
# mapped to the database rows through some sort of ORM (Hibernate, etc.)
# and a Mapper which maps these raw ORM entities to the graph of domain entities
# used by the Use Cases layer.
# The point is, that Gateway accesses or instantiates,
# and thus — depends on domain entities despite the fact that it is located in the Interface Adapters layer.
# When a use case needs some entities, it calls the gateway (through the port, of course)
# and receives them in a read-to-consume way, as domain entities.
