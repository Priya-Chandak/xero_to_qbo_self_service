
def final_report():
    print("inside final_report")
    from apps.home.routes import final_report_email_to_customer
    final_report_email_to_customer()