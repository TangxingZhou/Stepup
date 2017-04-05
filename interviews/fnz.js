'use strict';

var fruits = {
    'apple': 59, 
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
    'watermelon': 500
};
var leaves, fruits_list, price_list;

function FruitNode(node)
{
    this.level = node.level || 0;
    this.weight = node.weight || 0;
    this.values = node.values || 0;
    this.parents = null;
    this.children = [];
    this.create_child = function (props){
        var child = new FruitNode(props);
        child.parents = this;
        this.children.push(child);
    }
}

function FruitTree(tree)
{
    var root_node = new FruitNode({level: 0, weight: 0, values: tree['root_value']});
    this.root = root_node;
    this.current_node = root_node;
    this.levels_price = tree['levels_price'];
    this.next_node_weight = 0;
    this.leaves = [];
    this.grow = function (){
        var child;
        while (this.current_node != null)
        {
            if (this.current_node.values === 0)
            {
                this.leaves.push(this.current_node);
                this.next_node_weight = this.current_node.parents.weight + 1;
                this.current_node = this.current_node.parents.parents;
            }
            else
            {
                if (this.current_node.level === this.levels_price.length)
                {
                    this.next_node_weight = this.current_node.weight + 1;
                    this.current_node = this.current_node.parents;
                }
                else
                {
                    if (this.current_node.values >= this.levels_price[this.current_node.level] * this.next_node_weight)
                    {
                        child = {
                            'level': this.current_node.level + 1,
                            'weight': this.next_node_weight,
                            'values': this.current_node.values - this.next_node_weight * this.levels_price[this.current_node.level]
                        };
                        this.current_node.create_child(child);
                        this.next_node_weight = 0;
                        this.current_node = this.current_node.children[this.current_node.children.length - 1];
                    }
                    else
                    {
                        this.next_node_weight = this.current_node.weight + 1;
                        this.current_node = this.current_node.parents;
                    }
                }
            }
        }
    }
}

function sort_object_by_vale(obj)
{
    var props = [];
    var values = [];
    var tmp;
    for (var prop in obj)
    {
        props.push(prop);
        values.push(obj[prop]);
    }
    for (var i = 0; i < values.length - 1; i ++)
    {
        for (var j= values.length - 1; j > i ; j --)
        {
            if (values[j] > values[j - 1])
            {
                tmp = values[j];
                values[j] = values[j - 1];
                values[j -1] = tmp;
                tmp = props[j];
                props[j] = props[j - 1];
                props[j -1] = tmp;
            }
        }
    }
    return {'props': props, 'values': values};
}

function get_fruits_group(total_money)
{
    var fruits_tree;
    var sorted_by_price = sort_object_by_vale(fruits);
    fruits_list = sorted_by_price.props;
    price_list = sorted_by_price.values;
    var init_tree = {
        'root_value': total_money,
        'levels_price': price_list
    };
    fruits_tree = new FruitTree(init_tree);
    fruits_tree.grow();
    leaves = fruits_tree.leaves;
}

