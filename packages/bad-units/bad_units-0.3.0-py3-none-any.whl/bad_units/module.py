class UnitError(Exception):
    pass


class Unit:
    unit_type = None
    base_unit_per = None

    def __init__(self, amount=1):
        if amount < 0:
            raise UnitError("Unit amounts cannot be negative")
        self.amount = amount

    def to(self, other):
        if not isinstance(other, Unit):
            raise TypeError("Can only convert to another Unit")
        if self.unit_type != other.unit_type:
            raise UnitError("Units must be of the same type")
        return other.__class__((self.amount * self.base_units_per) / other.base_units_per)

    def __add__(self, other):
        if isinstance(other, Unit):
            if self.unit_type != other.unit_type:
                raise UnitError("Units must be of the same type")
            return self.__class__((self.base_units_per * self.amount + other.base_units_per * other.amount) / self.base_units_per)
        elif isinstance(other, CompoundUnit):
            return other + self
        else:
            raise TypeError("Can only add Unit or CompoundUnit")

    def __sub__(self, other):
        if isinstance(other, Unit):
            if self.unit_type != other.unit_type:
                raise UnitError("Units must be of the same type")
            return self.__class__((self.base_units_per * self.amount - other.base_units_per * other.amount) / self.base_units_per)
        elif isinstance(other, CompoundUnit):
            return CompoundUnit(self) - other
        else:
            raise TypeError("Can only subtract Unit or CompoundUnit")

    def __truediv__(self, other):
        return CompoundUnit(self, other)

    def __mul__(self, other):
        if isinstance(other, Unit):
            return CompoundUnit(self * other)
        elif isinstance(other, CompoundUnit):
            return CompoundUnit(self) * other
        else:
            raise TypeError("Can only multiply by Unit or CompoundUnit")

    def __repr__(self):
        return f"{self.amount:g} {self.__class__.__name__}"


class CompoundUnit:
    def __init__(self, numerator, denominator=None):
        self.numerator = numerator
        self.denominator = denominator

    def _check_compatibility(self, other):
        if not isinstance(other, CompoundUnit):
            raise TypeError("Can only add/subtract with another CompoundUnit")
        if self.numerator.unit_type != other.numerator.unit_type:
            raise UnitError("Cannot add/subtract: numerators mismatch")
        if (self.denominator and other.denominator):
            if self.denominator.unit_type != other.denominator.unit_type:
                raise UnitError("Cannot add/subtract: denominators mismatch")
        elif (self.denominator is None) != (other.denominator is None):
            raise UnitError("Cannot add/subtract: one has denominator, other does not")


    def __add__(self, other):
        if isinstance(other, Unit):
            if self.denominator is None:
                return CompoundUnit(self.numerator + other)
            else:
                raise UnitError("Cannot add Unit directly to CompoundUnit with denominator")
        self._check_compatibility(other)
        if self.denominator:
            new_numerator = self.numerator + other.numerator
            return CompoundUnit(new_numerator, self.denominator)
        else:
            new_numerator = self.numerator + other.numerator
            return CompoundUnit(new_numerator)

    def __sub__(self, other):
        if isinstance(other, Unit):
            if self.denominator is None:
                return CompoundUnit(self.numerator - other)
            else:
                raise UnitError("Cannot subtract Unit directly from CompoundUnit with denominator")
        self._check_compatibility(other)
        if self.denominator:
            new_numerator = self.numerator - other.numerator
            return CompoundUnit(new_numerator, self.denominator)
        else:
            new_numerator = self.numerator - other.numerator
            return CompoundUnit(new_numerator)

    def __truediv__(self, other):
        if isinstance(other, Unit):
            return CompoundUnit(self.numerator, self.denominator * other if self.denominator else other)
        elif isinstance(other, CompoundUnit):
            return CompoundUnit(self.numerator * other.denominator if other.denominator else self.numerator,
                                self.denominator * other.numerator if self.denominator else other.numerator)
        else:
            raise TypeError("Can only divide by Unit or CompoundUnit")

    def __mul__(self, other):
        if isinstance(other, Unit):
            return CompoundUnit(self.numerator * other, self.denominator)
        elif isinstance(other, CompoundUnit):
            new_numerator = self.numerator * other.numerator
            new_denominator = None
            if self.denominator and other.denominator:
                new_denominator = self.denominator * other.denominator
            elif self.denominator:
                new_denominator = self.denominator
            elif other.denominator:
                new_denominator = other.denominator
            return CompoundUnit(new_numerator, new_denominator)
        else:
            raise TypeError("Can only multiply by Unit or CompoundUnit")

    def __repr__(self):
        if self.denominator is None:
            return f"{self.numerator}"
        num_str = f"({self.numerator})" if isinstance(self.numerator, CompoundUnit) else f"{self.numerator}"
        den_str = f"({self.denominator})" if isinstance(self.denominator, CompoundUnit) else f"{self.denominator}"
        return f"{num_str}/{den_str}"