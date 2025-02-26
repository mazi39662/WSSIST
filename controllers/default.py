# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
import random
import string
import time
from datetime import datetime, timedelta, timezone

@auth.requires_login()
def index():
    return dict()

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def create_bundle():
    # Generate a random alphanumeric code
    random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Append current creation time to the code
    code_with_time = random_code + str(int(time.time()))

    form = SQLFORM(db.bundle_table)
    form.vars.item_code = code_with_time
    if form.process().accepted:
        response.flash = 'Bundle created successfully'
        redirect(URL('index'))
    
    return dict(form=form, random_code=code_with_time)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def view_bundle():
    bundle_id = request.args(0, cast=int, default=0)
    bundle = db.bundle_table(bundle_id) or redirect(URL('index'))
    return dict(bundle=bundle)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def edit_bundle():
    bundle_id = request.args(0, cast=int, default=0)
    bundle = db.bundle_table(bundle_id) or redirect(URL('index'))
    form = SQLFORM(db.bundle_table, bundle, deletable=True)
    if form.process().accepted:
        response.flash = 'Bundle updated successfully'
        redirect(URL('index'))
    return dict(form=form)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def delete_bundle():
    bundle_id = request.args(0, cast=int, default=0)
    db(db.bundle_table.id == bundle_id).delete()
    response.flash = 'Bundle deleted successfully'
    redirect(URL('index'))

# controllers/default.py

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def warehouse():
    warehouses = db().select(db.warehouse_table.ALL)
    return dict(warehouses=warehouses)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def create_warehouse():
    form = SQLFORM(db.warehouse_table)
    if form.process().accepted:
        response.flash = 'Warehouse created successfully'
        redirect(URL('warehouse'))
    return dict(form=form)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def view_warehouse():
    warehouse_id = request.args(0, cast=int, default=0)
    warehouse = db.warehouse_table(warehouse_id) or redirect(URL('warehouse'))
    return dict(warehouse=warehouse)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def edit_warehouse():
    warehouse_id = request.args(0, cast=int, default=0)
    warehouse = db.warehouse_table(warehouse_id) or redirect(URL('warehouse'))
    form = SQLFORM(db.warehouse_table, warehouse, deletable=True)
    if form.process().accepted:
        response.flash = 'Warehouse updated successfully'
        redirect(URL('warehouse'))
    return dict(form=form)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def delete_warehouse():
    warehouse_id = request.args(0, cast=int, default=0)
    db(db.warehouse_table.id == warehouse_id).delete()
    response.flash = 'Warehouse deleted successfully'
    redirect(URL('warehouse'))
    

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def item_index():
    bundle_id = request.args(0)
    branch = request.args(1)
   
    bargains = []

    if bundle_id is not None:
        items = db(db.bundle_item.bundle_id == bundle_id).select()
        
        reference_codes = [item.reference_code for item in items]

        total_purchased = 0

        for ref_code in reference_codes:
            total_purchased += db(
                                  (db.purchase_table.reference_code == ref_code)
                                 ).select(db.purchase_table.price.sum()).first()[db.purchase_table.price.sum()] or 0
        
        
        

        total_amount = 0
        total_price = 0
        total_quantity = 0
        total_sold = 0

        bundle_record = db(db.bundle_table.id == bundle_id).select(db.bundle_table.price).first()
        if bundle_record:
            total_price = bundle_record.price

        totalBundleSales = sum(item.price * item.sold for item in items)

        for item in items:
           
            bargains = db(db.bargain_table.bundle_item_id == item.id).select(orderby=~db.bargain_table.creation_time, limitby=(0, 1))
            item.has_bargains = bool(bargains)
            item.latest_bargain = bargains[0] if bargains else None
            
            if item.latest_bargain:
                try:
                    item.latest_bargain_price = float(item.latest_bargain.price)
                except AttributeError:
                    item.latest_bargain_price = 0
            else:
                item.latest_bargain_price = 0

            total_quantity += item.quantity
            total_sold += item.sold

            total_amount += item.amount

        return dict(
            items=items, 
            bundle_id=bundle_id, 
            bargains=bargains, 
            total_amount=total_amount, 
            total_price=total_price, 
            total_quantity=total_quantity, 
            total_sold=total_sold, 
            totalBundleSales=totalBundleSales, 
            total_purchased=total_purchased,
            
        )
    else:
        redirect(URL('default', 'bundles'))

    return dict(bundle_id=bundle_id, bargains=bargains)

