
from class_manager import *

class Person(Class_Manager):
    # at every class definition we need to set the attr in order to communicated with the upper class
    # we make class the carried all the function a user able to do based of type(client or supplier)
    # the important is that we let the client handle the order them self and we been able to do so
    # by every time a new client saved we initiated a place in card.json he can add product to it
    # and confirmed the order to start a new one
    attr = {"id":"unique non_saisie number",
            "fullname":'unique NotNull',
            "date_added":"date non_saisie",
            "type":"choice:client-fourniseur",
            "pays":"NotNull",
            "code_postal":"number",
            "adresse":"",
            # relation_child used to make change when the the parent instance change
            # non_saisie is the attribute that the user not see
            "relation_child":"non_field order:person_id",
            # sort used to give the key to sort with
            "sort":"non_field date_added"}
    def __init__(self,fullname='',date_added=str(datetime.date.today()),type="",pays='',code_postal=0,adresse=''):
        # automatically generate the id (autoincrement) of every class
        super(Person, self).__init__()
        self.fullname = fullname
        self.date_added = date_added
        self.type = type
        self.pays = pays
        self.code_postal = code_postal
        self.adresse = adresse

    def __str__(self):
        return f"{self.type}:name={self.fullname},id={self.id},montant rast a payee = {self.montant_rest_a_payee}"

    # add a row in cart.json file for the new client or clear it to make new order
    def init_cart(self):
        try:
            with open("cart.json", 'r') as cart:
                a = json.load(cart)
        except:
            a = {}
        a[str(self.id)] = {}
        with open("cart.json", "w") as file:
            json.dump(a,file)

    # override the save methode to include creating a row in card for the new client
    def save(self):
        if self.type == "client":
            self.init_cart()
        super().save()

    # add a product to the card by the client or update it
    def add_to_cart(self,product_id,update=False):
        cart = Cart(self.id)
        if update:
            print(f"the old quantity is {cart.cart[str(product_id)]['quantity']}")
        while True:
            x = int_input1("entre the quantity:")
            q = next(Product.get_all_obj_filter(id=product_id)).quantity
            # check if we have sufficient quantity
            if x > q:
                print(f"only {q} left in stock")
                print("do you want to order a less quantity:")
                s = input_in_list(["yes", "no"])
                if s == "no":
                    return -1
            else:
                break
        cart.add(product_id, x)
        print(f"change saved")

    # loop trough all the item in the client cart and add them to the database
    def confirme_order_client(self):
        cart = Cart(self.id)
        if cart.cart:
            a = cart.get_total_cost()
            print(f"the total amount is {a}$")
            print("do you want to confirme this order:")
            if input_in_list(['yes','no']) == "yes":
                order = Order()
                order.create_elem(person_id=self.id)
                order.save()
                for item in cart:
                    e = OrderItem()
                    e.create_elem(order_id=order.id,product_id=item["product"].id,quantity=item["quantity"])
                    prod = next(Product.get_all_obj_filter(id=item["product"].id))
                    prod.quantity -= item["quantity"]
                    e.save()
                self.init_cart()
            else:
                print('OK')
        else:
            print("you have no product in the cart")

    # for order of a supplier we take care of it with this methode
    @staticmethod
    def pass_order_fourniseur(id):
        order = Order()
        order.create_elem(person_id=id)
        order.save()
        while True:
            item = OrderItem()
            if item.create_elem(order_id=order.id) != -1:
                item.save()
            print("do you want to add another order line")
            if input_in_list(["yes","no"]) == "no":
                break

    # return all the orders of a user
    def order(self,**kwargs):
        return list(Order.get_all_obj_filter(person_id=self.id,**kwargs))

    @property
    def montant_rest_a_payee(self):
        return sum((y.total_montant-y.montant_deja_Paye) for y in self.order(etat_paiement='totalement_payee'))

# =====================================================================================================================

