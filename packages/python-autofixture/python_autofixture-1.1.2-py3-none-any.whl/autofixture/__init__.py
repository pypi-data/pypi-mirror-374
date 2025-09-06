import datetime
import decimal
import typing
import uuid
from decimal import Decimal
from enum import Enum
import random as rand
from types import NoneType

from autofixture.exceptions import AutoFixtureException

T = typing.TypeVar("T")


class FieldGenerator:
    __slots__ = ('predictable_func', 'random_func')
    
    def __init__(self, predictable_func, random_func):
        self.predictable_func = predictable_func
        self.random_func = random_func
    
    def __call__(self, is_predictable, key, target_obj, num=None, seed=None, list_limit=10, **kwargs):
        if is_predictable:
            value = self.predictable_func(num=num, seed=seed, key=key, **kwargs)
        else:
            value = self.random_func(key=key, list_limit=list_limit, **kwargs)
        setattr(target_obj, key, value)


class ListFieldGenerator(FieldGenerator):
    __slots__ = ('element_generator',)
    
    def __init__(self, element_generator):
        self.element_generator = element_generator
        super().__init__(self._predictable_list, self._random_list)
    
    def _predictable_list(self, num, key, **kwargs):
        return [self.element_generator(num=num, key=key, index=i, **kwargs) for i in range(num)]
    
    def _random_list(self, key, list_limit, **kwargs):
        return [self.element_generator(key=key, index=i, **kwargs) 
                for i in range(rand.randint(0, list_limit))]


class TypeRegistry:
    __slots__ = ('_generators',)
    
    def __init__(self):
        self._generators = {}
        self._setup_default_generators()
    
    def register(self, type_key, generator):
        self._generators[type_key] = generator
    
    def get_generator(self, type_key):
        return self._generators.get(type_key)
    
    def _setup_default_generators(self):
        # String generators
        self.register(str, FieldGenerator(
            lambda num, seed, key, **kw: f"{key}{seed}",
            lambda key, **kw: f"{key}{str(uuid.uuid4()).split('-')[0]}"
        ))
        
        # Integer generators
        self.register(int, FieldGenerator(
            lambda num, **kw: num,
            lambda **kw: rand.randint(0, 100)
        ))
        
        # Float generators
        self.register(float, FieldGenerator(
            lambda num, **kw: float(f"{num}.{''.join(str(num) for _ in range(num))}"),
            lambda **kw: rand.uniform(0, 100)
        ))
        
        # Boolean generators
        self.register(bool, FieldGenerator(
            lambda num, **kw: bool(num),
            lambda **kw: rand.choice([True, False])
        ))
        
        # Decimal generators
        self.register(Decimal, FieldGenerator(
            lambda num, **kw: Decimal(str(float(f"{num}.{''.join(str(num) for _ in range(num))}"))),
            lambda **kw: Decimal(str(rand.uniform(0, 100)))
        ))
        
        # Datetime generators
        self.register(datetime.datetime, FieldGenerator(
            lambda num, **kw: datetime.datetime(num, num, num, num, num, num),
            lambda **kw: datetime.datetime.now(datetime.timezone.utc)
        ))
        
        # List generators
        self.register(list[str], ListFieldGenerator(
            lambda num, seed, key, index, **kw: f"{key}{seed}{index}" if seed else f"{key}{str(uuid.uuid4()).split('-')[0]}"
        ))
        
        self.register(list[int], ListFieldGenerator(
            lambda num, index, **kw: num + index if num else rand.randint(0, 100)
        ))
        
        self.register(list[float], ListFieldGenerator(
            lambda num, index, **kw: float(f"{num}.{''.join(str(num) for _ in range(num))}") if num else rand.uniform(0, 100)
        ))
        
        self.register(list[bool], ListFieldGenerator(
            lambda num, **kw: bool(num) if num else rand.choice([True, False])
        ))
        
        self.register(list[datetime.datetime], ListFieldGenerator(
            lambda num, **kw: datetime.datetime(2, 2, 2, 2, 2, 2) if num else datetime.datetime.now(datetime.timezone.utc)
        ))
        
        self.register(list[decimal.Decimal], ListFieldGenerator(
            lambda num, **kw: Decimal(str(float(f"{num}.{''.join(str(num) for _ in range(num))}"))) if num else Decimal(str(rand.uniform(0, 100)))
        ))


class EnumGenerator(FieldGenerator):
    __slots__ = ('enum_type',)
    
    def __init__(self, enum_type):
        self.enum_type = enum_type
        super().__init__(self._predictable_enum, self._random_enum)
    
    def _predictable_enum(self, num, **kwargs):
        enum_list = list(self.enum_type)
        return enum_list[num % len(enum_list)]
    
    def _random_enum(self, **kwargs):
        return rand.choice(list(self.enum_type))


class EnumListGenerator(ListFieldGenerator):
    __slots__ = ('enum_type',)
    
    def __init__(self, enum_type):
        self.enum_type = enum_type
        enum_gen = EnumGenerator(enum_type)
        super().__init__(lambda **kw: enum_gen._predictable_enum(**kw) if kw.get('num') else enum_gen._random_enum(**kw))


class ObjectGenerator:
    __slots__ = ('autofixture_instance',)
    
    def __init__(self, autofixture_instance):
        self.autofixture_instance = autofixture_instance
    
    def __call__(self, obj_type, is_predictable, key, target_obj, num=None, seed=None, nest=0, **kwargs):
        created_obj = self.autofixture_instance.create(
            dto=obj_type, seed=seed, num=num, nest=nest + 1
        )
        setattr(target_obj, key, created_obj)


