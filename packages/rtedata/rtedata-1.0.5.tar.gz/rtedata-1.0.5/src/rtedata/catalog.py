from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Catalog:
    _structure: Dict[str, list[str]] = field(init=False, repr=False)

    def __post_init__(self):
        self.request_base_url = "https://digital.iservices.rte-france.com/open_api"
        self.docs_base_url = "https://data.rte-france.com/catalog/-/api/doc/user-guide"
        self.catalog_base_url = "https://data.rte-france.com/catalog/-/api"
      
        self._meta_mapping = {
            f"{self.request_base_url}/actual_generation/v1/" : {
                "docs_url": f"{self.docs_base_url}/Actual+Generation/1.1",
                "catalog_url": f"{self.catalog_base_url}/generation/Actual-Generation/v1.1",
                "category": "generation",
                "keys": {
                    "actual_generations_per_production_type": {"schema": {"record_path": "values", "meta": ["production_type"]}},
                    "actual_generations_per_unit": {"schema": {"record_path": "values", "meta": [["unit", "eic_code"], ["unit", "name"], ["unit", "production_type"]]}},
                    #"water_reserves": {"schema": {"record_path": "values", "meta": []}}, TBU
                    "generation_mix_15min_time_scale": {"schema": {"record_path": "values", "meta": ["production_type", "production_subtype"]}}
                }
            },
            
            f"{self.request_base_url}/generation_installed_capacities/v1/" : {
                "docs_url": f"{self.docs_base_url}/Generation+Installed+Capacities/1.1",
                "catalog_url": f"{self.catalog_base_url}/generation/Generation-Installed-Capacities/v1.1",
                "category": "generation",
                "keys": {
                    #"capacities_cpc": {"schema": {}},
                    #"capacities_per_production_type": {"schema": {"record_path": "values", "meta": []}}, 
                    "capacities_per_production_unit": {"schema": {"record_path": "values", "meta": [["production_unit", "code_eic"], ["production_unit", "name"], ["production_unit", "location"], ["production_unit", "code_eic_producteur"], ["production_unit", "name_producteur"]]}}
                }
            },
            
            f"{self.request_base_url}/unavailability_additional_information/v6/" : {
                "docs_url": f"{self.docs_base_url}/Unavailability+Additional+Information/6.0",
                "catalog_url": f"{self.catalog_base_url}/generation/Unavailability-Additional-Information/v6.0",
                "category": "generation",
                "keys": {
                    "other_market_information": {"schema": {"meta": ["identifier", "message_id", "version", "creation_date", "unavailability_type", "affected_asset_or_unit_eic_code", "affected_asset_or_unit_name", "affected_asset_or_unit_type", "affected_asset_or_unit_installed_capacity", "reason", "remarks", "status"]}},
                    "transmission_network_unavailabilities": {"schema": {"record_path": ["values_impacted_NTC"], "meta": ["identifier", "message_id", "version", "creation_date", "publication_date", "unavailability_type", "affected_asset_or_unit_eic_code", "affected_asset_or_unit_name", "affected_asset_or_unit_type", "affected_asset_or_unit_installed_capacity", "reason", "remarks", "event_status"]}}, 
                    "generation_unavailabilities": {"schema": {"record_path": ["values"], "meta": ["identifier", "version", "creation_date", "publication_date", "unavailability_type", "fuel_type", "market_participant", "market_participant_eic_code", "affected_asset_or_unit_eic_code", "affected_asset_or_unit_name", "affected_asset_or_unit_type", "affected_asset_or_unit_installed_capacity", "reason", "remarks", "event_status"]}}
                }
            },
            
            f"{self.request_base_url}/generation_forecast/v2/" : {
                "docs_url": f"{self.docs_base_url}/Generation+Forecast/2.1",
                "catalog_url": f"{self.catalog_base_url}/generation/Generation-Forecast/v2.1#",
                "category": "generation",
                "keys": {
                    "forecasts": {"schema": {"record_path": ["values"], "meta": ["type", "production_type", "sub_type"]}}
                },
            },
            
            f"{self.request_base_url}/balancing_energy/v4/" : {
                "docs_url": f"{self.docs_base_url}/Balancing+Energy/4.0",
                "catalog_url": f"{self.catalog_base_url}/market/Balancing-Energy/v4.0",
                "category": "market",
                "keys": {
                    "volumes_per_energy_type": {"schema": {"record_path": ["values"], "meta": ["resolution"]}},
                    "prices": {"schema": {"record_path": ["values"], "meta": ["resolution"]}},
                    "imbalance_data": {"schema": {"record_path": ["values"], "meta": ["resolution"]}},
                    "lead_times": {"schema": {"record_path": ["values"], "meta": ["resolution"]}},
                    "volumes_per_entity_type": {"schema": {"record_path": ["values"], "meta": ["resolution"]}},
                    "tso_offers": {"schema": {"record_path": ["values"], "meta": ["type", "tso_offering", "tso_activating"]}},
                    "volumes_per_reasons": {"schema": {"record_path": ["values"], "meta": ["resolution"]}}
                }
            },
            
            f"{self.request_base_url}/ecowatt/v5/" : {
                "docs_url": f"{self.docs_base_url}/Ecowatt/5.0",
                "catalog_url": f"{self.catalog_base_url}/consumption/Ecowatt/v5.0#",
                "category": "consumption",
                "keys": {
                    "signals": {"schema": {"record_path": ["values"], "meta": ['GenerationFichier', 'jour', 'dvalue', 'message']}}
                }
            },
            
            f"{self.request_base_url}/demand_response/v1/": {
                "docs_url": f"{self.docs_base_url}/231779",
                "catalog_url": f"{self.catalog_base_url}/consumption/Demand-Response/v1.1#",
                "category": "consumption",
                "keys": {
                    "volumes": {"schema": {"meta": ['start_date', 'end_date', 'updated_date', 'eic_code', 'name','trial_nebef_rules_agreement', 'trial_nebef_rules_qualification', 'nebef_rules_recognition', 'nebef_rules_qualification']}}
                }
            },
            
            f"{self.request_base_url}/tempo_like_supply_contract/v1/": {
                "docs_url": f"{self.docs_base_url}/Tempo+Like+Supply+Contract/1.1",
                "catalog_url": f"{self.catalog_base_url}/consumption/Tempo-Like-Supply-Contract/v1.1#",
                "category": "consumption",
                "keys": {
                    "tempo_like_calendars": {"schema": {"record_path": ["values"]}}
                }
            },
            
            f"{self.request_base_url}/consumption/v1/": {
                "docs_url": f"{self.docs_base_url}/Consumption/1.2",
                "catalog_url": f"{self.catalog_base_url}/consumption/Consumption/v1.2#",
                "category": "consumption",
                "keys": {
                    "annual_forecasts": {"schema": {"record_path": ["values"]}},
                    "weekly_forecasts": {"schema": {"record_path": ["values"], "meta": ["updated_date","peak"]}},
                    "short_term": {"schema": {"record_path": ["values"], "meta": ["type"]}}
                }
            },
            
            f"{self.request_base_url}/consolidated_consumption/v1/" : {
                "docs_url": f"{self.docs_base_url}/Consolidated+Consumption/1.0",
                "catalog_url": f"{self.catalog_base_url}/Consolidated-Consumption/v1.0#",
                "category": "consumption",
                "keys": {
                    "consolidated_power_consumption": {"schema": {"record_path": ["values"]}},
                    "consolidated_energy_consumption": {"schema": {"record_path": ["values"]}}
                }
            }
        }
      
        self._requests = {
            key: {
                "request_url": f"{base_url}{key}",
                "docs_url": api["docs_url"],
                "catalog_url": api["catalog_url"],
                "category": api["category"],
                "schema": details["schema"]
                }
                for base_url, api in self._meta_mapping.items()
                for key, details in api["keys"].items()
            }

    @property
    def keys(self) -> str:
        return list(self._requests.keys())
    
    def get_key_content(self, key: str) -> tuple[str]:
        key_content = self._requests.get(key, None)
        if key_content is None:
            raise KeyError(f"Request key '{key}' not in requests catalog")
        request_url = key_content.get("request_url")
        catalog_url = key_content.get("catalog_url")
        docs_url = key_content.get("docs_url", None)
        category = key_content.get("category")
        schema = key_content.get("schema")
        return request_url, catalog_url, docs_url, category, schema
    
    def to_markdown_by_category(self) -> str:
        from collections import defaultdict

        category_tables = defaultdict(list)

        for key in self._requests:
            request_url, catalog_url, docs_url, category, schema = self.get_key_content(key)
            docs_url = docs_url if docs_url is not None else "X"
            row = f"| `{key}` | *[Link]({catalog_url})* | *[Link]({docs_url})* |"
            category_tables[category].append(row)

        sections = []
        for category, rows in category_tables.items():
            section = [
                f"### 📂 {category.capitalize()} Data",
                "",
                "| *data_type* | Catalog URL | Documentation URL |",
                "|-------------------|------------------------|-------------------------|",
                *rows,
                ""  # Ajoute une ligne vide pour la séparation entre les sections
            ]
            sections.append("\n".join(section))

        return "\n\n".join(sections)

    def __repr__(self):
        _repr = "rtedata Catalog : \n"
        for i, key in enumerate(self._requests):
            request_url, catalog_url, docs_url, category, schema = self.get_key_content(key)
            _repr += f"{i} - {key} : \n"
            _repr += f"~> catalog url : {catalog_url} \n"
            if docs_url is not None:
                _repr += f"~> docs url : {docs_url} \n"
        return _repr
        
