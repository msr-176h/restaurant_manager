#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Store management application powered by Flask.
"""
# import from generic libraries.
from flask import Flask, render_template, send_from_directory, request
from flask_httpauth import HTTPDigestAuth
from datetime import datetime
import os.path

# import from own programs.
import configs
import mongodb_management
import store_information

# initialization
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = configs.SECRET_KEY
auth = HTTPDigestAuth()
users = configs.USERS

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.route('/')
@auth.login_required
def home():
    """ 
    display home page.

    Parameters
    ----------
    N/A

    Returns
    ----------
    render_template
        to "index.html" as home page.

    """
    user_name = auth.username()
    return render_template('index.html', user_name=user_name)


@app.route('/store_list')
@auth.login_required
def store_list():
    """ 
    display list of stores.

    Parameters
    ----------
    N/A

    Returns
    ----------
    render_template
        to "store_list.html"

    """
    sort = request.args.get('sort', None)
    order = request.args.get('order', None)
    store_list = mongodb_management.return_all_stores(sort=sort, order=order)
    return render_template('store_list.html', store_list=store_list)


@app.route('/store_detail/<_id>')
@auth.login_required
def store_detail(_id):
    """ 
    render store's detailed information.

    Parameters
    ----------
    _id: str
        id of mongodb's entry.

    Returns
    ----------
    render_template
        to "store_list.html" with following parameters:
        - 
        - 

    """
    co = mongodb_management.return_store(_id)
    print(co)
    if co:
        return render_template('store_detail.html',
                                store_info=co)
    else:
        errors = ['designated store is not existed.']
        return render_template('store_list.html',
                                errors=errors)


@app.route('/delete_store/<_id>')
@auth.login_required
def delete_store(_id):
    """ 
    delete store's information.

    Parameters
    ----------
    _id: str
        id of mongodb's entry.

    Returns
    ----------
    render_template
        to "store_list.html" with following parameters:
        - store_list
        - successes (in case deletion is succeeded): success massage.
        - errors (in case deletion is failed): error massage.

    """
    result = mongodb_management.delete_store(_id)
    store_list = mongodb_management.return_all_stores()
    if result:
        successes = ['successfully deleted.']
        return render_template('store_list.html',
                                store_list=store_list,
                                successes=successes)
    else:
        errors = ['designated store is not existed.']
        return render_template('store_list.html',
                                store_list=store_list,
                                errors=errors)


@app.route('/register_store', methods=['GET', 'POST'])
@auth.login_required
def register_store():
    """ 
    register new store's information.

    Parameters
    ----------
    _id: str
        id of mongodb's entry.

    Returns
    ----------
    render_template to "register_store.html"/"store_list.html".

    Notes
    ----------
    In case GET method, just render registeration form.
    In case POST method, validate user's input. After that, 
    if input is collect, store information is registered.

    """
    if request.method == 'GET':
        return render_template('register_store.html')
    elif request.method == 'POST':
        store_info = store_information.request2store_info(request.form)
        result, errors = store_information.validate_store_information(store_info)
        if result:
            if store_info['map']['address'] != '':
                store_information.generate_store_map(store_info)
            res = mongodb_management.insert_store(store_info)
            if not res: # insert error
                errors = ['insertion was missed.']
                return render_template('register_store.html',
                                        errors=errors)
            store_list = mongodb_management.return_all_stores()
            successes = ['successfully registered.']
            return render_template('store_list.html',
                                    store_list=store_list,
                                    successes=successes)
        else:
            return render_template('register_store.html',
                                    errors=errors)
    else:
        store_list = mongodb_management.return_all_stores()
        errors = ['Invalid method.']
        return render_template('store_list.html',
                                store_list=store_list,
                                errors=errors)


@app.route('/modify_store/<_id>', methods=['GET', 'POST'])
@auth.login_required
def modify_store(_id):
    """ 
    modify store's information.

    Parameters
    ----------
    _id: str
        id of mongodb's entry.

    Returns
    ----------
    render_template
        to "store_list.html" with following parameters:
        - 
        - 

    Notes
    ----------
    In case GET method, just render modification form.
    In case POST method, validate user's input. After that, 
    if input is collect, registerd store information is modified
    as follws input.

    """
    user_name = auth.username()
    if request.method == 'GET':
        store_info = mongodb_management.return_store(_id)
        return render_template('modify_store.html', 
                                store_info=store_info)
    elif request.method == 'POST':
        store_info = mongodb_management.return_store(_id)
        new_store_info = mongodb_management.return_store(_id)
        candidate = {}
        candidate['tags'] = []
        candidate['links'] = [{}]
        candidate['map'] = {}
        for k, v in request.form.items():
            if k in ['tag1', 'tag2', 'tag3']:
                candidate['tags'].append(v)
            elif k in ['url', 'url_note']:
                candidate['links'][0][k] = v
            elif k in ['address']:
                candidate['map'][k] = v
            elif k in ['latitude', 'longitude']:
                if v == '':
                    candidate['map'][k] = 0
                else:
                    candidate['map'][k] = float(v)
            else:
                candidate[k] = v
        if 'save_dir' in store_info['map']:
            candidate['map']['save_dir'] = store_info['map']['save_dir']
        for k, v in candidate.items():
            if store_info[k] != v: # if value is updated
                new_store_info[k] = v
        #new_store_info = store_information.request2store_info(request.form)
        print(new_store_info)
        result, errors = store_information.validate_store_information(new_store_info)
        if result:
            if new_store_info['map']['address'] != '' and store_info['map']['address'] != new_store_info['map']['address']:
                file_name = new_store_info['store_name'] + '_' + new_store_info['registered_date'] + '.html'
                new_store_info['map']['save_dir'] = os.path.join(configs.MAP_DIR, file_name)
                new_store_info['map']['latitude'], new_store_info['map']['longitude'] = store_information.address2map_info(new_store_info['map']['address'])
                store_information.generate_store_map(new_store_info)
            res = mongodb_management.replace_store_information(_id, new_store_info)
            if not res: # insert error
                errors = ['modification was missed.']
                return render_template('modify_store.html',
                                        store_info=store_info,
                                        errors=errors)
            store_list = mongodb_management.return_all_stores()
            successes = ['successfully modified.']
            return render_template('store_list.html',
                                    store_list=store_list,
                                    successes=successes)
        else:
            return render_template('modify_store.html',
                                    store_info=store_info,
                                    errors=errors)
    else:
        store_list = mongodb_management.return_all_stores()
        errors = ['Invalid method.']
        return render_template('store_list.html',
                                store_list=store_list,
                                errors=errors)


@app.route('/evaluate_store/<_id>', methods=['GET', 'POST'])
@auth.login_required
def evaluate_store(_id):
    """ 
    evaluate store's qualily.

    Parameters
    ----------
    _id: str
        id of mongodb's entry.

    Returns
    ----------
    render_template to "register_store.html"/"store_list.html".

    Notes
    ----------
    In case GET method, just render evaluation form.
    In case POST method, validate user's input. After that, 
    if input is collect, evaluation is registerd.

    """
    store_info = mongodb_management.return_store(_id)
    user = auth.username()
    print(request)
    if request.method == 'GET':
        date = datetime.now().strftime('%Y-%m-%d')
        return render_template('evaluate_store.html',
                                date=date,
                                user=user,
                                store_info=store_info)
    elif request.method == 'POST':
        evaluation = store_information.request2store_evaluation(request.form)
        result, errors = store_information.validate_store_evaluation(evaluation)
        if result:
            res = mongodb_management.update_store_evaluation(_id, evaluation)
            if not res: # update error
                errors = ['evaluation was missed.']
                return render_template('evaluate_store.html',
                                        store_info=store_info,
                                        user=user,
                                        errors=errors)
            store_list = mongodb_management.return_all_stores()
            successes = ['successfully evaluated.']
            return render_template('store_list.html',
                                    store_list=store_list,
                                    successes=successes)
        else:
            return render_template('evaluate_store.html',
                                    store_info=store_info,
                                    user=user,
                                    errors=errors)
    else:
        store_list = mongodb_management.return_all_stores()
        errors = ['Invalid method.']
        return render_template('store_list.html',
                                store_list=store_list,
                                store_info=store_info,
                                errors=errors)


@app.route('/modify_eval/<_id>/<index>', methods=['GET', 'POST'])
@auth.login_required
def modify_eval(_id, index):
    """ 
    delete store's evaluation.

    Parameters
    ----------
    _id: str
        id of mongodb's entry.
    index: int
        index of delation target.

    Returns
    ----------
    render_template to "store_detail.html"/"modify_eval.html".

    Notes
    ----------
    In case GET method, just render modification form.
    In case POST method, validate user's input. After that, 
    if input is collect, store evaluation is updated.

    """
    user_name = auth.username()
    if request.method == 'GET':
        store_info = mongodb_management.return_store(_id)
        store_eval = store_info["evaluation"]["evaluations"][int(index)]
        store_eval['index'] = int(index)
        return render_template('modify_eval.html', 
                                store_info=store_info,
                                store_eval=store_eval)
    elif request.method == 'POST':
        new_eval = store_information.request2store_evaluation(request.form)
        result, errors = mongodb_management.modify_eval(_id, int(index), new_eval, user_name)
        store_info = mongodb_management.return_store(_id)
        if result:
            successes = ['successfully modified.']
            return render_template('store_detail.html',
                                    store_info=store_info,
                                    successes=successes)
        else:
            store_eval = store_info["evaluation"]["evaluations"][int(index)]
            store_eval['index'] = int(index)
            return render_template('modify_eval.html',
                                    store_info=store_info,
                                    store_eval=store_eval,
                                    errors=errors)
    else:
        store_list = mongodb_management.return_all_stores()


@app.route('/delete_eval/<_id>/<index>')
@auth.login_required
def delete_eval(_id, index):
    """ 
    delete store's evaluation.

    Parameters
    ----------
    _id: str
        id of mongodb's entry.
    index: int
        index of delation target.

    Returns
    ----------
    render_template
        to "store_detail.html" with following parameters:
        - store_info
        - successes (in case deletion is succeeded): success massage.
        - errors (in case deletion is failed): error massage.

    """
    user_name = auth.username()
    result, errors = mongodb_management.delete_eval(_id, int(index), user_name)
    store_info = mongodb_management.return_store(_id)
    if result:
        successes = ['successfully deleted.']
        return render_template('store_detail.html',
                                store_info=store_info,
                                successes=successes)
    else:
        return render_template('store_detail.html',
                                store_info=store_info,
                                errors=errors)


@app.route('/robots.txt')
def serve_robots():
    """
    serve robots.txt
    """
    return send_from_directory(app.static_folder, 'robots.txt')


@app.errorhandler(404)
def page_not_found(_):
    """
    render 404 page
    """
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=14514)
