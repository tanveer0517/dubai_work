# -*- encoding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2018 (http://www.bistasolutions.com)
#
##############################################################################
import requests
import json
from PIL import Image
from io import BytesIO
from datetime import datetime
import base64
import os.path
from os import path
from geopy.geocoders import Nominatim


def LocationLogiLati(args):
    """
    Logitude and Latitude locator
    """
    try:
        loc = Nominatim().geocode(args)
        return {"lat":loc.latitude or "25.0978068", "long":loc.longitude or "55.1535988"}
    except:
        return {"lat":"25.0978068", "long":"55.1535988"}


"""
~~~~~~~~~~~~~
 Go Mart API 
~~~~~~~~~~~~~
1. setCity
2. setLocation
3. setTax
4. setCategory
5. setSubCategory
6. setUnit
7. setUser
8. setBrand
9. setStore
10. setStoreAdmin
11. setProduct
12. setProductRange
13. setStoreProduct
14. setStoreProductRange
15. setInventoryStock
16. setStoreDetail
17. setState
18. setStoreExtras
19. setDeliveryRegion
20. setGroup
21. setGroupFields
22. setOrderStatus
"""

# _API_URL = "http://www.indubuy.com/api/"
# _API_URL = "http://marakezcloud.com/api/"
_client_key = "gomartapi777"
headers = {
            'content-type': 'application/x-www-form-urlencoded',
           }


def image_open(img):
    return img


def setCity(_API_URL, id, name, code, state_id, _active):
    """
    Go Mart,POST method 
    API 1 : setCity

    @param erp_city_id: City id from the odoo create into the GoMart
    @param erp_city_name: City name from the odoo create into the GoMart
    @param erp_city_code: City code from the odoo create into the GoMart
    @param erp_state_id:State id of odoo 
    @param active : active state if active then value is 1 and else  active value is 2  
    """
    _data = {
            "client_key":_client_key,
            "erp_city_id":id,
            "erp_city_name":name,
            "erp_city_code":code,
            "erp_state_id":state_id,
            "active":_active
            }
    request_city = requests.post(_API_URL + "setCity", data=_data)
    if request_city.status_code == 200:
                    return{"status_code":request_city.status_code,
                         "json_dump":request_city.json(),
                         "data":_data,
                         "city_id":request_city.json().get("gomart_city_id")
                         }
    else:
        return{ "status_code":request_city.status_code,
                 "json_dump":request_city.json(),
                 "data":_data,
             }


def setLocation(_API_URL, state_id, city_id, loc_id, loc_name , _active):
    """
    Go Mart,POST method  
    API 2 : setLocation

    @param  erp_state_id:State ID of odoo
    @param  erp_city_id: City ID of odoo 
    @param erp_location_id: location id of odoo
    @param erp_location_name: location name  
    @param active: active state if active then value is 1 and else  active value is 2 
    """
    _data = {
            "client_key":_client_key,
            "erp_state_id":state_id,
            "erp_city_id":city_id,
            "erp_location_id":loc_id,
            "erp_location_name":loc_name,
            "active":_active
            }
    req_loc = requests.post(_API_URL + "setLocation", data=_data)
    if req_loc.status_code == 200:
            return {
                    "status_code":req_loc.status_code,
                    "location_id":req_loc.json().get("gomart_location_id"),
                    "data":_data,
                    "json_dump":req_loc.json(),
                    }
    else:
        return {
                "status_code":req_loc.status_code,
                "data":_data
                }


def setTax(_API_URL, id, title, value, start_dat, end_dat, _active):
    """
    Go Mart ,POST method 
    API 3 : setTax

    @param erp_tax_id: tax id 
    @param erp_tax_title :tax title
    @param erp_tax_value: tax value
    @param erp_start_date: start date
    @param erp_end_date: End date
    @param active: active state if active then value is 1 and else  active value is 2 
    """
    _data = {
            "client_key":_client_key,
            "erp_tax_id":id,
            "erp_tax_title":title,
            "erp_tax_value":value,
            "erp_start_date":start_dat,  # [Tax start date, format: 07-Apr-2018 ]
            "erp_end_date":end_dat,  # [Tax end date, format: 07-Apr-2018 ]
            "active":_active
            }
    req_tax = requests.post(_API_URL + "setTax", data=_data)
    if req_tax.status_code == 200:
            return {
                    "status_code":req_tax.status_code,
                    "tax_id":req_tax.json().get("gomart_tax_id"),
                    "json_dump":req_tax.json(),
                    "data":_data
                    }
    else:
        return {
                "status_code":req_tax.status_code,
                "data":_data
                }


