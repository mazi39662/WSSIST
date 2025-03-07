@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def bundle_bargain_request():
    fields = [
        db.bargain_requests.branch_name,
        db.bargain_requests.item_code,
        db.bargain_requests.item,
        db.bargain_requests.price_from,
        db.bargain_requests.price_to,
        db.bargain_requests.note,
        db.bargain_requests.request_date
    ]
    
    grid = SQLFORM.grid(db.bargain_requests, 
                        fields=fields,
                        create=False,
                        editable=False,
                        deletable=False,
                        details=True,
                        csv=True,
                        paginate=30,
                        orderby=~db.bargain_requests.request_date)
    return dict(grid=grid)


@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def manager_request():
    form = SQLFORM(db.bargain_requests).process(formname='new_record_form')
    
    fields = [
        db.bargain_requests.branch_name,
        db.bargain_requests.reference_code,
        db.bargain_requests.item_code,
        db.bargain_requests.item,
        db.bargain_requests.price_from,
        db.bargain_requests.price_to,
        db.bargain_requests.note,
        db.bargain_requests.request_date
    ]
    
    grid = SQLFORM.grid(db.bargain_requests, 
                        fields=fields,
                        create=True,
                        editable=True,
                        deletable=False,
                        details=True,
                        csv=False,
                        paginate=10,
                        orderby=~db.bargain_requests.request_date)
    
    return dict(grid=grid, form=form)

@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def review_item():
    return dict()


@auth.requires(auth.has_membership(auth.id_group('admin')) or
               auth.has_membership(auth.id_group('ceo')) or
               auth.has_membership(auth.id_group('super-admin')))
def fetch_cards():
    reference_code = request.vars.reference_code
    items_list = []
    if reference_code:
        items_query = db(db.bundle_item.reference_code.contains(reference_code))
        items = items_query.select()
        for item in items:
            bundle_info = db(db.bundle_table.id == item.bundle_id).select().first()
            if bundle_info:
                branch_info = db(db.branch_table.id == bundle_info.branch).select().first()
                branch_name = branch_info.name if branch_info else "Unknown Branch"
                bundle_description = bundle_info.description
                bundle_item_code = bundle_info.item_code
            else:
                branch_name = "Unknown Bundle"
                bundle_description = ""
                bundle_item_code = ""

            bargain = db(db.bargain_table.bundle_item_id == item.id).select(
                orderby=~db.bargain_table.creation_time,
                limitby=(0, 1)
            ).first()
            latest_bargain = bargain.bargain_price if bargain else None

            items_list.append({
                'id': item.id,
                'bundle_id': {
                    'id': bundle_info.id if bundle_info else "",
                    'branch': bundle_info.branch if bundle_info else "",
                    'item_code': bundle_item_code,
                    'description': bundle_description
                },
                'reference_code': item.reference_code,
                'price': item.price,
                'item': item.item,
                'description': item.description,
                'branch_name': branch_name,
                'latest_bargain': latest_bargain
            })
    return response.json(dict(items=items_list))

def fetch_cards_search():
    reference_code = request.vars.reference_code
    branch_id = request.vars.branch_id
    items_list = []

    if reference_code:
        # Query for bundle items matching the reference_code
        items_query = db(db.bundle_item.reference_code.contains(reference_code))

        # Iterate over each item
        items = items_query.select()
        for item in items:
            # Get the related bundle_table entry and ensure it matches the branch_id
            bundle_info = db(db.bundle_table.id == item.bundle_id).select().first()
            
            if bundle_info and bundle_info.branch == int(branch_id):  # Ensure the branch_id matches
                branch_info = db(db.branch_table.id == bundle_info.branch).select().first()
                branch_name = branch_info.name if branch_info else "Unknown Branch"
                bundle_description = bundle_info.description
                bundle_item_code = bundle_info.item_code
            else:
                branch_name = "Unknown Branch"
                bundle_description = ""
                bundle_item_code = ""

            # Skip items with "Unknown Branch"
            if branch_name == "Unknown Branch":
                continue

            # Get the latest bargain price for the bundle item
            bargain = db(db.bargain_table.bundle_item_id == item.id).select(
                orderby=~db.bargain_table.creation_time,
                limitby=(0, 1)
            ).first()
            latest_bargain = bargain.bargain_price if bargain else None

            # Add the item data to the response list
            items_list.append({
                'id': item.id,
                'bundle_id': {
                    'id': bundle_info.id if bundle_info else "",
                    'branch': bundle_info.branch if bundle_info else "",
                    'item_code': bundle_item_code,
                    'description': bundle_description
                },
                'reference_code': item.reference_code,
                'price': item.price,
                'item': item.item,
                'quantity': item.quantity,
                'sold': item.sold,
                'description': item.description,
                'branch_name': branch_name,
                'latest_bargain': latest_bargain
            })

    return response.json(dict(items=items_list))