class Category(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "nom":'unique NotNull',
            "relation_child":"non_field product:category_id",
            "sort":"non_field nom"}

    def __init__(self,nom=''):
        super(Category, self).__init__()
        self.nom = nom

    def __str__(self):
        return f"id={self.id}, nom={self.nom}"


    def product(self,**kwargs):
        return list(Product.get_all_obj_filter(category_id=self.id,**kwargs))

# =====================================================================================================================

class Product(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "nom":'unique NotNull',
            "category_id":"number relation:Category<->id",
            "prix":"number",
            "quantity":"number",
            'prix1':'number non_saisie',
            "seuil_de_camande":"number",
            'relation_child':'non_field order_item:product_id',
            "sort":"non_field prix"}

    def __init__(self,nom='',category_id='',prix=0,quantity=0,seuil_de_camande=0,prix1=-1):
        super(Product, self).__init__()
        self.nom = nom
        self.category_id = category_id
        # this attr prix is the price that we do the calculation with
        self.prix = prix
        self.quantity = quantity
        self.seuil_de_camande = seuil_de_camande
        # and this is where we store the original price
        self.prix1 = prix1

    def __str__(self):
        promo = self.promotions(promo_active=True)
        if promo:
            return f"id={self.id}, nom={self.nom}, quantity in the stock={self.quantity}" \
                   f"the original price is {self.prix1}, the promo price is {self.prix}"
        else:
            return f"id={self.id}, nom={self.nom}, prix={self.prix}, quantity in the stock={self.quantity}"

    def order_item(self,**kwargs):
        return list(OrderItem.get_all_obj_filter(product_id=self.id,**kwargs))

    def promotions(self,**kwargs):
        return list(Promotions.get_all_obj_filter(product_id=self.id,**kwargs))

    def set_prix(self):
        promo = self.promotions(promo_active=True)
        if promo:
            if promo[0].prix_promo != self.prix:
                self.prix1 = self.prix
                self.prix = promo[0].prix_promo
                self.save()
        elif self.prix1 != -1:
            self.prix = self.prix1
            self.prix1 = -1
            self.save()


# =====================================================================================================================

class Promotions(Class_Manager):
    attr = {"id": "unique non_saisie number",
            "date_debut": 'date',
            "date_fin":'date',
            "product_id": "number relation:Product<->id",
            "prix_promo": "number",
            # 'relation_child': 'non_field order_item:product_id',
            "sort": "non_field prix_promo"}

    def __init__(self,date_debut=str(datetime.date.today()),date_fin=str(datetime.date.today()),product_id=0,prix_promo=0):
        super(Promotions, self).__init__()
        self.date_debut = date_debut
        self.date_fin = date_fin
        self.product_id = product_id
        self.prix_promo = prix_promo
    def __str__(self):
        return f"promotions number {self.id} of the product {self.product.nom} begin at {self.date_debut}" \
               f",end at {self.date_fin} with a reduction of {self.reduction_ratio}% ,active={self.promo_active}"

    def input_check(self, a, b ,update=False):
        if str(a) == "prix_promo":
            x = int_input1("entre the promo price:")
            if x > self.product.prix or x < 0:
                print(f"the price is {self.product.prix} you must reduce the price")
                print("do you want to give a smaller price:")
                sel = input_in_list(["yes","no"])
                if sel == "yes":
                    return self.input_check(a, b, update)
                else:
                    return -1
            else:
                return x
        elif str(a) == 'date_debut':
            print("do you want to start the promo from the current date")
            if input_in_list(["yes", "no"]) == "no":
                x = saisir_date('enter date de debut de promo')
                if str_to_date(x) < datetime.date.today():
                    print(f"you cannot start a promo in the pass")
                    print("do you want to give a reason date de debut:")
                    sel = input_in_list(["yes", "no"])
                    if sel == "yes":
                        return self.input_check(a, b, update)
                    else:
                        return -1
                else:
                    return x
            return self.date_debut
        elif str(a) == 'date_fin':
            x = saisir_date('enter date de fin de promo')
            if str_to_date(x) < str_to_date(self.date_debut):
                print(f"you cannot give a date less than date de debut")
                print("do you want to give a reason date de fin:")
                sel = input_in_list(["yes", "no"])
                if sel == "yes":
                    return self.input_check(a, b, update)
                else:
                    return -1
            else:
                return x
        else:
            return super().input_check(a, b, update)

    def save(self):
        promotions = self.product.promotions(promo_active="True")
        if promotions:
            if str_to_date(self.date_debut) < str_to_date(promotions[0].date_fin):
                print("ce product already have a promo that active")
                print('entre you choice')
                a = input_in_list(['cancel the operation','cancel the previous promotions and replace it with this'])
                if a == 'cancel the operation':
                    return -1
                else:
                    promotions[0].remove()
        super().save()

    def remove(self):
        if self.promo_active:
            pro = self.product
            pro.prix = pro.prix1
            pro.prix1 = -1
            pro.save()

    @property
    def product(self):
        return next(Product.get_all_obj_filter())

    @property
    def reduction_ratio(self):
        return (self.prix_promo/self.product.prix)*100

    @property
    def promo_active(self):
        a = str_to_date(self.date_fin) >= datetime.date.today()
        return a

