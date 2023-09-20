import traceback

from apps.home.data_util import add_job_status
from apps.util.db_mongo import get_mongodb_database


def get_qbo_tax(job_id,task_id):
    try:
        db = get_mongodb_database()
        QBO_Tax = db["QBO_Tax"]

        Collection1 = db["QBO_Taxrate"]
        Collection2 = db["QBO_Taxcode"]

        qbo_taxrate1 = Collection1.find({'job_id':job_id})
        QBO_taxrate = []
        for p1 in qbo_taxrate1:
            QBO_taxrate.append(p1)

        qbo_taxcode1 = Collection2.find({'job_id':job_id})
        QBO_taxcode = []
        for p2 in qbo_taxcode1:
            QBO_taxcode.append(p2)

        arr = []
        for i in range(0, len(QBO_taxcode)):
            QuerySet = {}
            QuerySet1 = {}
            QuerySet['job_id']=job_id
            QuerySet["task_id"] = task_id
            QuerySet["taxcode_id"] = QBO_taxcode[i]["Id"]
            QuerySet["taxcode_name"] = QBO_taxcode[i]["Name"]

            if QBO_taxcode[i]["SalesTaxRateList"] != {"TaxRateDetail": []}:
                QuerySet["taxrate_id"] = QBO_taxcode[i]["SalesTaxRateList"][
                    "TaxRateDetail"
                ][0]["TaxRateRef"]["value"]
                QuerySet["taxrate_name"] = QBO_taxcode[i]["SalesTaxRateList"][
                    "TaxRateDetail"
                ][0]["TaxRateRef"]["name"]

                for j in range(0, len(QBO_taxrate)):
                    if QuerySet["taxrate_name"] == QBO_taxrate[j]["Name"]:
                        QuerySet1 = QBO_taxrate[j]["Rate"]
                    QuerySet["Rate"] = QuerySet1

                arr.append(QuerySet)

        for i1 in range(0, len(QBO_taxcode)):
            QuerySet = {}
            QuerySet1 = {}
            QuerySet['job_id']=job_id
            QuerySet["taxcode_id"] = QBO_taxcode[i1]["Id"]
            QuerySet["taxcode_name"] = QBO_taxcode[i1]["Name"]

            if QBO_taxcode[i1]["PurchaseTaxRateList"] != {"TaxRateDetail": []}:
                QuerySet["taxrate_id"] = QBO_taxcode[i1]["PurchaseTaxRateList"][
                    "TaxRateDetail"
                ][0]["TaxRateRef"]["value"]
                QuerySet["taxrate_name"] = QBO_taxcode[i1]["PurchaseTaxRateList"][
                    "TaxRateDetail"
                ][0]["TaxRateRef"]["name"]

                for j1 in range(0, len(QBO_taxrate)):
                    if QuerySet["taxrate_name"] == QBO_taxrate[j1]["Name"]:
                        QuerySet1 = QBO_taxrate[j1]["Rate"]

                    QuerySet["Rate"] = QuerySet1

                arr.append(QuerySet)

            else:
                pass

        QBO_Tax.insert_many(arr)

    except Exception as ex:
        traceback.print_exc()
        
