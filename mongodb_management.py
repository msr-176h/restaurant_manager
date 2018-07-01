#! /usr/bin/env python
# -*- coding: utf-8 -*-

# import from generic libraries.
import pymongo
import json
from bson.objectid import ObjectId

# import from own programs.
import configs
import store_information

def connect_mongodb(db_name, collection_name, db_address=configs.DB_ADDRESS, db_port=configs.DB_PORT):
    """
    connect mongodb.

    Parameters
    ----------
    db_name: str
    collection_name: str
    db_address, default configs.DB_ADDRESS (localhost): str
    db_port, default configs.DB_PORT(27017): int

    Returns
    ----------
    co: 
        collection's object

    """
    #client = pymongo.MongoClient('localhost', 27017)
    client = pymongo.MongoClient(db_address, db_port)
    db = client[db_name]
    co = db[collection_name]

    return co

def is_exist_mongodb_entry(_id):
    """
    audit whether designated entry is existed in mongodb.

    Parameters
    ----------
    _id: str
        id of mongodb's entry.

    Returns
    ----------
    True: bool
        if entry is existed, returns True.
    False: bool
        if not, returns False.

    """
    collection = connect_mongodb(configs.DB_NAME, configs.COL_NAME_STORE)
    co = collection.find({'_id': _id})
    if co:
        return True
    else:
        return False


def insert_store(store_info):
    """
    insert new stores information to mongodb.

    Parameters
    ----------
    store_info: dict (JSON)

    Returns
    ----------
    bool 
        True: success.
        False: some errors are occured.

    """
    ###################################################################
    #store_info = {}
    #store_info['store_name'] = 'test store'
    #store_info['experience'] = {'num': 0, 'experience': []}
    #store_info['evaluation'] = {'average': 0, 'evaluation': []}
    #store_info['registered_date'] = '2018-06-17'
    #store_info['map'] = {'latitude': 123, 'longitude': 135, 'address': ''}
    #store_info['links'] = []
    #store_info['note'] = ''
    #store_info['tags'] = ['meat']
    ###################################################################
    collection = connect_mongodb(configs.DB_NAME, configs.COL_NAME_STORE)
    co = collection.insert_one(store_info)
    if co:
        return co
    else:
        return False


def return_store(_id):
    """
    return store information designated by "_id".

    Parameters
    ----------
    _id: str

    Returns
    ----------
    co: bson
        if designated store's information is existed, returns it. 
    False: bool
        if not, returns False.

    See als0
    ----------
    ret_all_stores()

    """
    collection = connect_mongodb(configs.DB_NAME, configs.COL_NAME_STORE)
    co = collection.find_one({'_id': ObjectId(_id)})
    print(_id)
    if co:
        return co
    else:
        return False


def return_all_stores(sort=None, order=None):
    """
    return all store's information.

    Parameters
    ----------
    N/A

    Returns
    ----------
    store_list: list of JSON
        if function is succeeded, returns store list. 
    False: bool
        if not, returns False (some errors are occured).

    Notes
    ----------
    "store_list" is list of JSON, following is example:
        [
            {'store_name': 'hoge', 'registerer': 'fuga', ...},
            {'store_name': 'foo', 'registerer': 'buz', ...}
        ]

    """
    print(sort)
    print(order)
    store_list = []
    collection = connect_mongodb(configs.DB_NAME, configs.COL_NAME_STORE)


    if sort == None:
        co = collection.find()
    else:
        if order == 'a':
            co = collection.find().sort(sort, pymongo.ASCENDING)
        else: # 'd' and others
            co = collection.find().sort(sort, pymongo.DESCENDING)
    if co:
        return co
    else:
        return False


def replace_store_information(_id, new_store_info):
    """
    replace store information designated by "_id" to new store's one.

    Parameters
    ----------
    _id: str
    new_store_info: dict

    Returns
    ----------
    True: bool
    False: bool

    """
    collection = connect_mongodb(configs.DB_NAME, configs.COL_NAME_STORE)
    co = collection.find_one({'_id': ObjectId(_id)})
    co = new_store_info
    co['_id'] = ObjectId(_id)
    res = collection.save(co)
    if res:
        return True
    else:
        return False


def delete_store(_id):
    """
    delete store information designated by "_id".

    Parameters
    ----------
    _id: str

    Returns
    ----------
    True: bool
        if store information is correctly deleted, returns True.
    False: bool
        if not, returns False.


    """
    collection = connect_mongodb(configs.DB_NAME, configs.COL_NAME_STORE)
    co = collection.remove({'_id': ObjectId(_id)})
    if co['n'] > 0:
        return True
    else:
        return False


