from django.core.cache import cache

from hyakumori_crm.crm.schemas.contract import ContractType as ContractTypeEnum

from .models import ContractType


def get_all_contracttypes_map():
    result_cache = cache.get("get_all_contracttypes_map")
    if result_cache is not None:
        return result_cache
    result = dict(ContractType.objects.values_list("code", "name"))
    cache.set("get_all_contracttypes_map", result, None)
    return result


class ContractService:
    @classmethod
    def setup_contracts(cls):
        cache.delete("get_all_contracttypes_map")
        for contract_type in ContractTypeEnum:
            contract_type_instance, _ = ContractType.objects.get_or_create(
                name=contract_type.value
            )
            contract_type_instance.attributes["assignable"] = (
                contract_type.name != "fsc"
            )
            contract_type_instance.code = contract_type.name
            contract_type_instance.description = contract_type.value
            contract_type_instance.save()