@auth.requires_login()
def adjust_price():
    item_id = request.post_vars.item_id
    delta = int(request.post_vars.delta)

    item = db.bundle_item(item_id)
    if not item:
        return response.json({'status': 'error', 'message': 'Item not found'})

    # Define the steps for price adjustment
    price_steps = [1, 5, 10, 15, 20, 25, 35, 50, 75, 100, 150, 200, 250, 350, 450, 500]

    # Find the current price's index in the steps
    current_price = item.price
    try:
        current_index = price_steps.index(current_price)
    except ValueError:
        return response.json({'status': 'error', 'message': 'Price not in defined steps'})

    # Calculate the new price index based on delta
    new_index = current_index + delta

    # Ensure the new index is within bounds
    if new_index < 0:
        new_index = 0
    elif new_index >= len(price_steps):
        new_index = len(price_steps) - 1

    # Update the item's price
    new_price = price_steps[new_index]
    item.update_record(price=new_price)

    return response.json({'status': 'success', 'new_price': new_price})

@auth.requires_login()
def adjust_bargain_price():
    item_id = request.post_vars.item_id
    delta = int(request.post_vars.delta)

    # Find the item
    item = db.bundle_item(item_id)
    if not item:
        return response.json({'status': 'error', 'message': 'Item not found'})

    # Retrieve the latest bargain record or default to 0 if none exists
    latest_bargain = db(db.bargain_table.bundle_item_id == item_id).select(orderby=~db.bargain_table.creation_time).first()
    current_bargain_price = latest_bargain.bargain_price if latest_bargain else 0

    # Define price steps
    price_steps = [1, 5, 10, 15, 20, 25, 35, 50, 75, 100, 150, 200, 250, 350, 450, 500]

    # Find the index of the current bargain price
    try:
        current_index = price_steps.index(current_bargain_price)
    except ValueError:
        return response.json({'status': 'error', 'message': 'Bargain Price not in defined steps'})

    # Calculate the new bargain price index
    new_index = current_index + delta
    new_index = max(0, min(new_index, len(price_steps) - 1))
    new_bargain_price = price_steps[new_index]

    # Insert a new bargain record
    try:
        db.bargain_table.insert(
            bundle_item_id=item_id,
            bargain_price=new_bargain_price,
            bargain_type='#' + item_id + ' bargain',  # Use dynamic values if needed
            creation_time=request.now  # Use the current time for creation_time
        )
    except Exception as e:
        return response.json({'status': 'error', 'message': f'Insertion failed: {str(e)}'})

    return response.json({'status': 'success', 'new_bargain_price': new_bargain_price})


@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def create_item():
    bundle_id = request.args(0)

    while True:
        reference_code = '{:08d}'.format(random.randint(0, 99999999))

        existing_item = db(db.bundle_item.reference_code == reference_code).select().first()

        if not existing_item:
            break  

    form = SQLFORM(db.bundle_item)
    form.vars.bundle_id = bundle_id
    form.vars.reference_code = reference_code

    if form.process().accepted:
        response.flash = 'Item created successfully'
        redirect(URL('item_index', args=[bundle_id]))
    return dict(form=form, bundle_id=bundle_id)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def edit_item():
    item_id = request.args(0, cast=int, default=0)
    bundle_id = request.args(1)
    item = db.bundle_item(item_id) or redirect(URL('item_index'))
    form = SQLFORM(db.bundle_item, item, deletable=True)
    if form.process().accepted:
        response.flash = 'Item updated successfully'
        redirect(URL('item_index', args=[bundle_id]))
    return dict(form=form, item=item, item_id=item_id, bundle_id=bundle_id)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def view_item():
    item_id = request.args(0, cast=int, default=0)
    item = db.bundle_item(item_id) or redirect(URL('item_index'))
    return dict(item=item)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def delete_item():
    item_id = request.args(0, cast=int, default=0)
    db(db.bundle_item.id == item_id).delete()
    response.flash = 'Item deleted successfully'
    redirect(URL('item_index'))

# @auth.requires_login()