def update_store_evaluation(_id, evaluation):
    """
    update store evaluation.

    Parameters
    ----------
    _id: str
    evaluation: dict

    Returns
    ----------
    True: bool
        if store evaluation is correctly updated, returns True.
    False: bool
        if not, returns False.


    """
    collection = connect_mongodb(configs.DB_NAME, configs.COL_NAME_STORE)
    co = collection.find_one({'_id': ObjectId(_id)})
    if not co:
        return False

    co['evaluation']['evaluations'].append(evaluation)
    # calc and update average score/fee and last_visited
    ave_score = 0.0
    ave_fee = 0
    for i, e in enumerate(co['evaluation']['evaluations']):
        if i == 0:
            last_visited = e['visited_date']
        else:
            if last_visited < e['visited_date']:
                last_visited = e['visited_date']
        ave_score += e['score']
        ave_fee += e['fee']
    ave_score = round((ave_score / len(co['evaluation']['evaluations'])), 2)
    ave_fee = int(ave_fee / len(co['evaluation']['evaluations']))
    co['evaluation']['average'] = ave_score
    co['average_fee'] = ave_fee
    co['last_visited'] = last_visited
    res = collection.save(co)
    if res:
        return True
    else:
        return False


def modify_eval(_id, index, new_eval, user_name):
    """
    modify store's (designated by "_id") evaluation (designated by "index").

    Parameters
    ----------
    _id: str
    index: int
        index of modification target
    user_name: str

    Returns
    ----------
    True: bool
        if store information is correctly modified, returns True.
    False: bool
        if not, returns False.
    errors: list
        if errors occured, its reasons are stored. if not, this list will 
        be empty list.


    """
    errors = []
    collection = connect_mongodb(configs.DB_NAME, configs.COL_NAME_STORE)
    co = collection.find_one({'_id': ObjectId(_id)})
    try:
        target_eval = co['evaluation']['evaluations'][index]
    except:
        errors.append('index is out if range.')
        return False, errors

    if target_eval['user'] in [user_name, 'admin']:
        result, errors = store_information.validate_store_evaluation(new_eval)
        if not result:
            return False, errors
        co['evaluation']['evaluations'][index] = new_eval
        # calc and update average score/fee and last_visited
        ave_score = 0.0
        ave_fee = 0
        last_visited = ''
        for i, e in enumerate(co['evaluation']['evaluations']):
            if i == 0:
                last_visited = e['visited_date']
            else:
                if last_visited < e['visited_date']:
                    last_visited = e['visited_date']
            ave_score += e['score']
            ave_fee += e['fee']
        if len(co['evaluation']['evaluations']) > 0:
            ave_score = round((ave_score / len(co['evaluation']['evaluations'])), 2)
            ave_fee = int(ave_fee / len(co['evaluation']['evaluations']))
        else:
            ave_score = 0.0
            ave_fee = 0
        co['evaluation']['average'] = ave_score
        co['average_fee'] = ave_fee
        co['last_visited'] = last_visited
        res = collection.save(co)
        return True, errors
    else:
        errors.append('evaluation can be only modified by registered/admin user.')
        return False, errors


def delete_eval(_id, index, user_name):
    """
    delete store's (designated by "_id") evaluation (designated by "index").

    Parameters
    ----------
    _id: str
    index: int
        index of delete target
    user_name: str

    Returns
    ----------
    True: bool
        if store information is correctly deleted, returns True.
    False: bool
        if not, returns False.
    errors: list
        if errors occured, its reasons are stored. if not, this list will 
        be empty list.


    """
    errors = []
    collection = connect_mongodb(configs.DB_NAME, configs.COL_NAME_STORE)
    co = collection.find_one({'_id': ObjectId(_id)})
    try:
        target_eval = co['evaluation']['evaluations'][index]
    except:
        errors.append('index is out if range.')
        return False, errors

    if target_eval['user'] in [user_name, 'admin']:
        del co['evaluation']['evaluations'][index]
        # calc and update average score/fee and last_visited
        ave_score = 0.0
        ave_fee = 0
        last_visited = ''
        for i, e in enumerate(co['evaluation']['evaluations']):
            if i == 0:
                last_visited = e['visited_date']
            else:
                if last_visited < e['visited_date']:
                    last_visited = e['visited_date']
            ave_score += e['score']
            ave_fee += e['fee']
        if len(co['evaluation']['evaluations']) > 0:
            ave_score = round((ave_score / len(co['evaluation']['evaluations'])), 2)
            ave_fee = int(ave_fee / len(co['evaluation']['evaluations']))
        else:
            ave_score = 0.0
            ave_fee = 0
        co['evaluation']['average'] = ave_score
        co['average_fee'] = ave_fee
        co['last_visited'] = last_visited
        res = collection.save(co)
        return True, errors
    else:
        errors.append('evaluation can be only deleted by registered/admin user.')
        return False, errors


if __name__ == '__main__':
    insert_store(1)
