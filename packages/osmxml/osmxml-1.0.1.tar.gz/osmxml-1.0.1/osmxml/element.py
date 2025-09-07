from typing import Optional, List

from .xml import Xml   
from .attribute import XmlAttribute

class XmlElement(Xml):
    def __init__(
            self, 
            name: str, 
            attributes: Optional[List[XmlAttribute]] = None,
            children: Optional[List[Xml]] = None,
            is_closed: Optional[bool] = True,
        ):
        self._name = name 
        self._attributes = attributes.copy() if attributes is not None else []
        self._children = children.copy() if children is not None else []
        self._is_closed = is_closed 

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name


    @property
    def attributes(self) -> List[XmlAttribute]:
        return self._attributes.copy()

    @attributes.setter
    def attributes(self, attributes: List[XmlAttribute]):
        self._attributes = attributes


    @property
    def children(self) -> List[Xml]:
        return self._children.copy()

    @children.setter
    def children(self, children: List[Xml]):
        self._children = children


    @property
    def is_closed(self) -> bool:
        return self._is_closed

    @is_closed.setter
    def is_closed(self, value: bool):
        self._is_closed = value


    def add_attribute(self, attribute: XmlAttribute):
        self._attributes.append(attribute) 

    def get_attribute_by_index(self, index: int) -> Optional[XmlAttribute]:
        return self._attributes[index] if index < len(self.attributes) else None

    def get_attribute_by_name(self, name: str) -> Optional[XmlAttribute]:
        for attr in self.attributes:
            if attr.name == name:
                return attr
        return None

    def remove_attribute_by_index(self, index: int):
        del self._attributes[index]
    
    def remove_attribute_by_name(self, name: str):
        for attr in self.attributes:
            if attr.name == name:
                self.remove_attribute_by_index(self.attributes.index(attr))
                return


    def add_child(self, child: Xml):
        self._children.append(child)

    def get_child_by_index(self, index: int) -> Optional[Xml]:
        return self._children[index] if index < len(self.children) else None

    def get_child_by_name(self, name: str) -> Optional[Xml]:
        for child in self.children:
            if child.name == name:
                return child
        return None

    def remove_child_by_index(self, index: int):
        del self._children[index]
    
    def remove_child_by_name(self, name: str):
        for child in self.children:
            if child.name == name:
                self.remove_child_by_index(self.children.index(child))
                return


    def has_attributes(self):
        return len(self.attributes) > 0

    def has_children(self):
        return len(self.children) > 0


    def to_string(self, raw=True) -> str:
        attrs_str = self._combine_attributes()

        if (not self.has_children()):
            close_slash = "/" if self.is_closed else ""
            return "<{name}{attrs}{slash}>".format(name=self.name, attrs=attrs_str, slash=close_slash)

        tab =  "" if raw else "    "
        new_line =  "" if raw else "\n" 
        list_children_str = []
        for child in self.children:
            # Convert child to string
            child_str = child.to_string(raw=raw)
            # Add tabs before child
            child_tab_str = child_str.replace("{new_line}".format(new_line=new_line), "{new_line}{tab}".format(new_line=new_line, tab=tab))
            # Add child to list with new line with tab
            list_children_str.append("{new_line}{tab}{child}".format(new_line=new_line, tab=tab, child=child_tab_str))

        children_str = "".join(list_children_str) 
       
        closed_template = "<{name}{attrs}>{children}{new_line}</{name}>"
        non_closed_template = "<{name}{attrs}>{children}{new_line}"

        template = closed_template if self.is_closed else non_closed_template

        element_str = template.format(
            name=self.name,
            attrs=attrs_str,
            children=children_str,
            new_line=new_line,
        )

        return element_str.strip()

    def _combine_attributes(self) -> str:
        if (self.has_attributes()):
            return " {attrs}".format(attrs=" ".join(attr.to_string() for attr in self.attributes))
        return ""


    def __str__(self):
        return self.to_string(raw=True)

    def __repr__(self):
        repr = 'XmlElement(name="{name}",'
        repr = "".join([repr, " attributes=len({attrs_len}),"])
        repr = "".join([repr, " children=len({children_len}))"])
        repr = "".join([repr, " is_closed={is_closed})"])
        repr = repr.format(
                name=self.name,
                attrs_len=len(self.attributes),
                children_len=len(self.children),
                is_closed=self.is_closed,
        )
        return repr
