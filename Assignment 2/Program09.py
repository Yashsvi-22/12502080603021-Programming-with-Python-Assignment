
class Product:
    def __init__(self, product_id, name, stock, purchase_price, selling_price):
        self.product_id = product_id
        self.name = name
        self.stock = stock
        self.purchase_price = purchase_price
        self.selling_price = selling_price

    def total_value(self):
        return self.stock * self.purchase_price


class Inventory:
    def __init__(self, filename=None):
        self.products = {}

        if filename:
            self.load_from_file(filename)

    def add_product(self, product):
        if product.product_id in self.products:
            print("Product ID already exists!")
        else:
            self.products[product.product_id] = product
            print("Product added successfully.")

    def delete_product(self, product_id):
        if product_id in self.products:
            del self.products[product_id]
            print("Product deleted successfully.")
        else:
            print("Product not found.")

    def update_stock(self, product_id, new_stock):
        if product_id in self.products:
            self.products[product_id].stock = new_stock
            print("Stock updated successfully.")
        else:
            print("Product not found.")

    def total_valuation(self):
        return sum(p.total_value() for p in self.products.values())

    def compare(self, other):
        value1 = self.total_valuation()
        value2 = other.total_valuation()

        if value1 > value2:
            print("First inventory has higher total value.")
        elif value1 < value2:
            print("Second inventory has higher total value.")
        else:
            print("Both inventories have equal total value.")

    def __add__(self, other):
        merged = Inventory()

        for product_id, product in self.products.items():
            merged.products[product_id] = Product(
                product.product_id,
                product.name,
                product.stock,
                product.purchase_price,
                product.selling_price
            )

        for product_id, product in other.products.items():
            if product_id in merged.products:
                existing = merged.products[product_id]
                existing.stock += product.stock
                existing.purchase_price = min(
                    existing.purchase_price, product.purchase_price
                )
                existing.selling_price = max(
                    existing.selling_price, product.selling_price
                )
            else:
                merged.products[product_id] = Product(
                    product.product_id,
                    product.name,
                    product.stock,
                    product.purchase_price,
                    product.selling_price
                )

        return merged

    def load_from_file(self, filename):
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split()

                    if len(parts) != 5:
                        continue

                    product_id, name, stock, purchase, selling = parts

                    self.products[product_id] = Product(
                        product_id,
                        name,
                        int(stock),
                        int(purchase),
                        int(selling)
                    )
        except FileNotFoundError:
            print(f"File '{filename}' not found.")

    def save_to_file(self, filename):
        with open(filename, "w", encoding="utf-8") as file:
            for p in self.products.values():
                file.write(
                    f"{p.product_id} {p.name} {p.stock} "
                    f"{p.purchase_price} {p.selling_price}\n"
                )

    def display(self):
        if not self.products:
            print("Inventory is empty.")
            return

        for p in self.products.values():
            print(
                f"{p.product_id} {p.name} stock={p.stock} "
                f"purchase={p.purchase_price} "
                f"selling={p.selling_price}"
            )

        print("Total valuation:", self.total_valuation())


def main():
    inventory_a = Inventory("inventory_a.txt")
    inventory_b = Inventory("inventory_b.txt")

    while True:
        print("\n--- INVENTORY MANAGEMENT ---")
        print("1. Add product to Inventory A")
        print("2. Delete product from Inventory A")
        print("3. Update stock in Inventory A")
        print("4. Merge inventories")
        print("5. Compare inventories")
        print("6. Display Inventory A")
        print("7. Display Inventory B")
        print("8. Save inventories")
        print("9. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            product_id = input("Product ID: ")
            name = input("Product name (one word): ")
            stock = int(input("Stock quantity: "))
            purchase = int(input("Purchase price: "))
            selling = int(input("Selling price: "))

            inventory_a.add_product(
                Product(product_id, name, stock, purchase, selling)
            )

        elif choice == "2":
            product_id = input("Product ID to delete: ")
            inventory_a.delete_product(product_id)

        elif choice == "3":
            product_id = input("Product ID: ")
            new_stock = int(input("New stock quantity: "))
            inventory_a.update_stock(product_id, new_stock)

        elif choice == "4":
            merged = inventory_a + inventory_b
            print("\n--- MERGED INVENTORY ---")
            merged.display()
            merged.save_to_file("merged_inventory.txt")

        elif choice == "5":
            inventory_a.compare(inventory_b)

        elif choice == "6":
            inventory_a.display()

        elif choice == "7":
            inventory_b.display()

        elif choice == "8":
            inventory_a.save_to_file("inventory_a.txt")
            inventory_b.save_to_file("inventory_b.txt")
            print("Inventories saved successfully.")

        elif choice == "9":
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
