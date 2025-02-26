def index():
    import datetime
    
    # Get the selected date from the request
    selected_date = request.vars.get('selected_date')
    if selected_date:
        try:
            selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.date.today()  # Fallback to today if the date is invalid
    else:
        selected_date = datetime.date.today()
    
    # Define the start and end of the selected date
    start_of_selected_date = datetime.datetime.combine(selected_date, datetime.time.min)
    end_of_selected_date = datetime.datetime.combine(selected_date, datetime.time.max)
    
    # Fetch all purchases
    purchases = db().select(db.purchase_table.ALL)
    
    # Calculate the total sales price grouped by branch_id for the selected date
    total_sales_by_branch = db(
        (db.purchase_table.purchase_time >= start_of_selected_date) &
        (db.purchase_table.purchase_time <= end_of_selected_date)
    ).select(
        db.purchase_table.branch_id,
        db.branch_table.name,
        db.purchase_table.price.sum().coalesce_zero().with_alias('total_price'),
        left=db.branch_table.on(db.purchase_table.branch_id == db.branch_table.id),
        groupby=db.purchase_table.branch_id
    )
    
    # Convert the results to a dictionary for easier access in the view
    total_sales_dict = {row.branch_table.name: row.total_price for row in total_sales_by_branch}
    
    # Return purchases and total sales by branch name for the selected date
    return dict(purchases=purchases, total_sales_dict=total_sales_dict, selected_date=selected_date)
