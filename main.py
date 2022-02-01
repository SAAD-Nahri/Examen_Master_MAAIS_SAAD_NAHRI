from classes import *
import os


class Menu:
    def traiter_menu(self):
        if not (os.path.isfile(f"{Class_Manager.file_name}.json")):
            with open(f"{Class_Manager.file_name}.json", "w") as file:
                json.dump({}, file)

        print("welcome")
        L = ["1. sign in as admin",
             "2. sign in as client",
             "3. quitter le plrograme",
             ]
        while True:
            print("\n")
            afficher_list(L)
            choix = input_in_range(L)
            if choix == 1:
                self.admin_sign_in()
            elif choix == 2:
                self.client_sign_in()
            elif choix == 3:
                break

    def client_sign_in(self):
        print("Client Login")
        # username = input("Username : ")
        id = input("id : ")
        if list(Person.get_all_obj_filter(type="client", id=id)):
            print(f"welcome back {next(Person.get_all_obj_filter(type='client', id=id)).fullname}")
            self.client_session(next(Person.get_all_obj_filter(type="client", id=id)))
        else:
            print("Login details not recognised, if you have probleme sign in call the help center")

    def admin_sign_in(self):
        print("Admin Login")
        username = input("Username (root) : ")
        password = input("Password (root) : ")
        if username == "root":
            if password == "root":
                self.admin_session()
            else:
                print("Incorrect password !, if you have probleme sign in call the help center")
        else:
            print("Login details not recognised, if you have probleme sign in call the help center")

    def client_session(self,obj):
        L = ["1.show all the product",
             "2.show all the category",
             "3.search a product",
             "4.display all item in your cart, and the total cost",
             "5.add a product to the cart",
             "6.confirme the order",
             "7.payee un order",
             "8.show your statistic",
             "9.logout"]
        while True:
            # if the admin add a promotion will the client in the store
            for product in Product.get_all_obj_filter():
                product.set_prix()
            print("\n")
            afficher_list(L)
            choice = input_in_range(L)
            if choice == 1:
                # only show products that have quantity bigger than 0
                prod_list = list(Product.get_all_obj_filter(include=False,quantity=0))
                if prod_list:
                    for item in prod_list:
                        print(item)
                else:
                    print("stock empty come back later")
            elif choice == 2:
                for item in Category.get_all_obj_filter():
                    print(item)
            elif choice == 3:
                prod = input_in_list(list(Product.cherche_elem1(include=False,quantity=0)))
                if prod:
                    print(prod)
                    print("do you want to add it to your cart:")
                    if input_in_list(["yes", "no"]) == "yes":
                        obj.add_to_cart(prod.id)
                else:
                    print("no product")
            elif choice == 4:
                cart = Cart(obj.id)
                for item in cart:
                    print(str(item["product"])+"----------------quantity you order:"+str(item["quantity"]))
                print(f'total cost of order')
                while True:
                    if len(cart) > 0:
                        print("enter what do you want:")
                        a = input_in_list(
                            ['update product', "remove product", "clear the cart", "back to menu principal"])
                        if a == 'update product':
                            cart = Cart(obj.id)
                            i = int_input1("enter the id of the product")
                            if list(Product.get_all_obj_filter(id=i)):
                                if str(i) in cart.cart.keys():
                                    obj.add_to_cart(i,True)
                                else:
                                    print(f"product with id = {i} do not exist in the cart")
                        if a == "remove product":
                            i = int(input("enter the id of the product"))
                            if Product.get_all_obj_filter(id=i):
                                cart.remove(i)
                        if a == "clear the cart":
                            obj.init_cart()
                        if a == "back to menu principal":
                            break
                    else:
                        print("cart empty")
                        break
            elif choice == 5:
                i = int_input1("enter the id of the product")
                if list(Product.get_all_obj_filter(id=i)):
                    obj.add_to_cart(i)
                else:
                    print(f"no product with id={i} in the stock")
            elif choice == 6:
                obj.confirme_order_client()
            elif choice == 7:
                order = list(Order.get_all_obj_filter(person_id=obj.id))
                non_pay_order = list(order_item for order_item in order if (order_item.etat_paiement == "non_payee" or order_item.etat_paiement == "partialement_payee"))
                order = input_in_list(non_pay_order)
                if order:
                    pay = Paiement()
                    print(f"the order price is{order.total_montant}, you still have to pay {order.total_montant-order.montant_deja_Paye}")
                    pay.create_elem(order_id=order.id)
                else:
                    print("you have no order to pay")
            elif choice == 8:
                print("statistic")
                for elem in Order.get_all_obj_filter(person_id=obj.id):
                    print('--------------------------------------------------------------------------------------------')
                    print(f'order number {elem.id}, total cost {elem.total_montant}, etat_paiement {elem.etat_paiement} per unite')
                    for elem1 in elem.order_item():
                        print(f'you order {elem1.quantity} of {elem1.product.nom} with the price of {elem1.product.prix} ')
            elif choice == 9:
                print("logout")
                break

    def admin_session(self):
        L=["1.gestion des products",
           "2.gestion des clients and fourniseurs",
           "3.gestion des orders",
           "4.gestion des promotions",
           "5.show statistic",
           "6.logout"]
        while True:
            # if the promation is expire this will update the price of the product
            for product in Product.get_all_obj_filter():
                product.set_prix()
            # this will show alert of the quantity in the stock pass the seuil_de_camande
            for product in Product.get_all_obj_filter():
                if int(product.quantity) < int(product.seuil_de_camande):
                    print(f'product name {product.nom}, {product.quantity} item left in the stock wich is lower than {product.seuil_de_camande}')
            print("\n")
            afficher_list(L)
            choice = input_in_range(L)
            if choice == 1:
                self.gestion_des_products()
            elif choice == 2:
                self.gestion_des_persons()
            elif choice == 3:
                self.gestion_des_orders()
            elif choice == 4:
                self.gestion_des_promotions()
            elif choice == 5:
                self.statistic()
            elif choice == 6:
                print("logout")
                break

    def gestion_des_promotions(self):
        L = ["1.add promotion",
             "2.search promotion",
             "3.show all the promotions ",
             "4.back to menu principal",
             ]
        while True:
            print("\n")
            afficher_list(L)
            choice = input_in_range(L)
            if choice == 1:
                pro = Promotions()
                if pro.create_elem() != -1:
                    pro.save()
            elif choice == 2:
                pro = input_in_list(list(Promotions.cherche_elem1()))
                if pro:
                    print(pro)
                    while True:
                        print("enter what do you want:")
                        a = input_in_list(['update promotions', "remove promotions", "back to menu princupal"])
                        if a == 'update promotions':
                            pro.update_elem()
                        if a == "remove promotions":
                            pro.remove()
                            break
                        if a == "back to menu princupal":
                            break
                else:
                    print("nothing")
            elif choice == 3:
                if list(Promotions.get_all_obj_filter()):
                    for pro in Promotions.get_all_obj_filter():
                        print(f"promotion:{pro}")
                else:
                    print("no promotions find")
            elif choice == 4:
                print("gestion des promotions termine")
                break

    def gestion_des_products(self):
        L = ["1.add category",
             "2.search category",
             "3.add product",
             "4.search product",
             "5.show all the product group by category",
             "6.back to menu principal"]
        while True:
            print("\n")
            afficher_list(L)
            choice = input_in_range(L)
            if choice == 1:
                cat = Category()
                if cat.create_elem()!=-1:
                    cat.save()
            elif choice == 2:
                cat = input_in_list(list(Category.cherche_elem1()))
                if cat:
                    print(cat)
                    while True:
                        print("enter what do you want:")
                        a = input_in_list(['update Category', "remove Category", "back to menu princupal"])
                        if a == 'update Category':
                            cat.update_elem()
                        if a == "remove Category":
                            cat.remove()
                            break
                        if a == "back to menu princupal":
                            break
                else:
                    print("nothing")
            elif choice == 3:
                prod = Product()
                if prod.create_elem() != -1:
                    prod.save()
            elif choice == 4:
                prod = input_in_list(list(Product.cherche_elem1()))
                if prod:
                    print(prod)
                    while True:
                        print("enter what do you want:")
                        a = input_in_list(["update product","remove product", "back to menu princupal"])
                        if a == 'update product':
                            prod.update_elem()
                        if a == "remove product":
                            prod.remove()
                            break
                        if a == "back to menu princupal":
                            break
                else:
                    print("nothing")
            elif choice == 5:
                if list(Category.get_all_obj_filter()):
                    for cat in Category.get_all_obj_filter():
                        print(f"category:{cat.nom}")
                        for prod in Product.get_all_obj_filter(category_id=cat.id):
                            print(prod)
                else:
                    print("stock empty")
            elif choice == 6:
                print("gestion des product termine")
                break
    def gestion_des_persons(self):
        L = ["1.add user",
             "2.search user",
             "3.show all user",
             "4.back to menu principal"]
        while True:
            print("\n")
            afficher_list(L)
            choice = input_in_range(L)
            if choice == 1:
                user = Person()
                if user.create_elem() != -1:
                    user.save()
            elif choice == 2:
                user = input_in_list(list(Person.cherche_elem1()))
                if user:
                    print(user)
                    while True:
                        print("enter what do you want:")
                        a = input_in_list(['update user', "remove user", "back to menu gestion des user"])
                        if a == 'update user':
                            user.update_elem()
                        if a == "remove user":
                            user.remove()
                            break
                        if a == "back to menu gestion des user":
                            break
                else:
                    print("nothing")
            elif choice == 3:
                for type in ["client", "fourniseur"]:
                    print(f"user:{type}")
                    if list(Person.get_all_obj_filter(type=type)):
                        for user in Person.get_all_obj_filter(type=type):
                            print(user)
                    else:
                        print(f"no {type} created yet")
            elif choice == 4:
                print("gestion des user termine")
                break
    def gestion_des_orders(self):
        L = ["1.pass un order chez fourniseurs",
             "2.search order d'un client",
             "3.search order d'un fourniseurs",
             "4.show all order",
             "5.back to menu principal"]
        while True:
            print("\n")
            afficher_list(L)
            choice = input_in_range(L)
            if choice == 1:
                p_id = int_input1("donner id de fourniseurs")
                if list(Person.get_all_obj_filter(id=p_id, type="fourniseur")):
                    Person.pass_order_fourniseur(p_id)
                else:
                    print("invalide ID")
            elif choice == 2:
                order = list(Order.cherche_elem1(person___type="client"))
                if order:
                    order = input_in_list(order)
                    print(order)
                    while True:
                        print("enter what do you want:")
                        lis = ['traiter item of order', "mark the order as livree","remove order","back to menu princupal"]
                        if order.etat_livraison == "livree":
                            del lis[1]
                        a = input_in_list(lis)
                        if a == 'traiter item of order':
                            while True:
                                if len(list(order.order_item())) > 1:
                                    print("select order item that you want to traiter")
                                order_item = input_in_list(list(order.order_item()))
                                if order_item:
                                    print(order_item)
                                    li = ['update order item', "remove order item","mark an item of order as livree","back to menu traiter order"]
                                    if order_item.livraison == "livree":
                                        del li[2]
                                    b = input_in_list(li)
                                    if b == 'update order item':
                                        order_item.update_elem()
                                    if b == "remove order item":
                                        order_item.remove()
                                        break
                                    if b == "mark the item as livree":
                                        order_item.livraison = "livree"
                                    if b == "back to menu princupal":
                                        break
                        if a == "mark the order as livree":
                            for item in OrderItem.get_all_obj_filter(order_id=order.id):
                                item.livraison = "livree"
                        if a == "remove order":
                            for item in OrderItem.get_all_obj_filter(order_id=order.id):
                                item.remove()
                            order.remove()
                            break
                        if a == "back to menu traiter order":
                            break
                else:
                    print("ce client have no order")
            elif choice == 3:
                order = list(Order.cherche_elem1(person___type="fourniseur"))
                if order:
                    order = input_in_list(order)
                    while True:
                        print("enter what do you want:")
                        li = ['traiter item of order', "mark the order as livree", "remove order",
                              "pay the order", "back to menu traiter order"]
                        if order.etat_livraison == "livree":
                            del li[1]
                        a = input_in_list(li)
                        if a == 'traiter item of order':
                            while True:
                                if len(list(order.order_item())) > 1: print("select order item that you want to traiter")
                                order_item = input_in_list(list(order.order_item()))
                                lis = ['update order item', "remove order item", "mark an item of order as livree",
                                     "back to menu traiter order item"]
                                if order_item.livraison == "livree":
                                    del lis[2]
                                b = input_in_list(lis)
                                if b == 'update order item':
                                    if order_item.update_elem() == -1:
                                        print("this order already bought by some clients, you can not update it make a new one if you want")
                                        del lis[0]
                                if b == "remove order item":
                                    if order_item.remove() == -1:
                                        print("this order item already bought by some clients, you can not remove it make a new one if you want")
                                        del lis[1]
                                    else:
                                        break
                                if b == "mark the item as livree":
                                    order_item.livraison = "livree"
                                    order_item.product.quantity += order_item.quantity
                                    del lis[2]
                                if b == "back to menu traiter order item":
                                    break
                        if a == "mark the order as livree":
                            for item in OrderItem.get_all_obj_filter(order_id=order.id):
                                item.livraison = "livree"
                                item.save()
                                del li[1]
                        if a == "remove order":
                            item_id = []
                            for item in OrderItem.get_all_obj_filter(order_id=order.id):
                                # check if it can be deleted
                                if item.check_modifie():
                                    item_id.append(item.id)
                            if item_id:
                                print(f"order item number {item_id} can't removed the products is already consumed")
                                del li[2]
                                continue
                            for item in OrderItem.get_all_obj_filter(order_id=order.id):
                                item.remove()
                        if a == "pay the order":
                            pay = Paiement()
                            if pay.create_elem() != -1:
                                pay.save()
                        if a == "back to menu traiter order":
                            break
                else:
                    print("ce fourniseurs have no order")
            elif choice == 4:
                order = list(Order.get_all_obj_filter())
                if order:
                    for elem in order:
                        print(elem)
                else:
                    print("no order")
            elif choice == 5:
                print("gestion des order termine")
                break
    def statistic(self):
        print("do you want to add a date filter:")
        x = input_in_list(["yes","no"])
        if x == "yes":
            start_date = str_to_date(saisir_date("enter the start date"))
            end_date = str_to_date(saisir_date("enter the end date"))
        else:
            start_date = datetime.date(1111,12,12)
            end_date = datetime.date(9999,12,12)

        print(f"number des client est {len(list(Person.get_all_obj_filter(type='client',date_added__=[start_date,end_date])))}")

        n = len(list(x for x in Order.get_all_obj_filter(person___type='client',date_de_cammande__=[start_date,end_date])))
        print(f"number des command est {n}")

        print(f"""number des command livree est {len(list(Order.get_all_obj_filter(
            person___type='client',date_de_cammande__=[start_date,end_date],etat_livraison='livree')))}""")

        print(f"""number des command totalement payee est \
        {len(list(Order.get_all_obj_filter(
            person___type='client',date_de_cammande__=[start_date,end_date],etat_paiement='totalement_payee')))}""")

        print(f"""number des command livree et non payee est \
        {len(list(Order.get_all_obj_filter(
            person___type='client',date_de_cammande__=[start_date,end_date],etat_paiement='non_payee', etat_livraison='livree')))}""")

        print(f"""chiffre d'affaire global est \
        {sum(x.total_montant for x in Order.get_all_obj_filter(
            person___type='client',date_de_cammande__=[start_date,end_date]))}""")

        print(f"""chiffre d'affaire global encaisse est \
        {sum(x.montant_deja_Paye for x in Order.get_all_obj_filter(
            person___type='client',date_de_cammande__=[start_date,end_date]))}""")

        if n != 0:
            print(f"""Le panier moyen est \
            {sum(x.total_montant for x in Order.get_all_obj_filter(
                person___type='client',date_de_cammande__=[start_date,end_date]))*(1/n)}""")

        print(f"""les categories les plus vendue est:\
        {list(filter(lambda x:x[1]!=0,sorted(((x.nom, sum(sum(y.quantity for y in t.order_item(
        order___date_de_cammande__=[start_date,end_date]) if y.order.person.type == "client") 
        for t in x.product())) for x in Category.get_all_obj_filter()), reverse=True, key=lambda x: x[1])))[:5]}""")


        print(f"""les categories ayant apportée le plus d'argent est \
        {list(filter(lambda x:x[1]!=0,sorted(((x.nom, sum(sum(y.montant_total for y in t.order_item(order___date_de_cammande__=[start_date,end_date])
        if y.order.person.type == "client") for t in x.product())) for x in Category.get_all_obj_filter()), 
                reverse=True, key=lambda x: x[1])))[:5]}""")

        print(f"""les product les plus vendue est \
        {list(filter(lambda x:x[1]!=0,sorted(((x.nom, sum(y.quantity for y in x.order_item(order___date_de_cammande__=[start_date,end_date]) 
        if y.order.person.type == "client")) for x in Product.get_all_obj_filter()), 
                reverse=True, key=lambda x: x[1])))[:5]}""")

        print(f"""les product ayant apportée le plus d'argent est \
        {list(filter(lambda x:x[1]!=0,sorted(((x.nom, sum(y.montant_total for y in x.order_item(order___date_de_cammande__=[start_date,end_date])
        if y.order.person.type == "client")) for x in Product.get_all_obj_filter()),
                reverse=True, key=lambda x: x[1])))[:5]}""")

        print(f"""La liste des clients qui n'ont pas encore payé leurs factures \
        {sorted(((x.fullname, x.montant_rest_a_payee) for x in Person.get_all_obj_filter(type='client')
        if x.montant_rest_a_payee != 0), reverse=True, key=lambda x: x[1])[:5]}""")

        print(f"""La liste des clients ayant tout payé \
        {list(x.fullname for x in Person.get_all_obj_filter(type='client',montant_rest_a_payee=0))}""")

        print(f"""La liste des clients ayant effectué le plus de commandes \
        {sorted(((x.fullname, len(list(x.order())))
                 for x in Person.get_all_obj_filter(type='client')), reverse=True, key=lambda x: x[1])[:5]}""")

        print(f"""La liste des clients ayant le meilleur chiffre d'affaires \
        {list(filter(lambda x:x[1]!=0,sorted(((x.fullname, sum(y.total_montant for y in x.order()))
                 for x in Person.get_all_obj_filter(type='client')), reverse=True, key=lambda x: x[1])))[:5]}""")

if __name__ == '__main__':
    M = Menu()
    M.traiter_menu()