def search_price():
    branch_id = request.args(0)

    pht_timezone = timezone(timedelta(hours=8))
    current_date = datetime.now(pht_timezone).date()

    branch_name = "Unknown Branch"
    if branch_id:
        branch_info = db(db.branch_table.id == branch_id).select().first()
        if branch_info:
            branch_name = branch_info.name

    # Fetch purchases for the current date and branch
    purchase_table = db(
        (db.purchase_table.branch_id == branch_id) & 
        (db.purchase_table.purchase_time >= current_date) &
        (db.purchase_table.purchase_time < current_date + timedelta(days=1))
    ).select(orderby=~db.purchase_table.purchase_time)

    # Extract purchased reference codes from purchase_table
    purchased_reference_codes = {purchase.reference_code for purchase in purchase_table}

    # Fetch bundle IDs linked to the purchased reference codes
    bundle_ids = {
        bundle.bundle_id for bundle in db(
            db.bundle_item.reference_code.belongs(purchased_reference_codes)
        ).select(db.bundle_item.bundle_id)
    }

    # Fetch all bundle items where the bundle_id matches any in bundle_ids
    bundle_items = db(
        (db.bundle_item.bundle_id.belongs(bundle_ids))  # Match bundle IDs
    ).select(
        db.bundle_item.item.with_alias('item'),
        db.bundle_item.description.with_alias('description'),
        db.bundle_item.reference_code.with_alias('reference_code'),
        db.bundle_item.price.with_alias('price'),
        db.bundle_item.quantity.with_alias('quantity'),
        db.bundle_item.sold.with_alias('total_sold'),
        db.bundle_item.balance.with_alias('remaining_qty'),
        db.bundle_item.bundle_id.with_alias('bundle_id')
    )

    # Convert bundle items into summary data
    summary_data = [
        {
            'bundle_id': item.bundle_id,
            'item': item.item,
            'description': item.description,
            'reference_code': item.reference_code,
            'price': item.price,
            'total_sold': item.total_sold,
            'remaining_qty': item.remaining_qty
        }
        for item in bundle_items
    ]

    return dict(
        purchase_table=purchase_table, 
        branch_id=branch_id, 
        branch_name=branch_name, 
        current_date=current_date,
        summary_data=summary_data  # Now includes all bundle items related to purchased bundles
    )



import json

# @auth.requires_login()
def store_purchase():
    if request.env.request_method != 'POST':
        raise HTTP(405, "Method Not Allowed")
    
    data = json.loads(request.body.read().decode('utf-8'))

    # Iterate over each purchased item
    for purchase in data['purchases']:
        # Insert purchase into purchase_table
        db.purchase_table.insert(
            item=purchase['item'],
            reference_code=purchase['reference_code'],
            price=purchase['price'],
            branch_id=purchase.get('branch_id')  # Include branch_id if available
        )

        # Update the sold count for the purchased item in bundle_item table
        db_item = db(db.bundle_item.reference_code == purchase['reference_code']).select().first()
        if db_item:
            # Increment sold count by 1
            db_item.update_record(sold=db_item.sold + 1)
            # Calculate balance
            balance = db_item.quantity - db_item.sold
            # Update balance in bundle_item table
            db_item.update_record(balance=balance)

    return "Purchases stored successfully"

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def create_bargain():
    bundle_id = request.args(0)
    bargain_id = request.args(1)
    form = SQLFORM(db.bargain_table)

    form.vars.bundle_item_id = bundle_id

    if form.process().accepted:
        response.flash = 'Bargain created successfully'
        redirect(URL('list_bargains', args=[form.vars.bundle_item_id, bargain_id]))
    return dict(form=form, bargain_id=bargain_id)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def list_bargains():
    bundle_item_id = request.args(0)
    bargain_id = request.args(1)
    
    bargains = db(db.bargain_table.bundle_item_id == bundle_item_id).select()
    return dict(bargains=bargains, bundle_item_id=bundle_item_id, bargain_id=bargain_id)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def edit_bargain():
    bargain_id = request.args(0)
    args2 = request.args(1)
    form = SQLFORM(db.bargain_table, bargain_id)
    if form.process().accepted:
        response.flash = 'Bargain updated successfully'
        redirect(URL('list_bargains', args=[form.vars.bundle_item_id, args2]))
    return dict(form=form, bargain_id=bargain_id, args2=args2)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def delete_bargain():
    bargain_id = request.args(0)
    db(db.bargain_table.id == bargain_id).delete()
    response.flash = 'Bargain deleted successfully'
    redirect(URL('list_bargains', args=[request.args(1)]))

# @auth.requires(auth.has_membership(auth.id_group('admin')) or
#                auth.has_membership(auth.id_group('ceo')) or
#                auth.has_membership(auth.id_group('super-admin')))
def search_price_result():
    reference_code = request.vars.reference_code
    price = get_price_by_reference_code(reference_code)
    return dict(price=price)


# controllers/default.py
@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def branch_index():
    branches = db().select(db.branch_table.ALL)
    return dict(branches=branches)