# ======================================================================================================================
class Order(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "person_id": "number relation:Person<->id",
            "date_de_cammande": "date non_saisie",
            'relation_child':"non_field paiement:order_id-order_item:order_id",
            "sort":"non_field total_montant"}

    def __init__(self, person_id='', date_de_cammande=str(datetime.date.today())):
        super(Order, self).__init__()
        self.person_id = person_id
        self.date_de_cammande = date_de_cammande

    def __str__(self):
        return f"id={self.id},{self.person.type}:{self.person_id},Total montant:{self.total_montant}," \
               f",montant deja payee:{self.montant_deja_Paye},etat_livraison={self.etat_livraison}"

    @property
    def etat_livraison(self):
        l = [obj for obj in self.order_item() if obj.livraison == "livree"]
        if len(l) == len(list(self.order_item())):
            return "totalement_livree"
        elif len(l) == 0:
            return "non_livree"
        else:
            return "partialement_livree"

    @property
    def montant_deja_Paye(self):
        return sum(obj.montant for obj in self.paiement())

    @property
    def etat_paiement(self):
        if self.montant_deja_Paye == self.total_montant:
            return "totalement_payee"
        elif self.montant_deja_Paye == 0:
            return "non_payee"
        else:
            return "partialement_payee"

    @property
    def total_montant_hors_tax(self):
        return sum(obj.montant_hors_taxs for obj in self.order_item())

    @property
    def total_tva(self):
        return self.total_montant_hors_tax*self.TVA

    @property
    def total_montant(self):
        return self.total_montant_hors_tax + self.total_tva

    @property
    def person(self):
        return next(Person.get_all_obj_filter(id=self.person_id))

    def paiement(self,**kwargs):
        return Paiement.get_all_obj_filter(order_id=self.id,**kwargs)

    def order_item(self,**kwargs):
        return OrderItem.get_all_obj_filter(order_id=self.id,**kwargs)

# =====================================================================================================================