def setCategory(_API_URL, id , name, group_id, app_img, img_name, allow_product, _active):
    """
    Go Mart,Using POST method 
    API 4 : setCategory

    @param erp_category_id: Category id
    @param erp_category_name: Categroy
    @param erp_group_id: Group id
    @param erp_app_img: App img
    @param erp_image_name : Image name
    @param erp_product_allowed: Product Allowed
    @param active: active state if active then value is 1 and else  active value is 2 
    """
    _data = {
            "client_key":_client_key,
            "erp_category_id":int(id),
            "erp_category_name":name,
            "erp_group_id":int(group_id),
            "erp_app_img":app_img,
            "erp_image_name":img_name,
            "erp_product_allowed":allow_product,  # [1- Product allowed under category, 0- not allowed]
            "active":_active
            }
    req_cat = requests.post(_API_URL + "setCategory", data=_data)
    if req_cat.status_code == 200:
            return {
                    "status_code":req_cat.status_code,
                    "category_id":req_cat.json().get("gomart_category_id"),
                    "json_dump":req_cat.json(),
                    "data":_data
                    }
    else:
        return {
                "status_code":req_cat.status_code,
                "data":_data
                }


def setSubCategory(_API_URL, id, cat_id, sub_cat_name, group_id, img_name, _active):
    """
    Go Mart,Using POST method
    API 5 : setSubCategory
    @param erp_subcategory_id : Subcategory id
    @param erp_category_id: Category id
    @param erp_subcategory_name: Subcategory name
    @param erp_group_id: Group id
    @param erp_image_name : Image name
    @param active : active state if active then value is 1 and else  active value is 2 
    """
    _data = {
            "client_key":_client_key,
            "erp_subcategory_id":id,
            "erp_category_id":cat_id,
            "erp_subcategory_name":sub_cat_name,
            "erp_group_id":group_id,
            "erp_image_name":img_name,
            "active":_active
            }
    req_subcat = requests.post(_API_URL + "setSubCategory", data=_data)
    if req_subcat.status_code == 200:
            return {
                    "subcategory_id":req_subcat.json().get("gomart_subcategory_id"),
                    "status_code":req_subcat.status_code,
                    "data":_data,
                    "json_dump":req_subcat.json()
                    }
    else:
        return {
                "status_code":req_subcat.status_code,
                "data":_data
                }


def setUnit(_API_URL, id, name, _active):
    """
    Go Mart,Using POST method
    API 6 : setUnit
    
    @param erp_unit_id : Unit id
    @param erp_unit_name :Unit name
    @param active: active state if active then value is 1 and else  active value is 2  
    """
    _data = {
            "client_key":_client_key,
            "erp_unit_id":id,
            "erp_unit_name":name,
            "active":_active
            }
    req_unit = requests.post(_API_URL + "setUnit", data=_data)
    if req_unit.status_code == 200:
            return {
                    "status_code":req_unit.status_code,
                    "unit_id":req_unit.json().get("gomart_unit_id"),
                    "json_dump":req_unit.json(),
                    "data":_data
                    }
    else:
        return {
                "status_code":req_unit.status_code,
                "data":_data
                }


def setCustomer(_API_URL, id, first_name, last_name, dob, email, mobile, pwd, gender, _active):
    """
    Go Mart,Using POST method
    API 7 : setCustomer
    
    @param erp_customer_id: Customer id
    @param erp_first_name: First name
    @param erp_last_name: Last name
    @param erp_dob: Date-of-birth
    @param erp_email: Email
    @param erp_mobile: Mobile
    @param erp_password: Password
    @param erp_gender: Gender
    @param active: active state if active then value is 1 and else  active value is 2  
    """
    _data = {
            "client_key":_client_key,
            "erp_customer_id":id,
            "erp_first_name":first_name,
            "erp_last_name":last_name,
            "erp_dob":dob,  # [Date of birth, format: 07-Apr-2018 ]
            "erp_email":email,
            "erp_mobile":mobile,
            "erp_password":pwd,
            "erp_gender":gender,
            "active":_active
            }
    req_user = requests.post(_API_URL + "setCustomer", data=_data)
    if req_user.status_code == 200:
            return {
                    "status_code":req_user.status_code,
                    "user_id":req_user.json().get("gomart_user_id"),
                    "json_dump":req_user.json(),
                    "data":_data
                   }
    else:
        return {
                "data":_data,
                "status_code":req_user.status_code
                }


