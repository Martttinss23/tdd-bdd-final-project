# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import logging
import os
import unittest

from decimal import Decimal

from service import app
from service.models import db, Category, Product
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """It should Read a product"""
        # 1.Create a Product object using the ProductFactory
        product = ProductFactory()
        # 2.Add a log message displaying the product for debugging errors
        app.logger.debug(str(product))
        # 3.Set the ID of the product object to None and then create the product.
        product.id = None
        product.create()
        # 4.Assert that the product ID is not None
        self.assertIsNotNone(product.id)
        # 5.Fetch the product back from the database
        found_product = Product.find(product.id)
        # 6.Assert the properties of the found product are correct
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a Product"""
        # 1.Create a Product object using the ProductFactory
        product = ProductFactory()
        # 2.Add a log message displaying the product for debugging errors
        app.logger.debug(str(product))
        # 3. Set the ID of the product object to None and create the product.
        product.id = None
        product.create()
        # 4.Log the product object again after it has been created to verify
        #  that the product was created with the desired properties.
        app.logger.debug(str(product))
        # 5.Update the description property of the product object.
        new_description_str = "New description"
        product.description = new_description_str
        original_id = product.id
        product.update()
        # 6.Assert that that the id and description properties of the product object have been updated correctly.
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, new_description_str)
        # 7.Fetch all products from the database to verify that after updating the product,
        #  there is only one product in the system.
        products = Product.all()
        self.assertEqual(len(products), 1)
        # 8.Assert that the fetched product has the original id but updated description.
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, new_description_str)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        # 1.Create a Product object using the ProductFactory and save it to the database.
        product = ProductFactory()
        # 2.Assert that after creating a product and saving it to the database, there is only one product in the system.
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # 3.Remove the product from the database.
        product.delete()
        # 4.Assert if the product has been successfully deleted from the database.
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products"""
        # 1.Retrieve all products from the database and assign them to the products variable.
        products = Product.all()
        # 2.Assert there are no products in the database at the beginning of the test case.
        self.assertEqual(len(products), 0)
        # 3.Create five products and save them to the database.
        nr_products = 5
        for _ in range(nr_products):
            product = ProductFactory()
            product.create()
        # 4.Fetching all products from the database again and assert the count is 5
        self.assertEqual(len(Product.all()), nr_products)

    def test_find_product_by_name(self):
        """It should Find a Product by Name"""
        # 1.Create a batch of 5 Product objects using the ProductFactory and save them to the database.
        nr_products = 5
        products = ProductFactory.create_batch(nr_products)
        for product in products:
            product.create()
        # 2.Retrieve the name of the first product in the products list
        product_name = products[0].name
        # 3.Count the number of occurrences of the product name in the list
        nr_ocurrences = len([product for product in products if product.name == product_name])
        # 4.Retrieve products from the database that have the specified name.
        found_products = Product.find_by_name(product_name)
        # 5.Assert if the count of the found products matches the expected count.
        self.assertEqual(found_products.count(), nr_ocurrences)
        # 6.Assert that each product’s name matches the expected name.
        for product in found_products:
            self.assertEqual(product.name, product_name)

    def test_find_product_by_availability(self):
        """It should Find Products by Availability"""
        # 1.Create a batch of 10 Product objects using the ProductFactory and save them to the database.
        nr_products = 10
        products = ProductFactory.create_batch(nr_products)
        for product in products:
            product.create()
        # 2.Retrieve the availability of the first product in the products list
        product_available = products[0].available
        # 3.Count the number of occurrences of the product availability in the list
        nr_ocurrences = len([product for product in products if product.available == product_available])
        # 4.Retrieve products from the database that have the specified availability.
        found_products = Product.find_by_availability(product_available)
        # 5.Assert if the count of the found products matches the expected count.
        self.assertEqual(found_products.count(), nr_ocurrences)
        # 6.Assert that each product's availability matches the expected availability.
        for product in found_products:
            self.assertEqual(product.available, product_available)

    def test_find_product_by_category(self):
        """It should Find Products by Category"""
        # 1.Create a batch of 10 Product objects using the ProductFactory and save them to the database.
        nr_products = 10
        products = ProductFactory.create_batch(nr_products)
        for product in products:
            product.create()
        # 2.Retrieve the category of the first product in the products list
        product_category = products[0].category
        # 3.Count the number of occurrences of the product that have the same category in the list.
        nr_ocurrences = len([product for product in products if product.category == product_category])
        # 4.Retrieve products from the database that have the specified category.
        found_products = Product.find_by_category(product_category)
        # 5.Assert if the count of the found products matches the expected count.
        self.assertEqual(found_products.count(), nr_ocurrences)
        # 6.Assert that each product's category matches the expected category.
        for product in found_products:
            self.assertEqual(product.category, product_category)
