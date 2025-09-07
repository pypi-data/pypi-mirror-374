import unittest

from osmxml import XmlElement, XmlAttribute

class TestElement(unittest.TestCase):
    def test_init(self):
        element = XmlElement(name="element")

        self.assertEqual(element.name, "element")
        self.assertEqual(element.attributes, [])
        self.assertEqual(element.children, [])

    def test_full_init(self):
        attr1 = XmlAttribute(name="x1", value="value1")
        attr2 = XmlAttribute(name="x2", value="value2")
        attr3 = XmlAttribute(name="x3", value="value3")

        child1_attrs = [attr1]
        child1 = XmlElement(name="child1", attributes=child1_attrs) 

        element_attrs = [attr2, attr3]
        element_children = [child1]
        element = XmlElement(
            name="element",
            attributes=element_attrs,
            children=element_children
        )

        self.assertEqual(child1.name, "child1")
        self.assertEqual(child1.attributes, child1_attrs)
        self.assertIsNot(child1.attributes, child1_attrs)

        self.assertEqual(element.name, "element")
        self.assertEqual(element.attributes, element_attrs)
        self.assertEqual(element.children, element_children)
        self.assertIsNot(element.attributes, element_attrs)
        self.assertIsNot(element.children, element_children)

    def test_encapsulation(self):
        attr1 = XmlAttribute(name="x1", value="value1")
        attr2 = XmlAttribute(name="x2", value="value2")

        child1_attrs = [attr1]
        child1 = XmlElement(name="child1", attributes=child1_attrs) 

        element_attrs = [attr1, attr2]
        element_children = [child1]
        element = XmlElement(
            name="element",
            attributes=element_attrs,
            children=element_children
        )

        attrs = element.attributes
        attrs.pop()
        children = element.children
        children.pop()

        self.assertEqual(element.name, "element")
        self.assertEqual(element.attributes, element_attrs)
        self.assertEqual(element.children, element_children)

        element_attrs.pop()
        self.assertNotEqual(element.attributes, element_attrs)
        element_children.pop()
        self.assertNotEqual(element.children, element_children)

    def test_to_string(self):
        attr1 = XmlAttribute(name="x1", value="value1")
        attr2 = XmlAttribute(name="x2", value="value2")

        child1_attrs = [attr1]
        child1 = XmlElement(name="child1", attributes=child1_attrs) 
        child2 = XmlElement(name="child2") 

        element_attrs = [attr1, attr2]
        element_children = [child1, child2]
        element = XmlElement(
            name="element",
            attributes=element_attrs,
            children=element_children
        )

        tab = "    "
        element_test_str = '<element x1="value1" x2="value2">'
        element_test_str = "".join([element_test_str, '\n{tab}<child1 x1="value1"/>'])
        element_test_str = "".join([element_test_str, '\n{tab}<child2/>'])
        element_test_str = "".join([element_test_str, '\n</element>'])
        element_test_str = element_test_str.format(tab=tab) 

        self.assertEqual(element.to_string(raw=False), element_test_str)

    def test_get_child(self):
        element = XmlElement(
            name="test_element",

            children=[
                XmlElement(name="child_8123"),
                XmlElement(name="child_1298"),
                XmlElement(name="child_1923"),
            ]
        )

        assert element.get_child_by_index(0).name == "child_8123"
        assert element.get_child_by_index(1).name == "child_1298"
        assert element.get_child_by_index(2).name == "child_1923"

        assert element.get_child_by_name("child_8123").name == "child_8123"
        assert element.get_child_by_name("child_1298").name == "child_1298"
        assert element.get_child_by_name("child_1923").name == "child_1923"
    
    def test_get_attribute(self):
        element = XmlElement(
            name="test_element",
            attributes=[
                XmlAttribute(name="attr_8123", value="value_8123"),
                XmlAttribute(name="attr_1298", value="value_1298"),
                XmlAttribute(name="attr_1923", value="value_1923"),
            ]
        )

        assert element.get_attribute_by_index(0).name == "attr_8123"
        assert element.get_attribute_by_index(1).name == "attr_1298"
        assert element.get_attribute_by_index(2).name == "attr_1923"

        assert element.get_attribute_by_name("attr_8123").name == "attr_8123"
        assert element.get_attribute_by_name("attr_1298").name == "attr_1298"
        assert element.get_attribute_by_name("attr_1923").name == "attr_1923"