def setBrand(_API_URL, id, name, img, _active):
    """
    Go Mart,Using POST method
    API 8 : setBrand

    @param erp_brand_id: Brand id
    @param erp_brand_name: Brand name
    @param erp_image_name: Image name
    @param active : active state if active then value is 1 and else  active value is 2  
    """
    _data = {
            "client_key":_client_key,
            "erp_brand_id":id,
            "erp_brand_name":name,
            "erp_image_name":img,
            "active":_active
            }
    req_brand = requests.post(_API_URL + "setBrand", data=_data)
    if req_brand.status_code == 200:
            return {
                    "status_code":req_brand.status_code,
                    "brand_id":req_brand.json().get("gomart_brand_id"),
                    "json_dump":req_brand.json(),
                    "data":_data
                    }
    else:
        return {
                "status_code":req_brand.status_code,
                "data":_data
                }


def setStore(_API_URL, id, name, chain_id, city_id, loc_id, stat_id, about, merchant_type, commission, start_dat, flag,
            store_type, address, email, lattitude, longitude, web, phone1, phone2, floor_flag, rating, _active, erp_reg_id):
    """
    Go Mart,Using POST method
    API 9 : setStore

    @param erp_store_id:Store id 
    @param erp_store_name :Store name
    @param erp_store_chain_id : Store chain id
    @param erp_city_id: City id
    @param erp_location_id: Location id
    @param erp_state_id: State id
    @param erp_about: About
    @param erp_merchant_type: Merchant type
    @param erp_commisssion: Commission
    @param erp_start_date:Start date
    @param erp_chain_flag :Chain flag
    @param erp_primary_store: Primary store
    @param erp_address: Address
    @param erp_store_mail:Store mail
    @param erp_lattitude: Lattitude
    @param erp_longitude: Longitude
    @param erp_store_web: Store Website
    @param erp_store_phone1:Store Phone1
    @param erp_store_phone2:Store Phone2
    @param erp_floor_plan_flag: Floor plan flag
    @param erp_store_rating: Store rating
    @param active: active state if active then value is 1 and else  active value is 2   
    @param erp_reg_id: pass unique Character 
    """
    _data = {
            "client_key":_client_key,
            "erp_store_id":id ,
            "erp_store_name":name ,
            "erp_store_chain_id":chain_id,
            "erp_city_id":city_id,
            "erp_location_id":loc_id ,
            "erp_state_id":stat_id ,
            "erp_about":about,
            "erp_merchant_type":merchant_type,
            "erp_commission":commission,
            "erp_start_date":start_dat or str(datetime.now().date()),
            "erp_chain_flag":flag,
            "erp_primary_store":store_type,
            "erp_address":address,
            "erp_store_mail":email,
            "erp_lattitude":lattitude,
            "erp_longitude":longitude,
            "erp_store_web":web,
            "erp_store_phone1":phone1,
            "erp_store_phone2":phone2,
            "erp_floor_plan_flag":floor_flag,
            "erp_store_rating":rating,
            "active":_active,
            "erp_reg_id":erp_reg_id
            }

    req_store = requests.post(_API_URL + "setStore", data=_data, headers=headers)
    if req_store.status_code == 200 and req_store.json() and (req_store.json().get("gomart_store_id") and req_store.json().get("gomart_store_chain_id")):
            return {
                    "status_code":req_store.status_code,
                    "store_id":req_store.json().get("gomart_store_id"),
                    "chain_id":req_store.json().get("gomart_store_chain_id"),
                    "json_dump":req_store.json(),
                    "data":_data
                    }
    else:
        return {
                "json_dump":req_store.json(),
                "status_code":req_store.status_code,
                "data":_data
                }

    
def setStoreAdmin(_API_URL, id, store_chain_id, admin_id, admin_name, login, pwd, email, mobile, dob, admin_type,
                  super_admin, chain_super_admin, gender, erp_reg_id):
    """
    Go Mart,Using POST method
    API 10 : setStoreAdmin

    @param erp_store_id: Store id 
    @param erp_store_chain_id: Store chain id
    @param erp_adin_id:Odoo Admin ID 
    @param erp_admin_name: Admin name
    @param erp_login:Login
    @param erp_password:Password
    @param erp_email: E-mail
    @param erp_mobile : Mobile  
    @param erp_dob: Date-of-birth
    @param erp_admin_type: Admin Type
    @param erp_super_admin:Super admin
    @param erp_chain_super_admin:Chain Super admin
    @param erp_gender:Gender
    """
    _status = {}
    _data = {
            "client_key":_client_key,
            "erp_store_id":id,
            "erp_store_chain_id":store_chain_id,
            "erp_admin_id":admin_id,
            "erp_admin_name":admin_name,
            "erp_login":login,
            "erp_password":pwd,
            "erp_email":email,
            "erp_mobile":mobile,
            "erp_dob":dob,
            "erp_admin_type":admin_type,
            "erp_super_admin":super_admin,
            "erp_chain_super_admin":chain_super_admin,
            "erp_gender":gender,
            "erp_reg_id":erp_reg_id
            }
    store_admin = requests.post(_API_URL + "setStoreAdmin", data=_data, headers=headers)
    if (store_admin.status_code == 200) and (store_admin.json().get("code") == 200):
            return{
                    "status_code":store_admin.status_code,
                    "admin_id":store_admin.json().get("gomart_admin_id"),
                    "json_dump":store_admin.json(),
                    "data":_data
                  }
    else:
          return {"data":_data, "json_dump":store_admin.json(), "status_code":store_admin.status_code}