class OrderItem(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "order_id": "number relation:Order<->id",
            "product_id": "number relation:Product<->id",
            "livraison": "non_saisie choice:non_livree-livree",
            "quantity": "number",
            "sort":"non_field montant_total"}

    def __init__(self, order_id=0, product_id=0, livraison="Non_livree", quantity=0):
        super(OrderItem, self).__init__()
        self.order_id = order_id
        self.product_id = product_id
        self.livraison = livraison
        self.quantity = quantity

    def __str__(self):
        return f"id={self.id},product:{self.product.nom};quantity:{self.quantity}"

    # override the input_check methode to check for the quantity allowd to order by the client
    # but it useless as we check it in time the client added the product to the cart
    def input_check(self, a, b ,update=False):
        print(self.order.person.type)
        if str(a) == "quantity" and self.order.person.type == "client":
            x = int_input1("entre the quantity:")
            if x > self.product.quantity:
                print(f"only {self.product.quantity} left in stock")
                print("do you want to order a less quantity:")
                sel = input_in_list(["yes","no"])
                if sel == "yes":
                    return self.input_check(a, b, update)
                else:
                    return -1
            else:
                return x
        else:
            return super().input_check(a, b, update)

    # when we remove update an order we must check if the product is already consumed by the client
    # to complete the delete or update process
    def check_modifie(self):
        prod = self.product
        if self.livraison == "livree" and prod.quantity > self.quantity:
            return True
        return False

    # override the remove methode to handle the product quantity in case the order is remove
    def remove(self):
        person = self.order.person
        prod = self.product
        if person.type == "client":
            prod.quantity += self.quantity
            prod.save()
        if person.type == "fourniseur":
            if self.check_modifie():
                prod.quantity -= self.quantity
                prod.save()
            else:
                return -1
        super().remove()

    # override the save methode to handle the product quantity in in stock
    def save(self):
        person = self.order.person
        prod = self.product
        if person.type == "client":
            prod.quantity -= self.quantity
            prod.save()
        if person.type == "fourniseur":
            if self.livraison == "livree":
                prod.quantity += self.quantity
                prod.save()
        super().save()

    @property
    def order(self):
        return next(Order.get_all_obj_filter(id=self.order_id))

    @property
    def product(self):
        return next(Product.get_all_obj_filter(id=self.product_id))

    @property
    def montant_hors_taxs(self):
        return self.product.prix*self.quantity

    @property
    def montant_tva(self):
        return self.montant_hors_taxs*self.TVA

    @property
    def montant_total(self):
        return self.montant_hors_taxs+self.montant_tva

# ======================================================================================================================

class Paiement(Class_Manager):
    attr = {"id":"unique non_saisie number",
            "order_id": "number relation:Order<->id",
            "montant":"number",
            "date_payee":"date non_saisie",
            "mode_de_paiement":"choice:wire_transfere-cash"}

    def __init__(self,order_id='', montant=0,date_payee = str(datetime.date.today()), mode_de_paiement=''):
        super(Paiement, self).__init__()
        self.order_id = order_id
        self.montant = montant
        self.date_payee = date_payee
        self.mode_de_paiement = mode_de_paiement

    def __str__(self):
        return f"id={self.id},order id={self.order_id};montant={self.montant}"

    @property
    def order(self):
        return next(Order.get_all_obj_filter(id=self.order_id))

# =====================================================================================================================

# Cart class for trait cart.json
# we store in cart.json a dict that have keys client id and values a dict of the product id and quantity he order
class Cart:
    def __init__(self,person_id):
        self.person_id = person_id
        with open("cart.json",'r') as cart:
            self.cart = json.load(cart)[str(person_id)]

    def __len__(self):
        return len(self.cart)

    # it iterate trough the dict to add the product object to the value of the dict
    def __iter__(self):
        a = self.cart.copy()
        for p in a.keys():
            self.cart[str(p)]['product'] = next(Product.get_all_obj_filter(id=p))
            # if the client add it to the cart and not confirme the order
            # and other client order it it remove from the cart automatically
            if self.cart[str(p)]['quantity'] > self.cart[str(p)]['product'].quantity:
                print(f"{self.cart[str(p)]['product'].nom} is remove from cart only {self.cart[str(p)]['product'].quantity} left in stock")
                del self.cart[str(p)]
                e = Cart(self.person_id)
                e.remove(str(p))
        for item in self.cart.values():
            yield item

    # add product to cart.json
    def add(self, product_id, quantity=1):
        self.cart[str(product_id)] = {'quantity': quantity}
        self.save()

    # remove product from cart.json
    def remove(self, product_id):
        if product_id in self.cart.keys():
            del self.cart[product_id]
            self.save()

    # save in cart.json
    def save(self):
        with open("cart.json",'r') as cart:
            a = json.load(cart)
        a[str(self.person_id)] = self.cart
        with open("cart.json","w") as file:
            json.dump(a,file)

    # the total cost in the cart
    def get_total_cost(self):
        return sum(item['quantity'] * item['product'].prix for item in self)