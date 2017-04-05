using System;
using System.Collections.Generic;

namespace myapp
{

    class FruitNode
    {
        public int level, weight, value;
        public FruitNode parent;
        public List<FruitNode> children;

        public FruitNode(int node_level, int node_weight, int node_value)
        {
            level = node_level;
            weight = node_weight;
            value = node_value;
            parent = null;
            children  = new List<FruitNode>();
        }

        public void CreateChild(int child_weight, int child_value)
        {
            FruitNode child = new FruitNode(level + 1, child_weight, value - child_value * child_weight);
            child.parent = this;
            children.Add(child);
        }
    }

    class FruitTree
    {
        public FruitNode root, current_node;
        public List<FruitNode> leaves;
        public List<int> levels_price;
        public int next_node_weight;

        public FruitTree(int root_value, List<int> prices)
        {
            root = new FruitNode(0, 0, root_value);
            current_node = root;
            leaves = new List<FruitNode>();
            levels_price = new List<int>();
            foreach (int item in prices)
            {
                levels_price.Add(item);
            }
            next_node_weight = 0;
        }

        public void grow()
        {
            while (current_node != null)
            {
                if (current_node.value == 0)
                {
                    leaves.Add(current_node);
                    next_node_weight = current_node.parent.weight + 1;
                    current_node = current_node.parent.parent;
                }
                else
                {
                    if (current_node.level == levels_price.Count)
                    {
                        next_node_weight = current_node.weight + 1;
                        current_node = current_node.parent;
                    }
                    else
                    {
                        if (current_node.value >= levels_price[current_node.level] * next_node_weight)
                        {
                            current_node.CreateChild(next_node_weight, levels_price[current_node.level]);
                            next_node_weight = 0;
                            current_node = current_node.children[current_node.children.Count -1];
                        }
                        else
                        {
                            next_node_weight = current_node.weight + 1;
                            current_node = current_node.parent;
                        }
                    }
                }
            }
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            Dictionary<string, int> fruits_table = new Dictionary<string, int>();
            List<string> fruits_list = new List<string>();
            List<int> prices_list = new List<int>();
            fruits_table.Add("apple", 59);
            fruits_table.Add("banana", 32);
            fruits_table.Add("cocount", 155);
            fruits_table.Add("grapefruit", 128);
            fruits_table.Add("jackfruit", 1100);
            fruits_table.Add("kiwi", 41);
            fruits_table.Add("lemon", 70);
            fruits_table.Add("mango", 97);
            fruits_table.Add("orange", 73);
            fruits_table.Add("papaya", 254);
            fruits_table.Add("pear", 37);
            fruits_table.Add("pineapple", 399);
            fruits_table.Add("watermelonle", 500);
            foreach (KeyValuePair<string, int> kvp in fruits_table)
            {
                fruits_list.Add(kvp.Key);
                prices_list.Add(kvp.Value);
            }
            int tmp_price;
            string tmp_name;
            for (int i = 0; i < prices_list.Count - 1; i++)
            {
                for (int j = prices_list.Count - 1; j > i ; j--)
                {
                    if (prices_list[j] > prices_list[j - 1])
                    {
                        tmp_price = prices_list[j];
                        prices_list[j] = prices_list[j - 1];
                        prices_list[j - 1] = tmp_price;
                        tmp_name = fruits_list[j];
                        fruits_list[j] = fruits_list[j - 1];
                        fruits_list[j - 1] = tmp_name;
                    }
                }
            }
            Console.Write("How much do I have:");
            int total_money = Convert.ToInt32(Console.ReadLine());
            FruitTree fruits_tree = new FruitTree(total_money, prices_list);
            fruits_tree.grow();
            Console.WriteLine("{0} groups are found!", fruits_tree.leaves.Count);
            FruitNode node;
            int group_id = 0;
            Console.WriteLine("Name   Price   number   Total Money");
            foreach (FruitNode item in fruits_tree.leaves)
            {
                node = item;
                Console.WriteLine("--------Group {0}--------", ++ group_id);
                while (node != fruits_tree.root)
                {
                    if (node.weight != 0)
                    {
                        Console.WriteLine("{0}   {1}   {2}   {3}", fruits_list[node.level -1], prices_list[node.level -1], node.weight, prices_list[node.level - 1] * node.weight);
                    }
                    node = node.parent;
                }
            }
        }
    }
}
