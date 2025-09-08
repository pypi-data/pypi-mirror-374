import msgspec


class Position(msgspec.Struct):
    """
    Represents a 2D position with x and y coordinates.

    Provides a straightforward way to store and retrieve 2D positional
    data. Supports creation from a dictionary for flexible initialization.

    :ivar x: The x-coordinate of the position.
    :ivar y: The y-coordinate of the position.
    """

    x: float
    y: float

    def __mul__(self, other: float) -> "Position":
        return Position(self.x * other, self.y * other)

    @classmethod
    def from_dict(cls, other_position: dict[str, float]) -> "Position":
        """
        Creates a Position instance from a dictionary containing x and y values.

        :param other_position: Dictionary with keys "x" and "y" representing position
            coordinates.
        :type other_position: dict
        :return: A new Position instance initialized with the coordinates
            from the input dictionary.
            :rtype: Position
        """
        return Position(other_position["x"], other_position["y"])
