#!/usr/bin/env python3
"""
Database initialization script for Clean Architecture.
This script creates the database tables and initializes with sample data.
"""

import sys

from pathlib import Path

# Add the parent directory to Python path for imports
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

# Import after path setup to avoid E402 errors
from src.config.database import db_config  # noqa: E402
from src.adapters.di.container import container  # noqa: E402
from src.entities.customer import Customer  # noqa: E402
from src.entities.ingredient import Ingredient, IngredientType  # noqa: E402
from src.entities.product import Product, ProductCategory, ProductReceiptItem  # noqa: E402
from src.entities.order import Order, OrderItem  # noqa: E402
from src.entities.value_objects.money import Money  # noqa: E402
from src.entities.value_objects.sku import SKU  # noqa: E402


def init_database():
    """Initialize the database with tables and basic data"""
    print(f"Connecting to database: {db_config}")

    try:
        repository = container.customer_repository

        # Get or create anonymous customer
        anonymous_customer = repository.get_anonymous_customer()
        print(f"Anonymous customer created/found: {anonymous_customer}")

        print("Database initialization completed successfully!")

    except Exception as e:
        print(f"Error initializing database: {e}")
        sys.exit(1)


def create_sample_customers():
    """Create sample customer data"""
    print("Creating sample data...")

    try:
        repository = container.customer_repository

        # Create sample customers
        sample_customers = [
            {
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@example.com",
                "document": "98765432100",
            }
        ]

        for customer_data in sample_customers:
            # Check if customer already exists by email
            if repository.exists_by_email(customer_data["email"]):
                print(f"Customer with email {customer_data['email']} already exists, skipping...")
                continue
                
            # Check if customer already exists by document
            if repository.exists_by_document(customer_data["document"]):
                print(f"Customer with document {customer_data['document']} already exists, skipping...")
                continue

            customer = Customer.create_registered(
                first_name=customer_data["first_name"],
                last_name=customer_data["last_name"],
                email=customer_data["email"],
                document=customer_data["document"],
            )
            saved_customer = repository.save(customer)
            print(f"Created customer: {saved_customer.full_name}")

        print("Sample data creation completed!")

    except Exception as e:
        print(f"Error creating sample data: {e}")
        sys.exit(1)