def setProduct(_API_URL, id, name, cat_id, sub_cat_id, brand_id, family_id, small_description, description, _active):
    """
    GoMart,Using POST method
    API 11 : setProduct

    @param erp_product_id:Product id
    @param erp_product_name: Product name
    @param erp_category_id:Category id
    @param erp_subcategory_id : Subcategory id
    @param erp_brand_id: Brand id
    @param erp_family_id: Family id
    @param erp_small_description: Small description
    @param erp_description:Description
    @param active: active state if active then value is 1 and else  active value is 2
    """
    _data = {
            "client_key":_client_key,
            "erp_product_id":id,
            "erp_product_name":name,
            "erp_category_id":cat_id,
            "erp_subcategory_id":sub_cat_id,
            "erp_brand_id":brand_id,
            "erp_family_id":family_id,
            "erp_small_description":small_description,
            "erp_description":description,
            "active":_active
            }
    req_product = requests.post(_API_URL + "setProduct", data=_data, headers=headers)
    if req_product.status_code == 200:
            return { 
                    "status_code":req_product.status_code,
                    "product_id":req_product.json().get("gomart_product_id"),
                    "data":_data,
                    "json_dump":req_product.json()
                   }
    else:
        return{
                "data":_data,
                "status_code":req_product.status_code
              }


def setProductRange(_API_URL, product_id, id, name, uom_id, range_img, barcode, addedby):
    """
    Go Mart,Using POST method
    API 12 : setProductRange
    @param erp_product_id: Product id
    @param erp_range_id: Rang id
    @param erp_range_name: Rang name
    @param erp_uom_id: Unit of Measurement
    @param erp_range_image: Range image
    @param erp_barcode:Barcode
    @param erp_added_by: Added by 
    """
    _data = {
            "client_key":_client_key,
            "erp_product_id":product_id,
            "erp_range_id":id,
            "erp_range_name":name,
            "erp_uom_id":uom_id,
            "erp_range_image":range_img,
            "erp_barcode":barcode,
            "erp_added_by":addedby
            }
    req_range = requests.post(_API_URL + "setProductRange", data=_data, headers=headers)
    if req_range.status_code == 200:
            return{
                    "status_code":req_range.status_code,
                    "range_id":req_range.json().get("gomart_range_id"),
                    "data":_data,
                    "json_dump":req_range.json()
                    }
    else:
        return{"data":_data, "status_code":req_range.status_code}


def setStoreProduct(_API_URL, id, store_id, chain_id, product_id, cat_id, subcat_id, sku, gomart_store_id):
    """
    Go Mart,Using POST method
    API 13 : setStoreProduct

    @param erp_store_product_id: Store product id 
    @param erp_store_id: Store id 
    @param erp_store_chain_id : Store chain id 
    @param erp_product_id: Product id
    @param erp_category_id: Category id 
    @param erp_subcategory_id: Subcategory id 
    @param erp_store_sku: Store sku 
    """
    _data = {
            "client_key":_client_key,
            "erp_store_product_id":id,
            "erp_store_id":store_id,
            "erp_store_chain_id":chain_id,
            "erp_product_id":product_id,
            "erp_category_id":cat_id,
            "erp_subcategory_id":subcat_id,
            "erp_store_sku":sku,
            "store_id":gomart_store_id
            }
    req_store_product = requests.post(_API_URL + "setStoreProduct", data=_data, headers=headers)
    if req_store_product.status_code == 200:
            return {
                    "status_code":req_store_product.status_code,
                    "store_product_id":req_store_product.json().get("gomart_store_product_id"),
                    "data":_data,
                    "json_dump":req_store_product.json()
                   }
    else:
        return {"data":_data, "json_dump":req_store_product.json(), "status_code":req_store_product.status_code}