class ObjectListGenerator:
    __slots__ = ('autofixture_instance',)
    
    def __init__(self, autofixture_instance):
        self.autofixture_instance = autofixture_instance
    
    def __call__(self, obj_type, is_predictable, key, target_obj, num=None, seed=None, nest=0, list_limit=10, **kwargs):
        if is_predictable:
            objects = [self.autofixture_instance.create(dto=obj_type, seed=seed, num=num, nest=nest + 1) 
                      for _ in range(num)]
        else:
            objects = [self.autofixture_instance.create(dto=obj_type, seed=seed, num=num, nest=nest + 1) 
                      for _ in range(rand.randint(0, list_limit))]
        setattr(target_obj, key, objects)


class AutoFixture:
    
    def __init__(self):
        self.type_registry = TypeRegistry()
        self.object_generator = ObjectGenerator(self)
        self.object_list_generator = ObjectListGenerator(self)
    
    def register_custom_generator(self, type_key, generator):
        """Allow users to register custom field generators"""
        self.type_registry.register(type_key, generator)

    def create_many_dict(self, dto,
                         ammount,
                         seed=None,
                         num=None,
                         nest=0,
                         list_limit=100):
        many = self.create_many(dto=dto,
                                ammount=ammount,
                                seed=seed,
                                num=num,
                                nest=nest,
                                list_limit=list_limit)
        return list(map(lambda x: x.__dict__, many))

    def create_dict(self, dto,
                    seed=None,
                    num=None,
                    nest=0,
                    list_limit=100):
        return self.create(dto=dto,
                           seed=seed,
                           num=num,
                           nest=nest,
                           list_limit=list_limit).__dict__

    def create_many(self, dto,
                    ammount,
                    seed=None,
                    num=None,
                    nest=0,
                    list_limit=100):
        list_of_dtos = []
        for i in range(0, ammount):
            list_of_dtos.append(self.create(dto=dto,
                                            seed=seed,
                                            num=num,
                                            nest=nest,
                                            list_limit=list_limit))
        return list_of_dtos

    def create(self, dto: typing.Type[T],
               seed=None,
               num=None,
               nest=0,
               list_limit=10) -> T:
        self.__validate_predictable_data(num, seed)

        try:
            new_value = dto()
        except TypeError:
            raise AutoFixtureException("class must empty ctor, if a dataclass, must have fields initialised to "
                                       "sensible defaults or None")

        is_predictable_data = seed is not None and num is not None

        members = all_annotations(cls=dto).items()
        for (key, _type) in members:
            if self._should_generate_field(new_value, key, _type):
                self._generate_field(key, _type, new_value, is_predictable_data, 
                                   num, seed, nest, list_limit)

        return new_value
    
    def _should_generate_field(self, obj, key, field_type):
        current_value = getattr(obj, key)
        return (current_value is None or 
                (typing.get_origin(field_type) is list and current_value == []))
    
    def _normalize_optional_type(self, field_type):
        if typing.get_origin(field_type) is typing.Union:
            args = typing.get_args(field_type)
            non_none_args = [a for a in args if a is not NoneType]
            if len(non_none_args) == 1:
                return non_none_args[0]
        return field_type
    
    def _generate_field(self, key, field_type, target_obj, is_predictable, 
                       num, seed, nest, list_limit):
        field_type = self._normalize_optional_type(field_type)
        
        # Handle enums
        if type(field_type) is type(Enum):
            generator = EnumGenerator(field_type)
            generator(is_predictable, key, target_obj, num=num, seed=seed)
            return
        
        # Handle list of enums
        if typing.get_origin(field_type) is list:
            args = typing.get_args(field_type)
            if args and type(args[0]) is type(Enum):
                generator = EnumListGenerator(args[0])
                generator(is_predictable, key, target_obj, num=num, seed=seed, list_limit=list_limit)
                return
            
            # Handle list of custom objects
            if args and has_type_hints(args[0]):
                self.object_list_generator(args[0], is_predictable, key, target_obj, 
                                         num=num, seed=seed, nest=nest, list_limit=list_limit)
                return
        
        # Handle custom objects
        if has_type_hints(field_type):
            self.object_generator(field_type, is_predictable, key, target_obj, 
                                num=num, seed=seed, nest=nest)
            return
        
        # Handle registered types
        generator = self.type_registry.get_generator(field_type)
        if generator:
            generator(is_predictable, key, target_obj, num=num, seed=seed, list_limit=list_limit)
            return
        
        # Fallback - type not supported
        raise AutoFixtureException(f"Unsupported type: {field_type}")

    @staticmethod
    def __validate_predictable_data(num, seed):
        if seed is not None and num is None:
            raise AutoFixtureException("seed and num must be both set to create predictable data")
        if num is not None and seed is None:
            raise AutoFixtureException("seed and num must be both set to create predictable data")


def all_annotations(cls):
    d = {}
    for c in cls.mro():
        try:
            d.update(**c.__annotations__)
        except AttributeError:
            # object, at least, has no __annotations__ attribute.
            pass
    return d

def has_type_hints(t):
    origin = typing.get_origin(t)
    if origin is not None:
        # It's a generic like list[LayoutItem], get the inner type(s)
        args = typing.get_args(t)
        # For simplicity, just check the first arg recursively
        if args:
            return has_type_hints(args[0])
        else:
            return False
    else:
        # Normal class/type, try to get hints safely
        try:
            return bool(typing.get_type_hints(t))
        except (TypeError, AttributeError, NameError):
            return False