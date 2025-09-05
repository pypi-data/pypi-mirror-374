# XMLAccessor
This is a tool for loading python classes using XML.  

Loading xml to python classes sounds simple to begin with, XML is a nested structure and classes 
can be nested.  
The issue with directly casting to classes, or generating them, is you get highly nested structures, and cleaning them up afterwards is just as much work as parsing it yourself.  
Also if you only want a subsection of the data you end up needing to define a lot of classes just to pull it out.  

This library allows you to define the class structure you would like, then load the XML into it using a simple syntax.    
It is intended to be used in conjunction with the <tt>xml</tt> library and its elements, which are also used by the <tt>lxml</tt> library.   

## Install
<tt>pip install  XMLAccessor</tt>
### Include in file
<tt>from XMLAccesor import Accessor, SubAccessor, Transformer</tt>  

XMLAccessor uses 3 of its own classes as tools, <b>Accessor</b>, <b>SubAccessor</b> and <b>Transformer</b>.

(sidenote, what if they already have an __init__?)  
Let's say you have an XML file that looks like this 
```XML
<Application>
    <Section1>
        <Inner Type="test">Text Value</Inner>
        <Other>Something</Other>
    </Section1>
<Application>
```  
And you wanted to populate a class that looked like this 
```python
class Section1
    Type: str
    InnerText: str
    OtherText: str
```  
In order to populate those values, start by adding a LOADER_DICT attribute to the class.  
The LOADER_DICT has keys that should match your class attributes, and the values are list of Accessors, followed by any Transformers. That looks like this  
(explanation of those accessors is coming imminently)
```python
LOADER_DICT = {
    'Type' : [Accessor(tag='Section1'), Accessor(tag='Inner', attribute='Type')],
    'InnerText': [Accessor(tag='Section1'), Accessor(tag='Inner')],
    'Other' : [Accessor(tag='Section1'), Accessor(tag='Other')]
}
```  
So your resulting class looks like this   
```python
class Section1
    Type: str
    InnerText: str
    OtherText: str

    LOADER_DICT = {
    'Type' : [Accessor(tag='Section1'), Accessor(tag='Inner', attribute='Type')],
    'InnerText': [Accessor(tag='Section1'), Accessor(tag='Inner')],
    'Other' : [Accessor(tag='Section1'), Accessor(tag='Other')]
    }
```