def setStoreProductRange(_API_URL, product_rang_id, rang_id, store_id, chain_id, product_id, mrp_price, prod_disc,
                         price_offer, qty, unlimited, pur_limit, out_stock, low_stock, barcod, added_by, gomart_store_id):
    """
    Go Mart,Using POST method
    API 14 : setStoreProductRange

    @param erp_store_product_range_id: Store product rang id
    @param erp_range_id:Range id 
    @param erp_store_id: Store id 
    @param erp_store_chain_id: Store chain id 
    @param erp_store_product_id: Store product id 
    @param erp_mrp_price: Mrp price
    @param erp_prod_disc: Product discount
    @param erp_offer_price: Offer price
    @param erp_qty_available: Qty Avaliable
    @param erp_unlimited:Unlimited
    @param erp_pur_limit: Limit of quantity per purchase
    @param erp_out_of_stock: Out of stock
    @param erp_low_stock: Low stock reminder value
    @param erp_barcode: Barcode
    @param erp_added_by: Added by
    """
    _data = {
            "client_key":_client_key,
            "erp_store_product_range_id":product_rang_id,
            "erp_range_id":rang_id,
            "erp_store_id":store_id,
            "erp_store_chain_id":chain_id,
            "erp_store_product_id":product_id,
            "erp_mrp_price":mrp_price,
            "erp_prod_disc":prod_disc,
            "erp_offer_price":price_offer,
            "erp_qty_available":qty,
            "erp_unlimited":unlimited,  # [0 – Limited, 1 - Unlimited]
            "erp_pur_limit":pur_limit,  # [Integer value – Limit of quantity per purchase]
            "erp_out_of_stock":out_stock,  # [1 – Not outofstock, 2 - Outofstock]
            "erp_low_stock":low_stock,  # [Float - Low stock reminder value]
            "erp_barcode":barcod,
            "erp_added_by":added_by,
            "store_id":gomart_store_id
            }
    req_store_prod_rang = requests.post(_API_URL + "setStoreProductRange", data=_data, headers=headers)
    if req_store_prod_rang.status_code == 200:
            return {
                    "status_code":req_store_prod_rang.status_code,
                    "store_product_id":req_store_prod_rang.json().get("gomart_store_range_id"),
                    "data":_data,
                    "json_dump":req_store_prod_rang.json()
                   }
    else:
        return {
                "data":_data, "json_dump":req_store_prod_rang.json(), "status_code":req_store_prod_rang.status_code
                }


def setInventoryStock(_API_URL, store_rang_id, qty, unlimit, pur_limit, out_stock, low_stock, gomart_store_id):
    """
    Go Mart,Using POST method
    API 15 : setInventoryStock
    
    @param erp_store_product_range_id: Store product range id 
    @param erp_qty_available: Qty avalilable
    @param erp_unlimited: Unlimited
    @param erp_pur_limit:Limit of quantity per purchase
    @param erp_out_of_stock: Out-of-stock
    @param erp_low_stock: Low stock
    """
    _data = {
            "client_key":_client_key,
            "erp_store_product_range_id":store_rang_id,
            "erp_qty_available":qty,
            "erp_unlimited":unlimit,
            "erp_pur_limit":pur_limit,
            "erp_out_of_stock":out_stock,
            "erp_low_stock":low_stock,
            "store_id":gomart_store_id
            }
    req_store_prod_rang = requests.post(_API_URL + "setInventoryStock", data=_data)
    if req_store_prod_rang.status_code == 200:
            return {
                    "status_code":req_store_prod_rang.status_code,
                    "store_range_id":req_store_prod_rang.json().get("gomart_store_range_id"),
                    "data":_data,
                    "json_dump":req_store_prod_rang.json()
                    }
    else:
        return {"data":_data, "json_dump":req_store_prod_rang.json(), "status_code":req_store_prod_rang.status_code}


