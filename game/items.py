# Item and Inventory classes

from game.exceptions import ItemNotFoundError, InventoryFullError


class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


class Inventory:
    def __init__(self, capacity=6):
        self.items = []
        self.capacity = capacity

    def add_item(self, item):
        if len(self.items) >= self.capacity:
            raise InventoryFullError(self.capacity)
        self.items.append(item)

    def has_item(self, item_name):
        for item in self.items:
            if item.name.lower() == item_name.lower():
                return True
        return False

    def get_item(self, item_name):
        for item in self.items:
            if item.name.lower() == item_name.lower():
                return item
        raise ItemNotFoundError(item_name)

    def remove_item(self, item_name):
        item = self.get_item(item_name)
        self.items.remove(item)
        return item

    def get_names(self):
        return [item.name for item in self.items]
