import arrow

from hyakumori_crm.crm.models import Forest
from django.db import transaction

from hyakumori_crm.crm.schemas.contract import ContractTypeStatus


def process_contract_status(forest, logs):
    contracts = []
    for contract in forest.contracts:
        if contract.get("end_date") is not None \
           and arrow.get(contract.get("end_date"), "YYYY-MM-DD") < arrow.utcnow()\
           and contract["status"] == ContractTypeStatus.negotiated:  # only update negotiated status
            old_status = contract.get("status")
            contract["status"] = ContractTypeStatus.expired
            logs.append(
                f"Updated status of contract {contract.get('type')} of Forest {forest.internal_id} (ID: {forest.id}), "
                f"from '{old_status}' to '{contract.get('status')}'")
        contracts.append(contract)
    forest.contracts = contracts
    # bypass signal
    Forest.objects.filter(pk=forest.pk).update(contracts=contracts)


def update_status_task():
    try:
        logs = []
        with transaction.atomic():
            for forest in Forest.objects.iterator():
                process_contract_status(forest, logs)
        if len(logs) > 0:
            print("\n".join(logs))
    except Exception as e:
        print(str(e))