def setStoreDetail(_API_URL, store_id, chain_id, city_id, state_id, location_id, store_name,
                   store_type, address, lattitude, longitude, email, web, phone1, phone2,
                   about, onfloor, store_rate, _active, erp_reg_id):
    """
    Go Mart,Using POST method
    API 16 : setStoreDetail

    @param erp_store_id: Store id 
    @param erp_store_chain_id: Store chain id 
    @param erp_city_id : City id 
    @param erp_state_id : State id 
    @param erp_location_id : Location id 
    @param erp_store_name : Store name
    @param erp_primary_store : Primary store
    @param erp_address : Address
    @param erp_lattitude: Lattitude
    @param erp_longitude: Longitude
    @param erp_store_email:Store email
    @param erp_store_web: Store Website
    @param erp_store_phone1: Store phone1 
    @param erp_store_phone2: Store phon2
    @param erp_about: About
    @param erp_floor_plan_flag: Floor plan flag
    @param erp_store_rating: Store rating
    @param active: active state if active then value is 1 and else  active value is 2
    @param erp_reg_id: pass unique Character 
    """
    _data = {
            "client_key":_client_key,
            "erp_store_id":store_id,
            "erp_store_chain_id":chain_id,
            "erp_city_id":city_id,
            "erp_state_id":state_id,
            "erp_location_id":location_id,
            "erp_store_name":store_name,
            "erp_primary_store":store_type,  # [1-Primary Store,0-Non Primary Store]
            "erp_address":address,
            "erp_lattitude":lattitude,
            "erp_longitude":longitude,
            "erp_store_email":email,
            "erp_store_web":web,
            "erp_store_phone1":phone1,
            "erp_store_phone2":phone2,
            "erp_about":about,
            "erp_floor_plan_flag":onfloor,  # [1-Enabled,2-Not Enabled ]
            "erp_store_rating":store_rate,
            "active":_active,
            "erp_reg_id":erp_reg_id
            }
    req_store_details = requests.post(_API_URL + "setStoreDetail", data=_data, headers=headers)
    if req_store_details.status_code == 200:
            return {"status_code":req_store_details.status_code,
                    "store_chain_id":req_store_details.json().get("gomart_store_chain_id"),
                    "data":_data, "json_dump":req_store_details.json()}
    else:
        return {"data":_data, "json_dump":req_store_details.json(), "status_code":req_store_details.status_code}

    
def setState(_API_URL, name, id, _active):
    """
    Go Mart,Using POST method
    API 17 : setState

    @param erp_state_name: State name
    @param erp_state_id: State id 
    @param active:[1- State Active, 2- State Inactive]
    """
    _data = {
            "client_key":_client_key,
            "erp_state_name":name,
            "erp_state_id":id,
            "active":_active
            }
    req_state = requests.post(_API_URL + "setState", data=_data, headers=headers)
    if req_state.status_code == 200:
            return{"status_code":req_state.status_code, "json_dump":req_state.json(),
                 "data":_data, "state_id":req_state.json().get("gomart_state_id")}
    else:
        return {"status_code":req_state.status_code, "json_dump":req_state.json(), "data":_data}

    
