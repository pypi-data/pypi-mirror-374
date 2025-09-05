from dataclasses import dataclass
import xml.etree.ElementTree as ET
from typing import Callable
    
@dataclass
class SubAccessor():
    """
    -@tag: xml tag to access  
    -@cast_class: python class to cast found element to  
    -@is_list: If True looks for > 1 {tag} results, and returns list
    """
    tag: str
    cast_class: any
    is_list: bool = False

@dataclass
class Accessor:
    """
    -@tag: xml tag to access
    -@attribute: xml attribute from which to pull a value
    -@sub: list of SubAccessors
    """
    tag: str | None = None
    attribute: str | None = None
    subs: list[SubAccessor] | None = None
        
@dataclass
class Transformer():
    """
    -@func: Callable, must return a value
    """
    func: Callable
    

class XMLAccessor:
    
    
    @staticmethod
    def load_class_from_element(cast_class: any, element: ET.Element):
        """
        #### Inputs:
            -@cast_class: the class you want to populate
            -@element: xml element
        #### Expected Behaviour:
            - If you don't pass a class with a LOADER_DICT in, raise an exception
            - for each item in the LOADER_DICT;
            - pass the Accessors in the list to the _nested_access_xml to get a value
            - if it returns None, skip to the next item
            - if it's not None, apply any Transformers
            - set the attribute on the cast_class using the result values
        #### Returns:
            - the cast_class with attributes populated from the element
        """
        instance = cast_class()
        if(not hasattr(instance, 'LOADER_DICT')):
            raise Exception(f'"load_class_from_element" cast_class "{cast_class}" is missing a LOADER_DICT, which is required for this XMLAccessor to work')
        for key, value in instance.LOADER_DICT.items(): 
            accessors = [x for x in value if type(x) != Transformer]
            value_found_in_xml = XMLAccessor._nested_access_xml(accessors, element)
            if(value_found_in_xml == None):
                continue
            for x in [x for x in value if type(x) == Transformer]:
                value_found_in_xml = x.func(value_found_in_xml)
            setattr(instance, key, value_found_in_xml)
        return(instance)
    
    
    @staticmethod
    def _sub_access(sub_list: list[SubAccessor], curr_val: ET.Element):
        """
        #### Inputs:
            -@sub_list: list of SubAccessors
            -@curr_val: xml element
        #### Expected Behaviour:
            - Used for loading a class or list of classes from a list of SubAccessors
            - pop the first element off the sub_list
            - #case 1: if the tag_name doesn't find anything, and there are other options in the subs list,
                try again with the rest of the list
            - #case 2: if the tag_name doesn't find anything and there aren't other options, return None
            - #case 3: the tag_name does return a value, and the sub.is_list is true, so for each value found cast it into the 
                cast_class and return that list
            -# case 4: the tag_name search does return a value, the sub.is_list is false, so return the first value found, cast into 
                the cast_class
        #### Returns:
            - Either a class, or a list of classes, or None
        """
        sub = sub_list.pop(0)
        new_val = curr_val.find(sub.tag)
        if(new_val == None):
            if(len(sub_list) == 0):
                return(None) #case 1
            else:
                return(XMLAccessor._sub_access(sub_list, curr_val)) #case 2
        elif(sub.is_list):
            found_elements = curr_val.findall(sub.tag)
            return([XMLAccessor.load_class_from_element(sub.cast_class, x) for x in found_elements]) #case 3
        else:
            return(XMLAccessor.load_class_from_element(sub.cast_class, new_val)) #case 4
    
    
    @staticmethod
    def _nested_access_xml(accessor_list: list[Accessor], xml: ET.Element):
        """
        #### Inputs:
            -@accessor_list: list of Accessor instances
            -@xml: ET.Element
        #### Expected Behaviour:
            - Used for finding a value in xml using a list of Accessors
            - pop the first element off the list of Accessors
            - First check if the current accessor has a tag, if so enter it
            - case 1: The accessor tag yields no value on the search, return None
            - case 2: The Accessor has no subs, and an attribute is present. Return the value in the attribute
            - case 3: The Accessor has no subs, there is no attribute, and there are remanining values in the accessor_list,
                make a recursive call on the remaining accessors, using the current element
            - case 4: The Accessor has no subs, there is no attribute, no further elements in the accessor_list
                return the text of the element
            - case 5: The Accessor has subs, use the _sub_access function to get the value using these subs.
                there are no further Accessors, so return the value returned by this function
        #### Returns:
            - Either a string value from inside an XML element or attribute, 
                or 
            - a class that has been cast to by _sub_access
        """
        curr_val = xml
        accessor = accessor_list.pop(0)
        if(accessor.tag):
            curr_val = curr_val.find(accessor.tag)
            if(curr_val == None):
                return(None) #case 1
        if(accessor.subs == None):
            if(accessor.attribute):
                return(curr_val.get(accessor.attribute)) # case 2
            if(len(accessor_list)):
                return(XMLAccessor._nested_access_xml(accessor_list, curr_val)) #case 3           
            return(curr_val.text) #case 4
        else:
            return(XMLAccessor._sub_access(accessor.subs, curr_val)) # case 5  
        
    
    @staticmethod
    def to_dict(input: any):
        """
        #### Inputs: 
            -@input: expected to be initially called using a class
                it makes recursive calls 
        #### Expected Behaviour:
            - Used to turn nested classes into nested dicts 
            - has a base case of just returning the value, if passed anything other 
                than a class, list or dict
            - for dicts passed in, make a recursive call on each item and return the resulting dict
            - for lists, make a recursive call for each element and return the resulting list
            - for classes, make a recursive call using the __dict__ items, which will fall into the dict case
        #### Returns:
            - if passed a class, returns a dict 
        """
        if(hasattr(input, '__dict__')):
            return(XMLAccessor.to_dict(input.__dict__)) # class case
        elif isinstance(input, list):
            return([XMLAccessor.to_dict(x) for x in input]) #list case
        elif type(input) == dict:
            return({x: XMLAccessor.to_dict(y) for x, y in input.items()}) #dict case
        else:
            return(input) #base case 


    @staticmethod
    def find_class_by_attribute_value(value: any, attribute: str, match_value: any):
        """
        #### Inputs:
            -@value: pass in a class
            -@attribute: the attribute to search on 
            -@match_value: the value to match in that attribute
        #### Expected Behaviour:
            - Used to find a class based on its attribute matching a match_value
            - #match case: if the value passed in is a class, and has the the search attribute
                and it matches the match_value, return the value passed in
            - if the value passed in is a class but a match isn't found, recursively call the function on the other 
                values in the dict
            - else if a list is passed in (like above with the values), for each item in the list, 
                make a recursive call. If one of them matches return the value #list match case (which 
                will actually make the match using #match case 
            - return None if no match is made #base case
        #### Returns:
            - if a match is found, a class, else None
        """
        if(hasattr(value, '__dict__')):
            if(value.__dict__.get(attribute) == match_value):
                return(value) # match case
            return(XMLAccessor.find_class_by_attribute_value(value.__dict__.values(), attribute, match_value))
        elif isinstance(value, list) or isinstance(value, tuple):
            for val in value: 
                resp = XMLAccessor.find_class_by_attribute_value(val, attribute, match_value)
                if(resp != None):
                    return(resp) #list match case 
        elif isinstance(value, dict):
            return(XMLAccessor.find_class_by_attribute_value(value.values(), attribute, match_value))
        return(None) # base case 