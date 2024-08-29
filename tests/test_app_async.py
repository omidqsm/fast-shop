import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from data.Address import AddressRepo
from data.product import ProductRepo
from data.user import UserRepo
from helpers.crypto import Crypto
from model.model import User, Address, Product
from tests.app import pytest_app


async def get_access_header(client: AsyncClient, credentials: dict) -> dict:
    response = await client.post('/auth/login', json=credentials)
    access_token = response.json()['access_token']
    return {'X-API-Key': access_token}


@pytest_asyncio.fixture()
async def create_default_users():
    admin = User(
        nid="1111111111",
        first_name="admin",
        last_name="admin",
        phone="+9811111111",
        password=Crypto.get_hash("admin_password"),
        scopes="admin"
    )
    buyer = User(
        nid="2222222222",
        first_name="buyer",
        last_name="buyer",
        phone="+9822334455",
        password=Crypto.get_hash("buyer_password"),
    )
    user_repo = UserRepo()
    await user_repo.add((buyer, admin))


@pytest_asyncio.fixture()
async def create_user_and_address_and_products():
    user = User(
        nid="3333445645",
        first_name="user",
        last_name="user",
        phone="+9822334411",
        password=Crypto.get_hash("user_password"),
    )
    user = await UserRepo().add(user)
    address = Address(
        state="Tehran",
        city="Shahre Rey",
        postal_code="1234554321",
        description="this is an address",
        user=user
    )
    address = await AddressRepo().add(address)
    product_1 = Product(
        category="headset",
        price=500,
        quantity=15,
        info={
            "name": "beats"
        }
    )
    product_2 = Product(
        category="laptop",
        price=2000,
        quantity=10,
        info={
            "name": "samsung"
        }
    )
    p1, p2 = await ProductRepo().add((product_1, product_2))
    return user, address, p1, p2


@pytest.mark.asyncio
async def test_authentication():
    async with AsyncClient(transport=ASGITransport(app=pytest_app), base_url="http://test") as client:
        user = {
            "nid": "1234567890",
            "first_name": "omid",
            "last_name": "qsm",
            "phone": "+982133551020",
            "password": "ABCdef1234",
            "re_password": "ABCdef1234",
            "email": None,
        }
        response = await client.post('/auth/signup', json=user)
        assert response.status_code == 201
        response_data = response.json()
        pk = response_data.get('id')
        assert pk is not None

        response = await client.get('/auth/me')
        assert response.status_code == 403

        credentials = {'phone': '+982133551020', 'password': 'ABCdef1234'}
        access_header = await get_access_header(client, credentials)

        response = await client.get('/auth/me', headers=access_header)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['nid'] == user['nid']
        assert response_data['phone'] == '+982133551020'


@pytest.mark.asyncio
async def test_product_manipulation(create_default_users):
    async with AsyncClient(transport=ASGITransport(app=pytest_app), base_url="http://test") as client:
        product = {
          "category": "mobile",
          "info": {
              "name": "asus"
          },
          "price": 1200,
          "quantity": 10
        }

        response = await client.post('/product/', json=product)
        assert response.status_code == 403

        credentials = {'phone': '+9822334455', 'password': 'buyer_password'}
        user_access_header = await get_access_header(client, credentials)
        response = await client.post('/product/', json=product, headers=user_access_header)
        assert response.status_code == 403

        credentials = {'phone': '+9811111111', 'password': 'admin_password'}
        admin_access_header = await get_access_header(client, credentials)
        response = await client.post('/product/', json=product, headers=admin_access_header)
        assert response.status_code == 201

        response_data = response.json()
        pk = response_data.get('id')
        assert pk is not None

        url = f'/product/{pk}'

        response = await client.get(url)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data['category'] == 'mobile'
        assert response_data['info']['name'] == 'asus'

        response_data['category'] = 'laptop'
        response = await client.put(url, json=response_data, headers=admin_access_header)
        response_data = response.json()
        assert response_data['category'] == 'laptop'

        response = await client.delete(url, headers=admin_access_header)
        assert response.status_code == 204

        response = await client.get(url)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_address_manipulation(create_default_users):
    async with AsyncClient(transport=ASGITransport(app=pytest_app), base_url="http://test") as client:
        address = {
            "state": "Tehran",
            "city": "Tehran",
            "latitude": 10.123456,
            "longitude": 15.654321,
            "description": "Azadi Blvd",
            "postal_code": "1234567890"
        }

        credentials = {'phone': '+9822334455', 'password': 'buyer_password'}
        access_header = await get_access_header(client, credentials)
        response = await client.post('/address/', json=address, headers=access_header)
        assert response.status_code == 201

        response_data = response.json()
        pk = response_data.get('id')
        assert pk is not None

        url = f'/address/{pk}'

        response = await client.get(url, headers=access_header)
        assert response.status_code == 200
        #
        response_data = response.json()
        assert response_data['id'] == pk
        assert response_data['description'] == 'Azadi Blvd'

        response_data['description'] = 'Valiasr Ave'
        response = await client.put(url, json=response_data, headers=access_header)
        assert response.status_code == 200

        response = await client.get(url, headers=access_header)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['description'] == 'Valiasr Ave'

        response = await client.delete(url, headers=access_header)
        assert response.status_code == 204

        response = await client.get(url, headers=access_header)
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_order_manipulation(create_user_and_address_and_products):
    user, address, product_1, product_2 = create_user_and_address_and_products
    order = {
        "address_id": address.id,
        "products": [
            {
                "quantity": 5,
                "product_id": product_1.id,
            },
            {
                "quantity": 2,
                "product_id": product_2.id,
            },
        ]
    }

    async with AsyncClient(transport=ASGITransport(app=pytest_app), base_url="http://test") as client:
        credentials = {'phone': '+9822334411', 'password': 'user_password'}
        access_header = await get_access_header(client, credentials)

        response = await client.post('/order/', json=order, headers=access_header)
        assert response.status_code == 201

        response_data = response.json()
        pk = response_data.get('id')

        response = await client.get(f'/order/{pk}', headers=access_header)
        assert response.status_code == 200