def setStoreExtras(_API_URL, field_id, store_id, store_chain_id, order_prefix, order_amt, delivery_chrg,
                        delivery_flag, delivery_amt, delivery_msg, flag, delivery_dur,
                        terms, mon_flag, mon_st, mon_et, tue_flag, tue_st, tue_et, wed_flag,
                        wed_st, wed_et, thu_flag, thu_st, thu_et, fri_flag, fri_st, fri_et,
                        sat_flag, sat_st, sat_et, sun_flag, sun_st, sun_et, erp_reg_id, pay_options):
    """
    Go Mart,Using POST method
    API 18 : setStoreExtras
    
    @param erp_field_id: Field id 
    @param erp_store_id: Store id 
    @param erp_store_chain_id: Store chain id 
    @param erp_order_prefix: Order prefix
    @param erp_min_order_amt: Minimum order amount
    @param erp_delivery_charge: Delivery Charge
    @param erp_delivery_min_flag: Delivery minimum flag
    @param erp_delivery_min_amount: Delivery minimum amount 
    @param erp_delivery_min_message: Delivery minimum message
    @param erp_take_back_flag:[1-Not to be returned,2-Returned]
    @param erp_delivery_duration: Delivery duration
    @param erp_terms: Terms 
    @param erp_mon_flag: Monday flag
    @param erp_mon_stime:Monday Start time 
    @param erp_mon_etime: Monday End time 
    @param erp_tue_flag: Tuesday flag
    @param erp_tue_stime: Tuesday Start time 
    @param erp_tue_etime: Tuesday End time 
    @param erp_wed_flag: Wednesday flag
    @param erp_wed_stime: Wednesday Start time 
    @param erp_wed_etime: Wednesday End time 
    @param erp_thu_flag: Thursday flag
    @param erp_thu_stime: Thursday Start time 
    @param erp_thu_etime: Thursday End time 
    @param erp_fri_flag: Friday flag
    @param erp_fri_stime: Friday Start time 
    @param erp_fri_etime: Friday End time 
    @param erp_sat_flag: Saturday flag
    @param erp_sat_stime: Saturday Start time 
    @param erp_sat_etime: Saturday End time 
    @param erp_mon_flag: Sunday flag
    @param erp_mon_stime: Sunday Start time 
    @param erp_mon_etime: Sunday End time 
    @param erp_pay_options: (array [{1,’’},{4,’Sodexo’}]) – First Value if Pay Type, Second
                            value is pay type text incase pay type is 4.
                            Possible Pay Type IDS: 1 – Cash, 2- Online, 3 – Debit/Credit Card, 4 - Others
    """
    header = {
                'content-type': "application/x-www-form-urlencoded",
                'cache-control': "no-cache",
                'postman-token': "bef62fbf-649b-e667-df69-0f95313ddb51"
              }
    payload = "client_key=" + str(_client_key) + "&erp_field_id=" + str(field_id) + "&erp_store_id=" + str(store_id) + "&erp_store_chain_id=" + str(store_chain_id) + "&erp_order_prefix=" + str(order_prefix) + "&erp_min_order_amt=" + str(order_amt) + "&erp_delivery_charge=" + str(delivery_chrg) + "&erp_delivery_min_flag=" + str(delivery_flag) + "&erp_delivery_min_amount=" + str(delivery_amt) + "&erp_delivery_min_message=" + str(delivery_msg) + "&erp_take_back_flag=" + str(flag) + "&erp_delivery_duration=" + str(delivery_dur) + "&erp_terms=" + str(terms) + "&erp_mon_flag=" + str(mon_flag) + "&erp_mon_stime=" + str(mon_st) + "&erp_mon_etime=" + str(mon_et) + "&erp_tue_flag=" + str(tue_flag) + "&erp_tue_stime=" + str(tue_st) + "&erp_tue_etime=" + str(tue_et) + "&erp_wed_flag=" + str(wed_flag) + "&erp_wed_stime=" + str(wed_st) + "&erp_wed_etime=" + str(wed_et) + "&erp_thu_flag=" + str(thu_flag) + "&erp_thu_stime=" + str(thu_st) + "&erp_thu_etime=" + str(thu_et) + "&erp_fri_flag=" + str(fri_flag) + "&erp_fri_stime=" + str(fri_st) + "&erp_fri_etime=" + str(fri_et) + "&erp_sat_flag=" + str(sat_flag) + "&erp_sat_stime=" + str(sat_st) + "&erp_sat_etime=" + str(sat_et) + "&erp_sun_flag=" + str(sun_flag) + "&erp_sun_stime=" + str(sun_st) + "&erp_sun_etime=" + str(sun_et) + "&erp_reg_id=" + str(erp_reg_id)
    if pay_options:
        payload = payload + '&erp_pay_options=' + '"' + str(pay_options) + '"'
    else:
        payload = payload + '&erp_pay_options=' + 'None'
    _data = {
            "client_key":_client_key,
            "erp_field_id": field_id,  # Field ID 
            "erp_store_id": store_id,  # Store ID 
            "erp_store_chain_id": store_chain_id,  # Store Chain ID of Odoo 
            "erp_order_prefix": order_prefix,
            "erp_min_order_amt":order_amt,
            "erp_delivery_charge":delivery_chrg,
            "erp_delivery_min_flag":delivery_flag,  # [1-Delivery charge below Min order amount selected]
            "erp_delivery_min_amount":delivery_amt,
            "erp_delivery_min_message":delivery_msg,
            "erp_take_back_flag":flag,  # [1-Not to be returned,2-Returned]
            "erp_delivery_duration":delivery_dur,  # [string]
            "erp_terms":terms,
            "erp_mon_flag":mon_flag,  # [0- Active, 1- Inactive]
            "erp_mon_stime":mon_st,
            "erp_mon_etime":mon_et,
            "erp_tue_flag":tue_flag,  # [0- Active, 1- Inactive]
            "erp_tue_stime":tue_st,
            "erp_tue_etime":tue_et,
            "erp_wed_flag":wed_flag,  # [0- Active, 1- Inactive]
            "erp_wed_stime":wed_st,
            "erp_wed_etime":wed_et,
            "erp_thu_flag":thu_flag,  # [0- Active, 1- Inactive]
            "erp_thu_stime":thu_st,
            "erp_thu_etime":thu_et,
            "erp_fri_flag":fri_flag,  # [0- Active, 1- Inactive]
            "erp_fri_stime":fri_st,
            "erp_fri_etime":fri_et,
            "erp_sat_flag":sat_flag,  # [0- Active, 1- Inactive]
            "erp_sat_stime":sat_st,
            "erp_sat_etime":sat_et,
            "erp_sun_flag":sun_flag,  # [0- Active, 1- Inactive]
            "erp_sun_stime":sun_st,
            "erp_sun_etime":sun_et,
            "erp_reg_id":erp_reg_id,
            "erp_pay_options":pay_options  # 1 – Cash, 2- Online, 3 – Debit/Credit Card, 4 - Others
            
            }
    store_extras = requests.post(_API_URL + "setStoreExtras", data=payload, headers=header)
    if store_extras.status_code == 200: 
        return {"status_code":store_extras.status_code,
                "store_field_id":store_extras.json().get('gomart_store_field_id'),
                "data":_data, "json_dump":store_extras.json(),
                "payload":payload}
    else:
        return {"data":_data, "json_dump":store_extras.json() or "None", "status_code":store_extras.status_code}


