from datetime import datetime, timedelta

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def index():
    branches = db(db.branch_table).select()

    date_from = request.vars.date_from
    date_to = request.vars.date_to
    branch_id = request.vars.branch_id  
    default_date = datetime.now().date()

    if not (date_from and date_to):
        date_from = default_date
        date_to = date_from + timedelta(days=1)  # Default date_to to date_from + 1 day
    else:
        default_date = date_from
        date_to = datetime.strptime(date_to, "%Y-%m-%d")
        date_to = date_to.date()
    
    query = (db.bundle_table.creation_time >= date_from) & (db.bundle_table.creation_time < date_to)

    if branch_id:
        query &= (db.bundle_table.branch == int(branch_id))  

    bundle_table_data = db(query).select(orderby=~db.bundle_table.creation_time)

    for bundle in bundle_table_data:
        bundle_items = db(db.bundle_item.bundle_id == bundle.id).select()
        bundle.quantity_sum = sum(item.quantity for item in bundle_items)
        bundle.sold_sum = sum(item.sold for item in bundle_items)
        bundle.total_balance = sum(item.quantity - item.sold for item in bundle_items)
        bundle.total_prices_sold = sum(item.price * item.sold for item in bundle_items)

    return dict(
        bundle_table=bundle_table_data,
        bundle_table_data=bundle_table_data,
        default_date=default_date,
        date_from=date_from,
        date_to=date_to,
        branches=branches,  
        selected_branch_id=branch_id  
    )

def get_bundle_items():
    bundle_id = request.vars.bundle_id
    bundle_items = db(db.bundle_item.bundle_id == bundle_id).select()
    return response.json(dict(bundle_items=bundle_items))
