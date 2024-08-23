import pytest
from httpx import AsyncClient, ASGITransport

from tests.app import pytest_app


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
        assert response_data.get('id') is not None

        response = await client.get('/auth/me')
        assert response.status_code == 403

        credentials = {'phone': '+982133551020', 'password': 'ABCdef1234'}
        response = await client.post('/auth/login', json=credentials)
        assert response.status_code == 200

        access_token = response.json()['access_token']
        headers = {'X-API-Key': access_token}
        response = await client.get('/auth/me', headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['nid'] == user['nid']
        assert response_data['phone'] == '+982133551020'


@pytest.mark.asyncio
async def test_product_manipulation():
    async with AsyncClient(transport=ASGITransport(app=pytest_app), base_url="http://test") as client:
        product = {
          "category": "mobile",
          "info": {
              "name": "asus"
          },
          "price": 1200,
          "stock_quantity": 10
        }

        response = await client.post('/product/', json=product)
        assert response.status_code == 201

        response = await client.get('/product/1')
        assert response.status_code == 200

        response_data = response.json()
        assert response_data['category'] == 'mobile'
        assert response_data['info']['name'] == 'asus'

        response_data['category'] = 'laptop'
        response = await client.put('/product/', json=response_data)
        response_data = response.json()
        assert response_data['category'] == 'laptop'

        response = await client.delete('/product/1')
        assert response.status_code == 204

        response = await client.get('/product/1')
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_address_manipulation():
    async with AsyncClient(transport=ASGITransport(app=pytest_app), base_url="http://test") as client:
        address = {
            "state": "Tehran",
            "city": "Tehran",
            "latitude": 10.123456,
            "longitude": 15.654321,
            "description": "Azadi Blvd",
            "postal_code": "1234567890"
        }

        credentials = {'phone': '+982133551020', 'password': 'ABCdef1234'}
        response = await client.post('/auth/login', json=credentials)
        access_token = response.json()['access_token']
        headers = {'X-API-Key': access_token}
        response = await client.post('/address/', json=address, headers=headers)
        assert response.status_code == 201

        response = await client.get('/address/1', headers=headers)
        assert response.status_code == 200

        response_data = response.json()
        assert response_data['id'] == 1
        assert response_data['description'] == 'Azadi Blvd'

        response_data['description'] = 'Valiasr Ave'
        response = await client.put('/address/', json=response_data, headers=headers)
        assert response.status_code == 200

        response = await client.get('/address/1', headers=headers)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data['description'] == 'Valiasr Ave'

        response = await client.delete('/address/1', headers=headers)
        assert response.status_code == 204

        response = await client.get('/address/1', headers=headers)
        assert response.status_code == 404
