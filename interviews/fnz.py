#! -*- coding: utf-8 -*-


# The price table of fruits
FRUIT_PRICE = {'apple': 59,
               'banana': 32,
               'coconut': 155,
               'grapefruit': 128,
               'jackfruit': 1100,
               'kiwi': 41,
               'lemon': 70,
               'mango': 97,
               'orange': 73,
               'papaya': 254,
               'pear': 37,
               'pineapple': 399,
               'watermelon': 500}


class FruitNode(object):

    def __init__(self, node_level, node_value, node_weight=0):
        """
        The construction function
        :param node_level:
        :param node_value:
        :param node_weight:
        :return:
        """
        self.level = node_level
        self.value = node_value
        self.weight = node_weight
        self.parent = None
        self.children = []

    def create_child(self, child_value, child_weight):
        """
        The function to create a child
        :param child_value:
        :param child_weight:
        :return:
        """
        child = FruitNode(self.level + 1, self.value - child_value * child_weight, child_weight)
        child.parent = self
        self.children.append(child)


class FruitTree(object):

    def __init__(self, root_value, levels_price):
        """
        The construction function
        :param root_value:
        :param levels_price:
        :return:
        """
        self.root = FruitNode(0, root_value, 0)
        self.current_node = self.root
        self.levels_price = levels_price
        self.next_node_weight = 0
        self.leaf = []

    def grow(self):
        """
        To grow and find the leaf of the tree in recursion
        :return:
        """
        while self.current_node is not None:
            if self.current_node.value is 0:
                self.leaf.append(self.current_node)
                self.next_node_weight = self.current_node.parent.weight + 1
                self.current_node = self.current_node.parent.parent
            else:
                if self.current_node.level is len(self.levels_price):
                    self.next_node_weight = self.current_node.weight + 1
                    self.current_node = self.current_node.parent
                else:
                    if self.current_node.value >= self.levels_price[self.current_node.level] * self.next_node_weight:
                        self.current_node.create_child(self.levels_price[self.current_node.level],
                                                       self.next_node_weight)
                        self.next_node_weight = 0
                        self.current_node = self.current_node.children[-1]
                    else:
                        self.next_node_weight = self.current_node.weight + 1
                        self.current_node = self.current_node.parent

# The main function
if __name__ == '__main__':
    # Sort the price table of fruits
    fruit_list = []
    fruit_price = []
    for k, v in FRUIT_PRICE.items():
        fruit_list.append(k)
        fruit_price.append(v)
    for i in range(len(fruit_price) - 1):
        for j in range(len(fruit_price) - 1 - i):
            if fruit_price[-1 - j] > fruit_price[-2 - j]:
                fruit_price[-1 - j], fruit_price[-2 - j] = fruit_price[-2 - j], fruit_price[-1 - j]
                fruit_list[-1 - j], fruit_list[-2 - j] = fruit_list[-2 - j], fruit_list[-1 - j]
    # Inform the user to input the total money
    import re
    total_money = 0
    while True:
        total_money = raw_input('How much do I have:')
        if re.match(r'^[1-9]\d*', total_money) is None:
            print 'Sorry, you must input a right number of money!'
        else:
            total_money = int(total_money)
            break
    tree = FruitTree(total_money, fruit_price)
    tree.grow()
    shopping_list = []
    for leave in tree.leaf:
        node = leave
        shopping_list.append([])
        while node is not tree.root:
            shopping_list[-1].append(node.weight)
            node = node.parent
    print '{:*^40}'.format('')
    print 'Total Money is: {}'.format(total_money)
    print '{:*^40}'.format('')
    print 'The price table of fruits:\n'
    print '{:<15}'.format('Fruit') + '{}'.format('Price')
    for k, v in FRUIT_PRICE.items():
        print '{0:<15}'.format(k) + '{}'.format(v)
    print '{:*^40}'.format('')
    if len(tree.leaf) is 0:
        print 'There is no group!\n'
    elif len(tree.leaf) is 1:
        print 'There is 1 group:\n'
    else:
        print 'There is {} groups:\n'.format(len(tree.leaf))
    for group_id, group in enumerate(shopping_list):
        print '{:-^40}'.format('Group ' + str(group_id + 1))
        print '{0:^15}{1:^8}{2:^8}{3:^9}'.format('Fruit', 'Price', 'Amount', 'Total')
        group.reverse()
        for fruit_index, fruit_amount in enumerate(group):
            if fruit_amount != 0:
                print '{0:^15}{1:^8}{2:^8}{3:^9}'.format(fruit_list[fruit_index], fruit_price[fruit_index],
                                                         fruit_amount, fruit_price[fruit_index] * fruit_amount)
    print '\n{:*^40}'.format('')