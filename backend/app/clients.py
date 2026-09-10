from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import httpx
from .config import Settings
from .models import Product, SearchRequest


class TdSynnexClient(ABC):
    """Distributor boundary. Implementations return only normalized Product objects."""

    @abstractmethod
    async def search_products(self, request: SearchRequest) -> list[Product]: ...


def _product(index: int, category: str, maker: str, name: str, specs: dict[str, str], price: str | None,
             qty: int | None, countries: list[str] | None, lifecycle: str | None = "Active", orderable: bool = True) -> Product:
    now = datetime.now(timezone.utc)
    return Product(product_id=f"MOCK-{index:03}", sku=f"MOCK-SKU-{index:04}", manufacturer_part_number=f"MOCK-MPN-{index:04}",
        manufacturer=maker, model=f"Demo {index}", product_name=f"[MOCK] {name}", category=category,
        description=f"Demonstration-only {name.lower()} product; values are synthetic and not from TD SYNNEX.",
        technical_specifications=specs, unit_price=Decimal(price) if price else None, currency="USD",
        available_quantity=qty, warehouse="Mock LATAM Hub" if countries else None,
        fulfillment_region="Caribbean / Latin America" if countries else None, eligible_countries=countries,
        estimated_delivery=(now + timedelta(days=7)).date() if qty else None, warranty="3 years" if index % 4 else None,
        lifecycle_status=lifecycle, orderable=orderable, pricing_timestamp=now if price else None,
        inventory_timestamp=now if qty is not None else None)


MOCK_PRODUCTS = [
    _product(1,"Storage","Seagate","Exos 20TB Enterprise HDD",{"capacity":"20TB","form factor":"3.5-inch","interface":"SATA","speed":"7200 RPM","transfer rate":"285 MB/s","use":"enterprise NAS"},"389.00",18,["Jamaica","Barbados","Trinidad and Tobago","Panama"]),
    _product(2,"Storage","Western Digital","Ultrastar 20TB HDD",{"capacity":"20TB","form factor":"3.5-inch","interface":"SATA","speed":"7200 RPM","transfer rate":"269 MB/s","use":"enterprise storage"},"405.00",4,["Jamaica","Bahamas","Costa Rica"]),
    _product(3,"Storage","Toshiba","Enterprise 18TB HDD",{"capacity":"18TB","form factor":"3.5-inch","interface":"SATA","speed":"7200 RPM","transfer rate":"268 MB/s","use":"enterprise NAS"},"330.00",30,["Jamaica","Colombia"]),
    _product(4,"Storage","Seagate","Legacy 20TB HDD",{"capacity":"20TB","form factor":"3.5-inch","interface":"SATA","speed":"7200 RPM"},"299.00",20,["Jamaica"],"Discontinued",False),
    _product(5,"Storage","Synology","Rack NAS Appliance",{"capacity":"diskless","bays":"8","use":"enterprise NAS"},"1899.00",3,["Jamaica","Panama"]),
    _product(6,"Servers","Dell","PowerEdge Rack Server",{"cpu":"Xeon Silver","memory":"64GB","form factor":"2U","use":"virtualization"},"5299.00",5,["Jamaica","Mexico"]),
    _product(7,"Servers","HPE","ProLiant Tower Server",{"cpu":"Xeon E","memory":"32GB","form factor":"tower","use":"small business"},"2899.00",8,["Barbados","Trinidad and Tobago"]),
    _product(8,"Networking","Cisco","48-port Managed Switch",{"ports":"48","speed":"1GbE","uplinks":"10GbE","management":"managed"},"2199.00",12,["Jamaica","Panama","Colombia"]),
    _product(9,"Networking","Aruba","Wi-Fi 6 Access Point",{"wireless":"Wi-Fi 6","radios":"dual-band","use":"enterprise"},"699.00",40,["Jamaica","Bahamas"]),
    _product(10,"Networking","Ubiquiti","24-port PoE Switch",{"ports":"24","speed":"1GbE","power":"PoE+"},"489.00",0,["Jamaica","Costa Rica"]),
    _product(11,"End-user computing","Lenovo","ThinkPad Business Laptop",{"cpu":"Core Ultra 7","memory":"16GB","storage":"512GB SSD","display":"14-inch"},"1499.00",22,["Jamaica","Mexico"]),
    _product(12,"End-user computing","HP","ProBook Laptop",{"cpu":"Core i5","memory":"16GB","storage":"512GB SSD","display":"15.6-inch"},"999.00",15,["Trinidad and Tobago","Barbados"]),
    _product(13,"End-user computing","Dell","27-inch Business Monitor",{"display":"27-inch","resolution":"QHD","panel":"IPS"},"419.00",35,["Jamaica","Panama"]),
    _product(14,"Security","Fortinet","Next-generation Firewall",{"throughput":"10 Gbps","use":"branch security","support":"1 year"},"3299.00",6,["Jamaica","Dominican Republic"]),
    _product(15,"Security","Sophos","Endpoint Security License",{"term":"1 year","users":"100","delivery":"electronic"},"2400.00",999,["Jamaica","Brazil","Mexico"]),
    _product(16,"Licensing","Microsoft","Productivity Suite License",{"term":"1 year","users":"1","delivery":"electronic"},"145.00",9999,["Jamaica","Barbados","Colombia"]),
    _product(17,"Backup","Veeam","Backup Subscription",{"term":"1 year","workloads":"10","delivery":"electronic"},"1299.00",999,["Jamaica","Costa Rica"]),
    _product(18,"Backup","APC","1500VA UPS",{"capacity":"1500VA","topology":"line interactive","outlets":"8"},"649.00",7,["Jamaica","Bahamas"]),
    _product(19,"Storage","Kingston","Enterprise SSD",{"capacity":"3.84TB","form factor":"2.5-inch","interface":"SATA","use":"server"},None,11,["Jamaica","Panama"]),
    _product(20,"Security","Palo Alto Networks","Legacy Firewall",{"throughput":"5 Gbps","use":"branch security"},"1999.00",2,["Jamaica"],"End of life",False),
    _product(21,"Networking","Juniper","Core Router",{"throughput":"100 Gbps","use":"core network"},"9500.00",2,None),
    _product(22,"Servers","Cisco","Unknown-status Compute Node",{"cpu":"Xeon Gold","memory":"128GB"},"7800.00",3,["Jamaica"],None),
]


class MockTdSynnexClient(TdSynnexClient):
    async def search_products(self, request: SearchRequest) -> list[Product]:
        return [item.model_copy(deep=True) for item in MOCK_PRODUCTS]


class LiveTdSynnexClient(TdSynnexClient):
    """Placeholder until official API documentation and account contract are supplied.

    No endpoint, authentication flow, field mapping, region code, or retry semantics is
    assumed here. Configure only after validating the official account-specific docs.
    """
    def __init__(self, settings: Settings):
        self.settings = settings
        self._http = httpx.AsyncClient(timeout=settings.request_timeout_seconds)

    async def search_products(self, request: SearchRequest) -> list[Product]:
        raise NotImplementedError("Official TD SYNNEX API documentation is required to configure live mode")