Here the loader_dict is specifying how to access the values we'll store in each attribute of the dataclass.  
It does this through a chain of Accessors. 
## Accessor
Each Accessor is a class with 3 optional attributes
```python
tag: str
attribute: str 
subs: list[SubAccessor]
```
### tag attribute
Specifying a tag means it will find the first element with that tag. If you end your Accessor list with an Accessor that has only its .tag attribute populated, the text found within that tag is returned as a value.  
As seen above, the Accessors all look inside the 'Section1' element, then keep looking, in the case of InnerText and Other, the next Accessor only has a tag, so the values inside these tags are returned.  
### attribute attribute
At the end of your accessors you can specify an attribute of an element to retrieve.  
As you can't nest any further elements inside the attribute we take this as the end of the chain.   
In the above example, the second Accessor under the 'Type' key, gets the attribute inside the Inner tag.  
### Subs 
These are for loading classes within classes, they're explained in [SubAccessors](#subaccessors), but these docs make more sense in order. 
## load_class_from_element
This is the function you'll need to call to populate the class. Once you have a class with a LOADER_DICT, and an xml string or file loaded into an ET.Element, run:  
```python 
resulting_class = XMLAccessor.load_class_from_element({resulting class}, {xml element})
```
The syntax is:
```python
def load_class_from_element(cast_class: any, element: ET.Element)
```
(ET is an alias for xml.etree.ElementTree, these are interchangable for the lxml library elements.)
## SubAccessors
XML often re-uses elements, so you might want to replicate that in your class structure.  
Say we have XML like this 
```XML
<Family>
    <Person>
        <Age>50</Age>
        <Name>
            <FirstName>First</FirstName>
            <MiddleName>Middle</MiddleName>
            <LastName>Last</LastName>
        <Name>
    </Person>
    <Cat>
        <Colour>Orange</Colour>
        <Name>
            <FirstName>Moofie</FirstName>
            <MiddleName>The</MiddleName>
            <LastName>Cat</LastName>
        </Name>
</Family>
```  
You'd probably want to define your classes so that Person and Cat don't have all the name fields, but they have a .Name attribute to store a Name instance.   
You might make your class structure like this. 
```python
class Name:
    FirstName: str
    MiddleName: str
    LastName: str

class Person
    Age: int
    Name: Name

class Cat:
    Colour: str
    Name: Name
```
This is when we'll make use of the <tt>subs</tt> atribute of the Accessor. 
The SubAccessor has three attributes 
```python
tag_name: str
cast_class: any
is_list: bool = False
```
<b>tag_name</b> tells it what tag to look for  
<b>cast_class</b> tells it what the resulting class will be 
<b>is_list</b> tells it whether to look for a number of these elements and return a list, it defaults to False.  
To allow the nested class to be populated, we create an Accessor that looks like this <tt>Accessor(subs=[SubAccessor(tag_name='Name', cast_class=Name, is_list=False)])  </tt>
So the resulting loading classes would look like this (assuming you load Family as the root node)  
```python
class Name:
    FirstName: str
    MiddleName: str
    LastName: str

    LOADER_DICT = {
        'FirstName': [Accessor('FirstName')],
        'MiddleName': [Accessor('MiddleName')],
        'LastName': [Accessor('LastName')]
    }

class Person
    Age: int
    Name: Name

    LOADER_DICT = {
        'Age': [Accessor('Age'), Transformer(int)],
        'Name': [Accessor(subs=[SubAccessor('Name', Name)])],
    }

class Cat:
    Colour: str
    Name: Name

    LOADER_DICT = {
        'Colour': [Accessor('Colour')],
        'Name': [Accessor(subs=[SubAccessor('Name', Name)])]
    }
```
You'll also note that example of a Transformer. It's turning the str (all XML values must be strings) into an int. They're explained in the [Transformer section](#transformer).  
### Lists of elements
Let's we're looking at a person, who may have several phone numbers. 
```xml
<Person>
    <Name>Phillip</Name>
    <Phones>
        <Phone>
            <Mobile>04758294353</Mobile>
        </Phone>
        <Phone>
            <FixedPhone AreaCode="+61">12345678</FixedPhone>
        </Phone>
    </Phones>
</Person>
```   
I would want to populate the .phones on the Person class with a list of Phone instances.   
Create your innermost class first, so in this case Phone class, and its LOADER_DICT.  
The LOADER_DICT loading is non-strict, so if it can't find a value it won't populate it. This allows you to make more flexible classes, like in this example a phone with a Mobile and a Phone with a FixedPhone can share the same class.  
```python
class Phone:
    Mobile: str
    FixedPhone: str
    AreaCode: str
    
    LOADER_DICT = {
        'Mobile': [Accessor('Mobile')],
        'FixedPhone': [Accessor('FixedPhone')],
        'AreaCode': [Accessor('FixedPhone', 'AreaCode')]
    }
```   
And the person
```python
class Person:
    Name: str
    PhoneList: List[Phone]

    LOADER_DICT = {
        'Name' = [Accessor('Name')],
        'PhoneList': [Accessor(tag='Phones', subs=[SubAccessor('Phone', Phone, True)])]
    }
```  
See here the PhoneList accessor accesses the Phones element, and then within that we search for a list of 'Phone' tags, casting them to Phone class.
## Transformer
Transformers allow you to modify the value found by the Accessors.  
They just have one attribute '.func'. This can be any callable, as long as it returns a value.   
Add them to the LOADER_DICT at the end of a list of Accessors:  
```python
class Person
    Age: int

    LOADER_DICT = {
        'Age' : [Accessort('Person', 'Age'), Transformer(int)]
    }
```
(this works because int is a function in python). Remember to pass in the function without the (),  
You can add as many of them as you want, they just have to occur <b>AFTER</b> the Accessors for a given key, and must return a value.  
## Utility Functions
I've thrown in a couple of utility functions that work well in conjunction with casting xml to python classes.   
There are currently 2 of them, if you want to use them change your import to 
<tt>from XMLAccessor import XMLAccessor, Accessor, SubAccessor, Transformer</tt>
The utils are 2 static methods from the XMLAccessor class. 
### to_dict 
Once you populate nested classes in python it's surprisingly difficult to turn them into a printable structure.  
If you directly print it, you get one layer deep; if you try to json dump it you get a un-serialisable error. This makes it difficult to debug.  
I created a function to recursively convert the classes into dicts, so then you can print this or write it to a file. 
Call it with 
```python 
resulting_dict = XMLAccessor.to_dict({YOUR CLASS})
```
### find_class_by_value
In XML you often have one element refer to another using a unique ID. For example: 
```xml
<Family>
    <Person>
        <ID>IDABC</ID>
        <Name>Peter</Name>
        <Relative type="Son">IDXYZ</Relationship>
    </Person>
    <Person>
        <ID>IDXYZ</ID>
        <Name>Paul</Name>
        <Relative type="Father">IDABC</Relationship>
    </Person>
</Family>
``` 
(Usually the relationships are one-way, but it's just an example).  
Say you wanted to get all father-son pairs in your incoming data, you could read the relative field on a person, and if 
its type = 'Son', go get the Person with the following ID as their ID.  
This is where you would use find_class_by_value.  
Once you've cast this xml into classes, call 
<tt>resultingperson = XMLAccessor.find_class_by_value(Family, 'ID', 'IDABC')</tt>  
The syntax is 
```python
def find_class_by_value(root_class: any, attribute: str, match_value: any):
```  
So you pass in the starting point, then the attribute you want to match on, and the value you want to find. It will recursively go through
all the attributes to find the resulting class.  
### Note about __init__
To maintain flexibility the load_class_from_element needs to be able to instantiate an empty class then add attributes to it. For this reason you can't 
define an __init__ function on your classes with any arguments, otherwise we'll get a missing argument error when the function runs.  