def setDeliveryRegion(_API_URL, region_id, chain_id, location_id, erp_reg_id):
    """
    Go Mart,Using POST method
    API 19 : setDeliveryRegion

    @param erp_delivery_region_id: Delivery region id 
    @param erp_store_chain_id: Store chain id 
    @param erp_location_id: Location id 
    """
    _data = {
            "client_key":_client_key,
            "erp_delivery_region_id":region_id,
            "erp_store_chain_id":chain_id,
            "erp_location_id":location_id,
            "erp_reg_id":erp_reg_id,
            }
    delivery_region = requests.post(_API_URL + "setDeliveryRegion", data=_data, headers=headers)
    if delivery_region.status_code == 200: 
        return {"status_code":delivery_region.status_code, "region_id":delivery_region.json().get('gomart_delivery_region_id'),
                "data":_data, "json_dump":delivery_region.json()}
    else: 
        return {"status_code":delivery_region.status_code, "data":_data}


def setGroup(_API_URL, id, name):
    """
    Gomart API for the Set group
    API 20 : setGroup
    """
    _data = {"client_key":_client_key, "erp_group_id":id, "erp_group_name":name}
    group_request = requests.post(_API_URL + "setGroup", data=_data, headers=headers)
    if group_request.status_code == 200: 
        return {"status_code":group_request.status_code,
                "group_id":group_request.json().get('gomart_group_id'),
                "data":_data, "json_dump":group_request.json()}
    else: 
        return {"data":_data, "status_code":group_request.status_code}


def setGroupFields(_API_URL, group_id, field_id, label, field_type, data_type, no_char,
                   decimal_place, allow, unit, curr_type, fix_field_type, values):
    # Working 
    """
    Go Mart,Using POST method
    API 21 : setGroupFields
 
    @param erp_group_id: Group id 
    @param erp_field_id: Field id 
    @param field_label: Field Label
    @param field_type: Field type
    @param field_data_type: Field data type
    @param no_of_chars: Number of characters allowed in for Group field in case of
                        Characters, Numeric or Currency
    @param decimal_places: 0:  If decimal places not allowed, 1: If decimal places allowed in
                                case of Numeric and Currency
    @param interval_allowed:  0: If interval fields not allowed, 1: If interval fields not allowed
                                in case of Numeric, Date, Time or Currency
    @param measure_unit: 0: If measurement unit not allowed, 1: If measurement unit
                            allowed in case of Numeric
    @param currency_type: 0: If Currency type not allowed,
                             1: If currency type allowed in case of Currency
    @param fixed_field_type : If field_data_type is Fixed(i.e. 2), then type of fixed value.
                              1:Dropdown, 2: Checkbox, 3: Radio buttons
    @param fixed_values :  If field_data_type is Fixed(i.e. 2), then array for values of
                            fixed_field_type. Eg. array(“Yes”,”No”)
    """
    list1 = []
    _data = {
            "client_key":_client_key,
            "erp_group_id":group_id,
            "erp_field_id":field_id,
            "field_label":label,
            "field_type":field_type,  # field_type - 1: Characters, 2: Numeric, 3: Date, 4: Time, 5: Currency
            "field_data_type":data_type,
            "no_of_chars":no_char,
            "decimal_places":decimal_place,
            "interval_allowed":allow,
            "measure_unit":unit,
            "currency_type":curr_type,
            "fixed_field_type":fix_field_type,
            "fixed_values":list1
            }
    group_fields = requests.post(_API_URL + "setGroupFields", data=_data, headers=headers)
    if group_fields.status_code == 200: 
        return {"status_code":group_fields.status_code, "field_id":group_fields.json().get('gomart_field_id'),
                "data":_data, "json_dump":group_fields.json()}
    else: 
        return {"status_code":group_fields.status_code, "data":_data}


def setOrderStatus(_API_URL, order_id, order_status, store_id, store_chain_id):
    _data = {
            "client_key":_client_key,
            "erp_order_id":order_id,
            "erp_order_status":order_status,
            "erp_store_id":store_id,
            "erp_store_chain_id":store_chain_id
            }
    group_fields_API = requests.post(_API_URL + "setOrderStatus", data=_data, headers=headers)
    if group_fields_API.status_code == 200: 
        return  {"order_id":group_fields_API.json().get("gomart_order_id"),
                 "json_dump":group_fields_API.json(),
                 "data":_data, "status_code":group_fields_API.status_code}
    else:
        return {"status_code":group_fields_API.status_code, "json_dump":group_fields_API.json(), "data":_data}