@auth.requires_login()
def branch_pos():
    branches = db().select(db.branch_table.ALL)
    return dict(branches=branches)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def create_branch():
    form = SQLFORM(db.branch_table)
    if form.process().accepted:
        response.flash = 'Branch created successfully'
        redirect(URL('branch_index'))
    return dict(form=form)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def view_branch():
    branch_id = request.args(0, cast=int, default=0)
    branch = db.branch_table(branch_id) or redirect(URL('branch_index'))
    return dict(branch=branch)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def edit_branch():
    branch_id = request.args(0, cast=int, default=0)
    branch = db.branch_table(branch_id) or redirect(URL('branch_index'))
    form = SQLFORM(db.branch_table, branch, deletable=True)
    if form.process().accepted:
        response.flash = 'Branch updated successfully'
        redirect(URL('branch_index'))
    return dict(form=form, branch=branch)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def delete_branch():
    branch_id = request.args(0, cast=int, default=0)
    db(db.branch_table.id == branch_id).delete()
    response.flash = 'Branch deleted successfully'
    redirect(URL('branch_index'))

# bundles
@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def bundles():
    # Define the join query
    query = db.bundle_table.id > 0
    join = db.branch_table.on(db.bundle_table.branch == db.branch_table.id)

    # Define the fields to be displayed in the grid
    fields = [db.bundle_table.id,
              db.bundle_table.bundle_code,
              db.bundle_table.item_code,
              db.bundle_table.description,
              db.branch_table.name,
              db.branch_table.id]

    # Custom function to generate buttons for each row
    def generate_buttons(row):
        buttons = DIV(
            A('Items', _href=URL('default', 'item_index', args=[row.bundle_table.id, row.branch_table.id]), _class='btn btn-primary btn-sm'),
            A('View', _href=URL('default', 'view_bundle', args=[row.bundle_table.id]), _class='btn btn-info btn-sm'),
            A('Edit', _href=URL('default', 'edit_bundle', args=[row.bundle_table.id]), _class='btn btn-warning btn-sm')
        )
        if auth.has_membership(auth.id_group('super-admin')):
            buttons.append(A('Delete', _href=URL('default', 'delete_bundle', args=[row.bundle_table.id]), _class='btn btn-danger btn-sm'))
        return buttons

    # Create the grid
    grid = SQLFORM.grid(query,
                        fields=fields,
                        left=join,
                        deletable=False,
                        editable=False,
                        details=False,
                        create=True,
                        searchable=True,
                        paginate=30,
                        links=[dict(header='Actions', body=lambda row: generate_buttons(row))],
                        _class='custom-grid')

    return dict(grid=grid)



@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def pricecode_index():
    prices = db(db.price_code).select()
    return dict(prices=prices)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def pricecode_create():
    form = SQLFORM(db.price_code)
    if form.process().accepted:
        session.flash = 'Price code created successfully!'
        redirect(URL('pricecode_index'))
    return dict(form=form)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def pricecode_read():
    price_code = db.price_code(request.args(0)) or redirect(URL('pricecode_index'))
    return dict(price_code=price_code)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def pricecode_update():
    price_code = db.price_code(request.args(0)) or redirect(URL('pricecode_index'))
    form = SQLFORM(db.price_code, price_code, deletable=True)
    if form.process().accepted:
        session.flash = 'Price code updated successfully!'
        redirect(URL('pricecode_index'))
    return dict(form=form)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def pricecode_delete():
    db(db.price_code.id == request.args(0)).delete()
    session.flash = 'Price code deleted successfully!'
    redirect(URL('pricecode_index'))


# 
# Create Function
# Create Function
# Create Function
# Create Function
@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def create_purchase():
    branch_id = request.args(0, cast=int, default=None)
    form = SQLFORM(db.purchase_table, initial={'branch_id': branch_id})
    form.vars.branch_id = branch_id 
    print(branch_id)
    if form.process().accepted:
        response.flash = 'Purchase created successfully'
        redirect(URL('search_price', args=[branch_id]))
    return dict(form=form, branch_id=branch_id)



# Read Function
@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def purchase_index():
    branch_id = request.args(0, cast=int, default=None)
    purchases = db(db.purchase_table.branch_id == branch_id).select()
    return dict(purchases=purchases, branch_id=branch_id)

# Update Function
@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def edit_purchase():
    branch_id = request.args(0, cast=int, default=None)
    purchase_id = request.args(1, cast=int, default=0)
    purchase = db(db.purchase_table.id == purchase_id).select().first() or redirect(URL('purchase_index', args=[branch_id]))
    form = SQLFORM(db.purchase_table, purchase, deletable=True)
    if form.process().accepted:
        response.flash = 'Purchase updated successfully'
        redirect(URL('purchase_index', args=[branch_id]))
    return dict(form=form, purchase=purchase, branch_id=branch_id)

# Delete Function
@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def delete_purchase():
    branch_id = request.args(0, cast=int, default=None)
    purchase_id = request.args(1, cast=int, default=0)
    db(db.purchase_table.id == purchase_id).delete()
    response.flash = 'Purchase deleted successfully'
    redirect(URL('purchase_index', args=[branch_id]))


# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)
