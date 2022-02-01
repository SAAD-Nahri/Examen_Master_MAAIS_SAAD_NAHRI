# auteur = Nahri Saad
# Master MAAIS 2021-2022
# programation avancée
# Poo Project de gestion de stock

import classes
import json
from utility import *

# we will write a class that will handle all the class that will inherited from(create,delete,update,retrieve)
# and also will handle input validation we will use json file to store our data we use the Sqlite approach such
# as table for each class(client,order,product...) and relation between table(foreignkey relation..)

# in our stock management app the main approach is we will handle all the future and we will let the client
# do the order them self(that will avoid the of extra work)
# and we will handle the rest as we will see in the project code

# ======================================================================================================================
class Class_Manager:
    # the json file name that will store all the information
    file_name = "coo"
    TVA = 0.2

    def __init__(self):
        # every object will have an id equal the id of the previous(the same kind) incremented by one
        if self.all_item(False):
            self.id = int(list(self.all_item(False).keys())[-1])+1
        else:
            self.id = 0

    # check if a object dictionary existe in our json file
    @classmethod
    def existe_in_file(cls):
        try:
            b = cls.all_item()[str(cls.__name__)]
            return True
        except:
            return False
    # save an object in our json file
    def save(self):
        a = self.all_item()
        if not(self.existe_in_file()):
            a[str(self.__class__.__name__)] = {}
        a[str(self.__class__.__name__)][str(getattr(self, 'id'))] = self.__dict__
        with open(f"{self.file_name}.json", "w") as file:
            json.dump(a, file)

        # setattr(globals()[self.__class__.__name__], "id", getattr(globals()[self.__class__.__name__], 'id')+1)

    # get list of objects by there id
    @classmethod
    def get_elem_by_id(cls,*args):
        for i in args:
            if str(i) in cls.all_item(False).keys():
                yield cls.all_item(False)[str(i)]

    # search objects with the desire filter and "__" for range filter and "___" for attribute in the parent relation obj
    @classmethod
    def get_elem_filter(cls, include=True, **kwargs):
        # if no kwargs pass it return all the objects
        if kwargs:
            for elem in cls.all_item(False).values():
                obj = cls.dict_to_obj(elem)
                a = []
                for key, val in kwargs.items():
                    if "___" in key:
                        var1, var2 = key.split("___")
                        if "__" in var2:
                            var = getattr(getattr(obj, var1), var2.replace("__",""))
                            if var2.replace("__","") in getattr(getattr(obj, var1), "attr").keys() and "date" in getattr(getattr(obj, var1), "attr")[var2.replace("__","")]:
                                var = str_to_date(var)
                            e = var > val[0]
                            b = var < val[1]
                            c = e and b
                            a.append(c)
                        else:
                            c = str(getattr(getattr(obj, key.split("___")[0]), key.split("___")[1])) == str(val)
                        a.append(c)
                    elif "__" in key:
                        var = getattr(obj, key.split("__")[0])
                        if key.split("__")[0] in getattr(obj,"attr").keys() and "date" in getattr(obj,"attr")[key.split("__")[0]]:
                            var = str_to_date(var)
                        e = var > val[0]
                        b = var < val[1]
                        c = e and b
                        a.append(c)
                    else:
                        a.append(str(getattr(obj, key)) == str(val))
                if include:
                    # if no false in a it mean that all the filter are meet
                    # if not(False in a):
                    if all(a):
                        yield elem
                else:
                    # here it exclude rather than include
                    if a != list(kwargs.values()):
                        yield elem
        else:
            for elem in cls.all_item(False).values():
                yield elem

    # just an extend to the previous function as it return dict, and this return obj
    # we can do it in get_elem_filter function by using additional kwargs argument obj=True

    @classmethod
    def get_all_obj_filter(cls, include=True, **kwargs):
        for obj in cls.get_elem_filter(include,**kwargs):
            # dict_to_obj take dict and return instance of object
            yield cls.dict_to_obj(obj)

    # search object by one or many filter the user choose
    @classmethod
    def cherche_elem1(cls,include=False,**kwargs):
        li = getattr(cls, "attr").copy()
        for key, val in getattr(cls, "attr").items():
            if "non_field" in val:
                del li[key]
        l = list(li.keys())
        if len(l) > 1:
            print('taper le nombre de champ que tu veut filter par')
        filt = input_multiple_in_list(l)
        filt.update(kwargs)
        return cls.get_all_obj_filter(**filt)

    # take dict as argument and return instance of the class object
    @classmethod
    def dict_to_obj(cls, d):
        obj = cls()
        for key,val in d.items():
            setattr(obj, key, val)
        return obj

    # open json file and fetch all the data from it
    @classmethod
    def all_item(cls, all=True):
        with open(f"{cls.file_name}.json", "r") as file:
            a = json.load(file)
        if all:
            return a
        else:
            # if all equal to false it return only the data of the class table as a dict
            # that have id of the class instance as keys and data for instance as values
            if not (cls.existe_in_file()):
                return {}
            return a[str(cls.__name__)]

    # return list of object sorted by the parameter given in the definition of the class
    # it is possible to sort by the kwargs like we did in get_elem_filter(__,___)
    @classmethod
    def all_obj_sorted(cls, include=True, **kwargs):
        if "sort" in getattr(cls, "attr").keys():
            s = getattr(cls, "attr")['sort'].split()[-1]
            if "date" in getattr(cls, "attr")[s]:
                return list(cls.get_all_obj_filter(include, **kwargs)).sort(
                    key=lambda x: str_to_date(getattr(x, s)))
            return list(cls.get_all_obj_filter(include, **kwargs)).sort(
                key=lambda x: getattr(x, getattr(cls, "attr")['sort'].split()[-1]))

    # remove the instance from the json file
    def remove(self):
        a = self.all_item()
        # if the object have relation and get deleted we delete all the object related to it
        if "relation_child" in a[str(self.__class__.__name__)][str(self.id)].keys():
            for elem in a[str(self.__class__.__name__)][str(self.id)]["relation_child"].split()[-1].split("-"):
                for k in getattr(self, elem.split(":")[0]):
                    k.remove()
        del a[str(self.__class__.__name__)][str(self.id)]
        with open(f"{self.file_name}.json", "w") as file:
            json.dump(a,file)

    # this very important function as it handle the update of all object
    # and also carrie out the relation between class(when update on parent object it updated on all object related)
    #
    def update_elem(self):
        li = getattr(self,"attr").copy()
        for key,val in getattr(self,"attr").items():
            if "non_saisie" in val or "non_field" in val:
                del li[key]
        l = list(li.keys())
        if len(l) >= 2:
            print('taper le nombre de champ que tu veut modifie')
        atr = input_in_list(l)
        val = getattr(self, atr)
        print(f"the old value of {atr} is:{val}")
        val1 = self.input_check(atr,getattr(self,"attr")[str(atr)],True)
        if val1 == -1:
            return -1
        # it remove the old instance fron the file
        if self.remove() == -1:
            return -1
        if "relation_child" in getattr(self,"attr").keys() and atr == "id":
            for elem in getattr(self,"attr")["relation_child"].split()[-1].split("-"):
                for k in getattr(self, elem.split(":")[0]):
                    setattr(k, elem.split(":")[1], val1)
                    k.save()
        setattr(self,atr,val1)
        # and save the new one
        self.save()

    # this function handle all the creation of object and check to validate the inpute
    # as(unique field, relation field,date field)
    # also we can pass data that we not want the user to input
    def create_elem(self, **kwargs):
        s = getattr(self,"attr")
        for key,val in s.items():
            if key in kwargs.keys():
                setattr(self, key, kwargs[str(key)])
            else:
                if "non_field" in val or "non_saisie" in val:
                    continue
                ipt = self.input_check(key,val)
                if ipt == -1:
                    return -1
                setattr(self,key,ipt)

    # ensure that the input is satisfied the requirement
    def input_check(self, a, b, update=False):
        if "relation" in b:
            c = (b.split()[-1]).split(':')[-1]
            obj_cls_name, relation_key = c.split('<->')
            z = list(getattr(getattr(classes,str(obj_cls_name)), "get_elem_filter")())
            if z:
                if len(z) != 1:
                    print(f'select the value of {a} from the list of {obj_cls_name}')
                return input_in_list(z)[str(relation_key)]
            else:
                # in case the parent object not exist it send the user to created it
                print(f"we does not have any {obj_cls_name} in database, you must create one first")
                print("do you want to add it now:")
                a = input_in_list(["yes","no"])
                if a == "yes":
                    e = getattr(classes,str(obj_cls_name))()
                    if e.create_elem() != -1:
                        e.save()
                        return e.id
                else:
                    return -1
        # for the input of type choice
        elif "choice" in b :
            c = (b.split()[-1]).split(':')[-1]
            choices = c.split('-')
            print(f'select the value of {a} from the list of choice')
            return input_in_list(choices)
        else:
            while True:
                if "date" in b:
                    print("date format --> DD/MM/YYYY")
                print(f"enter the {a}")
                c = input("-->")
                if str(self.input_validation(a, b, c, update)) == str(c):
                    return self.input_validation(a, b, c, update)
                else:
                    # it print the error that accurate during enter data
                    print(self.input_validation(a, b, c, update))
                    print("do you want to cancel the operation: ")
                    # maybe he don't want to continue the process
                    if input_in_list(["yes","no"]) == "yes":
                        return -1

    # check the basic input validation and return the value or error message
    def input_validation(self, a, b, c, update=False):
        if "NotNull" in str(b):
            if c == '':
                return "this field can't be empty"
        if "date" in b:
            if not (is_date(c)):
                return f"does not match the date format DD/MM/YYYY, {c} must be in the correct date format"
        if "number" in b:
            if not (int_input(c)):
                return "this field must be an number"
            c = int(c)
        if "unique" in str(b):
            if update:
                if list(self.get_elem_filter(**{str(a): c})) and c != getattr(self, a):
                    return f"this field must be an unique, {c} already existe"
            else:
                if list(self.get_elem_filter(**{str(a): c})):
                    return f"this field must be an unique, {c} already existe"
        return c