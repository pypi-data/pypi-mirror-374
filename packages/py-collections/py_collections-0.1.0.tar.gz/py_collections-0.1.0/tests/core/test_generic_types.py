import pytest

from py_collections.collection import Collection, T


class TestCollectionGenericTypes:
    """Test suite for the Collection generic type functionality."""

    def test_int_collection(self):
        """Test Collection with int type."""
        int_collection: Collection[int] = Collection([1, 2, 3])

        # Test append with int
        int_collection.append(4)
        assert int_collection.all() == [1, 2, 3, 4]

        # Test first returns int
        first = int_collection.first()
        assert first == 1
        assert isinstance(first, int)

    def test_str_collection(self):
        """Test Collection with str type."""
        str_collection: Collection[str] = Collection(["hello", "world"])

        # Test append with str
        str_collection.append("test")
        assert str_collection.all() == ["hello", "world", "test"]

        # Test first returns str
        first = str_collection.first()
        assert first == "hello"
        assert isinstance(first, str)

    def test_list_collection(self):
        """Test Collection with list type."""
        list_collection: Collection[list[int]] = Collection([[1, 2], [3, 4]])

        # Test append with list
        list_collection.append([5, 6])
        assert list_collection.all() == [[1, 2], [3, 4], [5, 6]]

        # Test first returns list
        first = list_collection.first()
        assert first == [1, 2]
        assert isinstance(first, list)

    def test_dict_collection(self):
        """Test Collection with dict type."""
        dict_collection: Collection[dict] = Collection([{"a": 1}, {"b": 2}])

        # Test append with dict
        dict_collection.append({"c": 3})
        assert dict_collection.all() == [{"a": 1}, {"b": 2}, {"c": 3}]

        # Test first returns dict
        first = dict_collection.first()
        assert first == {"a": 1}
        assert isinstance(first, dict)

    def test_custom_class_collection(self):
        """Test Collection with custom class."""

        class Person:
            def __init__(self, name: str, age: int):
                self.name = name
                self.age = age

            def __eq__(self, other):
                if not isinstance(other, Person):
                    return False
                return self.name == other.name and self.age == other.age

        person_collection: Collection[Person] = Collection(
            [Person("Alice", 25), Person("Bob", 30)]
        )

        # Test append with Person
        new_person = Person("Charlie", 35)
        person_collection.append(new_person)

        # Test first returns Person
        first = person_collection.first()
        assert first.name == "Alice"
        assert first.age == 25
        assert isinstance(first, Person)

    def test_mixed_type_collection(self):
        """Test Collection with Any type (mixed types)."""
        mixed_collection: Collection[object] = Collection(
            [1, "hello", {"key": "value"}]
        )

        # Test append with different types
        mixed_collection.append([1, 2, 3])
        mixed_collection.append(None)

        # Test first returns the first element
        first = mixed_collection.first()
        assert first == 1
        assert isinstance(first, int)

    def test_empty_typed_collection(self):
        """Test empty Collection with type annotation."""
        empty_int_collection: Collection[int] = Collection()

        # Test append with int
        empty_int_collection.append(42)
        assert empty_int_collection.all() == [42]

        # Test first returns int
        first = empty_int_collection.first()
        assert first == 42
        assert isinstance(first, int)

    def test_none_collection(self):
        """Test Collection with None type."""
        none_collection: Collection[type(None)] = Collection([None, None])

        # Test append with None
        none_collection.append(None)
        assert none_collection.all() == [None, None, None]

        # Test first returns None
        first = none_collection.first()
        assert first is None

    def test_type_consistency(self):
        """Test that type annotations are consistent throughout operations."""
        int_collection: Collection[int] = Collection([1, 2, 3])

        # All operations should maintain int type
        items = int_collection.all()
        assert all(isinstance(item, int) for item in items)

        first = int_collection.first()
        assert isinstance(first, int)

        int_collection.append(4)
        new_items = int_collection.all()
        assert all(isinstance(item, int) for item in new_items)

    def test_generic_type_parameter(self):
        """Test that the generic type parameter T is properly exported."""
        # This test ensures that T is available for type annotations
        assert T is not None

        # Test using T in type annotations
        def create_collection(items: list[T]) -> Collection[T]:
            return Collection(items)

        # This should work without type errors
        int_list: list[int] = [1, 2, 3]
        collection = create_collection(int_list)
        assert isinstance(collection, Collection)

    def test_pydantic_model_collection(self):
        """Test Collection with Pydantic models."""
        try:
            from pydantic import BaseModel

            class User(BaseModel):
                name: str
                age: int
                email: str
                is_active: bool = True

            # Type-annotated Pydantic model collection
            users: Collection[User] = Collection(
                [
                    User(name="Alice", age=25, email="alice@example.com"),
                    User(name="Bob", age=30, email="bob@example.com", is_active=False),
                ]
            )

            # Test append with Pydantic model
            new_user = User(name="Charlie", age=35, email="charlie@example.com")
            users.append(new_user)

            # Test first returns Pydantic model
            first_user = users.first()
            assert isinstance(first_user, User)
            assert first_user.name == "Alice"
            assert first_user.age == 25
            assert first_user.email == "alice@example.com"
            assert first_user.is_active is True

            # Test all returns list of Pydantic models
            all_users = users.all()
            assert len(all_users) == 3
            assert all(isinstance(user, User) for user in all_users)

            # Test accessing Pydantic model attributes
            user_names = [user.name for user in all_users]
            assert user_names == ["Alice", "Bob", "Charlie"]

            # Test Pydantic model validation
            assert first_user.model_dump() == {
                "name": "Alice",
                "age": 25,
                "email": "alice@example.com",
                "is_active": True,
            }

        except ImportError:
            pytest.skip("Pydantic not available")

    def test_pydantic_model_with_nested_models(self):
        """Test Collection with nested Pydantic models."""
        try:
            from typing import List as PydanticList

            from pydantic import BaseModel

            class Address(BaseModel):
                street: str
                city: str
                country: str
                postal_code: str

            class Contact(BaseModel):
                name: str
                email: str
                phone: str
                addresses: list[Address]

            # Type-annotated nested Pydantic model collection
            contacts: Collection[Contact] = Collection(
                [
                    Contact(
                        name="Alice Johnson",
                        email="alice@example.com",
                        phone="+1-555-0101",
                        addresses=[
                            Address(
                                street="123 Main St",
                                city="New York",
                                country="USA",
                                postal_code="10001",
                            ),
                            Address(
                                street="456 Oak Ave",
                                city="Los Angeles",
                                country="USA",
                                postal_code="90210",
                            ),
                        ],
                    ),
                    Contact(
                        name="Bob Smith",
                        email="bob@example.com",
                        phone="+1-555-0202",
                        addresses=[
                            Address(
                                street="789 Pine Rd",
                                city="Chicago",
                                country="USA",
                                postal_code="60601",
                            )
                        ],
                    ),
                ]
            )

            # Test append with nested Pydantic model
            new_contact = Contact(
                name="Charlie Brown",
                email="charlie@example.com",
                phone="+1-555-0303",
                addresses=[
                    Address(
                        street="321 Elm St",
                        city="Boston",
                        country="USA",
                        postal_code="02101",
                    )
                ],
            )
            contacts.append(new_contact)

            # Test first returns nested Pydantic model
            first_contact = contacts.first()
            assert isinstance(first_contact, Contact)
            assert first_contact.name == "Alice Johnson"
            assert len(first_contact.addresses) == 2

            # Test accessing nested model attributes
            first_address = first_contact.addresses[0]
            assert isinstance(first_address, Address)
            assert first_address.street == "123 Main St"
            assert first_address.city == "New York"

            # Test all returns list of nested Pydantic models
            all_contacts = contacts.all()
            assert len(all_contacts) == 3
            assert all(isinstance(contact, Contact) for contact in all_contacts)

            # Test nested model serialization
            contact_data = first_contact.model_dump()
            assert "name" in contact_data
            assert "addresses" in contact_data
            assert len(contact_data["addresses"]) == 2

        except ImportError:
            pytest.skip("Pydantic not available")

    def test_pydantic_model_last_element(self):
        """Test last() method with Pydantic models."""
        try:
            from pydantic import BaseModel

            class User(BaseModel):
                name: str
                age: int
                email: str
                is_active: bool = True

            # Type-annotated Pydantic model collection
            users: Collection[User] = Collection(
                [
                    User(name="Alice", age=25, email="alice@example.com"),
                    User(name="Bob", age=30, email="bob@example.com", is_active=False),
                    User(name="Charlie", age=35, email="charlie@example.com"),
                ]
            )

            # Test last returns Pydantic model
            last_user = users.last()
            assert isinstance(last_user, User)
            assert last_user.name == "Charlie"
            assert last_user.age == 35
            assert last_user.email == "charlie@example.com"
            assert last_user.is_active is True

            # Test append and last
            new_user = User(name="David", age=40, email="david@example.com")
            users.append(new_user)
            assert users.last().name == "David"

        except ImportError:
            pytest.skip("Pydantic not available")

    def test_pydantic_model_all_items(self):
        """Test all() method with Pydantic models."""
        try:
            from pydantic import BaseModel

            class User(BaseModel):
                name: str
                age: int
                email: str
                is_active: bool = True

            # Type-annotated Pydantic model collection
            users: Collection[User] = Collection(
                [
                    User(name="Alice", age=25, email="alice@example.com"),
                    User(name="Bob", age=30, email="bob@example.com", is_active=False),
                    User(name="Charlie", age=35, email="charlie@example.com"),
                ]
            )

            # Test all returns list of Pydantic models
            all_users = users.all()
            assert len(all_users) == 3
            assert all(isinstance(user, User) for user in all_users)

            # Test accessing Pydantic model attributes
            user_names = [user.name for user in all_users]
            assert user_names == ["Alice", "Bob", "Charlie"]

            # Test append and all
            new_user = User(name="David", age=40, email="david@example.com")
            users.append(new_user)

            updated_all_users = users.all()
            assert len(updated_all_users) == 4
            assert updated_all_users[-1].name == "David"

        except ImportError:
            pytest.skip("Pydantic not available")