def create_sample_ingredients():
    """Create sample ingredient data"""
    print("Creating sample ingredients...")

    try:
        repository = container.ingredient_repository

        # Create sample ingredients
        sample_ingredients = [
            # Bread ingredients (for burgers)
            {
                "name": "Classic Bun",
                "price": Money.create(2.50),
                "is_active": True,
                "type": IngredientType.BREAD,
                "applies_to_burger": True,
                "applies_to_side": False,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            {
                "name": "Whole Wheat Bun",
                "price": Money.create(3.00),
                "is_active": True,
                "type": IngredientType.BREAD,
                "applies_to_burger": True,
                "applies_to_side": False,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            # Meat ingredients (for burgers)
            {
                "name": "Beef Patty",
                "price": Money.create(8.00),
                "is_active": True,
                "type": IngredientType.MEAT,
                "applies_to_burger": True,
                "applies_to_side": False,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            {
                "name": "Chicken Breast",
                "price": Money.create(7.50),
                "is_active": True,
                "type": IngredientType.MEAT,
                "applies_to_burger": True,
                "applies_to_side": False,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            {
                "name": "Veggie Patty",
                "price": Money.create(6.50),
                "is_active": True,
                "type": IngredientType.MEAT,
                "applies_to_burger": True,
                "applies_to_side": False,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            # Cheese ingredients (for burgers)
            {
                "name": "Cheddar Cheese",
                "price": Money.create(1.50),
                "is_active": True,
                "type": IngredientType.CHEESE,
                "applies_to_burger": True,
                "applies_to_side": False,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            {
                "name": "Swiss Cheese",
                "price": Money.create(1.75),
                "is_active": True,
                "type": IngredientType.CHEESE,
                "applies_to_burger": True,
                "applies_to_side": False,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            # Vegetable ingredients (for burgers)
            {
                "name": "Lettuce",
                "price": Money.create(0.50),
                "is_active": True,
                "type": IngredientType.VEGETABLE,
                "applies_to_burger": True,
                "applies_to_side": True,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            {
                "name": "Tomato",
                "price": Money.create(0.75),
                "is_active": True,
                "type": IngredientType.VEGETABLE,
                "applies_to_burger": True,
                "applies_to_side": True,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            {
                "name": "Onion",
                "price": Money.create(0.50),
                "is_active": True,
                "type": IngredientType.VEGETABLE,
                "applies_to_burger": True,
                "applies_to_side": True,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            # Salad ingredients (for burgers and sides)
            {
                "name": "Mixed Greens",
                "price": Money.create(1.00),
                "is_active": True,
                "type": IngredientType.SALAD,
                "applies_to_burger": True,
                "applies_to_side": True,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            # Sauce ingredients (for burgers and sides)
            {
                "name": "Ketchup",
                "price": Money.create(0.25),
                "is_active": True,
                "type": IngredientType.SAUCE,
                "applies_to_burger": True,
                "applies_to_side": True,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            {
                "name": "Mustard",
                "price": Money.create(0.25),
                "is_active": True,
                "type": IngredientType.SAUCE,
                "applies_to_burger": True,
                "applies_to_side": True,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            {
                "name": "Mayonnaise",
                "price": Money.create(0.30),
                "is_active": True,
                "type": IngredientType.SAUCE,
                "applies_to_burger": True,
                "applies_to_side": True,
                "applies_to_drink": False,
                "applies_to_dessert": False,
            },
            # Ice ingredients (for drinks)
            {
                "name": "Ice Cubes",
                "price": Money.create(0.10),
                "is_active": True,
                "type": IngredientType.ICE,
                "applies_to_burger": False,
                "applies_to_side": False,
                "applies_to_drink": True,
                "applies_to_dessert": False,
            },
            # Milk ingredients (for drinks)
            {
                "name": "Whole Milk",
                "price": Money.create(1.00),
                "is_active": True,
                "type": IngredientType.MILK,
                "applies_to_burger": False,
                "applies_to_side": False,
                "applies_to_drink": True,
                "applies_to_dessert": False,
            },
            {
                "name": "Almond Milk",
                "price": Money.create(1.50),
                "is_active": True,
                "type": IngredientType.MILK,
                "applies_to_burger": False,
                "applies_to_side": False,
                "applies_to_drink": True,
                "applies_to_dessert": False,
            },
            # Topping ingredients (for desserts)
            {
                "name": "Chocolate Sprinkles",
                "price": Money.create(0.75),
                "is_active": True,
                "type": IngredientType.TOPPING,
                "applies_to_burger": False,
                "applies_to_side": False,
                "applies_to_drink": False,
                "applies_to_dessert": True,
            },
            {
                "name": "Whipped Cream",
                "price": Money.create(0.50),
                "is_active": True,
                "type": IngredientType.TOPPING,
                "applies_to_burger": False,
                "applies_to_side": False,
                "applies_to_drink": False,
                "applies_to_dessert": True,
            },
        ]

        for ingredient_data in sample_ingredients:
            # Check if ingredient already exists by name
            if repository.exists_by_name(ingredient_data["name"]):
                print(f"Ingredient '{ingredient_data['name']}' already exists, skipping...")
                continue

            ingredient = Ingredient.create(
                name=ingredient_data["name"],
                price=ingredient_data["price"],
                is_active=ingredient_data["is_active"],
                type=ingredient_data["type"],
                applies_to_burger=ingredient_data["applies_to_burger"],
                applies_to_side=ingredient_data["applies_to_side"],
                applies_to_drink=ingredient_data["applies_to_drink"],
                applies_to_dessert=ingredient_data["applies_to_dessert"],
            )
            saved_ingredient = repository.save(ingredient)
            print(f"Created ingredient: {saved_ingredient.name} ({saved_ingredient.type}) - ${saved_ingredient.price}")

        print("Sample ingredients creation completed!")

    except Exception as e:
        print(f"Error creating sample ingredients: {e}")
        sys.exit(1)


def create_sample_products():
    """Create sample product data"""
    print("Creating sample products...")

    try:
        repository = container.product_repository
        ingredient_repository = container.ingredient_repository

        # Get existing ingredients to use in products
        all_ingredients = ingredient_repository.find_all()
        
        # Create ingredient lookup by name for easier reference
        ingredient_lookup = {ingredient.name.value: ingredient for ingredient in all_ingredients}
        
        # Verify all required ingredients exist
        required_ingredients = [
            "Classic Bun", "Whole Wheat Bun", "Beef Patty", "Chicken Breast", "Veggie Patty",
            "Cheddar Cheese", "Swiss Cheese", "Lettuce", "Tomato", "Onion", "Mixed Greens",
            "Ketchup", "Mustard", "Mayonnaise", "Ice Cubes", "Whole Milk", "Almond Milk",
            "Chocolate Sprinkles", "Whipped Cream"
        ]
        
        missing_ingredients = []
        for ingredient_name in required_ingredients:
            if ingredient_name not in ingredient_lookup:
                missing_ingredients.append(ingredient_name)
        
        if missing_ingredients:
            print(f"Warning: Missing ingredients: {missing_ingredients}")
            print("Please run create_sample_ingredients() first to ensure all ingredients exist.")
            return

        # Create sample products using valid test data structure
        sample_products = [
            # Burger products
            {
                "name": "Classic Burger",
                "price": Money.create(12.99),
                "category": ProductCategory.BURGER,
                "sku": SKU.create("BURG-2024-CLS"),
                "default_ingredient": [
                    ProductReceiptItem(ingredient_lookup["Classic Bun"], 1),
                    ProductReceiptItem(ingredient_lookup["Beef Patty"], 1),
                    ProductReceiptItem(ingredient_lookup["Cheddar Cheese"], 1),
                    ProductReceiptItem(ingredient_lookup["Lettuce"], 1),
                    ProductReceiptItem(ingredient_lookup["Tomato"], 1),
                    ProductReceiptItem(ingredient_lookup["Ketchup"], 1),
                ],
                "is_active": True,
            },
            {
                "name": "Chicken Burger",
                "price": Money.create(11.99),
                "category": ProductCategory.BURGER,
                "sku": SKU.create("BURG-2024-CHK"),
                "default_ingredient": [
                    ProductReceiptItem(ingredient_lookup["Classic Bun"], 1),
                    ProductReceiptItem(ingredient_lookup["Chicken Breast"], 1),
                    ProductReceiptItem(ingredient_lookup["Swiss Cheese"], 1),
                    ProductReceiptItem(ingredient_lookup["Lettuce"], 1),
                    ProductReceiptItem(ingredient_lookup["Onion"], 1),
                    ProductReceiptItem(ingredient_lookup["Mayonnaise"], 1),
                ],
                "is_active": True,
            },
            {
                "name": "Veggie Burger",
                "price": Money.create(10.99),
                "category": ProductCategory.BURGER,
                "sku": SKU.create("BURG-2024-VEG"),
                "default_ingredient": [
                    ProductReceiptItem(ingredient_lookup["Whole Wheat Bun"], 1),
                    ProductReceiptItem(ingredient_lookup["Veggie Patty"], 1),
                    ProductReceiptItem(ingredient_lookup["Cheddar Cheese"], 1),
                    ProductReceiptItem(ingredient_lookup["Mixed Greens"], 1),
                    ProductReceiptItem(ingredient_lookup["Tomato"], 1),
                    ProductReceiptItem(ingredient_lookup["Mustard"], 1),
                ],
                "is_active": True,
            },
            # Side products
            {
                "name": "Fresh Salad",
                "price": Money.create(5.99),
                "category": ProductCategory.SIDE,
                "sku": SKU.create("SIDE-2024-SAL"),
                "default_ingredient": [
                    ProductReceiptItem(ingredient_lookup["Mixed Greens"], 1),
                    ProductReceiptItem(ingredient_lookup["Tomato"], 1),
                    ProductReceiptItem(ingredient_lookup["Onion"], 1),
                    ProductReceiptItem(ingredient_lookup["Ketchup"], 1),
                ],
                "is_active": True,
            },
            {
                "name": "Garden Salad",
                "price": Money.create(6.99),
                "category": ProductCategory.SIDE,
                "sku": SKU.create("SIDE-2024-GRD"),
                "default_ingredient": [
                    ProductReceiptItem(ingredient_lookup["Mixed Greens"], 1),
                    ProductReceiptItem(ingredient_lookup["Lettuce"], 1),
                    ProductReceiptItem(ingredient_lookup["Tomato"], 1),
                    ProductReceiptItem(ingredient_lookup["Onion"], 1),
                    ProductReceiptItem(ingredient_lookup["Mayonnaise"], 1),
                ],
                "is_active": True,
            },
            # Drink products
            {
                "name": "Milk Shake",
                "price": Money.create(4.99),
                "category": ProductCategory.DRINK,
                "sku": SKU.create("DRNK-2024-MLK"),
                "default_ingredient": [
                    ProductReceiptItem(ingredient_lookup["Whole Milk"], 1),
                    ProductReceiptItem(ingredient_lookup["Ice Cubes"], 1),
                ],
                "is_active": True,
            },
            {
                "name": "Almond Milk Shake",
                "price": Money.create(5.99),
                "category": ProductCategory.DRINK,
                "sku": SKU.create("DRNK-2024-ALM"),
                "default_ingredient": [
                    ProductReceiptItem(ingredient_lookup["Almond Milk"], 1),
                    ProductReceiptItem(ingredient_lookup["Ice Cubes"], 1),
                ],
                "is_active": True,
            },
            # Dessert products
            {
                "name": "Ice Cream Sundae",
                "price": Money.create(6.99),
                "category": ProductCategory.DESSERT,
                "sku": SKU.create("DSSR-2024-ICE"),
                "default_ingredient": [
                    ProductReceiptItem(ingredient_lookup["Chocolate Sprinkles"], 1),
                    ProductReceiptItem(ingredient_lookup["Whipped Cream"], 1),
                ],
                "is_active": True,
            },
            {
                "name": "Chocolate Sundae",
                "price": Money.create(7.99),
                "category": ProductCategory.DESSERT,
                "sku": SKU.create("DSSR-2024-CHO"),
                "default_ingredient": [
                    ProductReceiptItem(ingredient_lookup["Chocolate Sprinkles"], 2),
                    ProductReceiptItem(ingredient_lookup["Whipped Cream"], 1),
                ],
                "is_active": True,
            },
        ]

        for product_data in sample_products:
            # Check if product already exists by SKU
            if repository.exists_by_sku(product_data["sku"]):
                print(f"Product with SKU {product_data['sku']} already exists, skipping...")
                continue
                
            # Check if product already exists by name
            if repository.exists_by_name(product_data["name"]):
                print(f"Product '{product_data['name']}' already exists, skipping...")
                continue

            try:
                product = Product.create(
                    name=product_data["name"],
                    price=product_data["price"],
                    category=product_data["category"],
                    sku=product_data["sku"],
                    default_ingredient=product_data["default_ingredient"],
                    is_active=product_data["is_active"],
                )
                saved_product = repository.save(product)
                print(f"Created product: {saved_product.name.value} ({saved_product.category}) - ${saved_product.price}")
            except Exception as e:
                print(f"Failed to create product {product_data['name']}: {e}")
                continue

        print("Sample products creation completed!")

    except Exception as e:
        print(f"Error creating sample products: {e}")
        sys.exit(1)


def create_sample_orders():
    """Create sample order data"""
    print("Creating sample orders...")

    try:
        repository = container.order_repository
        customer_repository = container.customer_repository
        product_repository = container.product_repository
        ingredient_repository = container.ingredient_repository

        # Get existing customers, products, and ingredients
        print("Retrieving existing data from database...")
        customers = customer_repository.find_all()
        products = product_repository.find_all()
        ingredients = ingredient_repository.find_all()
        
        print(f"Found {len(customers)} customers, {len(products)} products, {len(ingredients)} ingredients")
        
        if not customers:
            print("Warning: No customers found. Please run create_sample_customers() first.")
            return
            
        if not products:
            print("Warning: No products found. Please run create_sample_products() first.")
            return
            
        if not ingredients:
            print("Warning: No ingredients found. Please run create_sample_ingredients() first.")
            return

        # Create ingredient lookup by name for easier reference
        ingredient_lookup = {ingredient.name.value: ingredient for ingredient in ingredients}
        print(f"Available ingredients: {list(ingredient_lookup.keys())}")
        
        # Create product lookup by name for easier reference
        product_lookup = {product.name.value: product for product in products}
        print(f"Available products: {list(product_lookup.keys())}")
        
        # Define the sample orders with required products and ingredients
        sample_orders_config = [
            {
                "description": "Classic Burger Order",
                "required_products": ["Classic Burger"],
                "required_ingredients": ["Swiss Cheese", "Onion", "Tomato"],
                "items": [
                    {
                        "product_name": "Classic Burger",
                        "additional_ingredients": ["Swiss Cheese", "Onion"],
                        "remove_ingredients": ["Tomato"]
                    }
                ]
            },
            {
                "description": "Multiple Items Order",
                "required_products": ["Chicken Burger", "Milk Shake", "Fresh Salad"],
                "required_ingredients": ["Cheddar Cheese", "Mustard"],
                "items": [
                    {
                        "product_name": "Chicken Burger",
                        "additional_ingredients": ["Cheddar Cheese"],
                        "remove_ingredients": []
                    },
                    {
                        "product_name": "Milk Shake",
                        "additional_ingredients": [],
                        "remove_ingredients": []
                    },
                    {
                        "product_name": "Fresh Salad",
                        "additional_ingredients": ["Mustard"],
                        "remove_ingredients": []
                    }
                ]
            },
            {
                "description": "Veggie Order",
                "required_products": ["Veggie Burger", "Almond Milk Shake"],
                "required_ingredients": ["Lettuce", "Onion"],
                "items": [
                    {
                        "product_name": "Veggie Burger",
                        "additional_ingredients": ["Lettuce", "Onion"],
                        "remove_ingredients": []
                    },
                    {
                        "product_name": "Almond Milk Shake",
                        "additional_ingredients": [],
                        "remove_ingredients": []
                    }
                ]
            }
        ]
        
        # Validate all required products and ingredients exist
        for order_config in sample_orders_config:
            missing_products = [name for name in order_config["required_products"] if name not in product_lookup]
            if missing_products:
                print(f"Warning: Missing products for {order_config['description']}: {missing_products}")
                continue
                
            missing_ingredients = [name for name in order_config["required_ingredients"] if name not in ingredient_lookup]
            if missing_ingredients:
                print(f"Warning: Missing ingredients for {order_config['description']}: {missing_ingredients}")
                continue
        
        # Create orders using the first available customer
        customer = customers[0]
        print(f"Using customer: {customer.full_name} (internal_id: {customer.internal_id})")
        
        orders_created = 0
        for order_config in sample_orders_config:
            try:
                # Validate this specific order can be created
                missing_products = [name for name in order_config["required_products"] if name not in product_lookup]
                missing_ingredients = [name for name in order_config["required_ingredients"] if name not in ingredient_lookup]
                
                if missing_products or missing_ingredients:
                    print(f"Skipping {order_config['description']} - missing dependencies")
                    continue
                
                # Create order items
                order_items = []
                for item_config in order_config["items"]:
                    product = product_lookup[item_config["product_name"]]
                    
                    # Get additional ingredients
                    additional_ingredients = []
                    for ingredient_name in item_config["additional_ingredients"]:
                        if ingredient_name in ingredient_lookup:
                            additional_ingredients.append(ingredient_lookup[ingredient_name])
                    
                    # Get remove ingredients
                    remove_ingredients = []
                    for ingredient_name in item_config["remove_ingredients"]:
                        if ingredient_name in ingredient_lookup:
                            remove_ingredients.append(ingredient_lookup[ingredient_name])
                    
                    # Create order item
                    order_item = OrderItem(
                        order_internal_id=0,  # Will be set when order is saved
                        product=product,
                        additional_ingredient=additional_ingredients,
                        remove_ingredient=remove_ingredients
                    )
                    order_items.append(order_item)

                # Create order
                order = Order.create(
                    customer_internal_id=customer.internal_id,
                    order_items=order_items
                )
                
                # Set start date
                order.set_start_date()
                
                # Save order
                saved_order = repository.create(order)
                print(f"Created order: {order_config['description']} - ${saved_order.value.value} - {saved_order.get_total_items()} items")
                orders_created += 1
                
            except Exception as e:
                print(f"Failed to create order {order_config['description']}: {e}")
                continue

        print(f"Sample orders creation completed! Created {orders_created} orders.")

    except Exception as e:
        print(f"Error creating sample orders: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Initialize database
    init_database()

    # Create sample data if requested
    if "--sample-data" in sys.argv:
        print("Creating sample data in the correct order...")
        create_sample_customers()
        create_sample_ingredients()
        create_sample_products()
        create_sample_orders()
        print("Sample data creation completed!")
    elif "--ingredients-only" in sys.argv:
        print("Creating only ingredients...")
        create_sample_ingredients()
        print("Ingredients creation completed!")
    elif "--products-only" in sys.argv:
        print("Creating only products...")
        create_sample_products()
        print("Products creation completed!")
    elif "--orders-only" in sys.argv:
        print("Creating only orders...")
        create_sample_orders()
        print("Orders creation completed!")
    else:
        print("Database initialized. Use --sample-data to create sample data.")
        print("Use --ingredients-only to create only ingredients.")
        print("Use --products-only to create only products.")
        print("Use --orders-only to create only orders.")
